#!/usr/bin/env python3
"""Build an offline variant-axis classification report from saved artifacts.

This helper consumes saved JSON from ``lt_live_readonly_catalog_authority_audit.py``.
It does not read credentials, call the network, inspect Docker, clear cache,
deploy, or write ERPNext data.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SKIP_DIRECTORY_JSON = {
    "index.json",
    "blast-radius.json",
    "authority-packet-report.json",
    "variant-axis-classification.json",
}
CONFIGURATION_WORDS = {
    "color",
    "colour",
    "design",
    "theme",
    "themes",
    "style",
    "character",
    "photo",
    "message",
}
ADD_ON_WORDS = {"add", "extra", "upgrade", "foil number", "number"}
SKU_WORDS = {"size", "length", "height", "bouquet", "package", "tier"}


class VariantAxisClassificationBlocked(RuntimeError):
    """Raised when saved artifact input is missing or invalid."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        paths = collect_paths(args.input)
        products = [summarize_artifact(path, load_json(path)) for path in paths]
        if args.product:
            products = [
                product
                for product in products
                if args.product
                in {
                    product["product"].get("item_code"),
                    product["product"].get("product_setup"),
                    product["product"].get("route_slug"),
                }
            ]
        if not products:
            raise VariantAxisClassificationBlocked("no matching product artifacts found")
        report = build_report(products, paths)
        write_report(report, args.output, pretty=args.pretty)
    except VariantAxisClassificationBlocked as exc:
        print(f"[LT VARIANT AXIS CLASSIFICATION] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT VARIANT AXIS CLASSIFICATION] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[LT VARIANT AXIS CLASSIFICATION] " + ("FAIL" if report["blocked_product_count"] else "PASS"), file=sys.stderr)
    print(f"  products: {report['product_count']}", file=sys.stderr)
    print(f"  blocked_products: {report['blocked_product_count']}", file=sys.stderr)
    print(f"  current_variants: {report['total_current_variants']}", file=sys.stderr)
    print(f"  candidate_variants: {report['total_candidate_sku_variants']}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and report["blocked_product_count"]:
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", nargs="+", required=True, help="Saved audit JSON files or directories.")
    parser.add_argument("--output", help="Optional report JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--product", help="Optional item_code, Product Setup name, or route slug filter.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 when any product has blockers.")
    return parser.parse_args(argv)


def collect_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if not path.exists():
            raise VariantAxisClassificationBlocked(f"input does not exist: {path}")
        if path.is_dir():
            paths.extend(
                child
                for child in sorted(path.glob("*.json"))
                if child.is_file() and child.name not in SKIP_DIRECTORY_JSON and not child.name.endswith("-projection.json")
            )
        elif path.suffix.lower() == ".json":
            if path.name in SKIP_DIRECTORY_JSON or path.name.endswith("-projection.json"):
                raise VariantAxisClassificationBlocked(f"input is a report/projection artifact, not a product audit: {path}")
            paths.append(path)
        else:
            raise VariantAxisClassificationBlocked(f"input is not a JSON file or directory: {path}")
    unique = sorted({path.resolve() for path in paths})
    if not unique:
        raise VariantAxisClassificationBlocked("no saved audit JSON artifacts found")
    return unique


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise VariantAxisClassificationBlocked(f"input is not valid JSON: {path}: {exc}") from exc
    except OSError as exc:
        raise VariantAxisClassificationBlocked(f"could not read input: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise VariantAxisClassificationBlocked(f"JSON root must be an object: {path}")
    if not any(key in payload for key in ("rows", "counts", "blueprint_summary", "website_item_summary")):
        raise VariantAxisClassificationBlocked(f"not a recognized catalog authority audit artifact: {path}")
    return payload


def summarize_artifact(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows") if isinstance(payload.get("rows"), dict) else {}
    counts = payload.get("counts") if isinstance(payload.get("counts"), dict) else {}
    option_rows = as_list(rows.get("blueprint_option_rows"))
    price_rows = as_list(rows.get("blueprint_price_rows"))
    variant_rows = as_list(rows.get("variants"))
    current_variant_count = int_value(counts.get("variants"), default=len(variant_rows))
    current_item_price_count = int_value(counts.get("item_prices"), default=len(as_list(rows.get("item_prices"))))

    axes = [axis_summary(row) for row in option_rows]
    price_records = price_record_summaries(price_rows)
    price_axis_evidence = price_axis_analysis(axes, price_records)
    classified_axes = [
        classify_axis(axis, price_axis_evidence.get(axis["axis_name"], {}))
        for axis in axes
    ]
    candidate_sku_axes = [
        axis for axis in classified_axes if axis["candidate_classification"] == "sku_defining_variant_candidate"
    ]
    collapsed_axes = [
        axis["axis_name"]
        for axis in classified_axes
        if axis["current_selection_behavior"] == "SKU-defining variant"
        and axis["candidate_classification"] != "sku_defining_variant_candidate"
    ]
    candidate_variant_count = product_count(axis["value_count"] for axis in candidate_sku_axes)
    blockers = blockers_for_product(
        axes=classified_axes,
        price_records=price_records,
        current_variant_count=current_variant_count,
        current_item_price_count=current_item_price_count,
    )
    return {
        "artifact": str(path),
        "product": product_identifier(payload),
        "match_summary": payload.get("match_summary") if isinstance(payload.get("match_summary"), dict) else {},
        "proof_mode": "offline saved JSON artifact only; no live reads or writes",
        "artifact_limitations": [
            "Variant mapping is inferred from Product Setup price-row option_summary text unless a later artifact includes Item Variant Attribute rows.",
            "Classification evidence is planning-only and can be stale relative to live records.",
        ],
        "current": {
            "option_axis_count": len(axes),
            "sku_defining_axis_count": sum(1 for axis in axes if axis["current_selection_behavior"] == "SKU-defining variant"),
            "variant_count": current_variant_count,
            "item_price_count": current_item_price_count,
            "price_row_count": len(price_rows),
            "unique_price_count": len({record["price"] for record in price_records if record.get("price") is not None}),
        },
        "candidate": {
            "sku_defining_axes": [axis["axis_name"] for axis in candidate_sku_axes],
            "candidate_sku_variant_count": candidate_variant_count,
            "configuration_payload_axes": [
                axis["axis_name"]
                for axis in classified_axes
                if axis["candidate_classification"] in {"configuration_only_candidate", "review_or_configuration_candidate"}
            ],
            "paid_add_on_candidate_axes": [
                axis["axis_name"] for axis in classified_axes if axis["candidate_classification"] == "paid_add_on_candidate"
            ],
        },
        "collapse_summary": {
            "current_variant_count": current_variant_count,
            "candidate_sku_variant_count": candidate_variant_count,
            "reduction_count": max(0, current_variant_count - candidate_variant_count),
            "sku_axes_retained": [axis["axis_name"] for axis in candidate_sku_axes],
            "axes_reclassified_from_sku": collapsed_axes,
        },
        "price_strategy": price_strategy(classified_axes, price_records),
        "axes": classified_axes,
        "blockers": blockers,
        "status": "blocked" if blockers else "classification_ready_for_design_review",
        "next_action": next_action(blockers),
    }


def product_identifier(payload: dict[str, Any]) -> dict[str, Any]:
    identifier = payload.get("product_identifier") if isinstance(payload.get("product_identifier"), dict) else {}
    blueprint = payload.get("blueprint_summary") if isinstance(payload.get("blueprint_summary"), dict) else {}
    website = payload.get("website_item_summary") if isinstance(payload.get("website_item_summary"), dict) else {}
    route = str(identifier.get("route") or website.get("route") or "").strip()
    return {
        "product_setup": identifier.get("product_setup") or blueprint.get("name"),
        "item_code": identifier.get("item_code") or website.get("item_code") or blueprint.get("target_item_code"),
        "website_item": identifier.get("website_item") or website.get("name") or blueprint.get("target_website_item"),
        "product_name": identifier.get("product_name") or blueprint.get("product_name") or website.get("web_item_name"),
        "route": route,
        "route_slug": identifier.get("route_slug") or route.rstrip("/").split("/")[-1],
        "brand_lane": identifier.get("brand_lane") or blueprint.get("operating_brand"),
        "brand_lane_status": identifier.get("brand_lane_status") or "not_proved",
    }


def axis_summary(row: dict[str, Any]) -> dict[str, Any]:
    values = split_values(row.get("values"))
    return {
        "axis_name": text(row.get("axis_name")) or text(row.get("name")) or "unnamed axis",
        "current_selection_behavior": text(row.get("selection_behavior")) or text(row.get("role")) or "missing",
        "role": text(row.get("role")),
        "control_type": text(row.get("control_type")),
        "payload_target": text(row.get("payload_target")),
        "pricing_behavior": text(row.get("pricing_behavior")),
        "media_behavior": text(row.get("media_behavior")),
        "document_output": text(row.get("document_output")),
        "required": bool(row.get("required")),
        "min_selections": int_value(row.get("min_selections")),
        "max_selections": int_value(row.get("max_selections")),
        "value_count": len(values),
        "sample_values": values[:20],
    }


def price_record_summaries(rows: list[Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        price = decimal_text(row.get("price") or row.get("price_list_rate") or row.get("rate"))
        selections = parse_option_summary(text(row.get("option_summary")))
        records.append(
            {
                "item_code": text(row.get("item_code")),
                "price": price,
                "selections": selections,
            }
        )
    return records


def price_axis_analysis(axes: list[dict[str, Any]], records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for axis in axes:
        name = axis["axis_name"]
        compared_groups = 0
        differing_groups = 0
        example: dict[str, Any] | None = None
        grouped: dict[tuple[tuple[str, str], ...], dict[str, set[str]]] = {}
        for record in records:
            selections = record.get("selections") or {}
            if name not in selections or record.get("price") is None:
                continue
            other = tuple(sorted((key, value) for key, value in selections.items() if key != name))
            grouped.setdefault(other, {}).setdefault(selections[name], set()).add(record["price"])
        for other, by_value in grouped.items():
            if len(by_value) < 2:
                continue
            compared_groups += 1
            prices = {price for value_prices in by_value.values() for price in value_prices}
            if len(prices) > 1:
                differing_groups += 1
                if example is None:
                    example = {
                        "held_constant": dict(other),
                        "value_prices": {value: sorted(value_prices) for value, value_prices in by_value.items()},
                    }
        result[name] = {
            "price_affecting": differing_groups > 0,
            "compared_groups": compared_groups,
            "differing_groups": differing_groups,
            "example": example,
        }
    return result


def classify_axis(axis: dict[str, Any], price_evidence: dict[str, Any]) -> dict[str, Any]:
    axis_name = axis["axis_name"]
    lower_name = axis_name.lower()
    price_affecting = bool(price_evidence.get("price_affecting"))
    if price_affecting and not contains_any(lower_name, ADD_ON_WORDS):
        candidate = "sku_defining_variant_candidate"
        reason = "Changing this axis can change the Product Setup exact price while other axes stay constant."
    elif contains_any(lower_name, ADD_ON_WORDS):
        candidate = "paid_add_on_candidate"
        reason = "The axis reads like an optional add-on/modifier and should not create one variant per value without add-on proof."
    elif contains_any(lower_name, CONFIGURATION_WORDS) or axis["value_count"] > 12:
        candidate = "configuration_only_candidate"
        reason = "The axis is high-cardinality or customer-design choice data; it should travel in the cart/order payload unless separate SKU proof exists."
    elif contains_any(lower_name, SKU_WORDS):
        candidate = "review_or_configuration_candidate"
        reason = "The axis may affect sellable shape, but saved price rows did not prove it changes price."
    else:
        candidate = "review_or_configuration_candidate"
        reason = "Saved evidence does not prove this axis must define a sellable SKU."
    result = dict(axis)
    result.update(
        {
            "price_affecting": price_affecting,
            "price_evidence": price_evidence,
            "candidate_classification": candidate,
            "target_payload_target": target_payload_target(candidate),
            "classification_reason": reason,
            "mutation_approval": False,
            "candidate": {
                "classification": candidate,
                "target_payload_target": target_payload_target(candidate),
                "rationale": reason,
                "mutation_approval": False,
            },
        }
    )
    return result


def target_payload_target(candidate: str) -> str:
    return {
        "sku_defining_variant_candidate": "selected_options",
        "configuration_only_candidate": "configuration_groups",
        "paid_add_on_candidate": "add_ons_after_add_on_proof",
        "review_or_configuration_candidate": "quote_context_or_configuration_groups",
    }.get(candidate, "quote_context")


def price_strategy(axes: list[dict[str, Any]], price_records: list[dict[str, Any]]) -> dict[str, Any]:
    price_affecting_axes = [axis["axis_name"] for axis in axes if axis.get("price_affecting")]
    sku_axes = [axis["axis_name"] for axis in axes if axis["candidate_classification"] == "sku_defining_variant_candidate"]
    add_on_axes = [axis["axis_name"] for axis in axes if axis["candidate_classification"] == "paid_add_on_candidate"]
    return {
        "price_row_count": len(price_records),
        "price_affecting_axes": price_affecting_axes,
        "sku_price_axes": sku_axes,
        "non_sku_price_axes_requiring_runtime_or_add_on_design": [
            axis for axis in price_affecting_axes if axis not in sku_axes
        ],
        "paid_add_on_candidate_axes": add_on_axes,
        "strategy": (
            "Exact prices cannot be trusted after variant collapse until non-SKU price-affecting axes "
            "have add-on/runtime pricing proof and cart/order/document labels."
        )
        if any(axis for axis in price_affecting_axes if axis not in sku_axes)
        else "Candidate SKU axes can carry exact Item Prices after replacement design and rollback proof.",
    }


def blockers_for_product(
    *,
    axes: list[dict[str, Any]],
    price_records: list[dict[str, Any]],
    current_variant_count: int,
    current_item_price_count: int,
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    if not axes:
        blockers.append({"code": "missing_option_axes", "message": "Saved artifact has no Product Setup option axes."})
    if not price_records and current_variant_count:
        blockers.append({"code": "missing_price_rows", "message": "Saved artifact has variants but no Product Setup exact price rows."})
    non_candidate_sku_axes = [
        axis["axis_name"]
        for axis in axes
        if axis["current_selection_behavior"] == "SKU-defining variant"
        and axis["candidate_classification"] != "sku_defining_variant_candidate"
    ]
    if non_candidate_sku_axes:
        blockers.append(
            {
                "code": "current_sku_axes_need_reclassification",
                "message": "Current SKU-defining axes include configuration/add-on candidates.",
                "axes": non_candidate_sku_axes,
            }
        )
    if current_variant_count > 500:
        blockers.append(
            {
                "code": "variant_explosion_requires_no_write_plan",
                "message": "Variant count is too high for direct repair without classification, dependency mapping, rollback, and owner-scope approval.",
                "variant_count": current_variant_count,
                "item_price_count": current_item_price_count,
            }
        )
    return blockers


def build_report(products: list[dict[str, Any]], paths: list[Path]) -> dict[str, Any]:
    blocked = [product for product in products if product["blockers"]]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema_version": "lt-product-setup-variant-axis-classification-v1",
        "proof_mode": "offline saved JSON artifacts only; no live reads or writes",
        "input_artifacts": [str(path) for path in paths],
        "artifact_count": len(paths),
        "product_count": len(products),
        "blocked_product_count": len(blocked),
        "total_current_variants": sum(product["current"]["variant_count"] for product in products),
        "total_candidate_sku_variants": sum(product["candidate"]["candidate_sku_variant_count"] for product in products),
        "classification_contract": {
            "sku_defining_variant_candidate": "Axis appears to affect sellable price/shape and may remain a variant after design review.",
            "configuration_only_candidate": "Axis should travel as customer configuration/cart/order payload unless separate SKU proof exists.",
            "paid_add_on_candidate": "Axis should become an add-on line or add-on payload only after Item/price/order/document proof.",
            "review_or_configuration_candidate": "Axis needs business review before it can affect checkout or document behavior.",
        },
        "products": products,
        "next_safe_actions": [
            "Review candidate classifications with saved price evidence before any data mutation.",
            "Capture dependency and rollback targets for current variants, Item Prices, orders, invoices, payments, files, and public routes.",
            "Build a dry-run replacement/redirect plan before disabling, deleting, renaming, or repurposing any current variant records.",
        ],
    }


def next_action(blockers: list[dict[str, Any]]) -> str:
    if blockers:
        return "Use this as a planning blocker report; do not mutate catalog records."
    return "Classification is ready for design review; mutation still requires rollback and owner approval."


def parse_option_summary(summary: str) -> dict[str, str]:
    selections: dict[str, str] = {}
    for part in summary.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        clean_key = text(key)
        clean_value = text(value)
        if clean_key:
            selections[clean_key] = clean_value
    return selections


def split_values(raw: Any) -> list[str]:
    if isinstance(raw, list):
        values = raw
    else:
        values = str(raw or "").splitlines()
    return [text(value) for value in values if text(value)]


def contains_any(value: str, needles: set[str]) -> bool:
    return any(needle in value for needle in needles)


def product_count(values: Any) -> int:
    total = 1
    seen = False
    for value in values:
        seen = True
        total *= max(1, int_value(value))
    return total if seen else 0


def decimal_text(value: Any) -> str | None:
    try:
        return str(Decimal(str(value)).normalize())
    except (InvalidOperation, TypeError, ValueError):
        return None


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def text(value: Any) -> str:
    return str(value or "").strip()


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=pretty, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise VariantAxisClassificationBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
