#!/usr/bin/env python3
"""Build an offline Product Setup dependency/rollback target report.

This helper consumes saved JSON artifacts from
``lt_live_readonly_catalog_authority_audit.py``. It is source-only/offline:
no env files, network, Docker, browser profiles, ERPNext, cache clear, deploy,
provider action, or live mutation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_PRODUCT = "birthday-deliveries"
SCHEMA_VERSION = "lt-product-setup-dependency-rollback-v1"
PROOF_MODE = "offline saved catalog authority JSON artifacts only; no live reads, writes, cache clear, deploy, provider, payment, DNS, or customer action"
SKIP_DIRECTORY_JSON = {
    "index.json",
    "blast-radius.json",
    "authority-packet-report.json",
    "variant-axis-classification.json",
    "dependency-rollback-report.json",
}
CATEGORY_ORDER = [
    "variants",
    "item_prices",
    "website_item",
    "template_item",
    "product_setup",
    "option_rows",
    "media_gallery_rows",
]
FULL_REFERENCE_REQUIREMENTS = {
    "variants": [
        "Item Variant Attribute rows for every retained/current variant",
        "Sales Order Item.item_code references",
        "Sales Invoice Item.item_code references",
        "Cart, quote, payment, and receipt line references",
    ],
    "item_prices": [
        "Complete Standard Selling Item Price row snapshots",
        "Historical order/invoice/payment price references before rate changes",
        "Current checkout resolver proof for price source",
    ],
    "website_item": [
        "Live public route response and rendered page proof",
        "Shop listing/card reference proof",
        "Redirect/route dependency proof before route changes",
    ],
    "template_item": [
        "Template Item attributes and generated variant dependency proof",
        "Historical reference proof for template item_code",
        "Current Webshop resolver proof for template-to-variant behavior",
    ],
    "product_setup": [
        "Owner workflow/publish state proof",
        "Product Setup child-row full snapshots",
        "Historical Product Setup activity/reference proof",
    ],
    "option_rows": [
        "Cart/order/document label proof for every option axis",
        "Add-on runtime pricing proof for add-on candidate axes",
        "Replacement model owner-scope approval",
    ],
    "media_gallery_rows": [
        "File document attachment/reference proof for every image",
        "Website Slideshow row snapshots where a slideshow is linked",
        "Public product page gallery render proof",
    ],
}


class DependencyRollbackBlocked(RuntimeError):
    """Raised when local input/output is missing or invalid."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        paths = collect_paths(args.input)
        products = [build_product_report(path, load_json(path)) for path in paths]
        products = [product for product in products if matches_product(product, args.product)]
        if not products:
            raise DependencyRollbackBlocked(f"no matching product artifacts found for {args.product!r}")
        report = build_report(products, paths, args.product)
        write_report(report, args.output, pretty=args.pretty)
    except DependencyRollbackBlocked as exc:
        print(f"[LT PRODUCT SETUP DEPENDENCY ROLLBACK] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP DEPENDENCY ROLLBACK] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[LT PRODUCT SETUP DEPENDENCY ROLLBACK] " + ("FAIL" if report["blocked_product_count"] else "PASS"), file=sys.stderr)
    print(f"  products: {report['product_count']}", file=sys.stderr)
    print(f"  blocked_products: {report['blocked_product_count']}", file=sys.stderr)
    print(f"  blocker_count: {report['blocker_count']}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and report["blocker_count"]:
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", nargs="+", required=True, help="Saved audit JSON files or directories.")
    parser.add_argument("--output", help="Optional report JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--product", default=DEFAULT_PRODUCT, help=f"Item code, Product Setup, Website Item, or route slug filter. Defaults to {DEFAULT_PRODUCT}.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 when any blocker remains.")
    return parser.parse_args(argv)


def collect_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    explicit_files: set[Path] = set()
    for raw in inputs:
        path = Path(raw)
        if not path.exists():
            raise DependencyRollbackBlocked(f"input does not exist: {path}")
        if path.is_dir():
            paths.extend(
                child
                for child in sorted(path.glob("*.json"))
                if child.is_file() and child.name not in SKIP_DIRECTORY_JSON and not child.name.endswith("-projection.json")
            )
        elif path.suffix.lower() == ".json":
            paths.append(path)
            explicit_files.add(path.resolve())
        else:
            raise DependencyRollbackBlocked(f"input is not a JSON file or directory: {path}")
    unique = sorted({path.resolve() for path in paths})
    if not unique:
        raise DependencyRollbackBlocked("no saved audit JSON artifacts found")
    for path in unique:
        if path in explicit_files and (path.name in SKIP_DIRECTORY_JSON or path.name.endswith("-projection.json")):
            raise DependencyRollbackBlocked(f"explicit input is a report/projection artifact, not a product audit: {path}")
    return unique


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DependencyRollbackBlocked(f"input is not valid JSON: {path}: {exc}") from exc
    except OSError as exc:
        raise DependencyRollbackBlocked(f"could not read input: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DependencyRollbackBlocked(f"JSON root must be an object: {path}")
    if not is_audit_artifact(payload):
        raise DependencyRollbackBlocked(f"not a recognized catalog authority audit artifact: {path}")
    return payload


def is_audit_artifact(payload: dict[str, Any]) -> bool:
    return any(key in payload for key in ("rows", "counts", "blueprint_summary", "website_item_summary", "price_summary"))


def build_product_report(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    rows = payload.get("rows") if isinstance(payload.get("rows"), dict) else {}
    counts = payload.get("counts") if isinstance(payload.get("counts"), dict) else {}
    product = product_identifier(payload)
    categories = {
        "variants": variants_category(rows, counts),
        "item_prices": item_prices_category(rows, counts),
        "website_item": website_item_category(rows, payload),
        "template_item": template_item_category(rows, payload),
        "product_setup": product_setup_category(rows, payload),
        "option_rows": option_rows_category(rows, counts),
        "media_gallery_rows": media_gallery_category(rows, payload),
    }
    blockers = dedupe_blockers(
        [
            *existing_failure_blockers(payload),
            *authority_blockers(payload, product),
            *category_blockers(categories),
        ]
    )
    return {
        "artifact": str(path),
        "product_identifier": product,
        "status": "blocked" if blockers else "dependency_rollback_targets_captured",
        "proof_mode": PROOF_MODE,
        "source_artifact": {
            "generated_at": payload.get("generated_at"),
            "scope": payload.get("scope"),
            "top_level_keys": sorted(payload.keys()),
        },
        "saved_artifact_counts": stable_counts(counts, rows),
        "target_categories": categories,
        "rollback_capture_plan": rollback_capture_plan(categories),
        "blockers": blockers,
        "next_action": next_action(blockers),
        "approval_state": {
            "planning_only": True,
            "mutation_approved": False,
            "collapse_approved": False,
            "cache_clear_approved": False,
            "deploy_approved": False,
            "requires_owner_scope_approval": True,
            "requires_live_reference_proof": True,
            "requires_historical_reference_proof": True,
        },
    }


def product_identifier(payload: dict[str, Any]) -> dict[str, Any]:
    identifier = payload.get("product_identifier") if isinstance(payload.get("product_identifier"), dict) else {}
    website = payload.get("website_item_summary") if isinstance(payload.get("website_item_summary"), dict) else {}
    blueprint = payload.get("blueprint_summary") if isinstance(payload.get("blueprint_summary"), dict) else {}
    route = first_present(identifier, "route") or website.get("route")
    route_slug = first_present(identifier, "route_slug") or str(route or "").strip("/").split("/")[-1]
    return {
        "product_setup": first_present(identifier, "product_setup") or blueprint.get("name"),
        "item_code": first_present(identifier, "item_code") or website.get("item_code") or blueprint.get("target_item_code"),
        "website_item": first_present(identifier, "website_item") or website.get("name") or blueprint.get("target_website_item"),
        "product_name": first_present(identifier, "product_name") or blueprint.get("product_name") or website.get("web_item_name"),
        "route": route,
        "route_slug": route_slug,
        "brand_lane": first_present(identifier, "brand_lane") or blueprint.get("operating_brand"),
        "brand_lane_status": first_present(identifier, "brand_lane_status") or "not_proved",
    }


def matches_product(product_report: dict[str, Any], product_filter: str) -> bool:
    needle = normalize(product_filter)
    product = product_report["product_identifier"]
    values = {
        normalize(product.get("product_setup")),
        normalize(product.get("item_code")),
        normalize(product.get("website_item")),
        normalize(product.get("route_slug")),
        normalize(str(product.get("route") or "").strip("/").split("/")[-1]),
    }
    return needle in values


def variants_category(rows: dict[str, Any], counts: dict[str, Any]) -> dict[str, Any]:
    variants = rows_from(rows, "variants")
    count = int_value(counts.get("variants"), default=len(variants))
    rollback_rows = [
        compact_row(row, ("name", "item_code", "variant_of", "disabled", "is_sales_item", "is_stock_item", "image", "modified", "modified_by"))
        for row in variants
    ]
    return category(
        code="variants",
        doctype="Item",
        row_count=count,
        artifact_row_count=len(variants),
        rollback_snapshot_status="partial_saved_artifact_snapshot" if variants else "missing_from_artifact",
        dependency_fields=["Item.item_code", "Item.name", "Item.variant_of", "Item.disabled", "Item.image", "Item.is_sales_item", "Item.is_stock_item"],
        rollback_fields=["name", "item_code", "variant_of", "disabled", "image", "is_sales_item", "is_stock_item", "modified", "modified_by"],
        rollback_rows=rollback_rows,
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["variants"],
    )


def item_prices_category(rows: dict[str, Any], counts: dict[str, Any]) -> dict[str, Any]:
    prices = rows_from(rows, "item_prices")
    count = int_value(counts.get("item_prices"), default=len(prices))
    rollback_rows = [
        compact_row(row, ("name", "item_code", "price_list", "price_list_rate", "currency", "selling", "uom", "valid_from", "valid_upto", "modified", "modified_by"))
        for row in prices
    ]
    return category(
        code="item_prices",
        doctype="Item Price",
        row_count=count,
        artifact_row_count=len(prices),
        rollback_snapshot_status="partial_saved_artifact_snapshot" if prices else "missing_from_artifact",
        dependency_fields=["Item Price.item_code", "Item Price.price_list", "Item Price.price_list_rate", "Item Price.currency", "Item Price.selling"],
        rollback_fields=["name", "item_code", "price_list", "price_list_rate", "currency", "selling", "uom", "valid_from", "valid_upto", "modified", "modified_by"],
        rollback_rows=rollback_rows,
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["item_prices"],
    )


def website_item_category(rows: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    row = first_dict(rows.get("website_item")) or dict_value(payload, "website_item_summary")
    rollback_rows = [compact_row(row, ("name", "item_code", "route", "published", "website_image", "slideshow", "lt_commerce_lane", "lt_product_page_type", "modified", "modified_by"))] if row else []
    return category(
        code="website_item",
        doctype="Website Item",
        row_count=1 if row else 0,
        artifact_row_count=1 if row else 0,
        rollback_snapshot_status="partial_saved_artifact_snapshot" if row else "missing_from_artifact",
        dependency_fields=["Website Item.name", "Website Item.item_code", "Website Item.route", "Website Item.published", "Website Item.website_image", "Website Item.slideshow"],
        rollback_fields=["name", "item_code", "route", "published", "website_image", "slideshow", "lt_brand_description", "lt_product_details", "modified", "modified_by"],
        rollback_rows=rollback_rows,
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["website_item"],
    )


def template_item_category(rows: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    row = first_dict(rows.get("template_item")) or dict_value(payload, "template_item_summary")
    attributes = as_list(row.get("attributes")) if row else []
    rollback_rows = [compact_row(row, ("name", "item_code", "item_name", "has_variants", "disabled", "published_in_website", "image", "modified", "modified_by"))] if row else []
    extra = {"template_attribute_count": len(attributes), "template_attributes": [compact_row(attr, ("name", "attribute", "idx", "modified", "modified_by")) for attr in attributes]}
    return category(
        code="template_item",
        doctype="Item",
        row_count=1 if row else 0,
        artifact_row_count=1 if row else 0,
        rollback_snapshot_status="partial_saved_artifact_snapshot" if row else "missing_from_artifact",
        dependency_fields=["Item.item_code", "Item.has_variants", "Item.attributes", "Item.image", "Item.published_in_website"],
        rollback_fields=["name", "item_code", "item_name", "has_variants", "disabled", "published_in_website", "image", "attributes", "modified", "modified_by"],
        rollback_rows=rollback_rows,
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["template_item"],
        extra=extra,
    )


def product_setup_category(rows: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    row = first_dict(rows.get("blueprint")) or dict_value(payload, "blueprint_summary")
    rollback_rows = [compact_row(row, ("name", "product_slug", "product_name", "publish_status", "validation_status", "shop_visibility", "target_item_code", "target_website_item", "base_price", "operating_brand", "modified", "modified_by"))] if row else []
    return category(
        code="product_setup",
        doctype="LT Product Blueprint",
        row_count=1 if row else 0,
        artifact_row_count=1 if row else 0,
        rollback_snapshot_status="partial_saved_artifact_snapshot" if row else "missing_from_artifact",
        dependency_fields=["LT Product Blueprint.name", "target_item_code", "target_website_item", "publish_status", "operating_brand", "base_price"],
        rollback_fields=["name", "product_slug", "publish_status", "validation_status", "shop_visibility", "target_item_code", "target_website_item", "base_price", "operating_brand", "modified", "modified_by"],
        rollback_rows=rollback_rows,
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["product_setup"],
    )


def option_rows_category(rows: dict[str, Any], counts: dict[str, Any]) -> dict[str, Any]:
    option_rows = rows_from(rows, "blueprint_option_rows")
    count = int_value(counts.get("blueprint_option_rows"), default=len(option_rows))
    axes = [
        {
            "axis_name": row.get("axis_name"),
            "selection_behavior": row.get("selection_behavior"),
            "payload_target": row.get("payload_target"),
            "pricing_behavior": row.get("pricing_behavior"),
            "required": bool(row.get("required")),
            "value_count": len(split_values(row.get("values"))),
            "sample_values": split_values(row.get("values"))[:10],
        }
        for row in option_rows
    ]
    return category(
        code="option_rows",
        doctype="LT Product Blueprint Option",
        row_count=count,
        artifact_row_count=len(option_rows),
        rollback_snapshot_status="partial_saved_artifact_snapshot" if option_rows else "missing_from_artifact",
        dependency_fields=["axis_name", "selection_behavior", "payload_target", "pricing_behavior", "values", "document_output"],
        rollback_fields=["name", "idx", "axis_name", "selection_behavior", "payload_target", "pricing_behavior", "values", "modified", "modified_by"],
        rollback_rows=[compact_row(row, ("name", "idx", "axis_name", "selection_behavior", "payload_target", "pricing_behavior", "values", "required", "modified", "modified_by")) for row in option_rows],
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["option_rows"],
        extra={"axes": axes},
    )


def media_gallery_category(rows: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    gallery = rows_from(rows, "blueprint_gallery_rows")
    media_rules = rows_from(rows, "blueprint_media_rule_rows")
    website = first_dict(rows.get("website_item")) or dict_value(payload, "website_item_summary")
    template = first_dict(rows.get("template_item")) or dict_value(payload, "template_item_summary")
    primary_images = sorted({value for value in [website.get("website_image"), template.get("image")] if value})
    row_count = len(gallery) + len(media_rules) + len(primary_images)
    rollback_rows = [
        *[dict(compact_row(row, ("name", "idx", "image", "heading", "approved_for_customer", "modified", "modified_by")), source="blueprint_gallery_rows") for row in gallery],
        *[dict(compact_row(row, ("name", "idx", "rule_name", "rule_type", "variant_item", "image", "approved_for_customer", "modified", "modified_by")), source="blueprint_media_rule_rows") for row in media_rules],
        *[{"source": "primary_image_pointer", "image": image} for image in primary_images],
    ]
    extra = {
        "primary_images": primary_images,
        "website_item_slideshow": website.get("slideshow"),
        "gallery_row_count": len(gallery),
        "media_rule_row_count": len(media_rules),
    }
    return category(
        code="media_gallery_rows",
        doctype="LT Product Blueprint Gallery/Media plus Website Item media pointers",
        row_count=row_count,
        artifact_row_count=row_count,
        rollback_snapshot_status="partial_saved_artifact_snapshot" if row_count else "missing_from_artifact",
        dependency_fields=["Website Item.website_image", "Website Item.slideshow", "Item.image", "Gallery.image", "Media Rule.variant_item"],
        rollback_fields=["image", "slideshow", "gallery_image_rows", "media_rule_rows", "modified", "modified_by"],
        rollback_rows=rollback_rows,
        reference_requirements=FULL_REFERENCE_REQUIREMENTS["media_gallery_rows"],
        extra=extra,
    )


def category(
    *,
    code: str,
    doctype: str,
    row_count: int,
    artifact_row_count: int,
    rollback_snapshot_status: str,
    dependency_fields: list[str],
    rollback_fields: list[str],
    rollback_rows: list[dict[str, Any]],
    reference_requirements: list[str],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "category": code,
        "doctype": doctype,
        "row_count": row_count,
        "artifact_row_count": artifact_row_count,
        "rollback_snapshot_status": rollback_snapshot_status,
        "dependency_fields": dependency_fields,
        "rollback_fields_to_capture_before_mutation": rollback_fields,
        "rollback_rows": rollback_rows,
        "sample_rows": rollback_rows[:5],
        "all_rows_included": len(rollback_rows) == artifact_row_count,
        "live_reference_proof_status": "missing",
        "historical_reference_proof_status": "missing",
        "required_reference_proof": reference_requirements,
        "mutation_approval": False,
    }
    if extra:
        result.update(extra)
    return result


def existing_failure_blockers(payload: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = []
    for failure in as_list(payload.get("failures")):
        if str(failure).strip():
            blockers.append(blocker("source_audit_failure", str(failure), {"source": "artifact.failures"}))
    return blockers


def authority_blockers(payload: dict[str, Any], product: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = []
    brand_status = str(product.get("brand_lane_status") or "").strip()
    if not product.get("brand_lane") or brand_status not in {"proved", "verified", "resolved"}:
        blockers.append(
            blocker(
                "live_brand_lane_proof_missing",
                "Saved artifact does not prove live/public brand lane authority.",
                {"brand_lane": product.get("brand_lane"), "brand_lane_status": brand_status or None},
            )
        )
    public_summary = payload.get("public_summary") if isinstance(payload.get("public_summary"), dict) else {}
    if not public_summary or public_summary.get("skipped") or public_summary.get("status") != 200:
        blockers.append(
            blocker(
                "live_public_route_proof_missing",
                "Saved artifact does not prove the live public product route.",
                {"public_summary": public_summary or None},
            )
        )
    match = payload.get("match_summary") if isinstance(payload.get("match_summary"), dict) else {}
    candidates = as_list(match.get("candidate_blueprints"))
    if not candidates:
        blockers.append(
            blocker(
                "source_product_setup_candidate_proof_missing",
                "Saved artifact does not include Product Setup candidate proof.",
                {"match_summary": match or None},
            )
        )
    if not source_candidate_uniqueness_proved(candidates, product):
        blockers.append(
            blocker(
                "same_brand_source_uniqueness_proof_missing",
                "Saved artifact does not prove one source-active Product Setup for the same brand and target keys.",
                {"candidate_count": len(candidates), "brand_lane": product.get("brand_lane")},
            )
        )
    return blockers


def category_blockers(categories: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    blockers = []
    for code in CATEGORY_ORDER:
        category_data = categories[code]
        if category_data["rollback_snapshot_status"] != "partial_saved_artifact_snapshot":
            blockers.append(
                blocker(
                    f"{code}_rollback_snapshot_missing",
                    f"{code} rollback target rows are missing from the saved artifact.",
                    {"category": code, "row_count": category_data["row_count"]},
                )
            )
        blockers.append(
            blocker(
                f"{code}_live_reference_proof_missing",
                f"{code} live/runtime reference proof is missing.",
                {"category": code, "required_reference_proof": category_data["required_reference_proof"]},
            )
        )
        blockers.append(
            blocker(
                f"{code}_historical_reference_proof_missing",
                f"{code} historical reference proof is missing.",
                {"category": code, "required_reference_proof": category_data["required_reference_proof"]},
            )
        )
    media = categories["media_gallery_rows"]
    if media.get("website_item_slideshow"):
        blockers.append(
            blocker(
                "website_slideshow_row_snapshots_missing",
                "Website Item links a slideshow, but saved artifact does not include Website Slideshow child-row snapshots.",
                {"slideshow": media.get("website_item_slideshow")},
            )
        )
    if media.get("primary_images") or media.get("gallery_row_count") or media.get("media_rule_row_count"):
        blockers.append(
            blocker(
                "file_attachment_reference_proof_missing",
                "Saved artifact does not include File document attachment/reference proof for product media.",
                {"primary_images": media.get("primary_images"), "gallery_row_count": media.get("gallery_row_count"), "media_rule_row_count": media.get("media_rule_row_count")},
            )
        )
    return blockers


def source_candidate_uniqueness_proved(candidates: list[Any], product: dict[str, Any]) -> bool:
    brand = str(product.get("brand_lane") or "").strip()
    if not brand:
        return False
    active_statuses = {"Local Preview Ready", "Staging Ready", "Approved For Live"}
    same_brand_active = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
        and str(candidate.get("publish_status") or "").strip() in active_statuses
        and str(candidate.get("operating_brand") or "").strip() == brand
    ]
    return len(same_brand_active) == 1


def rollback_capture_plan(categories: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    plan = []
    for code in CATEGORY_ORDER:
        category_data = categories[code]
        plan.append(
            {
                "category": code,
                "doctype": category_data["doctype"],
                "target_row_count": category_data["row_count"],
                "artifact_row_count": category_data["artifact_row_count"],
                "rollback_snapshot_status": category_data["rollback_snapshot_status"],
                "fields_to_capture": category_data["rollback_fields_to_capture_before_mutation"],
                "reference_proof_required": category_data["required_reference_proof"],
            }
        )
    return plan


def build_report(products: list[dict[str, Any]], paths: list[Path], product_filter: str) -> dict[str, Any]:
    blocked = [product for product in products if product["blockers"]]
    blocker_breakdown: dict[str, int] = {}
    for product in products:
        for row in product["blockers"]:
            code = str(row.get("code") or "unknown")
            blocker_breakdown[code] = blocker_breakdown.get(code, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": "deterministic-offline-report",
        "deterministic": True,
        "proof_mode": PROOF_MODE,
        "product_filter": product_filter,
        "input_artifacts": [str(path) for path in paths],
        "artifact_count": len(paths),
        "product_count": len(products),
        "blocked_product_count": len(blocked),
        "blocker_count": sum(len(product["blockers"]) for product in products),
        "blocker_breakdown": dict(sorted(blocker_breakdown.items())),
        "target_category_order": CATEGORY_ORDER,
        "products": products,
        "next_safe_actions": [
            "Use this as an offline dependency/rollback target map only.",
            "Capture full pre-mutation row snapshots and live route/runtime proof before any write path.",
            "Prove historical order, invoice, payment, cart, file, and document references before disabling, deleting, renaming, repurposing, or collapsing variants.",
        ],
    }


def stable_counts(counts: dict[str, Any], rows: dict[str, Any]) -> dict[str, int]:
    keys = [
        "variants",
        "item_prices",
        "blueprint_price_rows",
        "blueprint_option_rows",
        "blueprint_gallery_rows",
        "blueprint_media_rule_rows",
        "blueprint_add_on_rows",
        "blueprint_conditional_price_rows",
    ]
    return {key: int_value(counts.get(key), default=len(rows_from(rows, key.replace("blueprint_", "blueprint_")))) for key in keys}


def next_action(blockers: list[dict[str, Any]]) -> str:
    if blockers:
        return "Blocked: collect full rollback snapshots plus live and historical reference proof before replacement model design can move toward mutation."
    return "Dependency/rollback targets are captured from saved artifacts; separate owner approval and live verification are still required before mutation."


def blocker(code: str, message: str, evidence: Any) -> dict[str, Any]:
    return {"code": code, "message": message, "evidence": evidence}


def dedupe_blockers(blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in blockers:
        key = str(row.get("code") or json.dumps(row, sort_keys=True, default=str))
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def rows_from(parent: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = parent.get(key)
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def first_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        for row in value:
            if isinstance(row, dict):
                return row
    return {}


def dict_value(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    return value if isinstance(value, dict) else {}


def compact_row(row: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {key: row.get(key) for key in keys if key in row}


def split_values(raw: Any) -> list[str]:
    if isinstance(raw, list):
        values = raw
    else:
        values = str(raw or "").splitlines()
    return [str(value).strip() for value in values if str(value).strip()]


def first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    return None


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize(value: Any) -> str:
    return str(value or "").strip().lower().strip("/")


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=True, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise DependencyRollbackBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
