#!/usr/bin/env python3
"""Build a no-mutation category media candidate report.

This script helps close the launch blocker where all customer-facing Item
Group category images are empty. It does not write ERPNext data. It ranks
existing product-source and portfolio-proof images so GL/Jeff can approve a
small, concrete review set later.
"""

from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SOURCE_IMAGE_DIR = ROOT / "_resources" / "catalog-source" / "images"
SLUG_TO_GROUP = ROOT / "_resources" / "catalog-source" / "slug_to_group.json"
CATALOG = ROOT / "_resources" / "catalog-source" / "catalog.json"
PORTFOLIO_CONTROLLER = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "www" / "portfolio.py"
PORTFOLIO_OPTIMIZED_DIR = (
    ROOT / "apps" / "locally_twisted" / "locally_twisted" / "public" / "images" / "portfolio" / "optimized"
)

CATEGORY_ORDER = [
    "Arches",
    "Balloon Drops",
    "Bouquets",
    "Columns",
    "Garlands",
    "Photo Ops & Backdrops",
    "Stands & Easels",
    "Table Decor",
]

CATEGORY_PORTFOLIO_MAP = {
    "Arches": {"balloon-arches"},
    "Columns": {"columns"},
    "Bouquets": {"balloon-bouquets"},
    "Garlands": {"garlands"},
    "Photo Ops & Backdrops": {"picture-perfect-backdrops"},
    "Table Decor": {"centerpieces"},
    "Stands & Easels": {"picture-perfect-backdrops"},
}

PREFERRED_PRODUCT_SLUGS = {
    "Arches": {"classic-arch", "premium-organic-arch", "6-color-rainbow-arch"},
    "Balloon Drops": {"balloon-drop"},
    "Columns": {"classic-column", "classic-organic-columns"},
    "Bouquets": {
        "birthday-deliveries",
        "mothers-day-bouquet",
        "unicorn-bouquet",
        "bandage-get-well-bouquet-latex-free",
        "butterfly-get-well-bouquet-latex-free",
        "shooting-star-get-well-bouquet-latex-free",
    },
    "Garlands": {"classic-organic-balloon-garland", "premium-organic-garland", "baby-shower-garland"},
    "Photo Ops & Backdrops": {"baby-shower-combination-photo-opt"},
    "Table Decor": {"marble-table-decor", "baby-table-decor", "easter-balloon-cups"},
    "Stands & Easels": {"classic-organic-for-easel", "6-graduation-stands"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate category media candidates without mutating ERPNext.")
    parser.add_argument("--json", default="output/category-media-candidates.json", help="JSON report path")
    parser.add_argument("--markdown", default="output/category-media-candidates.md", help="Markdown report path")
    parser.add_argument("--max-per-category", type=int, default=8, help="Candidates to keep per category")
    args = parser.parse_args()

    slug_to_group = _load_slug_to_group()
    products = _load_products()
    portfolio_items = _load_portfolio_items()
    report = _build_report(slug_to_group, products, portfolio_items, args.max_per_category)

    json_path = ROOT / args.json
    markdown_path = ROOT / args.markdown
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    print(f"[category-media] wrote {json_path.relative_to(ROOT)}")
    print(f"[category-media] wrote {markdown_path.relative_to(ROOT)}")
    print(
        "[category-media] categories: "
        + ", ".join(f"{name}={len(data['candidates'])}" for name, data in report["categories"].items())
    )
    return 0


def _load_slug_to_group() -> dict[str, str]:
    raw = json.loads(SLUG_TO_GROUP.read_text(encoding="utf-8"))
    return {slug: group for slug, group in raw.items() if not slug.startswith("_")}


def _load_products() -> dict[str, dict]:
    raw = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {product["slug"]: product for product in raw.get("products", [])}


def _load_portfolio_items() -> list[dict]:
    tree = ast.parse(PORTFOLIO_CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "GALLERY_ITEMS":
                    return ast.literal_eval(node.value)
    return []


def _build_report(
    slug_to_group: dict[str, str],
    products: dict[str, dict],
    portfolio_items: list[dict],
    max_per_category: int,
) -> dict:
    slugs_by_category: dict[str, list[str]] = {category: [] for category in CATEGORY_ORDER}
    for slug, group in slug_to_group.items():
        slugs_by_category.setdefault(group, []).append(slug)

    categories = {}
    for category in CATEGORY_ORDER:
        product_candidates = _product_candidates(category, slugs_by_category.get(category, []), products)
        portfolio_candidates = _portfolio_candidates(category, portfolio_items)
        candidates = sorted(product_candidates + portfolio_candidates, key=lambda item: item["score"], reverse=True)
        kept = candidates[:max_per_category]
        categories[category] = {
            "current_live_image_state": "empty in live DB as of 2026-05-06 recheck",
            "product_slugs": slugs_by_category.get(category, []),
            "candidate_count_before_trim": len(candidates),
            "top_candidate": kept[0] if kept else None,
            "candidates": kept,
            "review_notes": _review_notes(category, kept),
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "no_live_db_changes": True,
        "purpose": "Review packet for selecting representative Item Group images; this report does not assign images.",
        "source_inputs": {
            "slug_to_group": _rel(SLUG_TO_GROUP),
            "catalog": _rel(CATALOG),
            "source_images": _rel(SOURCE_IMAGE_DIR),
            "portfolio_controller": _rel(PORTFOLIO_CONTROLLER),
            "portfolio_optimized_images": _rel(PORTFOLIO_OPTIMIZED_DIR),
        },
        "categories": categories,
    }


def _product_candidates(category: str, slugs: list[str], products: dict[str, dict]) -> list[dict]:
    candidates = []
    preferred = PREFERRED_PRODUCT_SLUGS.get(category, set())
    for slug in slugs:
        product = products.get(slug, {})
        for path in _images_for_slug(slug):
            info = _image_info(path)
            is_primary = path.stem == slug
            score = 50
            if is_primary:
                score += 22
            if slug in preferred:
                score += 18
            score += _size_score(path.stat().st_size)
            if info.get("width") and info.get("height"):
                score += _shape_score(info["width"], info["height"])
            if path.suffix.lower() == ".webp":
                score += 2
            if path.stat().st_size < 20_000:
                score -= 10
            candidates.append(
                {
                    "kind": "product_source",
                    "score": score,
                    "path": _rel(path),
                    "product_slug": slug,
                    "product_name": product.get("name", slug),
                    "bytes": path.stat().st_size,
                    **info,
                    "reason": _product_reason(category, slug, is_primary),
                    "approval_note": "Good candidate for a shop category image if Jeff accepts this product as representative.",
                }
            )
    return candidates


def _portfolio_candidates(category: str, portfolio_items: list[dict]) -> list[dict]:
    allowed = CATEGORY_PORTFOLIO_MAP.get(category, set())
    if not allowed:
        return []
    candidates = []
    for item in portfolio_items:
        if item.get("category") not in allowed:
            continue
        stem = Path(item["image"]).stem
        path = PORTFOLIO_OPTIMIZED_DIR / f"{stem}.webp"
        if not path.exists():
            continue
        info = _image_info(path)
        score = 58 + _size_score(path.stat().st_size)
        if info.get("width") and info.get("height"):
            score += _shape_score(info["width"], info["height"])
        candidates.append(
            {
                "kind": "portfolio_proof",
                "score": score,
                "path": _rel(path),
                "portfolio_slug": item["slug"],
                "portfolio_title": item["title"],
                "portfolio_category": item["category"],
                "bytes": path.stat().st_size,
                **info,
                "reason": "Existing optimized installed-work proof image aligned to this visual category.",
                "approval_note": "Use only if the category surface should show real installed proof rather than an exact product-source photo.",
            }
        )
    return candidates


def _images_for_slug(slug: str) -> list[Path]:
    paths = [
        path
        for path in SOURCE_IMAGE_DIR.iterdir()
        if path.is_file() and (path.stem == slug or path.stem.startswith(f"{slug}--"))
    ]
    return sorted(paths, key=lambda path: (path.stem != slug, path.name))


def _image_info(path: Path) -> dict:
    try:
        with Image.open(path) as image:
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "aspect_ratio": round(image.width / image.height, 3) if image.height else None,
            }
    except Exception as exc:
        return {"image_read_error": str(exc)}


def _size_score(size: int) -> int:
    if size >= 500_000:
        return 14
    if size >= 200_000:
        return 10
    if size >= 80_000:
        return 6
    if size >= 30_000:
        return 2
    return 0


def _shape_score(width: int, height: int) -> int:
    ratio = width / height if height else 0
    if 0.75 <= ratio <= 1.9:
        return 8
    if 0.5 <= ratio <= 2.4:
        return 4
    return 0


def _product_reason(category: str, slug: str, is_primary: bool) -> str:
    pieces = [f"Source product maps to {category}."]
    if is_primary:
        pieces.append("Primary product image.")
    else:
        pieces.append("Additional product image.")
    if slug in PREFERRED_PRODUCT_SLUGS.get(category, set()):
        pieces.append("Product is a preferred representative for this category.")
    return " ".join(pieces)


def _review_notes(category: str, candidates: list[dict]) -> list[str]:
    notes = ["No ERPNext image fields were changed."]
    if not candidates:
        notes.append("No existing source candidate found; category needs new source media or manual selection.")
        return notes
    if len(candidates) < 3:
        notes.append("Thin candidate pool; review carefully before using this as a permanent category image.")
    if any(candidate["kind"] == "portfolio_proof" for candidate in candidates):
        notes.append("Portfolio proof candidates are polished but may not be exact product catalog photos.")
    if category in {"Balloon Drops", "Photo Ops & Backdrops"}:
        notes.append("Small catalog category; one strong image may be enough for launch if approved.")
    return notes


def _render_markdown(report: dict) -> str:
    lines = [
        "# Category Media Candidates",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "No live ERPNext image fields were changed. This is an approval packet for the 8 customer-facing shop categories.",
        "",
        "## Quick Picks For Review",
        "",
        "These are the highest-ranked first-pass choices. They still need Jeff/GL approval before any live category image assignment.",
        "",
    ]
    for category, data in report["categories"].items():
        candidate = data.get("top_candidate")
        if not candidate:
            lines.append(f"- **{category}:** no candidate found")
            continue
        label = candidate.get("product_name") or candidate.get("portfolio_title") or candidate.get("path")
        lines.append(
            f"- **{category}:** `{candidate['path']}` ({candidate['kind']}, score {candidate['score']}) - {label}"
        )
    lines.append("")

    for category, data in report["categories"].items():
        lines.extend([f"## {category}", ""])
        lines.append(f"Product slugs: {', '.join(data['product_slugs']) or '(none)'}")
        lines.append("")
        for index, candidate in enumerate(data["candidates"], start=1):
            label = candidate.get("product_name") or candidate.get("portfolio_title") or candidate.get("path")
            dims = ""
            if candidate.get("width") and candidate.get("height"):
                dims = f"{candidate['width']}x{candidate['height']}, "
            lines.append(
                f"{index}. `{candidate['path']}` - {candidate['kind']}, score {candidate['score']}, "
                f"{dims}{candidate['bytes']} bytes"
            )
            lines.append(f"   - Label: {label}")
            lines.append(f"   - Reason: {candidate['reason']}")
            lines.append(f"   - Approval note: {candidate['approval_note']}")
        if not data["candidates"]:
            lines.append("- No candidates found.")
        lines.append("")
        lines.append("Review notes:")
        for note in data["review_notes"]:
            lines.append(f"- {note}")
        lines.append("")
    return "\n".join(lines)


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
