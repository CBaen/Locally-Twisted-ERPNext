"""Generate LT shop category hero sources and breakpoint crops.

This is a narrow visual-asset generator for `/shop-items/<category>` heroes.
It uses the agency Together AI image key from the parent Built_by_Cameron
`.env`, writes dated source assets under `_resources/generated-hero-sources`,
and writes public WebP derivatives under the LT app hero asset folder.

The prompts intentionally use owner/Odoo balloon color names and swatch asset
references. Hex values are not treated as image-generation authority.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
AGENCY_ENV = REPO_ROOT.parents[1] / ".env"
MODEL = "black-forest-labs/FLUX.2-pro"
API_URL = "https://api.together.xyz/v1/images/generations"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

APP_ROOT = REPO_ROOT / "apps" / "locally_twisted" / "locally_twisted"
SWATCH_MAP_PATH = APP_ROOT / "catalog_contract" / "odoo_color_swatch_map.json"
PUBLIC_HERO_DIR = APP_ROOT / "public" / "images" / "heroes"
SOURCE_DIR = REPO_ROOT / "_resources" / "generated-hero-sources" / "2026-05-22"
PUBLIC_SWATCH_ROOT = APP_ROOT / "public"

SOURCE_SIZE = (2048, 416)
TARGETS = {
    "mobile": (828, 440),
    "tablet": (1640, 500),
    "desktop": (2732, 560),
}


@dataclass(frozen=True)
class HeroSpec:
    route: str
    title: str
    slug: str
    shape_prompt: str
    palette: tuple[str, ...]


HERO_SPECS = (
    HeroSpec(
        route="/shop-items/arches",
        title="Arches",
        slug="classic-arch-category-hero",
        shape_prompt=(
            "a full event balloon arch spanning a clean venue entry, visible as a true arch "
            "with both side bases and the overhead curve inside the center crop"
        ),
        palette=("Blue Slate", "Reflex Champagne", "Blush", "Dusk Green Tea", "White"),
    ),
    HeroSpec(
        route="/shop-items/columns",
        title="Columns",
        slug="classic-column-category-hero",
        shape_prompt=(
            "a pair of freestanding balloon columns for a school or civic entrance, each "
            "with stacked round latex balloons and clean weighted bases"
        ),
        palette=("Royal Blue", "Reflex Gold", "White", "Blue Slate", "black"),
    ),
    HeroSpec(
        route="/shop-items/bouquets",
        title="Bouquets",
        slug="mothers-day-bouquet-category-hero",
        shape_prompt=(
            "several finished balloon bouquets staged for pickup, ribboned and weighted, "
            "with round latex balloons and a giftable retail presentation"
        ),
        palette=("Pastel Pink", "Pastel Blue", "Pastel Yellow", "Pastel Purple", "Reflex Champagne"),
    ),
    HeroSpec(
        route="/shop-items/get-well-bouquets",
        title="Get-Well Bouquets",
        slug="bandage-get-well-bouquet-latex-free-category-hero",
        shape_prompt=(
            "a cheerful get-well balloon bouquet staged near a bright delivery table, soft "
            "and comforting, with no medical logos or readable text"
        ),
        palette=("Dusk Green Tea", "Pastel Yellow", "Robin's Egg", "White", "Blush"),
    ),
    HeroSpec(
        route="/shop-items/garlands",
        title="Garlands",
        slug="classic-organic-balloon-garland-category-hero",
        shape_prompt=(
            "an organic balloon garland flowing along a wall and corner installation, "
            "dense clusters of different balloon sizes, no arch shape"
        ),
        palette=("Reflex Champagne", "Dusk Rose", "eucalyptus", "White", "Blush"),
    ),
    HeroSpec(
        route="/shop-items/drops",
        title="Drops",
        slug="balloon-drop-category-hero",
        shape_prompt=(
            "a ceiling balloon drop net filled with bright balloons above an event floor, "
            "clearly ready to release, with safe venue rigging"
        ),
        palette=("Red", "Orange", "yellow", "Royal Blue", "Shamrock", "Violet", "White"),
    ),
    HeroSpec(
        route="/shop-items/grab-go",
        title="Grab & Go",
        slug="graduation-grab-n-go-category-hero",
        shape_prompt=(
            "grab-and-go balloon arrangements lined up for quick customer pickup, "
            "graduation-ready, compact, polished, and easy to carry"
        ),
        palette=("Reflex Gold", "black", "White", "Blue Slate", "Reflex Silver"),
    ),
    HeroSpec(
        route="/shop-items/table-decor",
        title="Table Decor",
        slug="marble-table-decor-category-hero",
        shape_prompt=(
            "low balloon table decor centerpieces on an event table, small polished "
            "arrangements that do not block conversation"
        ),
        palette=("Blush", "Reflex Champagne", "Dusk Rose", "White", "Clear"),
    ),
    HeroSpec(
        route="/shop-items/stands-easels",
        title="Stands & Easels",
        slug="6-graduation-stands-category-hero",
        shape_prompt=(
            "freestanding gold hoop display stands and slim metal easel frames with balloon "
            "clusters attached, vertical display hardware clearly visible, no poster board "
            "and no printed sign surface"
        ),
        palette=("Reflex Gold", "Royal Blue", "White", "black", "Reflex Silver"),
    ),
    HeroSpec(
        route="/shop-items/deliveries",
        title="Deliveries",
        slug="birthday-deliveries-category-hero",
        shape_prompt=(
            "finished balloon delivery arrangements staged near a clean studio loading "
            "area, tied, weighted, ready for local delivery, no vehicle logos"
        ),
        palette=("Reflex Champagne", "raspberry", "bubble Gum", "Pastel Pink", "White"),
    ),
    HeroSpec(
        route="/shop-items/seasonal-specialty",
        title="Seasonal & Specialty",
        slug="easter-balloon-cups-category-hero",
        shape_prompt=(
            "seasonal specialty balloon decor with playful spring party energy, polished "
            "custom pieces rather than generic retail balloons"
        ),
        palette=("Pastel Yellow", "Pastel Melon", "Pastel Green", "Teal", "Blush"),
    ),
)


def repo_rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)).replace("\\", "/")


def load_key() -> str:
    if not AGENCY_ENV.exists():
        raise SystemExit(f"Missing agency env file: {AGENCY_ENV}")
    for line in AGENCY_ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("VITE_TOGETHER_API_KEY="):
            value = line.split("=", 1)[1].strip()
            if value:
                return value
    raise SystemExit("VITE_TOGETHER_API_KEY not found in agency .env")


def load_swatch_map() -> dict:
    return json.loads(SWATCH_MAP_PATH.read_text(encoding="utf-8"))


def normalize_text(value: str | None) -> str:
    return " ".join(str(value or "").replace("-", " ").strip().lower().split())


def swatch_for_color(swatch_map: dict, color_name: str) -> str:
    key = f"latex colors|||{normalize_text(color_name)}"
    entry = (swatch_map.get("by_axis_normalized_value") or {}).get(key)
    if entry and entry.get("asset_url"):
        return str(entry["asset_url"])
    entry = (swatch_map.get("by_normalized_value") or {}).get(normalize_text(color_name))
    if entry and entry.get("asset_url"):
        return str(entry["asset_url"])
    return ""


def build_prompt(spec: HeroSpec, swatch_refs: list[str]) -> str:
    colors = ", ".join(spec.palette)
    refs = ", ".join(swatch_refs)
    return (
        "Photorealistic premium commercial event photography for a Utah balloon decor website, "
        f"extra-wide 4.9:1 website hero banner composition at {SOURCE_SIZE[0]}x{SOURCE_SIZE[1]}. "
        f"Subject: {spec.shape_prompt}. "
        f"Use only these owner/Odoo balloon color names as the palette: {colors}. "
        "Treat the named balloon colors and supplied swatch references as the authority, not hex values. "
        f"Swatch reference asset paths: {refs}. "
        "Realistic inflated latex balloons with correct glossy/matte supplier finishes where appropriate, "
        "polished Utah event styling, clean venue or studio setting, editorial lighting, premium but warm. "
        "Use a plain blank architectural background with no signage, no chalkboard, no plaques, no cards, "
        "no labels, no writing, no letters, no words, and no brand names anywhere in the image. "
        "Keep the main balloon form centered in the middle 40 percent so mobile crops still show the product. "
        "Leave calm darker negative space at the left and right for a black readability overlay. "
        "No readable text, no fake signage, no logos, no watermark, no cartoon style, no collage, no flat vector art."
    )


def generate_image(key: str, prompt: str, model: str) -> Image.Image:
    payload = {
        "model": model,
        "prompt": prompt,
        "width": SOURCE_SIZE[0],
        "height": SOURCE_SIZE[1],
        "n": 1,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        response_data = json.loads(response.read())
    first = response_data["data"][0]
    if first.get("b64_json"):
        payload_bytes = base64.b64decode(first["b64_json"])
    elif first.get("url"):
        image_request = urllib.request.Request(first["url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(image_request, timeout=120) as image_response:
            payload_bytes = image_response.read()
    else:
        raise RuntimeError(f"Unexpected Together response fields: {sorted(first)}")
    return Image.open(io.BytesIO(payload_bytes)).convert("RGB")


def save_derivatives(source: Image.Image, spec: HeroSpec) -> list[dict]:
    PUBLIC_HERO_DIR.mkdir(parents=True, exist_ok=True)
    derivatives = []
    for key, size in TARGETS.items():
        crop = ImageOps.fit(source, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        out_path = PUBLIC_HERO_DIR / f"{spec.slug}-{key}.webp"
        crop.save(out_path, "WEBP", quality=84, method=6)
        derivatives.append(
            {
                "key": key,
                "path": out_path.name,
                "width": size[0],
                "height": size[1],
                "bytes": out_path.stat().st_size,
            }
        )
    return derivatives


def write_contact_sheet(items: list[dict]) -> None:
    if not items:
        return
    cell_w, cell_h = 420, 150
    cols = 2
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        bold = ImageFont.truetype("arialbd.ttf", 16)
    except OSError:
        font = bold = None
    for index, item in enumerate(items):
        x = (index % cols) * cell_w
        y = (index // cols) * cell_h
        draw.rectangle([x, y, x + cell_w - 1, y + cell_h - 1], outline=(220, 220, 220))
        source = Image.open(SOURCE_DIR / item["source"]).convert("RGB")
        thumb = ImageOps.fit(source, (220, 92), method=Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x + 10, y + 14))
        draw.text((x + 244, y + 18), item["title"], fill=(20, 20, 20), font=bold)
        draw.text((x + 244, y + 44), item["route"], fill=(70, 70, 70), font=font)
        draw.text((x + 244, y + 68), ", ".join(item["palette"])[:38], fill=(70, 70, 70), font=font)
    sheet.save(SOURCE_DIR / "shop-category-generated-hero-contact-sheet.jpg", quality=92)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="Generate one route/title/slug substring.")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--pause", type=float, default=1.0)
    args = parser.parse_args()

    key = load_key()
    swatch_map = load_swatch_map()
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    selected = []
    needle = normalize_text(args.only) if args.only else ""
    for spec in HERO_SPECS:
        haystack = normalize_text(" ".join([spec.route, spec.title, spec.slug]))
        if needle and needle not in haystack:
            continue
        selected.append(spec)
    if not selected:
        raise SystemExit(f"No hero specs matched {args.only!r}")

    manifest_path = SOURCE_DIR / "shop-category-generated-hero-manifest.json"
    existing_items: dict[str, dict] = {}
    if manifest_path.exists():
        try:
            existing_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            existing_items = {
                str(item.get("slug")): item
                for item in existing_manifest.get("items", [])
                if item.get("slug")
            }
        except json.JSONDecodeError:
            existing_items = {}

    generated_items = []
    for index, spec in enumerate(selected, start=1):
        swatch_refs = [swatch_for_color(swatch_map, color) for color in spec.palette]
        missing = [color for color, ref in zip(spec.palette, swatch_refs) if not ref]
        if missing:
            raise SystemExit(f"{spec.title}: missing swatch refs for {missing}")
        prompt = build_prompt(spec, swatch_refs)
        print(f"[gen] {index}/{len(selected)} {spec.title} -> {spec.slug}")
        try:
            source = generate_image(key, prompt, model=args.model)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError(f"Together HTTP {exc.code} for {spec.title}: {body}") from exc
        source_path = SOURCE_DIR / f"{spec.slug}-source.webp"
        source.save(source_path, "WEBP", quality=92, method=6)
        derivatives = save_derivatives(source, spec)
        generated_items.append(
            {
                "route": spec.route,
                "title": spec.title,
                "slug": spec.slug,
                "source": source_path.name,
                "model": args.model,
                "source_width": source.width,
                "source_height": source.height,
                "palette": list(spec.palette),
                "swatch_refs": swatch_refs,
                "derivatives": derivatives,
                "prompt": prompt,
            }
        )
        print(f"[ok]  {repo_rel(source_path)}")
        if index < len(selected):
            time.sleep(args.pause)

    item_map = dict(existing_items)
    for item in generated_items:
        item_map[item["slug"]] = item
    final_items = [item_map[spec.slug] for spec in HERO_SPECS if spec.slug in item_map]

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api": "Together AI images/generations",
        "model_default": args.model,
        "source": "project VITE_TOGETHER_API_KEY from Built_by_Cameron .env",
        "note": (
            "Shop category representative generated heroes. Owner/Odoo swatches and "
            "balloon color names are prompt authority; sampled hex values are not."
        ),
        "source_size": list(SOURCE_SIZE),
        "targets": {key: list(value) for key, value in TARGETS.items()},
        "items": final_items,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_contact_sheet(final_items)
    print(f"[done] manifest {repo_rel(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
