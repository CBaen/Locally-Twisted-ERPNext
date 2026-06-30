#!/usr/bin/env python3
"""Preview Product Setup -> runtime projection from a read-only audit JSON.

This helper is intentionally offline: it reads one caller-provided audit JSON
file and writes/prints a proposed diff. It performs no API calls, credential
loading, cache clearing, or ERPNext mutation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PRICE_KEYS = (
    "exact_checkout_price",
    "checkout_price",
    "base_price",
    "price",
    "price_list_rate",
    "rate",
    "amount",
)
ITEM_CODE_KEYS = ("item_code", "target_item_code", "variant_item_code", "sku", "item")
PRODUCT_SETUP_STORY_KEYS = (
    "product_story",
    "story",
    "about_this_design",
    "about",
    "description",
    "product_description",
)
PRODUCT_SETUP_DETAILS_KEYS = (
    "product_details",
    "details",
    "included",
    "whats_included",
    "what_is_included",
    "long_description",
)
WEBSITE_STORY_KEYS = (
    "lt_brand_description",
    "brand_description",
    "web_long_description",
    "description",
)
WEBSITE_DETAILS_KEYS = (
    "lt_product_details",
    "product_details",
    "details",
    "website_description",
)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        audit = read_audit_json(args.audit_json)
        report = build_projection_report(audit, Path(args.audit_json))
        write_output(report, args.output, pretty=args.pretty)
    except ProjectionBlocked as exc:
        print(f"[LT PRODUCT SETUP PROJECTION PREVIEW] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP PROJECTION PREVIEW] FAIL: {exc}", file=sys.stderr)
        return 1

    has_drift = bool(report["drift_summary"]["overall_drift"])
    has_blockers = bool(report["blockers"])
    if args.fail_on_drift and (has_drift or has_blockers):
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-json", required=True, help="Read-only audit JSON produced by lt_live_readonly_product_api_audit.py.")
    parser.add_argument("--output", help="Optional output JSON path. Defaults to stdout.")
    parser.add_argument("--fail-on-drift", action="store_true", help="Exit nonzero when drift or blockers are present.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args(argv)


class ProjectionBlocked(RuntimeError):
    """Raised only for invalid local input/output, not business drift."""


def read_audit_json(path_value: str) -> dict[str, Any]:
    path = Path(path_value)
    if not path.exists():
        raise ProjectionBlocked(f"audit JSON does not exist: {path}")
    if path.is_dir():
        raise ProjectionBlocked(f"audit JSON path is a directory: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ProjectionBlocked("audit JSON root must be an object")
    return payload


def build_projection_report(audit: dict[str, Any], audit_path: Path) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    for failure in audit.get("failures") or []:
        add_blocker(blockers, "source_audit_failure", str(failure), "failures")
    blueprint_doc = merged_dicts(
        get_dict(audit, "blueprint"),
        get_dict(audit, "product_setup"),
        get_dict(audit, "blueprint_summary"),
        get_dict_path(audit, ("content_summary", "blueprint_content_fields")),
    )
    website_item_doc = merged_dicts(
        get_dict(audit, "website_item"),
        get_dict(audit, "website_item_summary"),
        get_dict_path(audit, ("content_summary", "website_item_content_fields")),
    )
    rows = get_dict(audit, "rows")
    blueprint_price_rows = first_list(
        get_list(rows, "blueprint_price_rows"),
        get_list(blueprint_doc, "price_rows"),
        get_list(audit, "blueprint_price_rows"),
        get_list(audit, "price_rows"),
    )
    item_price_rows = first_list(
        get_list(rows, "item_prices"),
        get_list(audit, "item_prices"),
        get_list(audit, "item_price_rows"),
    )
    variants = first_list(get_list(rows, "variants"), get_list(audit, "variants"))

    price_authority = extract_price_authority(blueprint_doc, blueprint_price_rows, audit, blockers)
    item_price_projection = build_item_price_projection(price_authority, item_price_rows, variants, blockers)
    copy_projection = build_copy_projection(blueprint_doc, website_item_doc, blockers)

    price_drift = bool(item_price_projection["changes"])
    copy_drift = bool(copy_projection["changes"])
    runtime_rates = sorted({money_to_json(row["current_rate"]) for row in item_price_projection["runtime_rows"]})

    public_summary = get_dict(audit, "public_summary")
    product_identifier = {
        "product_setup": first_present(blueprint_doc, ("name", "product_slug", "slug")),
        "item_code": first_present(website_item_doc, ("item_code",)) or first_present(blueprint_doc, ("target_item_code", "item_code")),
        "website_item": first_present(website_item_doc, ("name", "website_item", "target_website_item"))
        or first_present(blueprint_doc, ("target_website_item", "website_item")),
        "product_name": first_present(blueprint_doc, ("product_name", "item_name", "title"))
        or first_present(website_item_doc, ("web_item_name", "item_name", "title")),
    }
    route = first_present(website_item_doc, ("route", "public_route", "website_route")) or audit.get("route")
    if route:
        product_identifier["route"] = route
    else:
        add_blocker(blockers, "missing_route", "Audit JSON did not include a public route.", "website_item_summary.route")

    report = {
        "product_identifier": product_identifier,
        "route": route,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "approval_state": {
            "preview_only": True,
            "mutation_approved": False,
            "live_status_change_approved": False,
            "requires_pre_mutation_packet": True,
        },
        "drift_summary": {
            "overall_drift": price_drift or copy_drift,
            "blocker_count": len(blockers),
            "price": {
                "drift_detected": price_drift,
                "product_setup_price": money_to_json(price_authority.get("proposed_rate")),
                "product_setup_price_basis": price_authority.get("basis"),
                "product_setup_price_row_count": len(blueprint_price_rows),
                "runtime_item_price_values": runtime_rates,
                "runtime_item_price_row_count": len(item_price_rows),
                "public_price_strings": public_summary.get("price_strings"),
            },
            "copy": {
                "drift_detected": copy_drift,
                "suggested_change_count": len(copy_projection["changes"]),
                "requires_business_copy_approval": bool(copy_projection["changes"]),
            },
        },
        "blockers": blockers,
        "limitations": preview_limitations(audit),
        "proposed_changes": {
            "item_prices": item_price_projection["changes"],
            "website_item_copy": copy_projection["changes"],
        },
        "rollback_targets": {
            "item_prices": item_price_projection["rollback_targets"],
            "website_item_copy": copy_projection["rollback_targets"],
        },
        "evidence_sources": {
            "audit_json": str(audit_path),
            "audit_generated_at": audit.get("generated_at"),
            "audit_scope": audit.get("scope"),
            "top_level_keys": sorted(audit.keys()),
            "price_rows_path": "rows.blueprint_price_rows",
            "item_price_rows_path": "rows.item_prices",
            "product_setup_copy_path": "content_summary.blueprint_content_fields",
            "website_item_copy_path": "content_summary.website_item_content_fields",
        },
    }
    return report


def preview_limitations(audit: dict[str, Any]) -> list[dict[str, str]]:
    limitations = [
        {
            "code": "field_level_preview_only",
            "message": "This preview compares saved audit fields only; it does not approve cache clear, deploy, live write, payment, document, or customer-message action.",
        },
        {
            "code": "copy_requires_business_approval",
            "message": "Copy differences are suggestions only until the customer-approved public copy authority is decided.",
        },
        {
            "code": "rollback_snapshot_incomplete",
            "message": "Rollback targets are limited to fields present in the input artifact; a pre-mutation packet must capture full row snapshots before any write.",
        },
    ]
    if not audit.get("brand_lane"):
        limitations.append(
            {
                "code": "brand_lane_not_proved",
                "message": "The input artifact does not prove row-level brand lane authority.",
            }
        )
    if not audit.get("active_product_setup_uniqueness"):
        limitations.append(
            {
                "code": "active_product_setup_uniqueness_not_proved",
                "message": "The input artifact does not prove one active Product Setup per target item, route, and brand lane.",
            }
        )
    return limitations


def extract_price_authority(
    blueprint_doc: dict[str, Any],
    blueprint_price_rows: list[dict[str, Any]],
    audit: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    base_price, base_key = first_money(blueprint_doc, ("base_price", "checkout_price", "price"))
    row_prices = [extract_row_price(row) for row in blueprint_price_rows]
    row_prices = [row for row in row_prices if row["price"] is not None]
    row_price_values = {row["price"] for row in row_prices}

    if not row_prices:
        summary_values = get_list(get_dict(audit, "price_summary"), "blueprint_price_row_values")
        row_price_values = {value for value in (parse_money(value) for value in summary_values) if value is not None}

    authority: dict[str, Any] = {
        "base_price": base_price,
        "base_price_key": base_key,
        "row_prices": row_prices,
        "row_price_values": row_price_values,
        "proposed_rate": None,
        "basis": None,
        "item_code_price_map": {},
    }

    if row_prices and len(row_price_values) == 1:
        proposed_rate = next(iter(row_price_values))
        if base_price is not None and proposed_rate != base_price:
            add_blocker(
                blockers,
                "price_authority_conflict",
                "Product Setup base price and exact price rows disagree.",
                "blueprint_summary.base_price + rows.blueprint_price_rows",
            )
            return authority
        authority["proposed_rate"] = proposed_rate
        authority["basis"] = "uniform_product_setup_exact_price_rows"
        return authority

    item_code_price_map: dict[str, Decimal] = {}
    duplicate_item_codes: set[str] = set()
    for row in row_prices:
        item_code = first_present(row["row"], ITEM_CODE_KEYS)
        if not item_code or row["price"] is None:
            continue
        item_code = str(item_code)
        if item_code in item_code_price_map and item_code_price_map[item_code] != row["price"]:
            duplicate_item_codes.add(item_code)
        item_code_price_map[item_code] = row["price"]
    if duplicate_item_codes:
        add_blocker(
            blockers,
            "ambiguous_price_rows",
            f"Product Setup has conflicting exact prices for item codes: {sorted(duplicate_item_codes)}.",
            "rows.blueprint_price_rows",
        )
    elif item_code_price_map and len(item_code_price_map) == len(row_prices):
        authority["item_code_price_map"] = item_code_price_map
        authority["basis"] = "product_setup_price_rows_by_item_code"
        return authority

    if base_price is not None and not row_prices:
        authority["proposed_rate"] = base_price
        authority["basis"] = f"product_setup_{base_key}"
        return authority

    add_blocker(
        blockers,
        "missing_product_setup_price_authority",
        "Audit JSON did not include a uniform or item-code-mappable Product Setup price authority.",
        "blueprint_summary.base_price + rows.blueprint_price_rows",
    )
    return authority


def build_item_price_projection(
    authority: dict[str, Any],
    item_price_rows: list[dict[str, Any]],
    variants: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    rollback_targets: list[dict[str, Any]] = []
    runtime_rows: list[dict[str, Any]] = []

    if not item_price_rows:
        add_blocker(blockers, "missing_item_price_rows", "Audit JSON did not include Item Price rows.", "rows.item_prices")
        return {"changes": changes, "rollback_targets": rollback_targets, "runtime_rows": runtime_rows}

    proposed_uniform_rate = authority.get("proposed_rate")
    item_code_price_map = authority.get("item_code_price_map") or {}
    basis = authority.get("basis")
    if proposed_uniform_rate is not None and not count_compatible(authority, item_price_rows, variants):
        add_blocker(
            blockers,
            "ambiguous_uniform_price_projection",
            "Uniform Product Setup price rows are not count-compatible with runtime Item Price rows.",
            "rows.blueprint_price_rows + rows.item_prices",
        )
        return {"changes": changes, "rollback_targets": rollback_targets, "runtime_rows": runtime_rows}

    for row in item_price_rows:
        if not isinstance(row, dict):
            add_blocker(blockers, "invalid_item_price_row", "Item Price row is not an object.", "rows.item_prices")
            continue
        current_rate = parse_money(row.get("price_list_rate") if "price_list_rate" in row else row.get("rate"))
        runtime_rows.append({"name": row.get("name"), "item_code": row.get("item_code"), "current_rate": current_rate})
        if current_rate is None:
            add_blocker(
                blockers,
                "missing_item_price_rate",
                f"Item Price row {row.get('name') or '<unnamed>'} has no readable current rate.",
                "rows.item_prices.price_list_rate",
            )
            continue

        item_code = str(row.get("item_code") or "")
        proposed_rate = item_code_price_map.get(item_code) if item_code_price_map else proposed_uniform_rate
        if proposed_rate is None:
            add_blocker(
                blockers,
                "unmapped_item_price_row",
                f"Item Price row {row.get('name') or '<unnamed>'} could not be mapped to a Product Setup price.",
                "rows.item_prices.item_code",
            )
            continue
        if current_rate == proposed_rate:
            continue
        if not row.get("name"):
            add_blocker(
                blockers,
                "missing_item_price_name",
                f"Changed Item Price for item code {item_code or '<missing>'} has no row name for rollback.",
                "rows.item_prices.name",
            )
            continue
        change = {
            "doctype": "Item Price",
            "name": row.get("name"),
            "item_code": row.get("item_code"),
            "price_list": row.get("price_list"),
            "currency": row.get("currency"),
            "uom": row.get("uom"),
            "current_rate": money_to_json(current_rate),
            "proposed_rate": money_to_json(proposed_rate),
            "source": "Product Setup",
            "mapping_basis": basis,
            "auto_apply": False,
        }
        changes.append(change)
        rollback_targets.append(
            {
                "doctype": "Item Price",
                "name": row.get("name"),
                "field": "price_list_rate",
                "rollback_value": money_to_json(current_rate),
                "rollback_source": "audit_json",
            }
        )

    return {"changes": changes, "rollback_targets": rollback_targets, "runtime_rows": runtime_rows}


def count_compatible(authority: dict[str, Any], item_price_rows: list[dict[str, Any]], variants: list[dict[str, Any]]) -> bool:
    row_count = len(authority.get("row_prices") or [])
    if row_count == 0:
        return len(item_price_rows) == 1
    if row_count == len(item_price_rows):
        return True
    if variants and row_count == len(variants) and len(item_price_rows) in {len(variants), len(variants) + 1}:
        return True
    return False


def build_copy_projection(
    blueprint_doc: dict[str, Any],
    website_item_doc: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    changes: list[dict[str, Any]] = []
    rollback_targets: list[dict[str, Any]] = []
    website_item_name = first_present(website_item_doc, ("name", "website_item", "target_website_item"))

    copy_pairs = [
        ("story", PRODUCT_SETUP_STORY_KEYS, WEBSITE_STORY_KEYS),
        ("details", PRODUCT_SETUP_DETAILS_KEYS, WEBSITE_DETAILS_KEYS),
    ]
    for label, source_keys, target_keys in copy_pairs:
        source_key, source_value = first_text(blueprint_doc, source_keys)
        target_key, target_value = first_text(website_item_doc, target_keys)
        if source_value is None:
            add_blocker(
                blockers,
                f"missing_product_setup_{label}",
                f"Audit JSON did not include Product Setup {label} copy.",
                "content_summary.blueprint_content_fields",
            )
            continue
        if target_value is None:
            add_blocker(
                blockers,
                f"missing_website_item_{label}",
                f"Audit JSON did not include Website Item public {label} copy.",
                "content_summary.website_item_content_fields",
            )
            continue
        if normalize_text(source_value) == normalize_text(target_value):
            continue
        changes.append(
            {
                "doctype": "Website Item",
                "name": website_item_name,
                "field": target_key,
                "current_value": target_value,
                "suggested_value": source_value,
                "source_field": source_key,
                "source": "Product Setup",
                "requires_business_copy_approval": True,
                "auto_apply": False,
            }
        )
        rollback_targets.append(
            {
                "doctype": "Website Item",
                "name": website_item_name,
                "field": target_key,
                "rollback_value": target_value,
                "rollback_source": "audit_json",
            }
        )
    return {"changes": changes, "rollback_targets": rollback_targets}


def extract_row_price(row: dict[str, Any]) -> dict[str, Any]:
    price, key = first_money(row, PRICE_KEYS)
    return {"row": row, "price": price, "price_key": key}


def first_money(doc: dict[str, Any], keys: tuple[str, ...]) -> tuple[Decimal | None, str | None]:
    for key in keys:
        if key in doc:
            value = parse_money(doc.get(key))
            if value is not None:
                return value, key
    return None, None


def parse_money(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if not match:
            return None
        try:
            return Decimal(match.group(0))
        except InvalidOperation:
            return None
    return None


def money_to_json(value: Any) -> float | None:
    if value is None:
        return None
    decimal_value = parse_money(value)
    if decimal_value is None:
        return None
    return float(decimal_value)


def first_text(doc: dict[str, Any], keys: tuple[str, ...]) -> tuple[str | None, str | None]:
    for key in keys:
        value = doc.get(key)
        if isinstance(value, str) and value.strip():
            return key, value
    return None, None


def normalize_text(value: str) -> str:
    return " ".join(value.split()).strip()


def get_dict(doc: dict[str, Any], key: str) -> dict[str, Any]:
    value = doc.get(key)
    return value if isinstance(value, dict) else {}


def get_dict_path(doc: dict[str, Any], path: tuple[str, ...]) -> dict[str, Any]:
    current: Any = doc
    for key in path:
        if not isinstance(current, dict):
            return {}
        current = current.get(key)
    return current if isinstance(current, dict) else {}


def get_list(doc: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = doc.get(key)
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


def first_list(*lists: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for values in lists:
        if values:
            return values
    return []


def merged_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for doc in dicts:
        merged.update(doc)
    return merged


def first_present(doc: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = doc.get(key)
        if value not in (None, ""):
            return value
    return None


def add_blocker(blockers: list[dict[str, Any]], code: str, message: str, evidence: str) -> None:
    blocker = {"code": code, "message": message, "evidence": evidence}
    if blocker not in blockers:
        blockers.append(blocker)


def write_output(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    indent = 2 if pretty else None
    payload = json.dumps(report, indent=indent, sort_keys=pretty) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise ProjectionBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
