#!/usr/bin/env python3
"""Report product-page media visibility readiness without assigning images.

Run:
  python scripts/verify/product_page_media_visibility_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_contract.media_visibility import build_media_visibility_report


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
SOURCE_CATALOG = ROOT / "_resources/odoo-live/catalog.json"
SLUG_TO_GROUP = ROOT / "_resources/odoo-live/slug_to_group.json"
REPORT_PATH = ROOT / Path(
    "audits/odoo-erpnext-migration-audit-2026-05-08/"
    "20-product-page-media-visibility-report.md"
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


def _live_media_rows() -> list[dict[str, str]]:
    sql = """
    set sql_big_selects=1;
    set sql_select_limit=1000000;
    select
        wi.item_code as website_item_code,
        wi.route,
        wi.published,
        wi.website_image,
        wi.slideshow,
        i.name as item_code,
        i.variant_of,
        i.disabled,
        i.image,
        iva.attribute,
        iva.attribute_value
    from `tabWebsite Item` wi
    left join tabItem i
      on i.name = wi.item_code
      or i.variant_of = wi.item_code
    left join `tabItem Variant Attribute` iva
      on iva.parent = i.name
    order by wi.item_code, i.name, iva.idx;
    select count(*) as website_slideshows from `tabWebsite Slideshow`;
    select count(*) as website_slideshow_items from `tabWebsite Slideshow Item`;
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
    return _parse_mariadb_sets(proc.stdout)


def _parse_mariadb_sets(output: str) -> dict[str, object]:
    lines = [line for line in output.splitlines() if line.strip()]
    rows = []
    slideshow_count = 0
    slideshow_item_count = 0
    current_headers = None
    for line in lines:
        parts = line.split("\t")
        if parts[0] in {"website_item_code", "website_slideshows", "website_slideshow_items"}:
            current_headers = parts
            continue
        if not current_headers:
            continue
        row = dict(zip(current_headers, parts))
        if current_headers == ["website_slideshows"]:
            slideshow_count = int(row.get("website_slideshows") or 0)
        elif current_headers == ["website_slideshow_items"]:
            slideshow_item_count = int(row.get("website_slideshow_items") or 0)
        else:
            rows.append(row)
    return {
        "rows": rows,
        "website_slideshows": slideshow_count,
        "website_slideshow_items": slideshow_item_count,
    }


def main() -> int:
    parse_noop_args(__doc__)
    live_media = _live_media_rows()
    report = build_media_visibility_report(
        _products(),
        slug_to_group=_slug_to_group(),
        live_rows=live_media["rows"],
        website_slideshow_count=live_media["website_slideshows"],
        website_slideshow_item_count=live_media["website_slideshow_items"],
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report.to_markdown(), encoding="utf-8")

    if report.blockers:
        print("[PRODUCT PAGE MEDIA VISIBILITY] BLOCKED")
        print(f"report={REPORT_PATH}")
        for blocker in report.blockers:
            print(f"- {blocker}")
        return 2

    print("[PRODUCT PAGE MEDIA VISIBILITY] PASS")
    print(f"report={REPORT_PATH}")
    print(json.dumps(report.summary(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
