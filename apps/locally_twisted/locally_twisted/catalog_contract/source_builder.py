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
    OptionDependencyMatrixContract,
    ProductPageContract,
    RequiredOptionAxisContract,
)
from locally_twisted.product_page_labels import commerce_lane_label, product_page_type_label


CHECKOUT_CATEGORY_HINTS = {
    "bouquet",
    "bouquets",
    "deliveries",
    "get-well",
    "grab",
    "seasonal",
}

REVIEW_WARNING_PREFIX = "Axis needs review before import:"


def _axis_values(axis: Any) -> tuple[str, ...]:
    if not isinstance(axis, dict):
        return ()
    values = axis.get("values") or []
    return tuple(str(value.get("name") or "").strip() for value in values if isinstance(value, dict) and value.get("name"))


def _has_resolver_prices(rows: list[dict[str, Any]]) -> bool:
    if not rows:
        return False
    return all(row.get("erpnext_variant_price") is not None for row in rows)


def _checkout_category(slug: str, category_hint: str = "") -> bool:
    text = f"{slug} {category_hint}".lower()
    return any(hint in text for hint in CHECKOUT_CATEGORY_HINTS)


def _product_page_type(
    *,
    slug: str,
    category_hint: str,
    required_axes: list[RequiredOptionAxisContract],
    customization_axes: list[RequiredOptionAxisContract],
    warnings: list[str],
) -> str:
    if not slug:
        return "needs_review"
    if customization_axes:
        return "complex_custom_product"
    if len(required_axes) > 1:
        return "complex_custom_product"
    if any(warning.startswith(REVIEW_WARNING_PREFIX) for warning in warnings):
        return "complex_custom_product"
    if _checkout_category(slug, category_hint):
        return "simple_product"
    return "complex_custom_product"


def _commerce_lane(product_page_type: str) -> str:
    if product_page_type == "simple_product":
        return "checkout"
    if product_page_type == "complex_custom_product":
        return "quote_first"
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


def _dependency_matrices(
    variant_rows: list[dict[str, Any]],
    required_axes: list[RequiredOptionAxisContract],
) -> tuple[OptionDependencyMatrixContract, ...]:
    axes = tuple(axis.name for axis in required_axes)
    if not axes or not variant_rows:
        return ()

    seen: dict[tuple[tuple[str, str], ...], dict[str, str]] = {}
    for row in variant_rows:
        combo = row.get("combo") or {}
        if not isinstance(combo, dict):
            continue
        values = {
            axis: str(combo.get(axis) or "").strip()
            for axis in axes
            if str(combo.get(axis) or "").strip()
        }
        if set(values) != set(axes):
            continue
        key = tuple((axis, values[axis]) for axis in axes)
        seen[key] = values

    combinations = tuple(seen[key] for key in sorted(seen))
    if not combinations:
        return (
            OptionDependencyMatrixContract(
                axes=axes,
                valid_combinations=(),
                source_variant_rows=len(variant_rows),
                valid_combination_count=0,
                status="needs_review",
                note="Source variant rows did not produce a complete required-option dependency matrix.",
            ),
        )
    return (
        OptionDependencyMatrixContract(
            axes=axes,
            valid_combinations=combinations,
            source_variant_rows=len(variant_rows),
            valid_combination_count=len(combinations),
            note="Source valid_variants projected onto required product-page axes after customization/add-on axes are removed.",
        ),
    )


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
            warnings.append(f"{REVIEW_WARNING_PREFIX} {axis_name} - {classification.note}")

    primary_image = str(product.get("image_url") or "")
    gallery = [GalleryImageContract(url=primary_image, role="primary")] if primary_image else []
    for url in product.get("additional_image_urls") or []:
        gallery.append(GalleryImageContract(url=str(url), role="review_needed"))

    has_prices = _has_resolver_prices(variant_rows)
    if variant_rows and not has_prices:
        warnings.append("Variant product lacks resolver-backed erpnext_variant_price rows.")
    if gallery and any(image.role == "review_needed" for image in gallery):
        warnings.append("One or more alternate images need gallery/variant classification.")

    product_page_type = _product_page_type(
        slug=slug,
        category_hint=category_hint,
        required_axes=required_axes,
        customization_axes=customization_axes,
        warnings=warnings,
    )
    commerce_lane = _commerce_lane(product_page_type)

    return ProductPageContract(
        slug=slug,
        source_name=title,
        route=f"shop-items/{slug}" if slug else "",
        title=title,
        description_html=str(product.get("description") or ""),
        category_hint=category_hint,
        product_page_type=product_page_type,
        product_page_type_label=product_page_type_label(product_page_type),
        commerce_lane=commerce_lane,
        commerce_lane_label=commerce_lane_label(commerce_lane),
        primary_image=primary_image,
        gallery=tuple(gallery),
        required_axes=tuple(required_axes),
        customization_axes=tuple(customization_axes),
        add_ons=tuple(add_ons),
        dependency_matrices=_dependency_matrices(variant_rows, required_axes),
        source_variant_rows=len(variant_rows),
        has_resolver_prices=has_prices,
        warnings=tuple(warnings),
    )
