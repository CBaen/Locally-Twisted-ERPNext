"""Build product-page contracts from source catalog rows."""

from __future__ import annotations

from typing import Any

from locally_twisted.catalog_contract.addon_rules import classify_axis, known_add_on_contracts_for_axis
from locally_twisted.catalog_contract.color_rules import grouped_colors, is_balloon_color_axis
from locally_twisted.catalog_contract.models import (
    AddOnContract,
    ColorGroupContract,
    ColorOptionContract,
    GalleryImageContract,
    ProductPageContract,
    RequiredOptionAxisContract,
)


CHECKOUT_CATEGORY_HINTS = {
    "bouquet",
    "bouquets",
    "deliveries",
    "get-well",
    "grab",
    "seasonal",
}


def _axis_values(axis: Any) -> tuple[str, ...]:
    if not isinstance(axis, dict):
        return ()
    values = axis.get("values") or []
    return tuple(str(value.get("name") or "").strip() for value in values if isinstance(value, dict) and value.get("name"))


def _has_resolver_prices(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    return all(row.get("erpnext_variant_price") is not None for row in rows)


def _commerce_lane(slug: str, category_hint: str = "") -> str:
    text = f"{slug} {category_hint}".lower()
    if any(hint in text for hint in CHECKOUT_CATEGORY_HINTS):
        return "checkout"
    return "needs_review"


def _color_groups(values: tuple[str, ...]) -> tuple[ColorGroupContract, ...]:
    groups = []
    for group in grouped_colors(values):
        groups.append(
            ColorGroupContract(
                group=group["group"],
                options=tuple(ColorOptionContract(**option) for option in group["options"]),
            )
        )
    return tuple(groups)


def build_product_page_contract(product: dict[str, Any], *, category_hint: str = "") -> ProductPageContract:
    slug = str(product.get("slug") or "").strip()
    title = str(product.get("name") or slug).strip()
    variant_rows = product.get("valid_variants") or []
    attributes = product.get("attributes") or {}

    warnings: list[str] = []
    required_axes: list[RequiredOptionAxisContract] = []
    customization_axes: list[RequiredOptionAxisContract] = []
    add_ons: list[AddOnContract] = []

    for axis_name, axis in attributes.items():
        values = _axis_values(axis)
        if is_balloon_color_axis(axis_name):
            customization_axes.append(
                RequiredOptionAxisContract(
                    name=str(axis_name),
                    display_type=str(axis.get("display_type") or ""),
                    values=values,
                    status="customization",
                    selector_type="multi_select_drawer",
                    note="Balloon colors are visual multi-select customization, not a hidden dropdown. Preserve vendor/hex/swatch metadata.",
                    color_groups=_color_groups(values),
                )
            )
            warnings.append(f"Color axis removed from required ERPNext variants and needs customization/import handling: {axis_name}")
            continue

        classification = classify_axis(axis_name)
        if classification.status == "required":
            selector_type = "radio" if len(values) <= 8 else "single_select"
            required_axes.append(
                RequiredOptionAxisContract(
                    name=str(axis_name),
                    display_type=str(axis.get("display_type") or ""),
                    values=values,
                    status="required",
                    selector_type=selector_type,
                    note=classification.note,
                )
            )
        elif classification.status == "optional_addon":
            for row in known_add_on_contracts_for_axis(str(axis_name)):
                add_ons.append(AddOnContract(**row))
        else:
            warnings.append(f"Axis needs review before import: {axis_name} - {classification.note}")

    primary_image = str(product.get("image_url") or "")
    gallery = [GalleryImageContract(url=primary_image, role="primary")] if primary_image else []
    for url in product.get("additional_image_urls") or []:
        gallery.append(GalleryImageContract(url=str(url), role="review_needed"))

    has_prices = _has_resolver_prices(variant_rows)
    if variant_rows and not has_prices:
        warnings.append("Variant product lacks resolver-backed erpnext_variant_price rows.")
    if gallery and any(image.role == "review_needed" for image in gallery):
        warnings.append("One or more alternate images need gallery/variant classification.")

    return ProductPageContract(
        slug=slug,
        source_name=title,
        route=f"shop-items/{slug}" if slug else "",
        title=title,
        description_html=str(product.get("description") or ""),
        category_hint=category_hint,
        commerce_lane=_commerce_lane(slug, category_hint),
        primary_image=primary_image,
        gallery=tuple(gallery),
        required_axes=tuple(required_axes),
        customization_axes=tuple(customization_axes),
        add_ons=tuple(add_ons),
        source_variant_rows=len(variant_rows),
        has_resolver_prices=has_prices,
        warnings=tuple(warnings),
    )
