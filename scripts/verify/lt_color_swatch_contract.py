"""Verify source color swatches are localized and wired into product drawers."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = REPO_ROOT / "apps" / "locally_twisted"
LOCAL_APP = APP_ROOT / "locally_twisted"
CATALOG_PATH = REPO_ROOT / "_resources" / "odoo-live" / "catalog.json"
MAP_PATH = LOCAL_APP / "catalog_contract" / "lt_color_swatch_map.json"
ASSET_PREFIX = "/assets/locally_twisted/images/color-swatches/lt-catalog/"
FORBIDDEN_DEPLOYED_MAP_KEYS = {"source_url", "source_url_examples", "source_url_template", "source_catalog"}
FORBIDDEN_DEPLOYED_MAP_NEEDLES = ("5.78.136.133", "_resources/odoo-live", "color-swatches/odoo")

sys.path.insert(0, str(APP_ROOT))

from locally_twisted.catalog_contract.color_rules import COLOR_SWATCH_AXIS_NAMES, grouped_colors  # noqa: E402


def normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").replace("-", " ").strip().lower().split())


def normalize_value(value: str | None) -> str:
    display = " ".join(str(value or "").replace("-", " ").strip().split())
    digest = hashlib.sha1(display.encode("utf-8")).hexdigest()[:10]
    return f"{display.lower()}##{digest}"


def normalize_product(value: str | None) -> str:
    return str(value or "").strip().lower()


def map_key(*parts: str | None) -> str:
    if len(parts) == 3:
        product, axis_name, value_name = parts
        return "|||".join([normalize_product(product), normalize_text(axis_name), normalize_value(value_name)])
    if len(parts) == 2:
        axis_name, value_name = parts
        return "|||".join([normalize_text(axis_name), normalize_value(value_name)])
    return "|||".join(normalize_value(part) for part in parts)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def color_sources(catalog: dict) -> list[dict]:
    rows: list[dict] = []
    for product in catalog.get("products") or []:
        slug = str(product.get("slug") or "").strip()
        attributes = product.get("attributes") or {}
        for axis_name, axis_data in attributes.items():
            if normalize_text(axis_name) not in COLOR_SWATCH_AXIS_NAMES:
                continue
            for value in axis_data.get("values") or []:
                rows.append(
                    {
                        "product_slug": slug,
                        "axis_name": str(axis_name),
                        "value_name": str(value.get("name") or "").strip(),
                        "ptav_id": int(value.get("ptav_id") or 0),
                    }
                )
    return rows


def assert_map_coverage(sources: list[dict], swatch_map: dict) -> None:
    by_product = swatch_map.get("by_product_axis_value") or {}
    placeholder_by_product = swatch_map.get("placeholder_product_axis_value") or {}
    missing = []
    bad_assets = []
    for source in sources:
        key = map_key(source["product_slug"], source["axis_name"], source["value_name"])
        entry = by_product.get(key)
        if not entry:
            placeholder = placeholder_by_product.get(key)
            if not placeholder:
                missing.append(key)
            continue
        asset_url = str(entry.get("asset_url") or "")
        if not asset_url.startswith(ASSET_PREFIX):
            bad_assets.append(f"{key}: non-local asset {asset_url!r}")
            continue
        asset_path = LOCAL_APP / "public" / asset_url.removeprefix("/assets/locally_twisted/")
        if not asset_path.exists() or asset_path.stat().st_size <= 0:
            bad_assets.append(f"{key}: missing file {asset_path}")

    if missing:
        fail(f"{len(missing)} product color values are missing swatch map entries; first={missing[:5]}")
    if bad_assets:
        fail(f"{len(bad_assets)} swatch assets are invalid; first={bad_assets[:5]}")


def assert_deployed_map_is_source_free(swatch_map: dict) -> None:
    raw = json.dumps(swatch_map, sort_keys=True)
    key_hits = sorted(key for key in FORBIDDEN_DEPLOYED_MAP_KEYS if f'"{key}"' in raw)
    needle_hits = sorted(needle for needle in FORBIDDEN_DEPLOYED_MAP_NEEDLES if needle in raw)
    if key_hits or needle_hits:
        fail(
            "Deployable swatch map still carries reference-source data: "
            f"keys={key_hits}, needles={needle_hits}"
        )


def assert_runtime_drawer(product: str, axis_name: str, sources: list[dict], swatch_map: dict) -> dict:
    rows = [
        row
        for row in sources
        if normalize_product(row["product_slug"]) == normalize_product(product)
        and normalize_text(row["axis_name"]) == normalize_text(axis_name)
    ]
    values = [row["value_name"] for row in rows]
    if not values:
        fail(f"No {axis_name!r} rows found for product {product!r}")
    placeholder_keys = set((swatch_map.get("placeholder_product_axis_value") or {}).keys())
    placeholder_values = {
        row["value_name"]
        for row in rows
        if map_key(row["product_slug"], row["axis_name"], row["value_name"]) in placeholder_keys
    }

    groups = grouped_colors(values, axis_name=axis_name, item_code=product)
    options = [option for group in groups for option in group["options"]]
    missing_swatches = [
        option["name"]
        for option in options
        if option["name"] not in placeholder_values and not option.get("swatch_url")
    ]
    placeholder_owner_fallbacks = [
        option["name"]
        for option in options
        if option["name"] in placeholder_values and option.get("swatch_url")
    ]
    remote_swatches = [option["swatch_url"] for option in options if str(option.get("swatch_url") or "").startswith("http")]
    if len(options) != len(values):
        fail(f"Runtime drawer returned {len(options)} options for {len(values)} source values")
    if missing_swatches:
        fail(f"Runtime drawer is missing swatch URLs for {product}: {missing_swatches[:5]}")
    if remote_swatches:
        fail(f"Runtime drawer is using remote swatch URLs: {remote_swatches[:5]}")

    return {
        "product": product,
        "axis": axis_name,
        "groups": len(groups),
        "options": len(options),
        "owner_swatches": len([option for option in options if option.get("swatch_url")]),
        "same_name_owner_fallbacks": len(placeholder_owner_fallbacks),
        "hex_fallbacks": len([name for name in placeholder_values if name not in placeholder_owner_fallbacks]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", default="classic-arch")
    parser.add_argument("--axis", default="latex colors")
    args = parser.parse_args()

    catalog = load_json(CATALOG_PATH)
    swatch_map = load_json(MAP_PATH)
    sources = color_sources(catalog)
    if not sources:
        fail("No color sources found")
    assert_deployed_map_is_source_free(swatch_map)
    assert_map_coverage(sources, swatch_map)
    runtime = assert_runtime_drawer(args.product, args.axis, sources, swatch_map)

    print(
        json.dumps(
            {
                "ok": True,
                "source_values": len(sources),
                "mapped_values": swatch_map.get("mapped_product_axis_value_count"),
                "placeholder_values": swatch_map.get("placeholder_product_axis_value_count"),
                "unique_assets": swatch_map.get("unique_asset_count"),
                "runtime": runtime,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
