"""Pull owner-uploaded Odoo color swatches into local LT app assets.

The old Odoo shop stores color tile images on product.template.attribute.value
records. ERPNext/Webshop does not have a native image field for Item Attribute
Value rows, so this setup-only tool converts the reference images into LT-owned
assets plus a deployable map. The deployable map must not carry Odoo/reference
URLs; source provenance stays in reference/audit artifacts outside app runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "_resources" / "odoo-live" / "catalog.json"
APP_ROOT = REPO_ROOT / "apps" / "locally_twisted" / "locally_twisted"
ASSET_DIR = APP_ROOT / "public" / "images" / "color-swatches" / "lt-catalog"
MAP_PATH = APP_ROOT / "catalog_contract" / "lt_color_swatch_map.json"
ASSET_BASE_URL = "/assets/locally_twisted/images/color-swatches/lt-catalog/"
SOURCE_URL_TEMPLATE = "http://5.78.136.133/web/image/product.template.attribute.value/{ptav_id}/image"
COLOR_AXES = frozenset({"latex colors", "color palette", "number colors", "baby color"})
ODOO_PLACEHOLDER_SHA256S = frozenset(
    {
        "2d2bb80029f05effcb5471ca032c3556ad0b1a45f664a28551624f51070cbb1b",
    }
)


@dataclass(frozen=True)
class SwatchSource:
    product_slug: str
    product_name: str
    axis_name: str
    value_name: str
    ptav_id: int


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


def normalized_map_key(*parts: str | None) -> str:
    if len(parts) == 2:
        axis_name, value_name = parts
        return "|||".join([normalize_text(axis_name), normalize_text(value_name)])
    return "|||".join(normalize_text(part) for part in parts)


def extension_for_content_type(content_type: str) -> str:
    content_type = str(content_type or "").split(";", 1)[0].strip().lower()
    if content_type == "image/png":
        return ".png"
    if content_type == "image/webp":
        return ".webp"
    if content_type in {"image/jpeg", "image/jpg"}:
        return ".jpg"
    return ".img"


def load_sources(catalog_path: Path) -> list[SwatchSource]:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    sources: list[SwatchSource] = []
    for product in catalog.get("products") or []:
        slug = str(product.get("slug") or "").strip()
        name = str(product.get("name") or slug).strip()
        attributes = product.get("attributes") or {}
        for axis_name, axis_data in attributes.items():
            if normalize_text(axis_name) not in COLOR_AXES:
                continue
            for row in axis_data.get("values") or []:
                value_name = str(row.get("name") or "").strip()
                ptav_id = row.get("ptav_id")
                if not slug or not value_name or not ptav_id:
                    raise ValueError(f"Color swatch source row is missing slug, value name, or ptav_id: {row!r}")
                sources.append(
                    SwatchSource(
                        product_slug=slug,
                        product_name=name,
                        axis_name=str(axis_name),
                        value_name=value_name,
                        ptav_id=int(ptav_id),
                    )
                )
    return sources


def download_image(ptav_id: int, timeout: int) -> tuple[bytes, str]:
    url = SOURCE_URL_TEMPLATE.format(ptav_id=ptav_id)
    request = urllib.request.Request(url, headers={"User-Agent": "LocallyTwistedSwatchImport/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            payload = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not download Odoo swatch {ptav_id}: {exc}") from exc

    if not str(content_type).startswith("image/"):
        raise RuntimeError(f"Odoo swatch {ptav_id} did not return an image content type: {content_type!r}")
    if len(payload) < 100:
        raise RuntimeError(f"Odoo swatch {ptav_id} returned too few bytes: {len(payload)}")
    return payload, content_type


def build_map(sources: list[SwatchSource], timeout: int, dry_run: bool) -> dict:
    by_product_axis_value: dict[str, dict] = {}
    by_axis_value: dict[str, dict] = {}
    by_value: dict[str, dict] = {}
    by_axis_normalized_value: dict[str, dict] = {}
    by_normalized_value: dict[str, dict] = {}
    placeholder_product_axis_value: dict[str, dict] = {}
    assets: dict[str, dict] = {}

    if not dry_run:
        ASSET_DIR.mkdir(parents=True, exist_ok=True)

    for index, source in enumerate(sources, start=1):
        payload, content_type = download_image(source.ptav_id, timeout=timeout)
        digest = hashlib.sha256(payload).hexdigest()
        extension = extension_for_content_type(content_type)
        filename = f"{digest[:24]}{extension}"
        asset_url = f"{ASSET_BASE_URL}{filename}"
        asset_path = ASSET_DIR / filename

        key = map_key(source.product_slug, source.axis_name, source.value_name)
        if digest in ODOO_PLACEHOLDER_SHA256S:
            placeholder_product_axis_value[key] = {
                "axis_name": source.axis_name,
                "content_type": content_type,
                "product_name": source.product_name,
                "product_slug": source.product_slug,
                "ptav_id": source.ptav_id,
                "sha256": digest,
                "status": "source_placeholder_image",
                "value_name": source.value_name,
            }
            continue

        if not dry_run and not asset_path.exists():
            asset_path.write_bytes(payload)

        entry = {
            "asset_url": asset_url,
            "axis_name": source.axis_name,
            "content_type": content_type,
            "filename": filename,
            "product_name": source.product_name,
            "product_slug": source.product_slug,
            "ptav_id": source.ptav_id,
            "sha256": digest,
            "value_name": source.value_name,
        }
        by_product_axis_value[key] = entry
        by_axis_value.setdefault(map_key(source.axis_name, source.value_name), entry)
        by_value.setdefault(map_key(source.value_name), entry)
        by_axis_normalized_value.setdefault(normalized_map_key(source.axis_name, source.value_name), entry)
        by_normalized_value.setdefault(normalized_map_key(source.value_name), entry)
        assets.setdefault(
            digest,
            {
                "asset_url": asset_url,
                "content_type": content_type,
                "filename": filename,
                "sha256": digest,
            },
        )

        if index % 100 == 0:
            print(f"downloaded {index}/{len(sources)} swatch rows", file=sys.stderr)

    return {
        "schema_version": "lt-color-swatches-v1",
        "asset_base_url": ASSET_BASE_URL,
        "source_lineage": "reference-derived-local-assets",
        "color_axes": sorted(COLOR_AXES),
        "product_axis_value_count": len(sources),
        "mapped_product_axis_value_count": len(by_product_axis_value),
        "placeholder_product_axis_value_count": len(placeholder_product_axis_value),
        "unique_asset_count": len(assets),
        "by_product_axis_value": dict(sorted(by_product_axis_value.items())),
        "by_axis_value": dict(sorted(by_axis_value.items())),
        "by_value": dict(sorted(by_value.items())),
        "by_axis_normalized_value": dict(sorted(by_axis_normalized_value.items())),
        "by_normalized_value": dict(sorted(by_normalized_value.items())),
        "placeholder_product_axis_value": dict(sorted(placeholder_product_axis_value.items())),
        "assets": dict(sorted(assets.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    parser.add_argument("--map", type=Path, default=MAP_PATH)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sources = load_sources(args.catalog)
    if not sources:
        raise SystemExit("No color swatch sources found in Odoo catalog export")

    swatch_map = build_map(sources, timeout=args.timeout, dry_run=args.dry_run)
    if not args.dry_run:
        args.map.write_text(json.dumps(swatch_map, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "product_axis_values": swatch_map["product_axis_value_count"],
                "mapped_product_axis_values": swatch_map["mapped_product_axis_value_count"],
                "placeholder_product_axis_values": swatch_map["placeholder_product_axis_value_count"],
                "unique_assets": swatch_map["unique_asset_count"],
                "map_path": str(args.map),
                "asset_dir": str(ASSET_DIR),
                "dry_run": args.dry_run,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
