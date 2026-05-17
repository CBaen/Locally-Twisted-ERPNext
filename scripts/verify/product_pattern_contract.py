#!/usr/bin/env python3
"""Build ERPNext/Frappe ProductPatternContract architecture report.

This verifier is read-only. It joins the reusable Odoo option-pattern mapper
with current ERPNext Website Item, Item, Item Price, and variant-attribute rows.
It classifies all source product pages by generic architecture capability, not
by product-name exceptions.

Run:
  python scripts/verify/product_pattern_contract.py
  python scripts/verify/product_pattern_contract.py --json
  python scripts/verify/product_pattern_contract.py --report output/product-pattern-contract.json
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from locally_twisted.catalog_contract.erpnext_pattern_contract import build_erpnext_product_pattern_report
from locally_twisted.catalog_contract.addon_rules import known_add_on_contracts_for_axis
from locally_twisted.catalog_contract.pattern_mapper import build_product_pattern_report


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
SOURCE_CATALOG = ROOT / "_resources" / "odoo-live" / "catalog.json"
DEFAULT_REPORT = ROOT / "output" / "product-pattern-contract.json"
DEFAULT_MARKDOWN = ROOT / "output" / "product-pattern-contract.md"


class ProductPatternContractFail(Exception):
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full ProductPatternContract JSON")
    parser.add_argument("--report", help="Write ProductPatternContract JSON to this path")
    parser.add_argument("--markdown", help="Write Markdown report to this path")
    args = parser.parse_args()

    try:
        source = _source_catalog()
        products = list(source.get("products") or [])
        source_artifact = _source_pattern_artifact(source, products)
        erpnext_rows = _erpnext_rows(products)
        report = build_erpnext_product_pattern_report(
            source_artifact,
            erpnext_rows,
            metadata={
                "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "source_catalog": str(SOURCE_CATALOG.relative_to(ROOT)),
                "source_scraped_at": source.get("scraped_at"),
                "erpnext_site": SITE,
                "erpnext_container": CONTAINER,
                "logic_note": "Product names are examples only; capability is classified from source patterns and ERPNext records.",
            },
        )
    except ProductPatternContractFail as exc:
        print(f"[PRODUCT PATTERN CONTRACT] FAIL\n  - {exc}")
        return 1

    artifact = report.to_artifact()
    inventory_failures, checkout_gate_failures = _contract_failures(artifact)
    failures = inventory_failures + checkout_gate_failures

    report_path = _rooted(args.report) if args.report else DEFAULT_REPORT
    markdown_path = _rooted(args.markdown) if args.markdown else DEFAULT_MARKDOWN
    report_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    print(f"[PRODUCT PATTERN CONTRACT] wrote {report_path.relative_to(ROOT)}")
    print(f"[PRODUCT PATTERN CONTRACT] wrote {markdown_path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps(artifact, indent=2, sort_keys=True))
    else:
        _print_summary(artifact, failures)

    return 0 if not failures else 2


def _source_catalog() -> dict[str, Any]:
    if not SOURCE_CATALOG.exists():
        raise ProductPatternContractFail(f"missing source catalog: {SOURCE_CATALOG.relative_to(ROOT)}")
    data = json.loads(SOURCE_CATALOG.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("products"), list):
        raise ProductPatternContractFail("source catalog must be an object with products list")
    return data


def _source_pattern_artifact(source: dict[str, Any], products: list[dict[str, Any]]) -> dict[str, Any]:
    report = build_product_pattern_report(
        products,
        metadata={
            "source_catalog": str(SOURCE_CATALOG.relative_to(ROOT)),
            "source_scraped_at": source.get("scraped_at"),
        },
    )
    artifact = report.to_artifact()
    raw_by_slug = {str(row.get("slug") or ""): row for row in products}
    for row in artifact.get("products") or []:
        raw = raw_by_slug.get(str(row.get("slug") or "")) or {}
        row["source_rows"] = [
            {
                "combo": dict(source_row.get("combo") or {}),
                "price": source_row.get("erpnext_variant_price", source_row.get("price")),
            }
            for source_row in raw.get("valid_variants") or []
            if isinstance(source_row, dict)
        ]
    return artifact


def _erpnext_rows(products: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    slugs = [str(row.get("slug") or "") for row in products if row.get("slug")]
    if not slugs:
        raise ProductPatternContractFail("no source slugs available")
    quoted = ", ".join(_sql_literal(slug) for slug in sorted(set(slugs)))
    source_or_published = (
        f"item_code in ({quoted}) "
        "or item_code in (select item_code from `tabWebsite Item` where published = 1)"
    )
    variant_of_source_or_published = (
        f"variant_of in ({quoted}) "
        "or variant_of in (select item_code from `tabWebsite Item` where published = 1)"
    )
    aliased_source_or_published = (
        f"i.item_code in ({quoted}) "
        "or i.item_code in (select item_code from `tabWebsite Item` where published = 1)"
    )
    aliased_variant_of_source_or_published = (
        f"i.variant_of in ({quoted}) "
        "or i.variant_of in (select item_code from `tabWebsite Item` where published = 1)"
    )
    queries = {
        "website_items": f"""
select
  name,
  item_code,
  web_item_name,
  route,
  published,
  item_group,
  lt_product_page_type,
  lt_commerce_lane
from `tabWebsite Item`
where published = 1
order by item_code;
""",
        "items": f"""
select
  name,
  item_code,
  item_name,
  item_group,
  has_variants,
  variant_of,
  disabled,
  image
from tabItem
where {source_or_published} or {variant_of_source_or_published}
order by coalesce(nullif(variant_of, ''), item_code), item_code;
""",
        "item_prices": f"""
select
  ip.item_code,
  ip.price_list,
  ip.selling,
  ip.price_list_rate,
  ip.currency
from `tabItem Price` ip
join tabItem i on i.item_code = ip.item_code
where ip.price_list = 'Standard Selling'
  and ip.selling = 1
  and ({aliased_source_or_published} or {aliased_variant_of_source_or_published})
order by ip.item_code;
""",
        "variant_attributes": f"""
select
  iva.parent,
  iva.attribute,
  iva.attribute_value
from `tabItem Variant Attribute` iva
join tabItem i on i.name = iva.parent
where {aliased_source_or_published} or {aliased_variant_of_source_or_published}
order by iva.parent, iva.idx;
""",
        "line_fields": f"""
select dt, fieldname
from `tabCustom Field`
where dt in ('Sales Order Item', 'Sales Invoice Item')
  and fieldname in (
    'custom_lt_product_template_item',
    'custom_lt_product_page_type',
    'custom_lt_configuration_version',
    'custom_lt_configuration_summary',
    'custom_lt_configuration_json'
  )
union
select parent as dt, fieldname
from tabDocField
where parent in ('Sales Order Item', 'Sales Invoice Item')
  and fieldname in (
    'custom_lt_product_template_item',
    'custom_lt_product_page_type',
    'custom_lt_configuration_version',
    'custom_lt_configuration_summary',
    'custom_lt_configuration_json'
  )
order by dt, fieldname;
""",
    }
    add_on_item_codes = _add_on_item_codes(products)
    if add_on_item_codes:
        quoted_add_ons = ", ".join(_sql_literal(item_code) for item_code in add_on_item_codes)
        queries["add_on_prices"] = f"""
select
  item_code,
  price_list,
  selling,
  price_list_rate,
  currency
from `tabItem Price`
where price_list = 'Standard Selling'
  and selling = 1
  and item_code in ({quoted_add_ons})
order by item_code;
"""
    return {name: _mariadb_dicts(query) for name, query in queries.items()}


def _add_on_item_codes(products: list[dict[str, Any]]) -> list[str]:
    item_codes = {
        str(contract.get("item_code") or "")
        for product in products
        for axis_name in (product.get("attributes") or {})
        for contract in known_add_on_contracts_for_axis(str(axis_name))
        if contract.get("item_code")
    }
    return sorted(item_codes)


def _mariadb_dicts(query: str) -> list[dict[str, Any]]:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "mariadb",
        "--batch",
        "--raw",
        "--execute",
        "set SQL_SELECT_LIMIT=DEFAULT;\n" + query.strip(),
    ]
    proc = subprocess.run(cmd, text=True, encoding="utf-8", capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise ProductPatternContractFail(
            f"mariadb query failed\nQUERY:\n{query}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    output = proc.stdout.strip()
    if not output:
        return []
    reader = csv.DictReader(StringIO(output), delimiter="\t")
    return [dict(row) for row in reader]


def _contract_failures(artifact: dict[str, Any]) -> tuple[list[str], list[str]]:
    inventory_failures: list[str] = []
    checkout_gate_failures: list[str] = []
    if artifact.get("schema_version") != "lt-erpnext-product-pattern-contract-v1":
        inventory_failures.append("unexpected schema_version")
    if artifact.get("read_only") is not True:
        inventory_failures.append("artifact must be read_only")
    if artifact.get("destructive_allowed") is not False:
        inventory_failures.append("artifact must not allow destructive action")
    summary = artifact.get("summary") or {}
    if int(summary.get("source_products") or 0) < 53:
        inventory_failures.append(f"expected at least 53 source products, found {summary.get('source_products')}")
    if int(summary.get("explicit_checkout_products") or 0) != 53:
        inventory_failures.append(
            "current explicit checkout product count changed; expected 53, "
            f"found {summary.get('explicit_checkout_products')}"
        )
    products = artifact.get("products")
    if not isinstance(products, list):
        return inventory_failures + ["products must be a list"], checkout_gate_failures
    for row in products:
        if not row.get("slug"):
            inventory_failures.append("product row missing slug")
        if not row.get("capability"):
            inventory_failures.append(f"{row.get('slug')} missing capability")
        if not isinstance(row.get("server_boundary"), dict):
            checkout_gate_failures.append(f"{row.get('slug')} missing server_boundary")
        if not isinstance(row.get("checkout_eligibility"), dict):
            checkout_gate_failures.append(f"{row.get('slug')} missing checkout_eligibility")
        if _requires_multi_color_contract(row) and _website_lane(row) == "checkout":
            if not _has_multi_color_server_boundary(row):
                checkout_gate_failures.append(f"{row.get('slug')} missing multi-color checkout server boundary")
    inventory_failures.extend(artifact.get("inventory_failures") or [])
    checkout_gate_failures.extend(artifact.get("checkout_gate_failures") or [])
    return inventory_failures, checkout_gate_failures


def _requires_multi_color_contract(row: dict[str, Any]) -> bool:
    patterns = set(row.get("patterns") or [])
    return bool(patterns & {"large_single_choice_color", "multi_color_recipes"})


def _has_multi_color_server_boundary(row: dict[str, Any]) -> bool:
    boundary = row.get("server_boundary") or {}
    schema = boundary.get("selected_config_schema") or {}
    customization = boundary.get("customization_validation") or {}
    cart_key = boundary.get("cart_line_key_contract") or {}
    return bool(
        schema.get("color_recipes")
        and customization.get("status") == "ready_multi_color_recipe_contract"
        and customization.get("single_select_color_allowed") is False
        and cart_key.get("requires_color_recipes_in_canonical_json") is True
    )


def _website_lane(row: dict[str, Any]) -> str:
    return str((row.get("checkout_eligibility") or {}).get("website_lane") or "")


def _print_summary(artifact: dict[str, Any], failures: list[str]) -> None:
    summary = artifact.get("summary") or {}
    print("[PRODUCT PATTERN CONTRACT] " + ("PASS" if not failures else "FAIL"))
    print(f"  source_products: {summary.get('source_products')}")
    print(f"  explicit_checkout_products: {summary.get('explicit_checkout_products')}")
    print(f"  direct_checkout_ready_products: {summary.get('direct_checkout_ready_products')}")
    print(f"  inventory_ok: {artifact.get('inventory_ok')}")
    print(f"  checkout_gate_ok: {artifact.get('checkout_gate_ok')}")
    print(f"  internal_hold_supported_products: {summary.get('quote_first_supported_products')}")
    print(f"  missing_or_needs_review_products: {summary.get('missing_or_needs_review_products')}")
    print(f"  capability_counts: {_format_counts(summary.get('capability_counts') or {})}")
    print(f"  website_lane_counts: {_format_counts(summary.get('website_lane_counts') or {})}")
    print(f"  checkout_blocker_counts: {_format_counts(summary.get('checkout_blocker_counts') or {})}")
    print(f"  deferred_control_counts: {_format_counts(summary.get('checkout_deferred_control_counts') or {})}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _sql_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
