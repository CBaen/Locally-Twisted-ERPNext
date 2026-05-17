#!/usr/bin/env python3
"""Build the non-destructive V1 Odoo-to-ERPNext import manifest.

The manifest narrows global source/price/media/add-on blockers to the approved
V1 import subset. It reads existing source/audit artifacts only and writes
evidence files; it does not connect to ERPNext and does not purge, import, or
delete.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from locally_twisted.catalog_import_subset import OWNER_EXPLICIT_EXCLUDED_SLUGS, OWNER_MUST_WORK_SLUGS
from locally_twisted.catalog_contract import build_product_page_contract
from locally_twisted.catalog_contract.pattern_mapper import (
    build_product_pattern_contract as build_source_pattern_contract,
)
from locally_twisted.catalog_variant_rules import project_required_variant_combo


AUDIT_ROOT = ROOT / "audits" / "odoo-erpnext-migration-audit-2026-05-08"
SOURCE_ROOT = ROOT / "_resources" / "odoo-live"
RUNTIME_MODULE = APP_PATH / "locally_twisted" / "product_page_runtime.py"
PURGE_SCOPE_JSON = AUDIT_ROOT / "16-catalog-purge-scope-dry-run.json"
PRICE_ENRICHMENT_JSON = AUDIT_ROOT / "21-product-page-price-enrichment-candidates.json"
PRICE_REVIEW_JSON = AUDIT_ROOT / "24-product-page-price-review-packet.json"
MEDIA_PACKET_JSON = AUDIT_ROOT / "23-product-page-media-classification-packet.json"
ADD_ON_PACKET_JSON = AUDIT_ROOT / "22-product-add-on-approval-packet.json"
OUTPUT_JSON = AUDIT_ROOT / "25-v1-odoo-erpnext-import-manifest.json"
OUTPUT_MD = AUDIT_ROOT / "25-v1-odoo-erpnext-import-manifest.md"
RUNTIME_CONSTANTS = {}


def main() -> int:
    parse_noop_args(__doc__)
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = build_manifest(generated_at)
    OUTPUT_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(manifest), encoding="utf-8")

    summary = manifest["summary"]
    ok = manifest["validation"]["ok"]
    print("[V1 ODOO ERPNext IMPORT MANIFEST] " + ("PASS" if ok else "FAIL"))
    print(f"json={OUTPUT_JSON}")
    print(f"md={OUTPUT_MD}")
    print(
        f"included={summary['included_products']} excluded={summary['excluded_products']} "
        f"sale_units={summary['v1_sale_units']} price_review_units={summary['v1_price_review_units']} "
        f"extra_images_held={summary['v1_extra_images_held']}"
    )
    for error in manifest["validation"]["errors"]:
        print(f"validation_error={error}")
    return 0 if ok else 1


def build_manifest(generated_at: str) -> dict[str, Any]:
    runtime_constants = _runtime_constants()
    config_version = runtime_constants["CONFIG_VERSION"]
    line_fieldnames = runtime_constants["LINE_FIELDNAMES"]
    purge_scope = _read_json(PURGE_SCOPE_JSON)
    included_slugs = list(purge_scope["v1_subset"]["included_slugs"])
    included_set = set(included_slugs)
    excluded_products = purge_scope["v1_subset"]["excluded_products"]

    catalog = _catalog_by_slug()
    slug_to_group = _slug_to_group()
    price_enrichment = {row["slug"]: row for row in _read_json(PRICE_ENRICHMENT_JSON)["products"]}
    price_review = {row["slug"]: row for row in _read_json(PRICE_REVIEW_JSON)["products"]}
    media_packet = {row["slug"]: row for row in _read_json(MEDIA_PACKET_JSON)["products"]}
    add_on_axes = _add_on_axes_by_slug()

    products: list[dict[str, Any]] = []
    warning_counts = Counter()
    sale_units_by_source = Counter()
    v1_price_review_units = 0
    v1_extra_images_held = 0
    confirmed_add_on_product_count = 0
    review_only_add_on_product_count = 0

    for slug in included_slugs:
        source = catalog[slug]
        category_hint = slug_to_group.get(slug, "")
        contract = build_product_page_contract(source, category_hint=category_hint)
        source_pattern_contract = build_source_pattern_contract(source).to_dict()
        warnings = _warning_codes(contract)
        warning_counts.update(warnings)

        price_row = price_enrichment.get(slug, {})
        source_price_resolution = _source_price_resolution(source, contract, price_row)
        review_row = price_review.get(slug, {})
        media_row = media_packet.get(slug, {})
        sale_units = source_price_resolution["sale_units"]
        for unit in sale_units:
            sale_units_by_source[unit.get("price_resolution_status") or "unknown"] += 1

        review_units = int(source_price_resolution["counts"]["source_price_missing_checkout_hold"]) + int(
            source_price_resolution["counts"]["conflict_needs_fix"]
        )
        extra_images = int(media_row.get("extra_image_count") or 0)
        v1_price_review_units += review_units
        v1_extra_images_held += extra_images
        confirmed_add_ons = [row for row in contract.add_ons if row.status == "confirmed"]
        if confirmed_add_ons:
            confirmed_add_on_product_count += 1
        review_only_axes = add_on_axes.get(slug, [])
        if review_only_axes:
            review_only_add_on_product_count += 1
        import_status, status_reasons = _product_import_status(
            contract=contract,
            review_units=review_units,
            review_only_axes=review_only_axes,
        )

        products.append(
            {
                "slug": slug,
                "source_name": source.get("name"),
                "odoo_id": source.get("odoo_id"),
                "source_url": source.get("url"),
                "include_in_v1": True,
                "ecommerce_import_status": import_status,
                "status_reasons": status_reasons,
                "source_trace": _source_trace(source, source_pattern_contract),
                "erpnext_mapping": {
                    "template_item_code": slug,
                    "website_item_code": slug,
                    "item_group": category_hint,
                    "route": contract.route,
                    "website_item_fields": {
                        "lt_product_page_type": contract.product_page_type,
                        "lt_commerce_lane": contract.commerce_lane,
                    },
                    "line_level_configuration_fields": line_fieldnames,
                    "configuration_version": config_version,
                },
                "product_contract": {
                    "product_page_type": contract.product_page_type,
                    "commerce_lane": contract.commerce_lane,
                    "source_pattern_class": list(source_pattern_contract.get("patterns") or []),
                    "required_axes": [
                        {
                            "name": axis.name,
                            "values": list(axis.values),
                            "selector_type": axis.selector_type,
                            "status": axis.status,
                        }
                        for axis in contract.required_axes
                    ],
                    "customization_axes": [axis.name for axis in contract.customization_axes],
                    "source_variant_rows": contract.source_variant_rows,
                    "warning_codes": warnings,
                },
                "price_manifest": {
                    "expected_units": source_price_resolution["expected_units"],
                    "candidate_units": source_price_resolution["candidate_units"],
                    "review_units": review_units,
                    "decision": _price_decision(source_price_resolution),
                    "resolution_counts": source_price_resolution["counts"],
                    "sale_units": _sale_unit_manifest(sale_units),
                },
                "media_manifest": {
                    "primary_image_url": media_row.get("primary_image_url") or contract.primary_image,
                    "primary_decision": "import_as_primary_image",
                    "extra_image_count": extra_images,
                    "extra_image_decision": "hold_until_classified",
                    "extra_images": [
                        {
                            "source_index": image.get("source_index"),
                            "url": image.get("url"),
                            "decision": "hold_until_classified",
                        }
                        for image in media_row.get("images") or []
                    ],
                },
                "add_on_manifest": {
                    "confirmed_checkout_add_ons": [
                        {
                            "key": add_on.key,
                            "label": add_on.label,
                            "item_code": add_on.item_code,
                            "source_attribute": add_on.source_attribute,
                            "unit_price": add_on.unit_price,
                            "quantity_min": add_on.quantity_min,
                            "quantity_max": add_on.quantity_max,
                            "requires_value": add_on.requires_value,
                            "receipt_label": add_on.receipt_label,
                            "status": add_on.status,
                        }
                        for add_on in confirmed_add_ons
                    ],
                    "review_only_axes_from_global_packet": review_only_axes,
                    "decision": "no_v1_review_only_add_on_blocker" if not review_only_axes else "hide_add_on_until_mapped",
                },
            }
        )

    excluded_reason_counts = Counter(row["primary_exclusion_reason"] for row in excluded_products)
    excluded_price_review_units = _excluded_price_review_units(price_review, included_set)
    excluded_extra_images = _excluded_extra_images(media_packet, included_set)
    excluded_add_on_products = _excluded_add_on_products(add_on_axes, included_set)
    status_counts = Counter(row["ecommerce_import_status"] for row in products)

    manifest = {
        "schema_version": "lt-v1-odoo-erpnext-import-manifest-v1",
        "generated_at": generated_at,
        "read_only": True,
        "destructive_allowed": False,
        "source_artifacts": {
            "source_catalog": str((SOURCE_ROOT / "catalog.json").relative_to(ROOT)),
            "slug_to_group": str((SOURCE_ROOT / "slug_to_group.json").relative_to(ROOT)),
            "purge_scope": str(PURGE_SCOPE_JSON.relative_to(ROOT)),
            "price_enrichment": str(PRICE_ENRICHMENT_JSON.relative_to(ROOT)),
            "price_review": str(PRICE_REVIEW_JSON.relative_to(ROOT)),
            "media_packet": str(MEDIA_PACKET_JSON.relative_to(ROOT)),
            "add_on_packet": str(ADD_ON_PACKET_JSON.relative_to(ROOT)),
        },
        "runtime_contract": {
            "configuration_version": config_version,
            "line_fieldnames": line_fieldnames,
        },
        "summary": {
            "included_products": len(included_slugs),
            "excluded_products": len(excluded_products),
            "excluded_by_primary_reason": dict(sorted(excluded_reason_counts.items())),
            "v1_sale_units": sum(int(row["price_manifest"]["candidate_units"] or 0) for row in products),
            "v1_price_review_units": v1_price_review_units,
            "v1_price_units_by_source": dict(sorted(sale_units_by_source.items())),
            "v1_extra_images_held": v1_extra_images_held,
            "v1_confirmed_add_on_products": confirmed_add_on_product_count,
            "v1_review_only_add_on_products": review_only_add_on_product_count,
            "excluded_price_review_units": excluded_price_review_units,
            "excluded_extra_images": excluded_extra_images,
            "excluded_review_only_add_on_products": excluded_add_on_products,
            "v1_source_warning_counts": dict(sorted(warning_counts.items())),
            "v1_status_counts": dict(sorted(status_counts.items())),
        },
        "owner_decisions_still_needed": [
            {
                "id": "v1_source_price_resolution",
                "scope": "V1 included products",
                "count": v1_price_review_units,
                "decision_needed": "Resolve source price conflicts, or keep source-missing sale units blocked from checkout until priced.",
                "safe_default": "source_price_missing_checkout_hold",
            },
            {
                "id": "v1_extra_images",
                "scope": "V1 included products",
                "count": v1_extra_images_held,
                "decision_needed": "Only needed if extras should publish in V1; otherwise the manifest holds them and imports primary images only.",
                "safe_default": "hold_until_classified",
            },
            {
                "id": "v1_review_only_add_ons",
                "scope": "V1 included products with review-only add-on axes",
                "count": review_only_add_on_product_count,
                "decision_needed": "Approve each review-only add-on family for checkout add-on controls, or keep those add-on controls hidden until mapped.",
                "safe_default": "hide_add_on_until_mapped",
            },
        ],
        "blocker_reduction": {
            "source_contract": f"Corrected V1 includes Odoo-imported products as sellable product targets when source trace and backend schema are present. Warning counts inside V1: {dict(sorted(warning_counts.items()))}.",
            "price_review": f"Corrected V1 prices are derived from source artifacts where possible. Resolution counts: {dict(sorted(sale_units_by_source.items()))}. Excluded live-snapshot review units: {excluded_price_review_units}.",
            "media": f"{v1_extra_images_held} global extra image rows apply to corrected V1; {excluded_extra_images} belong to products outside this generated subset. Primary images are source-backed and extras are held unless approved.",
            "add_ons": f"{review_only_add_on_product_count} corrected V1 products have review-only add-on axes. Those add-on controls stay hidden until mapped; the products themselves remain sellable targets. Confirmed foil_number add-on remains available where eligible.",
        },
        "products": products,
        "excluded_products": excluded_products,
        "next_command_sequence": [
            "python scripts/verify/v1_odoo_erpnext_import_manifest.py",
            "python scripts/verify/catalog_purge_scope_dry_run.py",
            "python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json",
            "python scripts/setup/stage_seed_data.py",
            "bench --site frontend backup --with-files",
            "bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs \"{'dry_run': True}\"",
        ],
    }
    manifest["validation"] = _validate_manifest(manifest)
    return manifest


def _source_trace(product: dict[str, Any], source_pattern_contract: dict[str, Any]) -> dict[str, Any]:
    """Carry source identity and mapper semantics into the import manifest."""
    return {
        "odoo_product_id": product.get("odoo_id"),
        "source_url": product.get("url"),
        "source_integrity": source_pattern_contract.get("source_integrity") or {},
        "source_pattern_class": list(source_pattern_contract.get("patterns") or []),
        "source_axis_hashes": _source_axis_hashes(source_pattern_contract),
        "source_variant_pointers": _source_variant_pointers(product),
    }


def _source_axis_hashes(source_pattern_contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for axis in source_pattern_contract.get("axis_contracts") or []:
        rows.append(
            {
                "name": axis.get("name"),
                "source_value_hash": axis.get("source_value_hash"),
                "source_value_count": axis.get("source_value_count"),
                "patterns": axis.get("patterns") or [],
                "primitive_key": axis.get("primitive_key"),
                "selector_key": axis.get("selector_key"),
            }
        )
    return rows


def _source_variant_pointers(product: dict[str, Any]) -> dict[str, Any]:
    pointers = []
    for index, row in enumerate(product.get("valid_variants") or []):
        combo = row.get("combo") or {}
        pointers.append(
            {
                "source_index": index,
                "ptav_ids": row.get("ptav_ids") or [],
                "combo": dict(combo) if isinstance(combo, dict) else {},
                "price": row.get("price"),
                "erpnext_variant_price": row.get("erpnext_variant_price"),
            }
        )
    encoded = json.dumps(pointers, sort_keys=True, separators=(",", ":"), default=str)
    return {
        "source_variant_count": len(pointers),
        "source_variant_pointer_hash": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        "source_variant_pointer_samples": pointers[:10],
    }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _catalog_by_slug() -> dict[str, dict[str, Any]]:
    catalog = _read_json(SOURCE_ROOT / "catalog.json")
    products = catalog.get("products") if isinstance(catalog, dict) else catalog
    return {row["slug"]: row for row in products}


def _slug_to_group() -> dict[str, str]:
    rows = _read_json(SOURCE_ROOT / "slug_to_group.json")
    return {key: value for key, value in rows.items() if not key.startswith("_")}


def _add_on_axes_by_slug() -> dict[str, list[str]]:
    packet = _read_json(ADD_ON_PACKET_JSON)
    by_slug: dict[str, list[str]] = {}
    for axis in packet.get("review_axes") or []:
        for product in axis.get("products") or []:
            by_slug.setdefault(product["slug"], []).append(axis["axis"])
    return by_slug


def _warning_codes(contract) -> list[str]:
    codes: list[str] = []
    for warning in contract.warnings:
        if warning.startswith("Axis needs review before import:"):
            codes.append("axis_needs_review")
        elif warning.startswith("Color axis removed"):
            codes.append("color_axis_customization")
        elif "lacks resolver-backed" in warning:
            codes.append("missing_resolver_prices")
        elif "alternate images" in warning:
            codes.append("unclassified_gallery_images")
        else:
            codes.append("other")
    return sorted(set(codes))


def _source_price_resolution(product: dict[str, Any], contract, price_row: dict[str, Any] | None = None) -> dict[str, Any]:
    axes = [axis.name for axis in contract.required_axes]
    rows = product.get("valid_variants") or []
    groups: dict[tuple[tuple[str, str], ...], list[dict[str, Any]]] = {}
    if rows:
        for row in rows:
            combo = project_required_variant_combo(row.get("combo") or {})
            key = tuple((axis, str(combo.get(axis) or "")) for axis in axes) if axes else (("single SKU", ""),)
            groups.setdefault(key, []).append(row)
    else:
        groups[(("single SKU", ""),)] = [{"combo": {}, "price": product.get("base_price")}]

    sale_units = []
    counts: Counter[str] = Counter()
    enrichment_prices = _price_enrichment_prices(price_row)
    for key in sorted(groups):
        source_rows = groups[key]
        prices = sorted(
            {
                _price_string(row.get("price", product.get("base_price")))
                for row in source_rows
                if row.get("price", product.get("base_price")) is not None
            }
        )
        projected_combo = {axis: value for axis, value in key if axis != "single SKU"}
        enrichment_price = enrichment_prices.get(_combo_key(projected_combo))
        if enrichment_price:
            status = "source_price_ready"
            chosen_price = enrichment_price
            decision = "use_price_enrichment_artifact"
            price_source_kind = "price_enrichment_artifact"
        elif not prices:
            status = "source_price_missing_checkout_hold"
            chosen_price = None
            decision = "block_checkout_until_price_set"
            price_source_kind = "source_hold"
        elif len(prices) > 1:
            status = "conflict_needs_fix"
            chosen_price = None
            decision = "fix_conflicting_source_prices_before_import"
            price_source_kind = "source_hold"
        else:
            status = "source_price_ready"
            chosen_price = prices[0]
            decision = "use_source_artifact_price"
            price_source_kind = "odoo_source_artifact"
        counts[status] += 1
        sale_units.append(
            {
                "sale_unit_key": _sale_unit_key(projected_combo),
                "projected_required_combo": projected_combo,
                "chosen_price": chosen_price,
                "price_source_kind": price_source_kind,
                "price_resolution_status": status,
                "price_decision": decision,
                "source_prices": prices,
                "source_row_count": len(source_rows),
            }
        )
    return {
        "expected_units": len(sale_units),
        "candidate_units": len(sale_units),
        "counts": {
            "source_price_ready": counts.get("source_price_ready", 0),
            "source_price_missing_checkout_hold": counts.get("source_price_missing_checkout_hold", 0),
            "conflict_needs_fix": counts.get("conflict_needs_fix", 0),
        },
        "sale_units": sale_units,
    }


def _price_enrichment_prices(price_row: dict[str, Any] | None) -> dict[tuple[tuple[str, str], ...], str]:
    result = {}
    for unit in (price_row or {}).get("sale_units") or []:
        chosen = unit.get("chosen_price")
        if chosen in (None, ""):
            continue
        result[_combo_key(unit.get("projected_required_combo") or {})] = str(chosen)
    return result


def _combo_key(combo: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(axis), str(value)) for axis, value in (combo or {}).items()))


def _price_decision(resolution: dict[str, Any]) -> str:
    counts = resolution["counts"]
    if counts["conflict_needs_fix"]:
        return "conflict_needs_fix_before_import"
    if counts["source_price_missing_checkout_hold"]:
        return "missing_source_prices_recorded_as_checkout_hold"
    return "source_price_ready"


def _product_import_status(*, contract, review_units: int, review_only_axes: list[str]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if contract.product_page_type == "needs_review" or contract.commerce_lane == "needs_review":
        reasons.append("backend contract is needs_review")
        return "blocked", reasons
    if review_units:
        reasons.append(f"{review_units} sale unit price(s) need source-price fix or checkout hold")
    review_notes = []
    if review_only_axes:
        review_notes.append("review-only add-on axis hidden until mapped")
    if reasons:
        return "fix_needed", reasons
    return "ready", review_notes or ["product data maps to current ERPNext backend contract"]


def _sale_unit_manifest(sale_units: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "sale_unit_key": row.get("sale_unit_key"),
            "projected_required_combo": row.get("projected_required_combo") or {},
            "chosen_price": row.get("chosen_price"),
            "price_source_kind": row.get("price_source_kind"),
            "price_resolution_status": row.get("price_resolution_status"),
            "price_decision": row.get("price_decision"),
            "source_prices": row.get("source_prices") or [],
            "source_row_count": row.get("source_row_count"),
        }
        for row in sale_units
    ]


def _price_string(value: Any) -> str:
    return f"{float(value):.2f}"


def _sale_unit_key(combo: dict[str, str]) -> str:
    if not combo:
        return "single SKU"
    return "; ".join(f"{key}={value}" for key, value in sorted(combo.items()))


def _excluded_price_review_units(price_review: dict[str, dict[str, Any]], included_set: set[str]) -> int:
    return sum(
        int(row.get("review_unit_count") or 0)
        for slug, row in price_review.items()
        if slug not in included_set
    )


def _excluded_extra_images(media_packet: dict[str, dict[str, Any]], included_set: set[str]) -> int:
    return sum(
        int(row.get("extra_image_count") or 0)
        for slug, row in media_packet.items()
        if slug not in included_set
    )


def _excluded_add_on_products(add_on_axes: dict[str, list[str]], included_set: set[str]) -> int:
    return sum(1 for slug in add_on_axes if slug not in included_set)


def _validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    included = {row["slug"] for row in manifest["products"]}
    excluded = {row["slug"] for row in manifest["excluded_products"]}

    leaked_exclusions = sorted(set(OWNER_EXPLICIT_EXCLUDED_SLUGS) & included)
    if leaked_exclusions:
        errors.append(f"Owner-explicit excluded products leaked into import subset: {', '.join(leaked_exclusions)}")

    missing_exclusions = sorted(set(OWNER_EXPLICIT_EXCLUDED_SLUGS) - excluded)
    if missing_exclusions:
        errors.append(f"Owner-explicit excluded products missing from excluded set: {', '.join(missing_exclusions)}")

    missing_must_work = sorted(set(OWNER_MUST_WORK_SLUGS) - included)
    if missing_must_work:
        errors.append(f"Owner must-work products not included: {', '.join(missing_must_work)}")

    bad_contract = [
        row["slug"]
        for row in manifest["products"]
        if row["product_contract"]["commerce_lane"] == "needs_review"
        or row["product_contract"]["product_page_type"] == "needs_review"
    ]
    if bad_contract:
        errors.append(f"Needs-review products leaked into import subset: {', '.join(bad_contract)}")

    missing_source_trace = []
    variant_pointer_mismatches = []
    missing_axis_hashes = []
    missing_pattern_class = []
    for row in manifest["products"]:
        trace = row.get("source_trace") or {}
        slug = row["slug"]
        if not trace.get("odoo_product_id") or not trace.get("source_url") or not trace.get("source_integrity"):
            missing_source_trace.append(slug)
        if not trace.get("source_pattern_class"):
            missing_pattern_class.append(slug)
        axis_hashes = trace.get("source_axis_hashes") or []
        if any(not axis.get("source_value_hash") for axis in axis_hashes):
            missing_axis_hashes.append(slug)
        expected_variants = int((row.get("product_contract") or {}).get("source_variant_rows") or 0)
        variant_pointers = trace.get("source_variant_pointers") or {}
        actual_variants = int(variant_pointers.get("source_variant_count") or 0)
        if expected_variants != actual_variants or (
            expected_variants and not variant_pointers.get("source_variant_pointer_hash")
        ):
            variant_pointer_mismatches.append(f"{slug}: expected {expected_variants}, got {actual_variants}")
    if missing_source_trace:
        errors.append(f"Included products missing source identity/integrity trace: {', '.join(missing_source_trace)}")
    if missing_pattern_class:
        errors.append(f"Included products missing source pattern class: {', '.join(missing_pattern_class)}")
    if missing_axis_hashes:
        errors.append(f"Included products missing source axis hashes: {', '.join(missing_axis_hashes)}")
    if variant_pointer_mismatches:
        errors.append("Included products lost source variant pointers: " + "; ".join(variant_pointer_mismatches))

    return {
        "ok": not errors,
        "errors": errors,
        "checks": [
            "no_owner_exclusions_active",
            "owner_must_work_products_are_included",
            "no_needs_review_backend_contracts",
            "odoo_products_allowed_when_backend_contract_exists",
            "source_ids_axis_hashes_variant_pointers_and_pattern_class_preserved",
        ],
    }


def render_markdown(manifest: dict[str, Any]) -> str:
    summary = manifest["summary"]
    lines = [
        "# V1 Odoo-to-ERPNext Import Manifest",
        "",
        f"- Generated: `{manifest['generated_at']}`",
        "- Mode: read-only manifest; no purge, import, delete, or ERPNext mutation.",
        "- V1 scope: Odoo-imported products that fit the current ERPNext backend/schema contract.",
        "- Variants, cups, and high-variant products are not blanket exclusions.",
        "- No owner exclusion list is active for Odoo-imported products.",
        "",
        "## Summary",
        "",
        f"- Included products: {summary['included_products']}",
        f"- Excluded products: {summary['excluded_products']} ({_format_counts(summary['excluded_by_primary_reason'])})",
        f"- V1 sale units: {summary['v1_sale_units']}",
        f"- V1 price units needing source fix or checkout hold: {summary['v1_price_review_units']}",
        f"- V1 price resolution statuses: {_format_counts(summary['v1_price_units_by_source'])}",
        f"- V1 extra images held out of import: {summary['v1_extra_images_held']}",
        f"- V1 confirmed add-on products: {summary['v1_confirmed_add_on_products']}",
        f"- V1 review-only add-on products: {summary['v1_review_only_add_on_products']}",
        f"- V1 product statuses: {_format_counts(summary['v1_status_counts'])}",
        f"- Validation: {'PASS' if manifest['validation']['ok'] else 'FAIL'}",
        "",
        "## Blocker Reduction",
        "",
    ]
    for key, value in manifest["blocker_reduction"].items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(["", "## Owner Decisions Still Needed", ""])
    for row in manifest["owner_decisions_still_needed"]:
        lines.append(f"- `{row['id']}` ({row['count']}): {row['decision_needed']} Safe default: `{row['safe_default']}`.")

    lines.extend(
        [
            "",
            "## ERPNext Field Mapping",
            "",
            "- Template Item / Website Item code: source slug.",
            "- Item Group: source `slug_to_group` mapping.",
            "- Website Item `lt_product_page_type`: source product-page contract.",
            "- Website Item `lt_commerce_lane`: source commerce-lane contract.",
            f"- Line configuration version: `{manifest['runtime_contract']['configuration_version']}`.",
            f"- Line fields: `{json.dumps(manifest['runtime_contract']['line_fieldnames'], sort_keys=True)}`.",
            "- Confirmed foil-number add-on: `ADDON-FOIL-NUMBER` runtime contract for eligible bouquet products.",
            "- Odoo-imported products should import as sellable checkout targets; review-only add-on controls stay hidden until mapped.",
            "",
            "## Included Products",
            "",
            "| Product | Slug | Status | Lane | Required Axis | Sale Units | Price Review | Extra Images Held | Add-ons |",
            "|---|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in manifest["products"]:
        axes = ", ".join(axis["name"] for axis in row["product_contract"]["required_axes"]) or "single SKU"
        add_ons = ", ".join(add_on["key"] for add_on in row["add_on_manifest"]["confirmed_checkout_add_ons"]) or "none"
        lines.append(
            "| "
            + " | ".join(
                [
                    row["source_name"],
                    f"`{row['slug']}`",
                    row["ecommerce_import_status"],
                    row["product_contract"]["commerce_lane"],
                    axes,
                    str(row["price_manifest"]["candidate_units"]),
                    str(row["price_manifest"]["review_units"]),
                    str(row["media_manifest"]["extra_image_count"]),
                    add_ons,
                ]
            )
            + " |"
        )

    lines.extend(["", "## Next Command Sequence", ""])
    lines.extend(f"- `{command}`" for command in manifest["next_command_sequence"])
    lines.append("")
    return "\n".join(lines)


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _runtime_constants() -> dict[str, Any]:
    global RUNTIME_CONSTANTS
    if RUNTIME_CONSTANTS:
        return RUNTIME_CONSTANTS

    tree = ast.parse(RUNTIME_MODULE.read_text(encoding="utf-8"))
    constants: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in {"CONFIG_VERSION", "LINE_FIELDNAMES"}:
                constants[target.id] = ast.literal_eval(node.value)
    missing = {"CONFIG_VERSION", "LINE_FIELDNAMES"} - constants.keys()
    if missing:
        raise SystemExit(f"FATAL: missing runtime constants in {RUNTIME_MODULE}: {sorted(missing)}")
    RUNTIME_CONSTANTS = constants
    return constants


if __name__ == "__main__":
    raise SystemExit(main())
