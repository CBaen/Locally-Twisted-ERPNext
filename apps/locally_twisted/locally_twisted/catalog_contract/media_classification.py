"""Source-backed media classification packet for product-page imports.

This module is pure reporting code. It keeps source extra images out of live
ERPNext media fields until GL/Locally Twisted classifies each image's role.
"""
from __future__ import annotations

from typing import Any

from locally_twisted.catalog_contract.source_builder import build_product_page_contract


SCHEMA_VERSION = "lt-product-page-media-classification-packet-v1"
SAFE_DEFAULT = "ignored_artifact"
HOLD_STATUS = "hold_until_classified"
ALLOWED_ROLES = (
    "primary",
    "gallery",
    "variant_image",
    "reference",
    "ignored_artifact",
)


def build_media_classification_packet(
    products: list[dict[str, Any]],
    *,
    slug_to_group: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a JSON-safe packet for unclassified source extra images."""
    slug_to_group = slug_to_group or {}
    rows = [
        _product_row(product, slug_to_group=slug_to_group)
        for product in products
        if product.get("additional_image_urls")
    ]
    image_count = sum(row["extra_image_count"] for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "purpose": "Source media classification packet before ERPNext product-page import or public ecommerce reopen.",
        "warning": (
            "This packet does not assign media. Source extra images must remain "
            "out of Website Slideshow, variant image, reference image, and gallery claims until approved."
        ),
        "safe_default": SAFE_DEFAULT,
        "hold_status": HOLD_STATUS,
        "allowed_roles": list(ALLOWED_ROLES),
        "source_product_count": len(products),
        "products_with_extra_images": len(rows),
        "source_extra_image_count": image_count,
        "unclassified_image_count": image_count,
        "approved_gallery_count": 0,
        "assigned_variant_image_count": 0,
        "products": rows,
    }


def _product_row(product: dict[str, Any], *, slug_to_group: dict[str, str]) -> dict[str, Any]:
    slug = str(product.get("slug") or "").strip()
    contract = build_product_page_contract(product, category_hint=slug_to_group.get(slug, ""))
    images = [
        {
            "source_index": index,
            "url": str(url),
            "current_role": SAFE_DEFAULT,
            "classification_status": HOLD_STATUS,
            "hold_reason": "Source extra image has no approved media role yet.",
            "safe_default": SAFE_DEFAULT,
            "allowed_roles": list(ALLOWED_ROLES),
        }
        for index, url in enumerate(product.get("additional_image_urls") or [], start=1)
        if str(url or "").strip()
    ]
    return {
        "slug": slug,
        "title": str(product.get("name") or slug).strip(),
        "source_url": str(product.get("url") or product.get("source_url") or "").strip(),
        "primary_image_url": str(product.get("image_url") or "").strip(),
        "category_hint": slug_to_group.get(slug, ""),
        "product_page_type": contract.product_page_type,
        "product_page_type_label": contract.product_page_type_label,
        "commerce_lane": contract.commerce_lane,
        "commerce_lane_label": contract.commerce_lane_label,
        "extra_image_count": len(images),
        "images": images,
    }
