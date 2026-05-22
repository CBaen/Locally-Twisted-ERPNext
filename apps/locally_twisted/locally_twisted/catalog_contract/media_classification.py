"""Source-backed media classification packet for product-page imports."""
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
    """Build a JSON-safe packet for source extra image roles."""
    slug_to_group = slug_to_group or {}
    rows = [
        _product_row(product, slug_to_group=slug_to_group)
        for product in products
        if product.get("additional_image_urls")
    ]
    image_count = sum(row["extra_image_count"] for row in rows)
    raw_url_count = sum(row["source_extra_url_count"] for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "purpose": "Source media classification packet before ERPNext product-page import or public ecommerce reopen.",
        "warning": (
            "Approved source product-gallery media must render through Product Setup and Website Slideshow. "
            "Unclassified extras still default to ignored_artifact / hold_back."
        ),
        "safe_default": SAFE_DEFAULT,
        "hold_status": HOLD_STATUS,
        "allowed_roles": list(ALLOWED_ROLES),
        "source_product_count": len(products),
        "products_with_extra_images": len(rows),
        "source_extra_url_count": raw_url_count,
        "source_extra_image_count": image_count,
        "held_back_ignored_artifact_count": 0,
        "unsafe_unclassified_image_count": 0,
        "unclassified_image_count": 0,
        "approved_gallery_count": image_count,
        "assigned_variant_image_count": 0,
        "approved_reference_count": 0,
        "products": rows,
    }


def _product_row(product: dict[str, Any], *, slug_to_group: dict[str, str]) -> dict[str, Any]:
    slug = str(product.get("slug") or "").strip()
    contract = build_product_page_contract(product, category_hint=slug_to_group.get(slug, ""))
    images = []
    for image in contract.gallery:
        if image.role == "primary":
            continue
        images.append(
            {
                "source_index": len(images) + 1,
                "url": image.url,
                "current_role": image.role,
                "classification_status": image.classification_status,
                "render_policy": image.render_policy,
                "role_reason": image.role_reason,
                "hold_reason": "",
                "safe_default": SAFE_DEFAULT,
                "allowed_roles": list(ALLOWED_ROLES),
            }
        )
    return {
        "slug": slug,
        "title": str(product.get("name") or slug).strip(),
        "source_url": str(product.get("url") or product.get("source_url") or "").strip(),
        "primary_image_url": str(product.get("image_url") or "").strip(),
        "source_extra_url_count": len(product.get("additional_image_urls") or []),
        "category_hint": slug_to_group.get(slug, ""),
        "product_page_type": contract.product_page_type,
        "product_page_type_label": contract.product_page_type_label,
        "commerce_lane": contract.commerce_lane,
        "commerce_lane_label": contract.commerce_lane_label,
        "extra_image_count": len(images),
        "images": images,
    }
