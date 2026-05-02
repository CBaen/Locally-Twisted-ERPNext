#!/usr/bin/env python3
"""Read-only inventory of LT backend schema ownership and cascade surfaces.

This does not mutate ERPNext. It collects enough live state to decide what is
code-owned, what is DB-only, and where the next CRM cascade can safely attach.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import runpy
import subprocess
import sys
from collections import Counter, defaultdict
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
ROOT = pathlib.Path(__file__).resolve().parents[2]
HOOKS_PATH = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "hooks.py"
SEED_DIR = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "seed"

CORE_COUNTS = [
    "Lead",
    "Contact",
    "Customer",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Task",
    "Communication",
    "LT Service Type",
    "LT Lead Service Type",
    "LT Lead Photo",
    "LT Newsletter Signup",
]
SCHEMA_DOCTYPES = [
    "Custom Field",
    "Property Setter",
    "DocType",
    "Workspace",
    "Number Card",
    "Dashboard Chart",
    "Calendar View",
    "Kanban Board",
    "Role Profile",
    "Module Profile",
]
STALE_TERMS = [
    "Event Package",
    "Delivery Only",
    "Pickup Only",
]
INTENTIONAL_STALE_REFERENCES = {
    ("apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py", "Event Package"),
    ("apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py", "Delivery Only"),
    ("scripts/verify/contact_service_logic.py", "Event Package"),
    ("scripts/verify/lead_backend_intake_parity.py", "Event Package"),
    ("scripts/verify/lead_backend_intake_parity.py", "Delivery Only"),
}
SCAN_GLOBS = [
    "apps/locally_twisted/locally_twisted/**/*.py",
    "apps/locally_twisted/locally_twisted/**/*.html",
    "apps/locally_twisted/locally_twisted/**/*.js",
    "scripts/setup/*.py",
    "scripts/fix/*.py",
    "scripts/translate/*.py",
    "scripts/verify/*.py",
]
SYNC_OWNER_HINTS = {
    "sync_contact_intake_backend.py",
    "sync_crm_pipeline.py",
    "sync_stage_cascade.py",
    "sync_backend_workspaces.py",
    "add_product_description_fields.py",
}


def bench_execute(
    method: str,
    *,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    timeout: int = 90,
) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if args is not None:
        cmd.extend(["--args", json.dumps(args)])
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_all(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    return bench_execute("frappe.get_all", args=[doctype], kwargs=kwargs) or []


def get_count(doctype: str, filters: dict[str, Any] | None = None) -> int:
    kwargs: dict[str, Any] = {"doctype": doctype}
    if filters:
        kwargs["filters"] = filters
    return int(bench_execute("frappe.client.get_count", kwargs=kwargs) or 0)


def load_hooks() -> dict[str, Any]:
    return runpy.run_path(str(HOOKS_PATH))


def fixture_names(hooks: dict[str, Any], dt: str | None = None) -> list[str]:
    names: list[str] = []
    for fixture in hooks.get("fixtures", []) or []:
        if dt and fixture.get("dt") != dt:
            continue
        for filter_row in fixture.get("filters", []) or []:
            if len(filter_row) >= 3 and filter_row[0] == "name" and filter_row[1] == "in":
                names.extend(str(value) for value in filter_row[2])
    return sorted(set(names))


def ownership_sources() -> dict[str, str]:
    sources = {}
    for path in sorted((ROOT / "apps" / "locally_twisted" / "locally_twisted").glob("*.py")):
        if path.name == "__init__.py":
            continue
        sources[path.name] = path.read_text(encoding="utf-8", errors="replace")
    if SEED_DIR.exists():
        for path in sorted(SEED_DIR.glob("*.py")):
            if path.name == "__init__.py":
                continue
            sources[f"seed/{path.name}"] = path.read_text(encoding="utf-8", errors="replace")
    return sources


def classify_custom_fields(
    rows: list[dict[str, Any]],
    hooks: dict[str, Any],
    sources: dict[str, str] | None = None,
) -> dict[str, list[str]]:
    fixture_owned = set(fixture_names(hooks, "Custom Field"))
    source_text = "\n".join((sources or {}).values())
    sync_owned: set[str] = set()
    db_only: set[str] = set()

    for row in rows:
        name = str(row["name"])
        fieldname = str(row.get("fieldname") or "")
        if name in fixture_owned:
            continue
        quoted_fieldname = f'"{fieldname}"' in source_text or f"'{fieldname}'" in source_text
        lt_field = (
            fieldname.startswith("custom_")
            or fieldname.startswith("lt_")
            or fieldname.startswith("lt-")
        )
        if name in source_text or (lt_field and quoted_fieldname):
            sync_owned.add(name)
        else:
            db_only.add(name)

    code_owned = fixture_owned | sync_owned
    return {
        "code_owned": sorted(name for name in code_owned if any(row["name"] == name for row in rows)),
        "fixture_owned": sorted(name for name in fixture_owned if any(row["name"] == name for row in rows)),
        "sync_owned": sorted(sync_owned),
        "db_only": sorted(db_only),
    }


def read_scan_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for pattern in SCAN_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if path.is_dir() or "__pycache__" in path.parts:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith("scripts/verify/backend_schema_inventory"):
                continue
            sources[rel] = path.read_text(encoding="utf-8", errors="replace")
    return sources


def find_stale_terms(
    sources: dict[str, str],
    terms: list[str],
    ignored: set[tuple[str, str]] | None = None,
) -> list[dict[str, str]]:
    findings = []
    ignored = ignored or set()
    for path, text in sorted(sources.items()):
        for term in terms:
            if term in text and (path, term) not in ignored:
                findings.append({"path": path, "term": term})
    return findings


def collect_inventory() -> dict[str, Any]:
    hooks = load_hooks()
    code_sources = ownership_sources()
    scan_code = read_scan_sources()

    custom_fields = get_all(
        "Custom Field",
        fields=[
            "name",
            "dt",
            "fieldname",
            "label",
            "fieldtype",
            "options",
            "depends_on",
            "hidden",
            "read_only",
            "in_list_view",
            "in_standard_filter",
        ],
        order_by="dt asc, fieldname asc",
        limit_page_length=5000,
    )
    property_setters = get_all(
        "Property Setter",
        fields=["name", "doc_type", "doctype_or_field", "field_name", "property", "value"],
        order_by="doc_type asc, field_name asc, property asc",
        limit_page_length=5000,
    )
    doctypes = get_all(
        "DocType",
        fields=["name", "module", "custom", "istable", "issingle"],
        order_by="module asc, name asc",
        limit_page_length=5000,
    )

    counts = {doctype: get_count(doctype) for doctype in CORE_COUNTS}
    schema_counts = {doctype: get_count(doctype) for doctype in SCHEMA_DOCTYPES}

    custom_field_ownership = classify_custom_fields(custom_fields, hooks, code_sources)
    stale_findings = find_stale_terms(scan_code, STALE_TERMS, ignored=INTENTIONAL_STALE_REFERENCES)

    custom_fields_by_dt = Counter(str(row.get("dt")) for row in custom_fields)
    property_setters_by_doc = Counter(str(row.get("doc_type")) for row in property_setters)
    custom_doctypes = [
        row for row in doctypes
        if row.get("custom") or row.get("module") == "Locally Twisted" or str(row.get("name", "")).startswith("LT ")
    ]

    pipeline_counts = get_all(
        "Lead",
        fields=["custom_pipeline_stage as stage", "count(name) as count"],
        group_by="custom_pipeline_stage",
        order_by="custom_pipeline_stage asc",
        limit_page_length=100,
    )
    sales_order_dates = get_all(
        "Sales Order",
        fields=["delivery_date", "count(name) as count"],
        group_by="delivery_date",
        order_by="delivery_date asc",
        limit_page_length=100,
    )
    task_stage_counts = get_all(
        "Task",
        fields=["custom_pipeline_stage as stage", "status", "count(name) as count"],
        group_by="custom_pipeline_stage, status",
        order_by="custom_pipeline_stage asc, status asc",
        limit_page_length=100,
    )

    return {
        "core_counts": counts,
        "schema_counts": schema_counts,
        "custom_fields_by_dt": dict(sorted(custom_fields_by_dt.items())),
        "property_setters_by_doc": dict(sorted(property_setters_by_doc.items())),
        "custom_doctypes": custom_doctypes,
        "custom_field_ownership": custom_field_ownership,
        "fixture_names": {
            "Custom Field": fixture_names(hooks, "Custom Field"),
            "Item Group": fixture_names(hooks, "Item Group"),
            "Item Attribute": fixture_names(hooks, "Item Attribute"),
        },
        "sync_owner_scripts": sorted(name for name in code_sources if pathlib.Path(name).name in SYNC_OWNER_HINTS),
        "stale_findings": stale_findings,
        "intentional_stale_references": [
            {"path": path, "term": term}
            for path, term in sorted(INTENTIONAL_STALE_REFERENCES)
        ],
        "pipeline_counts": pipeline_counts,
        "sales_order_dates": sales_order_dates,
        "task_stage_counts": task_stage_counts,
    }


def emit_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# Backend Schema Inventory",
        "",
        "## Core Counts",
        "",
    ]
    for key, value in inventory["core_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Schema Counts", ""])
    for key, value in inventory["schema_counts"].items():
        lines.append(f"- {key}: {value}")

    ownership = inventory["custom_field_ownership"]
    lines.extend(["", "## Custom Field Ownership", ""])
    lines.append(f"- Code-owned total: {len(ownership['code_owned'])}")
    lines.append(f"- Fixture-owned: {', '.join(ownership['fixture_owned']) or 'none'}")
    lines.append(f"- Sync-owned total: {len(ownership['sync_owned'])}")
    lines.append(f"- DB-only total: {len(ownership['db_only'])}")
    for name in ownership["db_only"]:
        lines.append(f"  - {name}")

    lines.extend(["", "## Custom Fields By DocType", ""])
    for key, value in inventory["custom_fields_by_dt"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Property Setters By DocType", ""])
    for key, value in inventory["property_setters_by_doc"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "## Custom / LT DocTypes", ""])
    for row in inventory["custom_doctypes"]:
        flags = []
        if row.get("istable"):
            flags.append("child table")
        if row.get("issingle"):
            flags.append("single")
        flag_text = f" ({', '.join(flags)})" if flags else ""
        lines.append(f"- {row['name']} - module {row.get('module')}{flag_text}")

    lines.extend(["", "## Current Pipeline Counts", ""])
    for row in inventory["pipeline_counts"]:
        lines.append(f"- {row.get('stage') or '(blank)'}: {row.get('count')}")

    lines.extend(["", "## Task Stage Counts", ""])
    for row in inventory["task_stage_counts"]:
        lines.append(f"- {row.get('stage') or '(blank)'} / {row.get('status')}: {row.get('count')}")

    lines.extend(["", "## Sales Order Booking Dates", ""])
    for row in inventory["sales_order_dates"]:
        lines.append(f"- {row.get('delivery_date') or '(blank)'}: {row.get('count')}")

    lines.extend(["", "## Stale Term Scan", ""])
    if inventory["stale_findings"]:
        for row in inventory["stale_findings"]:
            lines.append(f"- {row['term']}: {row['path']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Intentional Old-Label Guardrails", ""])
    for row in inventory["intentional_stale_references"]:
        lines.append(f"- {row['term']}: {row['path']}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    args = parser.parse_args()

    try:
        inventory = collect_inventory()
    except Exception as exc:
        print("[BACKEND SCHEMA INVENTORY] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True, default=str))
    else:
        print(emit_markdown(inventory))
        print("[BACKEND SCHEMA INVENTORY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
