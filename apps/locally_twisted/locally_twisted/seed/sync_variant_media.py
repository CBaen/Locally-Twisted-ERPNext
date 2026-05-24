"""Map LT catalog seed extra product photos onto ERPNext variant Items.

Run in-process:
    bench --site frontend execute locally_twisted.seed.sync_variant_media.execute \
        --kwargs '{"data_dir":"/tmp/lt-variant-media"}'

The host wrapper at scripts/setup/sync_variant_media.py stages the source files
into the container before calling this module.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import unquote, urlparse

import frappe


SITE_FILES_DIR = Path("/home/frappe/frappe-bench/sites/frontend/public/files")
LT_SEED_ARTIFACT_DIR = "lt_catalog_seed"
REFERENCE_FALLBACK_DIRS_ENV = "LT_REFERENCE_SEED_DIRS"
DEFAULT_DATA_DIRS = [
    Path("/tmp/lt-variant-media"),
    Path(f"/home/frappe/frappe-bench/apps/locally_twisted/locally_twisted/seed/{LT_SEED_ARTIFACT_DIR}"),
]
IGNORED_ATTRIBUTES = {
    "baby color",
    "color palette",
    "hair color",
    "latex colors",
    "number colors",
    "skin color",
}


def _local_reference_fallback_dirs() -> list[Path]:
    raw = os.environ.get(REFERENCE_FALLBACK_DIRS_ENV, "")
    return [Path(part) for part in raw.split(os.pathsep) if part.strip()]


def _find_data_dir(data_dir: str | None) -> Path:
    if data_dir:
        p = Path(data_dir)
        if (p / "catalog.json").exists() and (p / "images").exists():
            return p
        raise FileNotFoundError(f"variant media data_dir is missing catalog.json/images: {p}")

    for p in DEFAULT_DATA_DIRS:
        if (p / "catalog.json").exists() and (p / "images").exists():
            return p
    for p in _local_reference_fallback_dirs():
        if (p / "catalog.json").exists() and (p / "images").exists():
            print(
                "WARNING: using local-development reference media fallback. "
                f"Do not use this path for staging/bootstrap: {p}"
            )
            return p
    raise FileNotFoundError(
        "Could not find LT catalog seed artifact for variant media sync. "
        f"Staging/bootstrap requires locally_twisted/seed/{LT_SEED_ARTIFACT_DIR}/ "
        "with catalog.json and images/. Do not fix deployment by bind-mounting "
        "historical reference scrape paths. For local development only, set "
        f"{REFERENCE_FALLBACK_DIRS_ENV} to an explicit reference directory."
    )


def _normalize(text: str) -> str:
    text = unquote(text or "").lower()
    text = text.replace(".webp", " ").replace(".png", " ").replace(".jpg", " ").replace(".jpeg", " ")
    text = text.replace("feet", "ft").replace("foot", "ft")
    text = text.replace("'", " ft ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _normalize(text))


def _url_label(url: str) -> str:
    path = urlparse(url).path
    label = Path(unquote(path)).name
    return label or url


def _source_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _attr_values(prod: dict) -> dict[str, list[str]]:
    values_by_attr: dict[str, list[str]] = {}
    for attr_name, attr_def in (prod.get("attributes") or {}).items():
        if attr_name.lower() in IGNORED_ATTRIBUTES:
            continue

        raw_values = attr_def.get("values") if isinstance(attr_def, dict) else attr_def
        values = []
        for value in raw_values or []:
            if isinstance(value, dict):
                label = value.get("name") or value.get("value_name") or value.get("attribute_value")
            else:
                label = str(value)
            if label:
                values.append(label)
        values_by_attr[attr_name] = values
    return values_by_attr


def _looks_like_match(label_norm: str, label_compact: str, attr_name: str, value: str) -> bool:
    value_norm = _normalize(value)
    value_compact = _compact(value)
    if not value_norm:
        return False

    if value_norm in label_norm or value_compact in label_compact:
        return True

    size = re.fullmatch(r"(\d+)\s*ft", value_norm)
    if size:
        number = size.group(1)
        return (
            f"{number} ft" in label_norm
            or f"{number}ft" in label_compact
            or f"{number}arch" in label_compact
            or f"{number}standard" in label_compact
        )

    attr_norm = _normalize(attr_name)
    if attr_norm == "led lights":
        if value_norm == "add led lights":
            return "light up" in label_norm or "led" in label_norm
        if value_norm == "no lights":
            return "no light" in label_norm

    if attr_norm == "topper" and value_norm == "logo":
        return "logo" in label_norm

    return False


def _attribute_weight(attr_name: str) -> int:
    name = attr_name.lower()
    if any(term in name for term in ("size", "height", "length")):
        return 100
    if name in {"design", "topper", "easter designs", "delivery themes", "add bouquet"}:
        return 60
    if name == "led lights":
        return 50
    return 40


def _candidate_matches(prod: dict, label: str) -> list[dict[str, object]]:
    label_norm = _normalize(label)
    label_compact = _compact(label)
    matches = []
    for attr_name, values in _attr_values(prod).items():
        for value in values:
            if _looks_like_match(label_norm, label_compact, attr_name, value):
                matches.append(
                    {
                        "attribute": attr_name,
                        "value": value,
                        "weight": _attribute_weight(attr_name),
                    }
                )
    return matches


def _source_images(prod: dict, images_dir: Path) -> list[dict[str, object]]:
    slug = prod["slug"]
    images = []
    for index, url in enumerate(prod.get("additional_image_urls") or [], 1):
        files = sorted(images_dir.glob(f"{slug}--extra-{index:02d}.*"))
        if not files:
            continue
        source = files[0]
        label = _url_label(url)
        images.append(
            {
                "source": source,
                "label": label,
                "size": source.stat().st_size,
                "index": index,
                "hash": _source_hash(source),
            }
        )
    return images


def _image_candidates(prod: dict, images_dir: Path) -> list[dict[str, object]]:
    slug = prod["slug"]
    candidates_by_key: dict[str, dict[str, object]] = {}

    for source_image in _source_images(prod, images_dir):
        source = source_image["source"]
        label = source_image["label"]
        matches = _candidate_matches(prod, label)
        if not matches:
            continue

        # The scrape has both image_128 and image_1024 URLs. Keep the largest
        # file for the same semantic label so storefront variants get the best
        # available source.
        key = _compact(label)
        existing = candidates_by_key.get(key)
        candidate = {
            "source": source,
            "label": label,
            "matches": matches,
            "size": source_image["size"],
            "index": source_image["index"],
            "hash": source_image["hash"],
        }
        if not existing or candidate["size"] > existing["size"]:
            candidates_by_key[key] = candidate

    return list(candidates_by_key.values())


def _variant_attrs(item_code: str) -> dict[str, str]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": item_code},
        fields=["attribute", "attribute_value"],
        order_by="idx asc",
    )
    return {row.attribute: row.attribute_value for row in rows}


def _score_candidate(candidate: dict[str, object], variant_attrs: dict[str, str]) -> int:
    score = 0
    for match in candidate["matches"]:
        attr = match["attribute"]
        if variant_attrs.get(attr) != match["value"]:
            return 0
        score += int(match["weight"])
    return score


def _best_candidate(candidates: list[dict[str, object]], variant_attrs: dict[str, str]) -> dict[str, object] | None:
    best = None
    best_score = 0
    for candidate in candidates:
        score = _score_candidate(candidate, variant_attrs)
        if score <= 0:
            continue
        if not best or (score, candidate["size"], -int(candidate["index"])) > (
            best_score,
            best["size"],
            -int(best["index"]),
        ):
            best = candidate
            best_score = score
    return best


def _ensure_file_attached(source: Path, item_code: str) -> str:
    file_url = f"/files/{source.name}"
    target = SITE_FILES_DIR / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.stat().st_size != source.stat().st_size:
        shutil.copy2(source, target)

    existing = frappe.db.exists(
        "File",
        {
            "file_url": file_url,
            "attached_to_doctype": "Item",
            "attached_to_name": item_code,
        },
    )
    if not existing:
        file_doc = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": source.name,
                "file_url": file_url,
                "is_private": 0,
                "attached_to_doctype": "Item",
                "attached_to_name": item_code,
            }
        )
        file_doc.insert(ignore_permissions=True)
    return file_url


def _compact_label(row: dict[str, object]) -> str:
    return str(row.get("label") or "")


def _sync_product(prod: dict, images_dir: Path, dry_run: bool, include_details: bool = False) -> dict[str, object]:
    slug = prod["slug"]
    source_images = _source_images(prod, images_dir)
    candidates = _image_candidates(prod, images_dir)
    if not candidates:
        result = {
            "slug": slug,
            "source_image_count": len(source_images),
            "candidate_count": 0,
            "mapped": 0,
            "unchanged": 0,
            "skipped": 0,
        }
        if include_details:
            result.update(
                {
                    "candidate_labels": [],
                    "used_candidate_labels": [],
                    "unmatched_image_labels": [_compact_label(row) for row in source_images],
                    "review_reason": "no defensible option-label matches" if source_images else "",
                }
            )
        return result

    variants = frappe.get_all(
        "Item",
        filters={"variant_of": slug, "disabled": 0},
        fields=["name", "image"],
        limit_page_length=0,
    )

    mapped = 0
    unchanged = 0
    skipped = 0
    used_candidate_labels = set()
    for variant in variants:
        attrs = _variant_attrs(variant.name)
        candidate = _best_candidate(candidates, attrs)
        if not candidate:
            skipped += 1
            continue

        used_candidate_labels.add(_compact_label(candidate))
        source = candidate["source"]
        file_url = f"/files/{source.name}"
        if variant.get("image") == file_url:
            unchanged += 1
            continue

        mapped += 1
        if not dry_run:
            file_url = _ensure_file_attached(source, variant.name)
            frappe.db.set_value("Item", variant.name, "image", file_url, update_modified=False)

    result = {
        "slug": slug,
        "source_image_count": len(source_images),
        "candidate_count": len(candidates),
        "variant_count": len(variants),
        "mapped": mapped,
        "unchanged": unchanged,
        "skipped": skipped,
    }
    if include_details:
        candidate_keys = {_compact(candidate["label"]) for candidate in candidates}
        unmatched = [
            _compact_label(row)
            for row in source_images
            if _compact(str(row.get("label") or "")) not in candidate_keys
        ]
        review_reasons = []
        if unmatched:
            review_reasons.append("some source images did not match option labels")
        if skipped:
            review_reasons.append("some variants still fall back to the parent image")
        result.update(
            {
                "candidate_labels": sorted({_compact_label(row) for row in candidates}),
                "used_candidate_labels": sorted(used_candidate_labels),
                "unmatched_image_labels": unmatched,
                "review_reason": "; ".join(review_reasons),
            }
        )
    return result


def execute(
    data_dir: str | None = None,
    slug_filter: str | None = None,
    dry_run: bool = False,
    include_details: bool = False,
) -> str:
    data_path = _find_data_dir(data_dir)
    catalog = json.loads((data_path / "catalog.json").read_text(encoding="utf-8"))
    images_dir = data_path / "images"

    products = catalog.get("products") or []
    if slug_filter:
        products = [prod for prod in products if prod.get("slug") == slug_filter]

    frappe.flags.ignore_permissions = True
    results = []
    for prod in products:
        if not prod.get("attributes"):
            continue
        results.append(_sync_product(prod, images_dir, dry_run=bool(dry_run), include_details=bool(include_details)))

    summary = {
        "data_dir": str(data_path),
        "dry_run": bool(dry_run),
        "include_details": bool(include_details),
        "products_checked": len(results),
        "products_with_candidates": sum(1 for row in results if row["candidate_count"]),
        "products_needing_review": sum(1 for row in results if row.get("review_reason")),
        "mapped": sum(int(row["mapped"]) for row in results),
        "unchanged": sum(int(row["unchanged"]) for row in results),
        "skipped": sum(int(row["skipped"]) for row in results),
        "results": results,
    }
    if not dry_run:
        frappe.db.commit()
    return json.dumps(summary, indent=2)
