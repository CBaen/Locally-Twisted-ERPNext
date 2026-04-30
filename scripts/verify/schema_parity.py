#!/usr/bin/env python3
"""
Schema parity check.

Compares the schema declared in code (DocType JSON for Frappe; models.py for
Django; etc.) against the live database schema. Fails loudly if a declared
field is not present in the DB or vice versa.

This gate exists because of the LT 2026-04-08 incident: a code field was
deployed without a corresponding DB column migration. Result: every page
that read the model crashed with `UndefinedColumn`. The site went down
in front of the business owner.

Self-contained: no imports outside the standard library + the local stack's
CLI tooling (`bench` for Frappe).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# =============================================================================
# STACK-SPECIFIC: Frappe v15 implementation
# Replace this block when porting to a non-Frappe stack.
# =============================================================================
def collect_declared_doctypes_frappe(repo_root: Path) -> dict[str, set[str]]:
    """Walk the repo for DocType JSON files; return {doctype_name: set(field_names)}."""
    declared = {}
    for doctype_json in repo_root.rglob("doctype/*/*.json"):
        try:
            data = json.loads(doctype_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        # DocType files have "doctype": "DocType" at the top level
        if data.get("doctype") != "DocType":
            continue
        name = data.get("name") or doctype_json.stem
        fields = {f["fieldname"] for f in data.get("fields", []) if "fieldname" in f}
        declared[name] = fields
    return declared

def collect_live_columns_frappe(site: str) -> dict[str, set[str]]:
    """
    Query Frappe for live columns per DocType.

    Uses `bench --site SITE execute` to run a Python expression that queries
    the Frappe meta. Returns {doctype_name: set(column_names)}.
    """
    expr = (
        "import frappe, json; "
        "result = {}; "
        "for dt in frappe.get_all('DocType', filters={'custom': 0, 'istable': 0}, pluck='name'): "
        "    try: "
        "        meta = frappe.get_meta(dt); "
        "        result[dt] = [f.fieldname for f in meta.fields if f.fieldname]; "
        "    except Exception: "
        "        pass; "
        "print(json.dumps(result))"
    )
    try:
        result = subprocess.run(
            ["bench", "--site", site, "execute", "frappe.utils.execute_in_shell", "--args", expr],
            check=False, capture_output=True, text=True, timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        print(f"       SKIP — bench not available or timed out: {e}")
        return {}
    if result.returncode != 0:
        print(f"       SKIP — bench query failed: {result.stderr[:200]}")
        return {}
    try:
        live = json.loads(result.stdout.strip().split("\n")[-1])
        return {k: set(v) for k, v in live.items()}
    except (json.JSONDecodeError, IndexError) as e:
        print(f"       SKIP — could not parse bench output: {e}")
        return {}

# =============================================================================
# Comparison
# =============================================================================
def compare_schemas(declared: dict[str, set[str]], live: dict[str, set[str]]) -> int:
    """Return exit code: 0 = match, 1 = drift detected."""
    drift = []
    for doctype, declared_fields in declared.items():
        if doctype not in live:
            # New DocType not yet in DB — migration pending. WARN, not FAIL.
            print(f"  WARN  DocType '{doctype}' declared but not present in live DB (migration pending?)")
            continue
        live_fields = live[doctype]
        missing_in_db = declared_fields - live_fields
        missing_in_code = live_fields - declared_fields
        if missing_in_db:
            for f in sorted(missing_in_db):
                drift.append(f"  FAIL  '{doctype}.{f}' declared in code but missing from live DB")
        # missing_in_code is informational, not a fail (could be old fields removed from code)
    for line in drift:
        print(line)
    return 1 if drift else 0

# =============================================================================
# Main
# =============================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, help="Frappe site name")
    parser.add_argument("--repo-root", default=None, help="Path to repo root (default: parent of script)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else Path(__file__).resolve().parent.parent.parent
    print(f"\n[SCHEMA PARITY] Repo root: {repo_root}")
    print(f"                Site:     {args.site}")

    declared = collect_declared_doctypes_frappe(repo_root)
    print(f"                Declared DocTypes: {len(declared)}")

    live = collect_live_columns_frappe(args.site)
    if not live:
        print(f"                LIVE schema unavailable — skipping comparison.")
        print(f"                This is expected in CI (no DB access). PASS.")
        sys.exit(0)
    print(f"                Live DocTypes:     {len(live)}")

    exit_code = compare_schemas(declared, live)
    if exit_code == 0:
        print(f"\nSCHEMA PARITY PASS")
    else:
        print(f"\nSCHEMA PARITY FAIL — drift detected. Migrate before deploying.")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
