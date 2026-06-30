#!/usr/bin/env python3
"""Verify Product Setup price/copy authority parity from a saved JSON artifact.

This verifier is intentionally no-write and offline. It consumes either:

- a live read-only product audit JSON, or
- a no-write Product Setup projection preview JSON.

It does not read `.env`, credentials, the network, Docker, or ERPNext.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PRICE_TERMS = (
    "price",
    "rate",
    "amount",
    "base_price",
    "item price",
    "standard selling",
    "price_list_rate",
)
COPY_TERMS = (
    "copy",
    "description",
    "story",
    "details",
    "brand_description",
    "product_details",
    "product_story",
    "lt_brand_description",
    "lt_product_details",
    "web_long_description",
    "short_description",
)


class ContractError(Exception):
    """Raised when the verifier cannot read the supplied artifact."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = load_json(Path(args.input))
        detected_type = detect_input_type(payload, args.input_type)
        if detected_type == "projection":
            report = report_from_projection(payload, args)
        else:
            report = report_from_audit(payload, args)
    except ContractError as exc:
        report = {
            "status": "fail",
            "drift_count": 0,
            "blocker_count": 1,
            "drift": [],
            "blockers": [str(exc)],
            "input_summary": {
                "path": str(Path(args.input)),
                "requested_type": args.input_type,
            },
        }
        print_report(report, json_output=args.json)
        return 1

    print_report(report, json_output=args.json)
    return 0 if report["status"] == "pass" else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", required=True, help="Saved audit or projection JSON artifact.")
    parser.add_argument(
        "--input-type",
        choices=("auto", "audit", "projection"),
        default="auto",
        help="Artifact type. Default: auto.",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full machine-readable report.")
    parser.add_argument("--allow-copy-drift", action="store_true", help="Do not fail on copy drift.")
    parser.add_argument("--allow-price-drift", action="store_true", help="Do not fail on price drift.")
    return parser.parse_args(argv)


def load_json(path: Path) -> Any:
    if not path.exists():
        raise ContractError(f"input does not exist: {path}")
    if path.is_dir():
        raise ContractError(f"input is a directory: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"input is not valid JSON: {exc}") from exc
    except OSError as exc:
        raise ContractError(f"could not read input: {exc}") from exc


def detect_input_type(payload: Any, requested: str) -> str:
    if requested != "auto":
        return requested
    if not isinstance(payload, dict):
        raise ContractError("input JSON must be an object")
    if any(key in payload for key in ("drift_summary", "proposed_changes", "projection_summary")):
        return "projection"
    if any(key in payload for key in ("price_summary", "content_summary", "blueprint_summary", "website_item_summary")):
        return "audit"
    raise ContractError(
        "could not auto-detect input type; expected live audit keys "
        "(price_summary/content_summary) or projection keys (drift_summary/proposed_changes)"
    )


def report_from_projection(payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[Any] = []
    drift: list[dict[str, Any]] = []

    collect_blockers(blockers, payload.get("blockers"))
    collect_blockers(blockers, payload.get("blocking_reasons"))

    proposed_changes = projection_changes(payload.get("proposed_changes"))
    for change in proposed_changes:
        category = classify_payload(change)
        if category in {"price", "copy"}:
            drift.append(
                {
                    "type": category,
                    "source": "projection.proposed_changes",
                    "message": projection_change_message(change, category),
                    "evidence": safe_json_value(change),
                }
            )

    drift_summary = payload.get("drift_summary") or payload.get("projection_summary") or {}
    if isinstance(drift_summary, dict):
        collect_blockers(blockers, drift_summary.get("blockers"))
        collect_projection_drifts(drift, drift_summary, skip_count_categories={entry.get("type") for entry in drift})
    elif isinstance(drift_summary, list):
        for entry in drift_summary:
            add_projection_drift(drift, entry)

    if not drift and not blockers and not any(key in payload for key in ("drift_summary", "proposed_changes", "projection_summary")):
        blockers.append("projection artifact is missing drift_summary/proposed_changes evidence")
    if not proposed_changes and not drift_summary:
        blockers.append("projection artifact has no proposed_changes or drift_summary to inspect")

    return finalize_report(
        drift=dedupe_drift(drift),
        blockers=dedupe_blockers(blockers),
        input_summary={
            "path": str(Path(args.input)),
            "requested_type": args.input_type,
            "detected_type": "projection",
            "proposed_change_count": len(proposed_changes),
            "has_drift_summary": bool(drift_summary),
        },
        allow_price_drift=args.allow_price_drift,
        allow_copy_drift=args.allow_copy_drift,
    )


def projection_changes(value: Any) -> list[Any]:
    if isinstance(value, dict):
        changes: list[Any] = []
        for key, entries in value.items():
            for entry in as_list(entries):
                if isinstance(entry, dict):
                    changes.append({"projection_group": key, **entry})
                else:
                    changes.append({"projection_group": key, "value": entry})
        return changes
    return as_list(value)


def collect_projection_drifts(
    drift: list[dict[str, Any]],
    summary: dict[str, Any],
    *,
    skip_count_categories: set[Any],
) -> None:
    for key in ("drift", "drifts", "items", "rows"):
        for entry in as_list(summary.get(key)):
            add_projection_drift(drift, entry)

    for category, terms in (("price", ("price_drift", "price_drift_count", "price")), ("copy", ("copy_drift", "copy_drift_count", "copy"))):
        if category in skip_count_categories:
            continue
        for term in terms:
            if term not in summary:
                continue
            value = summary.get(term)
            if drift_flag_is_present(value):
                drift.append(
                    {
                        "type": category,
                        "source": f"projection.drift_summary.{term}",
                        "message": f"projection reports {category} drift via {term}: {value}",
                        "evidence": safe_json_value(value),
                    }
                )


def add_projection_drift(drift: list[dict[str, Any]], entry: Any) -> None:
    category = classify_payload(entry)
    if category not in {"price", "copy"}:
        return
    drift.append(
        {
            "type": category,
            "source": "projection.drift_summary",
            "message": projection_change_message(entry, category),
            "evidence": safe_json_value(entry),
        }
    )


def drift_flag_is_present(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, (list, tuple, set)):
        return len(value) > 0
    if isinstance(value, dict):
        signal_keys = [
            key
            for key in ("drift_detected", "count", "drift_count", "total", "has_drift", "exists")
            if key in value
        ]
        if signal_keys:
            return any(drift_flag_is_present(value[key]) for key in signal_keys)
        for key in ("drift_detected", "count", "drift_count", "total", "has_drift", "exists"):
            if key in value and drift_flag_is_present(value[key]):
                return True
        return bool(value)
    return bool(value)


def report_from_audit(payload: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    blockers: list[Any] = []
    drift: list[dict[str, Any]] = []

    collect_blockers(blockers, payload.get("failures"))
    inspect_audit_price(payload, drift, blockers)
    inspect_audit_copy(payload, drift, blockers)

    return finalize_report(
        drift=dedupe_drift(drift),
        blockers=dedupe_blockers(blockers),
        input_summary={
            "path": str(Path(args.input)),
            "requested_type": args.input_type,
            "detected_type": "audit",
            "generated_at": payload.get("generated_at"),
            "host": payload.get("host"),
            "blueprint": (payload.get("blueprint_summary") or {}).get("name"),
            "website_item": (payload.get("website_item_summary") or {}).get("name"),
            "item_code": (payload.get("template_item_summary") or {}).get("item_code")
            or (payload.get("website_item_summary") or {}).get("item_code"),
            "counts": payload.get("counts") or {},
        },
        allow_price_drift=args.allow_price_drift,
        allow_copy_drift=args.allow_copy_drift,
    )


def inspect_audit_price(payload: dict[str, Any], drift: list[dict[str, Any]], blockers: list[Any]) -> None:
    price_summary = payload.get("price_summary") if isinstance(payload.get("price_summary"), dict) else {}
    rows = payload.get("rows") if isinstance(payload.get("rows"), dict) else {}
    blueprint_summary = payload.get("blueprint_summary") if isinstance(payload.get("blueprint_summary"), dict) else {}

    base_price = first_price(
        price_summary.get("blueprint_base_price"),
        blueprint_summary.get("base_price"),
        payload.get("base_price"),
    )
    setup_price_rows = rows_from_likely_keys(rows, "blueprint_price_rows", "price_rows", "product_setup_price_rows")
    item_price_rows = rows_from_likely_keys(rows, "item_prices", "item_price_rows", "runtime_item_prices")

    setup_row_prices = prices_from_rows(setup_price_rows, ("price", "base_price", "checkout_price", "price_list_rate", "rate"))
    summary_setup_prices = prices_from_values(price_summary.get("blueprint_price_row_values"))
    runtime_prices = prices_from_rows(item_price_rows, ("price_list_rate", "rate", "price", "amount"))
    summary_runtime_prices = prices_from_values(price_summary.get("item_price_values"))

    setup_prices = unique_prices([*(setup_row_prices or summary_setup_prices), *([base_price] if base_price is not None else [])])
    item_prices = unique_prices(runtime_prices or summary_runtime_prices)

    if base_price is None:
        blockers.append("missing Product Setup base price evidence")
    if not setup_price_rows and not summary_setup_prices:
        blockers.append("missing Product Setup price row evidence")
    if not setup_prices:
        blockers.append("missing Product Setup price values")
    if not item_price_rows and not summary_runtime_prices:
        blockers.append("missing Item Price row evidence")
    if not item_prices:
        blockers.append("missing Item Price values")

    if setup_row_prices and base_price is not None and unique_prices(setup_row_prices) != [base_price]:
        drift.append(
            {
                "type": "price",
                "source": "live_audit.product_setup",
                "message": "Product Setup base price differs from Product Setup price rows",
                "evidence": {
                    "base_price": price_label(base_price),
                    "price_row_values": price_labels(unique_prices(setup_row_prices)),
                },
            }
        )

    setup_by_item = prices_by_item(setup_price_rows, ("price", "base_price", "checkout_price", "price_list_rate", "rate"))
    runtime_by_item = prices_by_item(item_price_rows, ("price_list_rate", "rate", "price", "amount"))
    compared_codes = sorted(set(setup_by_item) & set(runtime_by_item))
    missing_runtime_codes = sorted(set(setup_by_item) - set(runtime_by_item))
    if missing_runtime_codes:
        blockers.append(
            "missing Item Price evidence for Product Setup item_code(s): "
            + ", ".join(missing_runtime_codes[:10])
            + (f" and {len(missing_runtime_codes) - 10} more" if len(missing_runtime_codes) > 10 else "")
        )

    mismatched_codes = [
        code for code in compared_codes if unique_prices(setup_by_item[code]) != unique_prices(runtime_by_item[code])
    ]
    if mismatched_codes:
        setup_values = unique_prices([price for code in mismatched_codes for price in setup_by_item[code]])
        runtime_values = unique_prices([price for code in mismatched_codes for price in runtime_by_item[code]])
        drift.append(
            {
                "type": "price",
                "source": "live_audit.item_price_rows",
                "message": (
                    f"Product Setup price rows differ from Item Price authority for "
                    f"{len(mismatched_codes)} item_code(s)"
                ),
                "evidence": {
                    "affected_count": len(mismatched_codes),
                    "examples": mismatched_codes[:10],
                    "product_setup_values": price_labels(setup_values),
                    "item_price_values": price_labels(runtime_values),
                    "public_price_strings": (payload.get("public_summary") or {}).get("price_strings"),
                },
            }
        )
    elif setup_prices and item_prices and setup_prices != item_prices:
        drift.append(
            {
                "type": "price",
                "source": "live_audit.price_summary",
                "message": "Product Setup price values differ from Item Price authority values",
                "evidence": {
                    "product_setup_values": price_labels(setup_prices),
                    "item_price_values": price_labels(item_prices),
                    "public_price_strings": (payload.get("public_summary") or {}).get("price_strings"),
                },
            }
        )


def inspect_audit_copy(payload: dict[str, Any], drift: list[dict[str, Any]], blockers: list[Any]) -> None:
    content_summary = payload.get("content_summary") if isinstance(payload.get("content_summary"), dict) else {}
    setup_fields = first_dict(
        content_summary.get("blueprint_content_fields"),
        payload.get("blueprint_content_fields"),
        payload.get("product_setup_content_fields"),
    )
    public_fields = first_dict(
        content_summary.get("website_item_content_fields"),
        payload.get("website_item_content_fields"),
        payload.get("public_content_fields"),
    )

    if not setup_fields:
        blockers.append("missing Product Setup story/details copy evidence")
    if not public_fields:
        blockers.append("missing Website Item public copy evidence")

    setup_story = first_text_from(setup_fields, "product_story", "story", "about_this_design", "about", "description")
    setup_details = first_text_from(setup_fields, "product_details", "details", "whats_included", "included", "copy")
    public_story = first_text_from(public_fields, "lt_brand_description", "brand_description", "description", "web_long_description")
    public_details = first_text_from(public_fields, "lt_product_details", "product_details", "web_long_description", "short_description")

    if setup_fields and setup_story is None:
        blockers.append("missing Product Setup story/about copy field")
    if setup_fields and setup_details is None:
        blockers.append("missing Product Setup details/included copy field")
    if public_fields and public_story is None:
        blockers.append("missing Website Item public story/description field")
    if public_fields and public_details is None:
        blockers.append("missing Website Item public details field")

    compare_copy_pair(
        drift,
        label="story",
        setup_value=setup_story,
        public_value=public_story,
        setup_field=field_name_for(setup_fields, "product_story", "story", "about_this_design", "about", "description"),
        public_field=field_name_for(public_fields, "lt_brand_description", "brand_description", "description", "web_long_description"),
    )
    compare_copy_pair(
        drift,
        label="details",
        setup_value=setup_details,
        public_value=public_details,
        setup_field=field_name_for(setup_fields, "product_details", "details", "whats_included", "included", "copy"),
        public_field=field_name_for(public_fields, "lt_product_details", "product_details", "web_long_description", "short_description"),
    )


def compare_copy_pair(
    drift: list[dict[str, Any]],
    *,
    label: str,
    setup_value: str | None,
    public_value: str | None,
    setup_field: str | None,
    public_field: str | None,
) -> None:
    if setup_value is None or public_value is None:
        return
    setup_text = normalize_copy(setup_value)
    public_text = normalize_copy(public_value)
    if setup_text == public_text:
        return
    drift.append(
        {
            "type": "copy",
            "source": "live_audit.website_item_copy",
            "message": f"Product Setup {label} copy differs from Website Item public {label} copy",
            "evidence": {
                "product_setup_field": setup_field,
                "website_item_field": public_field,
                "product_setup_excerpt": excerpt(setup_text),
                "website_item_excerpt": excerpt(public_text),
            },
        }
    )


def finalize_report(
    *,
    drift: list[dict[str, Any]],
    blockers: list[Any],
    input_summary: dict[str, Any],
    allow_price_drift: bool,
    allow_copy_drift: bool,
) -> dict[str, Any]:
    unallowed = [
        entry
        for entry in drift
        if not ((entry.get("type") == "price" and allow_price_drift) or (entry.get("type") == "copy" and allow_copy_drift))
    ]
    status = "pass" if not unallowed and not blockers else "fail"
    return {
        "status": status,
        "drift_count": len(drift),
        "blocker_count": len(blockers),
        "drift": drift,
        "blockers": blockers,
        "input_summary": {
            **input_summary,
            "allow_price_drift": allow_price_drift,
            "allow_copy_drift": allow_copy_drift,
            "unallowed_drift_count": len(unallowed),
        },
    }


def print_report(report: dict[str, Any], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
        return

    label = "[PRODUCT SETUP AUTHORITY PARITY CONTRACT]"
    print(f"{label} {report['status'].upper()}")
    summary = report.get("input_summary") or {}
    print(f"  input_type: {summary.get('detected_type') or summary.get('requested_type')}")
    print(f"  drift_count: {report['drift_count']}")
    print(f"  blocker_count: {report['blocker_count']}")
    if report["blockers"]:
        print("  blockers:")
        for blocker in report["blockers"][:12]:
            print(f"    - {format_blocker(blocker)}")
        if len(report["blockers"]) > 12:
            print(f"    - ... {len(report['blockers']) - 12} more")
    if report["drift"]:
        print("  drift:")
        for entry in report["drift"][:12]:
            allowed = drift_allowed(entry, summary)
            suffix = " (allowed by flag)" if allowed else ""
            print(f"    - {entry.get('type', 'unknown')}: {entry.get('message')}{suffix}")
        if len(report["drift"]) > 12:
            print(f"    - ... {len(report['drift']) - 12} more")


def drift_allowed(entry: dict[str, Any], summary: dict[str, Any]) -> bool:
    return bool(
        (entry.get("type") == "price" and summary.get("allow_price_drift"))
        or (entry.get("type") == "copy" and summary.get("allow_copy_drift"))
    )


def collect_blockers(blockers: list[Any], value: Any) -> None:
    for entry in as_list(value):
        if entry not in (None, "", [], {}):
            blockers.append(safe_json_value(entry))


def rows_from_likely_keys(parent: dict[str, Any], *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        rows = parent.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def prices_from_rows(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[Decimal]:
    prices: list[Decimal] = []
    for row in rows:
        value = first_present(row, *keys)
        price = to_price(value)
        if price is not None:
            prices.append(price)
    return prices


def prices_by_item(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[str, list[Decimal]]:
    result: dict[str, list[Decimal]] = {}
    for row in rows:
        item_code = str(row.get("item_code") or row.get("target_item_code") or row.get("name") or "").strip()
        if not item_code:
            continue
        value = first_present(row, *keys)
        price = to_price(value)
        if price is not None:
            result.setdefault(item_code, []).append(price)
    return result


def prices_from_values(value: Any) -> list[Decimal]:
    return [price for price in (to_price(item) for item in as_list(value)) if price is not None]


def first_price(*values: Any) -> Decimal | None:
    for value in values:
        price = to_price(value)
        if price is not None:
            return price
    return None


def to_price(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def unique_prices(values: list[Decimal]) -> list[Decimal]:
    return sorted(set(values))


def price_label(value: Decimal) -> str:
    return f"{value:.2f}"


def price_labels(values: list[Decimal]) -> list[str]:
    return [price_label(value) for value in values]


def first_dict(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, dict):
            return value
    return {}


def first_text_from(mapping: dict[str, Any], *keys: str) -> str | None:
    value = first_present(mapping, *keys)
    if value in (None, ""):
        return None
    return str(value)


def field_name_for(mapping: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return key
    return None


def first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    return None


def normalize_copy(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value))
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(value: str, limit: int = 160) -> str:
    text = normalize_copy(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def classify_payload(value: Any) -> str:
    text = json.dumps(safe_json_value(value), sort_keys=True, default=str).lower()
    has_price = any(term in text for term in PRICE_TERMS)
    has_copy = any(term in text for term in COPY_TERMS)
    if has_price and not has_copy:
        return "price"
    if has_copy and not has_price:
        return "copy"
    if has_price:
        return "price"
    if has_copy:
        return "copy"
    return "unknown"


def projection_change_message(value: Any, category: str) -> str:
    if isinstance(value, dict):
        field = value.get("field") or value.get("fieldname") or value.get("target_field")
        target = value.get("target") or value.get("doctype") or value.get("record") or value.get("name")
        if field and target:
            return f"projection reports {category} drift for {target}.{field}"
        if field:
            return f"projection reports {category} drift for {field}"
    return f"projection reports {category} drift"


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def safe_json_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): safe_json_value(inner) for key, inner in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json_value(inner) for inner in value]
    return str(value)


def dedupe_blockers(blockers: list[Any]) -> list[Any]:
    seen: set[str] = set()
    result: list[Any] = []
    for blocker in blockers:
        key = json.dumps(safe_json_value(blocker), sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        result.append(blocker)
    return result


def dedupe_drift(drift: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for entry in drift:
        key = json.dumps(entry, sort_keys=True, default=str)
        if key in seen:
            continue
        seen.add(key)
        result.append(entry)
    return result


def format_blocker(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, default=str)


if __name__ == "__main__":
    sys.exit(main())
