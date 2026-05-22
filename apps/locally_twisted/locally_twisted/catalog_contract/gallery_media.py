"""Canonical product-gallery media helpers for source catalog rows."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


@dataclass(frozen=True)
class CanonicalGallerySource:
    url: str
    label: str
    source_index: int
    first_index: int
    key: str
    source_path: Path | None = None
    file_size: int = 0

    @property
    def file_url(self) -> str:
        return f"/files/{self.source_path.name}" if self.source_path else ""


def canonical_gallery_sources(product: dict, images_dir: Path | None = None) -> list[CanonicalGallerySource]:
    """Return deduped, ordered, renderable source gallery images."""
    slug = str(product.get("slug") or "").strip()
    by_key: dict[str, CanonicalGallerySource] = {}

    for index, url in enumerate(product.get("additional_image_urls") or [], start=1):
        clean_url = str(url or "").strip()
        if not clean_url:
            continue
        key = _semantic_key(clean_url)
        label = _url_label(clean_url)
        source_path = _source_path(slug, index, images_dir)
        candidate = CanonicalGallerySource(
            url=clean_url,
            label=label,
            source_index=index,
            first_index=by_key.get(key).first_index if key in by_key else index,
            key=key,
            source_path=source_path,
            file_size=source_path.stat().st_size if source_path and source_path.exists() else 0,
        )
        existing = by_key.get(key)
        if not existing or _quality_score(candidate) > _quality_score(existing):
            by_key[key] = candidate

    return sorted(by_key.values(), key=lambda row: row.first_index)


def source_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _source_path(slug: str, index: int, images_dir: Path | None) -> Path | None:
    if not slug or not images_dir:
        return None
    matches = sorted(images_dir.glob(f"{slug}--extra-{index:02d}.*"))
    return matches[0] if matches else None


def _quality_score(source: CanonicalGallerySource) -> tuple[int, int, int]:
    return (_image_size_rank(source.url), source.file_size, -source.source_index)


def _image_size_rank(url: str) -> int:
    match = re.search(r"/image_(\d+)(?:/|$)", url)
    return int(match.group(1)) if match else 0


def _semantic_key(url: str) -> str:
    path = unquote(urlparse(url).path)
    match = re.search(r"/web/image/([^/]+)/([^/]+)/image_\d+/", path)
    if match:
        return f"{match.group(1)}:{match.group(2)}"
    return _compact(_url_label(url))


def _url_label(url: str) -> str:
    path = urlparse(url).path
    label = Path(unquote(path)).name
    label = re.sub(r"\.(webp|png|jpe?g)$", "", label, flags=re.IGNORECASE)
    return label or url


def _compact(text: str) -> str:
    text = unquote(text or "").lower()
    text = re.sub(r"\.(webp|png|jpe?g)$", "", text)
    text = re.sub(r"[^a-z0-9]+", "", text)
    return text
