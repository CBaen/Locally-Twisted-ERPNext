#!/usr/bin/env python3
"""Verify product-page template price readiness against live ERPNext.

Run:
  python scripts/verify/product_page_price_readiness_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.price_readiness import build_price_readiness_report


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
PRICE_LIST = "Standard Selling"
SOURCE_CATALOG = ROOT / "_resources/odoo-live/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/odoo-live/slug_to_group.json"
REPORT_PATH = ROOT / Path(
    "audits/odoo-erpnext-migration-audit-2026-05-08/"
    "19-product-page-price-readiness-report.md"
)


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _products() -> list[dict]:
    data = _load_json(SOURCE_CATALOG)
    if isinstance(data, dict):
        return list(data.get("products") or [])
    return list(data or [])


def _slug_to_group() -> dict[str, str]:
    if not SLUG_TO_GROUP.exists():
        return {}
    return {str(k): str(v) for k, v in _load_json(SLUG_TO_GROUP).items() if not str(k).startswith("_")}


def _live_price_rows(slugs: list[str]) -> list[dict[str, str]]:
    quoted = ", ".join("'" + slug.replace("'", "''") + "'" for slug in slugs)
    sql = f"""
    set sql_big_selects=1;
    set sql_select_limit=1000000;
    select
        coalesce(nullif(i.variant_of, ''), i.name) as template_item,
        wi.lt_product_page_type as current_product_page_type,
        wi.lt_commerce_lane as current_commerce_lane,
        wi.route as current_route,
        wi.published as current_published,
        i.name as item_code,
        i.variant_of,
        i.disabled,
        ip.price_list_rate,
        iva.attribute,
        iva.attribute_value
    from tabItem i
    left join `tabWebsite Item` wi
      on wi.item_code = coalesce(nullif(i.variant_of, ''), i.name)
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
    products = _products()
    report = build_price_readiness_report(
        products,
        slug_to_group=_slug_to_group(),
        live_rows=_live_price_rows([str(product.get("slug") or "") for product in products]),
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.to_markdown(), encoding="utf-8")

    if report.failures:
        print("[PRODUCT PAGE PRICE READINESS] FAIL")
        print(f"report={REPORT_PATH}")
        for failure in report.failures:
            print(f"- {failure}")
        return 1

    print("[PRODUCT PAGE PRICE READINESS] PASS")
    print(f"report={REPORT_PATH}")
    print(json.dumps(report.summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
