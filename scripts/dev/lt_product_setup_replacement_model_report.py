#!/usr/bin/env python3
"""Build a no-write Product Setup replacement model report.

This helper combines Phase 9 variant-axis classification with Phase 10
dependency/rollback target capture. It may optionally read the original saved
catalog authority artifact to derive candidate SKU prices from current exact
price rows. It never reads live ERPNext, credentials, Docker, browser profiles,
providers, cache state, or customer systems.
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lt-product-setup-replacement-model-v1"
PROOF_MODE = (
    "offline saved classification, rollback, and optional catalog authority JSON "
    "artifacts only; no live reads, writes, cache clear, deploy, provider, payment, DNS, or customer action"
)
DEFAULT_PRODUCT = "birthday-deliveries"


class ReplacementModelBlocked(RuntimeError):
    """Raised when input files are missing or not the expected report shape."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        classification = load_json(Path(args.classification), "classification")
        rollback = load_json(Path(args.rollback), "rollback")
        source = load_json(Path(args.source_artifact), "source") if args.source_artifact else {}
        product = find_product(classification.get("products"), args.product, identifier_key="product")
        rollback_product = find_product(rollback.get("products"), args.product, identifier_key="product_identifier")
        report = build_report(
            classification=classification,
            classification_product=product,
            rollback=rollback,
            rollback_product=rollback_product,
            source=source,
            product_filter=args.product,
        )
        write_report(report, args.output, pretty=args.pretty)
    except ReplacementModelBlocked as exc:
        print(f"[LT PRODUCT SETUP REPLACEMENT MODEL] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP REPLACEMENT MODEL] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[LT PRODUCT SETUP REPLACEMENT MODEL] " + ("FAIL" if report["blocker_count"] else "PASS"), file=sys.stderr)
    print(f"  product: {report['product']['item_code']}", file=sys.stderr)
    print(f"  candidate_sku_variants: {report['replacement_model']['candidate_sku_variant_count']}", file=sys.stderr)
    print(f"  blockers: {report['blocker_count']}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and report["blocker_count"]:
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--classification", required=True, help="Phase 9 variant-axis classification report JSON.")
    parser.add_argument("--rollback", required=True, help="Phase 10 dependency/rollback report JSON.")
    parser.add_argument("--source-artifact", help="Optional saved catalog authority audit JSON for exact price-row derivation.")
    parser.add_argument("--product", default=DEFAULT_PRODUCT, help=f"Product filter. Defaults to {DEFAULT_PRODUCT}.")
    parser.add_argument("--output", help="Optional report JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 while blockers remain.")
    return parser.parse_args(argv)


def load_json(path: Path, expected: str) -> dict[str, Any]:
    if not path.exists():
        raise ReplacementModelBlocked(f"{expected} input does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReplacementModelBlocked(f"{expected} input is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReplacementModelBlocked(f"{expected} JSON root must be an object: {path}")
    if expected == "classification" and payload.get("schema_version") != "lt-product-setup-variant-axis-classification-v1":
        raise ReplacementModelBlocked(f"classification input has unexpected schema_version: {payload.get('schema_version')}")
    if expected == "rollback" and payload.get("schema_version") != "lt-product-setup-dependency-rollback-v1":
        raise ReplacementModelBlocked(f"rollback input has unexpected schema_version: {payload.get('schema_version')}")
    if expected == "source" and not any(key in payload for key in ("rows", "counts", "blueprint_summary")):
        raise ReplacementModelBlocked(f"source artifact is not a catalog authority audit artifact: {path}")
    return payload


def find_product(products: Any, product_filter: str, *, identifier_key: str) -> dict[str, Any]:
    for row in products if isinstance(products, list) else []:
        if not isinstance(row, dict):
            continue
        identifier = row.get(identifier_key) if isinstance(row.get(identifier_key), dict) else {}
        values = {
            normalize(identifier.get("product_setup")),
            normalize(identifier.get("item_code")),
            normalize(identifier.get("website_item")),
            normalize(identifier.get("route_slug")),
            normalize(str(identifier.get("route") or "").strip("/").split("/")[-1]),
        }
        if normalize(product_filter) in values:
            return row
    raise ReplacementModelBlocked(f"no matching product found in {identifier_key} report for {product_filter!r}")


def build_report(
    *,
    classification: dict[str, Any],
    classification_product: dict[str, Any],
    rollback: dict[str, Any],
    rollback_product: dict[str, Any],
    source: dict[str, Any],
    product_filter: str,
) -> dict[str, Any]:
    product = merged_product_identifier(classification_product, rollback_product)
    axes = classification_product.get("axes") if isinstance(classification_product.get("axes"), list) else []
    sku_axes = axes_by_classification(axes, "sku_defining_variant_candidate")
    config_axes = axes_by_classification(axes, "configuration_only_candidate") + axes_by_classification(axes, "review_or_configuration_candidate")
    add_on_axes = axes_by_classification(axes, "paid_add_on_candidate")
    source_price_rows = price_rows_from_source(source)
    candidate_sku_rows = candidate_sku_variants(product, sku_axes, source_price_rows)
    current_snapshot = current_snapshot_from_reports(classification_product, rollback_product)
    model = {
        "status": "blocked_no_write_model",
        "mutation_approval": False,
        "collapse_approval": False,
        "cache_clear_approval": False,
        "deploy_approval": False,
        "candidate_sku_axes": [axis_for_report(axis) for axis in sku_axes],
        "candidate_sku_variant_count": len(candidate_sku_rows),
        "candidate_sku_variants": candidate_sku_rows,
        "configuration_payload_axes": [configuration_axis(axis) for axis in config_axes],
        "paid_add_on_candidate_axes": [add_on_axis(axis, source_price_rows) for axis in add_on_axes],
        "current_records_to_preserve": current_snapshot,
        "proposed_record_actions": proposed_record_actions(current_snapshot, candidate_sku_rows, config_axes, add_on_axes),
    }
    blockers = blocker_list(classification_product, rollback_product, sku_axes, config_axes, add_on_axes, source_price_rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": "deterministic-offline-report",
        "deterministic": True,
        "proof_mode": PROOF_MODE,
        "product_filter": product_filter,
        "input_reports": {
            "classification_schema_version": classification.get("schema_version"),
            "rollback_schema_version": rollback.get("schema_version"),
            "source_artifact_used": bool(source),
        },
        "product": product,
        "current_model": current_snapshot,
        "replacement_model": model,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "next_safe_actions": [
            "Review this no-write replacement model against owner intent and current live proof.",
            "Build add-on/runtime pricing and payload-preservation contracts before any Product Setup apply path.",
            "Create a pre-mutation release packet with full reference checks, rollback command/procedure, public/cart/document verification, and owner approval before any catalog write.",
        ],
    }


def merged_product_identifier(classification_product: dict[str, Any], rollback_product: dict[str, Any]) -> dict[str, Any]:
    left = classification_product.get("product") if isinstance(classification_product.get("product"), dict) else {}
    right = rollback_product.get("product_identifier") if isinstance(rollback_product.get("product_identifier"), dict) else {}
    keys = ["product_setup", "item_code", "website_item", "product_name", "route", "route_slug", "brand_lane", "brand_lane_status"]
    return {key: left.get(key) if left.get(key) not in (None, "") else right.get(key) for key in keys}


def axes_by_classification(axes: list[Any], classification: str) -> list[dict[str, Any]]:
    return [axis for axis in axes if isinstance(axis, dict) and axis.get("candidate_classification") == classification]


def axis_for_report(axis: dict[str, Any]) -> dict[str, Any]:
    return {
        "axis_name": axis.get("axis_name"),
        "value_count": axis.get("value_count"),
        "values": axis.get("sample_values", []),
        "price_affecting": bool(axis.get("price_affecting")),
        "target_payload_target": axis.get("target_payload_target"),
        "mutation_approval": False,
    }


def configuration_axis(axis: dict[str, Any]) -> dict[str, Any]:
    row = axis_for_report(axis)
    row["contract"] = "Preserve customer selection in cart/order/document payload; do not create SKU variants from this axis without new proof."
    row["payload_preservation_proof"] = "missing"
    return row


def add_on_axis(axis: dict[str, Any], source_price_rows: list[dict[str, Any]]) -> dict[str, Any]:
    row = axis_for_report(axis)
    row["contract"] = "Paid add-on candidate; requires enabled add-on Item, Standard Selling Item Price, cart expansion, order/invoice/payment/receipt labels, and public proof."
    row["runtime_pricing_proof"] = "missing"
    row["derived_price_effects"] = price_effects_for_axis(axis.get("axis_name"), source_price_rows)
    return row


def price_rows_from_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows = source.get("rows") if isinstance(source.get("rows"), dict) else {}
    result = []
    for row in rows.get("blueprint_price_rows", []) if isinstance(rows.get("blueprint_price_rows"), list) else []:
        if not isinstance(row, dict):
            continue
        result.append(
            {
                "item_code": text(row.get("item_code")),
                "price": decimal_text(row.get("price") or row.get("price_list_rate") or row.get("rate")),
                "selections": parse_option_summary(text(row.get("option_summary"))),
            }
        )
    return result


def candidate_sku_variants(product: dict[str, Any], sku_axes: list[dict[str, Any]], source_price_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(sku_axes) != 1:
        return []
    axis = sku_axes[0]
    product_code = text(product.get("item_code")) or DEFAULT_PRODUCT
    rows = []
    for value in sorted(axis.get("sample_values", []), key=option_sort_key):
        value_text = text(value)
        rows.append(
            {
                "proposed_item_code": f"{product_code}-{slug(value_text)}",
                "template_item_code": product_code,
                "sku_axis": axis.get("axis_name"),
                "sku_value": value_text,
                "price_strategy": base_price_for_sku(axis.get("axis_name"), value_text, source_price_rows),
                "mutation_approval": False,
            }
        )
    return rows


def base_price_for_sku(axis_name: Any, value: str, source_price_rows: list[dict[str, Any]]) -> dict[str, Any]:
    matching_prices = sorted(
        {
            row["price"]
            for row in source_price_rows
            if row.get("price") is not None and row.get("selections", {}).get(text(axis_name)) == value
        },
        key=decimal_sort_key,
    )
    if not matching_prices:
        return {
            "status": "missing_source_price_rows",
            "exact_item_price_approved": False,
            "reason": "No saved exact price rows were available for this candidate SKU value.",
        }
    return {
        "status": "blocked_price_range_from_current_rows",
        "candidate_base_price": matching_prices[0],
        "observed_current_prices": matching_prices,
        "exact_item_price_approved": False,
        "reason": "Use the low observed current price only as a design hint until add-on/runtime pricing and owner approval define exact Item Prices.",
    }


def price_effects_for_axis(axis_name: Any, source_price_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    name = text(axis_name)
    effects: dict[str, set[str]] = {}
    for row in source_price_rows:
        value = row.get("selections", {}).get(name)
        if value and row.get("price") is not None:
            effects.setdefault(value, set()).add(row["price"])
    return [
        {"value": value, "observed_current_prices": sorted(prices, key=decimal_sort_key), "approved_add_on_price": None}
        for value, prices in sorted(effects.items())
    ]


def current_snapshot_from_reports(classification_product: dict[str, Any], rollback_product: dict[str, Any]) -> dict[str, Any]:
    current = classification_product.get("current") if isinstance(classification_product.get("current"), dict) else {}
    categories = rollback_product.get("target_categories") if isinstance(rollback_product.get("target_categories"), dict) else {}
    return {
        "current_variant_count": current.get("variant_count"),
        "current_item_price_count": current.get("item_price_count"),
        "current_option_axis_count": current.get("option_axis_count"),
        "rollback_rows": {
            key: len((categories.get(key) or {}).get("rollback_rows", [])) if isinstance(categories.get(key), dict) else 0
            for key in ["variants", "item_prices", "option_rows", "media_gallery_rows"]
        },
        "rollback_status": rollback_product.get("status"),
        "rollback_blocker_count": len(rollback_product.get("blockers", [])) if isinstance(rollback_product.get("blockers"), list) else 0,
    }


def proposed_record_actions(
    current_snapshot: dict[str, Any],
    candidate_sku_rows: list[dict[str, Any]],
    config_axes: list[dict[str, Any]],
    add_on_axes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "target": "current_variant_items",
            "current_count": current_snapshot.get("current_variant_count"),
            "proposed_action": "preserve_until_release_packet_approves_specific_disable_or_supersede_path",
            "approved": False,
        },
        {
            "target": "candidate_sku_items",
            "candidate_count": len(candidate_sku_rows),
            "proposed_action": "design_only_generate_after_owner_approval_and_rollback_packet",
            "approved": False,
        },
        {
            "target": "configuration_payload_axes",
            "candidate_count": len(config_axes),
            "proposed_action": "design_only_preserve_payload_in_cart_order_document_context",
            "approved": False,
        },
        {
            "target": "paid_add_on_axes",
            "candidate_count": len(add_on_axes),
            "proposed_action": "design_only_expand_to_add_on_items_after_runtime_and_document_proof",
            "approved": False,
        },
    ]


def blocker_list(
    classification_product: dict[str, Any],
    rollback_product: dict[str, Any],
    sku_axes: list[dict[str, Any]],
    config_axes: list[dict[str, Any]],
    add_on_axes: list[dict[str, Any]],
    source_price_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    blockers.extend(prefixed_blockers("classification", classification_product.get("blockers")))
    blockers.extend(prefixed_blockers("rollback", rollback_product.get("blockers")))
    if len(sku_axes) != 1:
        blockers.append(blocker("candidate_sku_axis_count_needs_review", "Replacement model expects exactly one SKU axis for this design report.", {"sku_axis_count": len(sku_axes)}))
    if config_axes:
        blockers.append(blocker("configuration_payload_preservation_proof_missing", "Configuration axes need cart/order/document payload preservation proof before collapse.", {"axes": [axis.get("axis_name") for axis in config_axes]}))
    if add_on_axes:
        blockers.append(blocker("paid_add_on_runtime_proof_missing", "Paid add-on candidates need enabled Items, Item Prices, cart expansion, checkout, document, payment, and receipt labels.", {"axes": [axis.get("axis_name") for axis in add_on_axes]}))
    price_affecting_add_ons = [axis.get("axis_name") for axis in add_on_axes if axis.get("price_affecting")]
    if price_affecting_add_ons:
        blockers.append(blocker("non_sku_price_axis_requires_add_on_pricing", "A non-SKU axis affects current saved price and needs explicit add-on/runtime pricing proof.", {"axes": price_affecting_add_ons}))
    if not source_price_rows:
        blockers.append(blocker("source_price_rows_missing_for_replacement_design", "Replacement model lacks saved exact price rows for candidate SKU price hints.", {}))
    blockers.append(blocker("owner_scope_approval_missing", "Owner/business approval is required before replacing current SKU shape.", {}))
    blockers.append(blocker("pre_mutation_release_packet_missing", "No write path is allowed until a release packet binds environment, diffs, rollback, verification, and approvals.", {}))
    return dedupe_blockers(blockers)


def prefixed_blockers(prefix: str, rows: Any) -> list[dict[str, Any]]:
    result = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        code = text(row.get("code")) or "unknown"
        result.append(blocker(f"{prefix}_{code}", text(row.get("message")) or code, row.get("evidence", row)))
    return result


def blocker(code: str, message: str, evidence: Any) -> dict[str, Any]:
    return {"code": code, "message": message, "evidence": evidence}


def dedupe_blockers(blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for row in blockers:
        key = row["code"]
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def parse_option_summary(summary: str) -> dict[str, str]:
    selections: dict[str, str] = {}
    for part in summary.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        if text(key):
            selections[text(key)] = text(value)
    return selections


def decimal_text(value: Any) -> str | None:
    try:
        decimal = Decimal(str(value)).normalize()
        return format(decimal, "f")
    except (InvalidOperation, TypeError, ValueError):
        return None


def decimal_sort_key(value: str) -> Decimal:
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return Decimal("0")


def slug(value: str) -> str:
    return "-".join(part for part in "".join(ch.lower() if ch.isalnum() else " " for ch in value).split() if part)


def option_sort_key(value: Any) -> tuple[int, str]:
    lower = text(value).lower()
    preferred = {
        "small": 10,
        "medium": 20,
        "large": 30,
    }
    return (preferred.get(lower, 100), lower)


def normalize(value: Any) -> str:
    return str(value or "").strip().lower().strip("/")


def text(value: Any) -> str:
    return str(value or "").strip()


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=True, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise ReplacementModelBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
