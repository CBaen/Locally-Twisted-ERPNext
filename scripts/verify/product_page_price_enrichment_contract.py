#!/usr/bin/env python3
"""Verify source price enrichment candidates for product-page imports.

Run:
  python scripts/verify/product_page_price_enrichment_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.price_enrichment import build_price_enrichment_report


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
PRICE_LIST = "Standard Selling"
SOURCE_CATALOG = ROOT / "_resources/catalog-source/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/catalog-source/slug_to_group.json"
REPORT_PATH = ROOT / Path(
    "audits/catalog-import-audit-2026-05-08/"
    "21-product-page-price-enrichment-report.md"
)
ARTIFACT_PATH = ROOT / Path(
    "audits/catalog-import-audit-2026-05-08/"
    "21-product-page-price-enrichment-candidates.json"
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _source_catalog() -> dict:
    data = _load_json(SOURCE_CATALOG)
    if isinstance(data, dict):
        return data
    return {"products": list(data or [])}


def _products(source_catalog: dict) -> list[dict]:
    return list(source_catalog.get("products") or [])


def _slug_to_group() -> dict[str, str]:
    if not SLUG_TO_GROUP.exists():
        return {}
    return {str(k): str(v) for k, v in _load_json(SLUG_TO_GROUP).items() if not str(k).startswith("_")}


def _live_price_rows(slugs: list[str]) -> list[dict[str, str]]:
    quoted = ", ".join("'" + slug.replace("'", "''") + "'" for slug in slugs)
    sql = f"""
    set sql_select_limit=1000000;
    select
        coalesce(nullif(i.variant_of, ''), i.name) as template_item,
        i.name as item_code,
        i.variant_of,
        i.disabled,
        ip.price_list_rate,
        ip.currency,
        iva.attribute,
        iva.attribute_value
    from tabItem i
    left join `tabItem Price` ip
      on ip.item_code = i.name
     and ip.price_list = '{PRICE_LIST}'
     and ip.selling = 1
    left join `tabItem Variant Attribute` iva
      on iva.parent = i.name
    where i.name in ({quoted})
       or i.variant_of in ({quoted})
    order by template_item, i.name, iva.idx;
    """
    cmd = [
        "docker",
        "exec",
        "-i",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "mariadb",
        "--batch",
        "--raw",
    ]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError(f"mariadb query failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return []
    headers = lines[0].split("\t")
    return [dict(zip(headers, line.split("\t"))) for line in lines[1:]]


def main() -> int:
    parse_noop_args(__doc__)
    source_catalog = _source_catalog()
    products = _products(source_catalog)
    live_rows = _live_price_rows([str(product.get("slug") or "") for product in products])
    report = build_price_enrichment_report(
        products,
        slug_to_group=_slug_to_group(),
        live_rows=live_rows,
        metadata={
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source_catalog_path": str(SOURCE_CATALOG),
            "source_scraped_at": source_catalog.get("scraped_at"),
            "source_product_count": source_catalog.get("product_count") or len(products),
            "erpnext_site": SITE,
            "price_list": PRICE_LIST,
            "currency": _currency(products, live_rows),
            "live_query_item_count": len({row.get("item_code") for row in live_rows if row.get("item_code")}),
            "live_query_item_price_count": len(
                {
                    row.get("item_code")
                    for row in live_rows
                    if row.get("item_code") and row.get("price_list_rate") not in (None, "", "NULL")
                }
            ),
        },
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.to_markdown(), encoding="utf-8")
    ARTIFACT_PATH.write_text(
        json.dumps(report.to_candidate_artifact(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _assert_artifact_shape(report.to_candidate_artifact())

    if report.blockers:
        print("[PRODUCT PAGE PRICE ENRICHMENT] BLOCKED")
        print(f"report={REPORT_PATH}")
        print(f"artifact={ARTIFACT_PATH}")
        for blocker in report.blockers:
            print(f"- {blocker}")
        return 2

    print("[PRODUCT PAGE PRICE ENRICHMENT] PASS")
    print(f"report={REPORT_PATH}")
    print(f"artifact={ARTIFACT_PATH}")
    print(json.dumps(report.summary(), indent=2, sort_keys=True))
    return 0


def _currency(products: list[dict], live_rows: list[dict]) -> str:
    source_currencies = {str(product.get("currency") or "").strip() for product in products if product.get("currency")}
    live_currencies = {str(row.get("currency") or "").strip() for row in live_rows if row.get("currency") not in (None, "", "NULL")}
    currencies = sorted((source_currencies | live_currencies) - {""})
    return currencies[0] if len(currencies) == 1 else ",".join(currencies)


def _assert_artifact_shape(artifact: dict) -> None:
    required_header = {
        "generated_at",
        "source_catalog_path",
        "source_scraped_at",
        "source_product_count",
        "erpnext_site",
        "price_list",
        "currency",
        "live_query_item_count",
        "live_query_item_price_count",
    }
    header = artifact.get("header") or {}
    missing_header = sorted(required_header - set(header))
    if missing_header:
        raise RuntimeError(f"price enrichment artifact missing header fields: {missing_header}")
    summary = artifact.get("summary") or {}
    if int(summary.get("source_variant_rows") or 0) <= int(summary.get("expected_sale_units") or 0):
        raise RuntimeError("price enrichment artifact must preserve source rows, not only collapsed sale units")
    products = artifact.get("products") or []
    if not products:
        raise RuntimeError("price enrichment artifact has no product rows")
    required_product = {
        "slug",
        "legacy_source_id",
        "name",
        "source_url",
        "product_page_type",
        "commerce_lane",
        "required_axes",
        "customization_axes",
        "add_ons",
        "axis_review_warnings",
        "price_status",
        "purge_reimport_status",
        "source_rows",
        "sale_units",
    }
    for product in products:
        missing = sorted(required_product - set(product))
        if missing:
            raise RuntimeError(f"price enrichment artifact product {product.get('slug')} missing fields: {missing}")
        if product.get("source_rows"):
            row = product["source_rows"][0]
            required_source_row = {
                "source_row_index",
                "ptav_ids",
                "source_combo",
                "source_price",
                "projected_required_combo",
                "dropped_axes",
                "sale_unit_key",
                "live_match_status",
                "live_item_codes",
                "live_price",
                "blockers",
            }
            missing_row = sorted(required_source_row - set(row))
            if missing_row:
                raise RuntimeError(f"price enrichment artifact source row missing fields: {missing_row}")
        if product.get("sale_units"):
            sale_unit = product["sale_units"][0]
            required_sale_unit = {
                "source_row_count",
                "live_active_match_count",
                "live_priced_match_count",
                "distinct_live_prices",
                "chosen_price",
                "price_source_kind",
            }
            missing_unit = sorted(required_sale_unit - set(sale_unit))
            if missing_unit:
                raise RuntimeError(f"price enrichment artifact sale unit missing fields: {missing_unit}")


if __name__ == "__main__":
    raise SystemExit(main())
