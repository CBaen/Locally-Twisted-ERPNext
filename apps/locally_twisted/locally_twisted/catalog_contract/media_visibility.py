"""Read-only media visibility reporting for product-page contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from locally_twisted.catalog_contract.source_builder import build_product_page_contract


RENDERABLE_EXTRA_ROLES = {"gallery", "variant_image", "reference"}
SAFE_HELD_EXTRA_ROLE = "ignored_artifact"
KNOWN_MEDIA_ROLES = {"primary", *RENDERABLE_EXTRA_ROLES, SAFE_HELD_EXTRA_ROLE}


@dataclass(frozen=True)
class MediaVisibilityRow:
    slug: str
    product_page_type_label: str
    commerce_lane_label: str
    source_primary_images: int
    source_extra_images: int
    approved_gallery_images: int
    approved_variant_images: int
    reference_images: int
    held_back_ignored_artifacts: int
    live_website_image: bool
    live_slideshow: bool
    active_variants: int
    active_variant_images: int
    distinct_variant_images: int
    unclassified_source_images: int

    @property
    def needs_media_review(self) -> bool:
        return self.held_back_ignored_artifacts > 0 or self.unclassified_source_images > 0


@dataclass(frozen=True)
class MediaVisibilityReport:
    rows: tuple[MediaVisibilityRow, ...]
    website_slideshow_count: int = 0
    website_slideshow_item_count: int = 0
    blockers: tuple[str, ...] = field(default_factory=tuple)

    def summary(self) -> dict[str, Any]:
        return {
            "source_products": len(self.rows),
            "products_with_source_primary_image": sum(1 for row in self.rows if row.source_primary_images),
            "products_with_source_extra_images": sum(1 for row in self.rows if row.source_extra_images),
            "source_extra_images": sum(row.source_extra_images for row in self.rows),
            "approved_gallery_images": sum(row.approved_gallery_images for row in self.rows),
            "approved_variant_images": sum(row.approved_variant_images for row in self.rows),
            "reference_images": sum(row.reference_images for row in self.rows),
            "held_back_ignored_artifacts": sum(row.held_back_ignored_artifacts for row in self.rows),
            "unclassified_source_images": sum(row.unclassified_source_images for row in self.rows),
            "website_items_with_live_image": sum(1 for row in self.rows if row.live_website_image),
            "website_items_with_slideshow": sum(1 for row in self.rows if row.live_slideshow),
            "website_slideshows": self.website_slideshow_count,
            "website_slideshow_items": self.website_slideshow_item_count,
            "active_variants": sum(row.active_variants for row in self.rows),
            "active_variant_images": sum(row.active_variant_images for row in self.rows),
            "products_with_active_variant_images": sum(1 for row in self.rows if row.active_variant_images),
        }

    def to_markdown(self) -> str:
        summary = self.summary()
        lines = [
            "# Product Page Media Visibility Report",
            "",
            "This read-only report checks media evidence for the two reusable product-page template types.",
            "It does not assign, move, approve, delete, or upload images.",
            "",
            "## Summary",
            "",
            f"- Source products checked: {summary['source_products']}",
            f"- Products with source primary image: {summary['products_with_source_primary_image']}",
            f"- Products with source extra images: {summary['products_with_source_extra_images']}",
            f"- Source extra images: {summary['source_extra_images']}",
            f"- Approved gallery images: {summary['approved_gallery_images']}",
            f"- Approved variant images: {summary['approved_variant_images']}",
            f"- Reference images: {summary['reference_images']}",
            f"- Held-back ignored artifacts: {summary['held_back_ignored_artifacts']}",
            f"- Unsafe unclassified source extra images: {summary['unclassified_source_images']}",
            f"- Website Items with live primary image: {summary['website_items_with_live_image']}",
            f"- Website Items with slideshow field set: {summary['website_items_with_slideshow']}",
            f"- Website Slideshow records: {summary['website_slideshows']}",
            f"- Website Slideshow Item records: {summary['website_slideshow_items']}",
            f"- Active variants: {summary['active_variants']}",
            f"- Active variants with image: {summary['active_variant_images']}",
            f"- Products with active variant images: {summary['products_with_active_variant_images']}",
            "",
            "## Gate Result",
            "",
        ]
        if self.blockers:
            lines.append("**BLOCKED for media-ready product import.**")
            lines.append("")
            lines.extend(f"- {blocker}" for blocker in self.blockers)
        else:
            lines.append("**PASS for media visibility readiness.**")

        lines.extend([
            "",
            "## Interpretation",
            "",
            "Live ERPNext primary images and some variant images are evidence of current stored media, not proof that source media is fully classified.",
            "Source extras marked ignored_artifact are intentionally held back and are non-blocking because product pages must not render them.",
            "Gallery, variant_image, and reference media may render only when the backend/source contract approves that role.",
            "The current public ecommerce pause means rendered product-page media proof must use authenticated/internal access or explicitly report the pause as the blocker.",
            "",
            "## Product Coverage",
            "",
            "| Slug | Template | Lane | Source primary | Source extras | Gallery | Variant | Reference | Held ignored | Unsafe unclassified | Live primary | Live slideshow | Active variants | Variant images | Distinct variant images |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|",
        ])
        for row in self.rows:
            lines.append(
                f"| {row.slug} | {row.product_page_type_label} | {row.commerce_lane_label} | "
                f"{row.source_primary_images} | {row.source_extra_images} | "
                f"{row.approved_gallery_images} | {row.approved_variant_images} | {row.reference_images} | "
                f"{row.held_back_ignored_artifacts} | {row.unclassified_source_images} | "
                f"{'yes' if row.live_website_image else 'no'} | {'yes' if row.live_slideshow else 'no'} | "
                f"{row.active_variants} | {row.active_variant_images} | {row.distinct_variant_images} |"
            )
        return "\n".join(lines)


def build_media_visibility_report(
    products: list[dict[str, Any]],
    *,
    slug_to_group: dict[str, str],
    live_rows: list[dict[str, Any]],
    website_slideshow_count: int,
    website_slideshow_item_count: int,
) -> MediaVisibilityReport:
    live = _LiveMediaCatalog(live_rows)
    rows: list[MediaVisibilityRow] = []
    blockers: list[str] = []
    contracts_by_slug: dict[str, Any] = {}

    for product in products:
        contract = build_product_page_contract(
            product,
            category_hint=slug_to_group.get(str(product.get("slug") or ""), ""),
        )
        contracts_by_slug[contract.slug] = contract
        slug = str(product.get("slug") or "")
        source_extra_images = len(product.get("additional_image_urls") or [])
        live_row = live.coverage_for(slug)
        source_extra_roles = [
            image.role
            for image in contract.gallery
            if image.role != "primary"
        ]
        row = MediaVisibilityRow(
            slug=contract.slug,
            product_page_type_label=contract.product_page_type_label,
            commerce_lane_label=contract.commerce_lane_label,
            source_primary_images=1 if product.get("image_url") else 0,
            source_extra_images=source_extra_images,
            approved_gallery_images=sum(1 for role in source_extra_roles if role == "gallery"),
            approved_variant_images=sum(1 for role in source_extra_roles if role == "variant_image"),
            reference_images=sum(1 for role in source_extra_roles if role == "reference"),
            held_back_ignored_artifacts=sum(1 for role in source_extra_roles if role == SAFE_HELD_EXTRA_ROLE),
            live_website_image=live_row["live_website_image"],
            live_slideshow=live_row["live_slideshow"],
            active_variants=live_row["active_variants"],
            active_variant_images=live_row["active_variant_images"],
            distinct_variant_images=live_row["distinct_variant_images"],
            unclassified_source_images=sum(1 for role in source_extra_roles if role not in KNOWN_MEDIA_ROLES),
        )
        rows.append(row)

    unclassified_products = [row for row in rows if row.unclassified_source_images]
    unclassified_images = sum(row.unclassified_source_images for row in rows)
    if unclassified_products:
        blockers.append(
            f"{len(unclassified_products)} products have {unclassified_images} unsafe unclassified source extra images."
        )
    unsafe_held_rows = [
        row.slug
        for row in rows
        if row.held_back_ignored_artifacts
        and _held_media_has_unsafe_rendering(contracts_by_slug.get(row.slug))
    ]
    if unsafe_held_rows:
        blockers.append(
            "Held ignored_artifact media is missing hold_back render policy for: "
            + ", ".join(unsafe_held_rows[:10])
        )
    role_count_mismatches = [
        row.slug
        for row in rows
        if row.source_extra_images
        != (
            row.approved_gallery_images
            + row.approved_variant_images
            + row.reference_images
            + row.held_back_ignored_artifacts
            + row.unclassified_source_images
        )
    ]
    if role_count_mismatches:
        blockers.append(
            "Source extra image counts do not match backend media-role classifications for: "
            + ", ".join(role_count_mismatches[:10])
        )
    approved_gallery_images = sum(row.approved_gallery_images for row in rows)
    if approved_gallery_images and (website_slideshow_count == 0 or website_slideshow_item_count == 0):
        blockers.append("Approved gallery media exists but no ERPNext Website Slideshow records are present.")
    if not approved_gallery_images and (website_slideshow_count or website_slideshow_item_count):
        blockers.append("ERPNext Website Slideshow records exist without source-approved gallery media.")
    missing_primary = [row.slug for row in rows if row.source_primary_images and not row.live_website_image]
    if missing_primary:
        blockers.append("Live ERPNext is missing primary Website Item images for: " + ", ".join(missing_primary[:10]))

    return MediaVisibilityReport(
        rows=tuple(rows),
        website_slideshow_count=website_slideshow_count,
        website_slideshow_item_count=website_slideshow_item_count,
        blockers=tuple(blockers),
    )


class _LiveMediaCatalog:
    def __init__(self, rows: list[dict[str, Any]]):
        self._products: dict[str, dict[str, Any]] = {}
        for row in rows:
            slug = _clean(row.get("website_item_code"))
            if not slug:
                continue
            product = self._products.setdefault(
                slug,
                {
                    "website_image": _clean(row.get("website_image")),
                    "slideshow": _clean(row.get("slideshow")),
                    "variants": {},
                },
            )
            if _clean(row.get("website_image")):
                product["website_image"] = _clean(row.get("website_image"))
            if _clean(row.get("slideshow")):
                product["slideshow"] = _clean(row.get("slideshow"))

            item_code = _clean(row.get("item_code"))
            if not item_code or _clean(row.get("variant_of")) != slug:
                continue
            variant = product["variants"].setdefault(
                item_code,
                {
                    "disabled": _clean(row.get("disabled")),
                    "image": _clean(row.get("image")),
                },
            )
            if _clean(row.get("image")):
                variant["image"] = _clean(row.get("image"))

    def coverage_for(self, slug: str) -> dict[str, Any]:
        product = self._products.get(slug) or {}
        variants = [
            variant
            for variant in (product.get("variants") or {}).values()
            if variant.get("disabled") in {"0", 0}
        ]
        variant_images = [variant.get("image") for variant in variants if variant.get("image")]
        return {
            "live_website_image": bool(product.get("website_image")),
            "live_slideshow": bool(product.get("slideshow")),
            "active_variants": len(variants),
            "active_variant_images": len(variant_images),
            "distinct_variant_images": len(set(variant_images)),
        }


def _clean(value: Any) -> str:
    if value in (None, "NULL"):
        return ""
    return str(value).strip()


def _held_media_has_unsafe_rendering(contract: Any) -> bool:
    if not contract:
        return True
    return any(
        image.role == SAFE_HELD_EXTRA_ROLE
        and (
            getattr(image, "classification_status", "") != "hold_until_classified"
            or getattr(image, "render_policy", "") != "hold_back"
            or not getattr(image, "role_reason", "")
        )
        for image in contract.gallery
    )
