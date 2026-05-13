"""Shared product-page axis projection rules."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis


COLOR_RECIPE_PATTERNS = frozenset(
    {
        "large_single_choice_color",
        "multi_color_recipe_customization",
        "multi_color_recipes",
    }
)
SINGLE_COLOR_SALE_UNIT_PATTERNS = frozenset(
    {
        "single_color_sale_unit",
        "explicit_single_color_sale_unit",
    }
)


def live_variant_axis_projection(
    *,
    attribute: str,
    values: Sequence[Any],
    source_axis_contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Project one live ERPNext variant axis into the product-page contract."""

    clean_attribute = _clean(attribute)
    clean_values = tuple(_clean(value) for value in values if _clean(value))
    source_axis_contract = source_axis_contract or {}
    color_axis = is_balloon_color_axis(clean_attribute)
    color_recipe = color_axis and source_color_axis_requires_recipe(
        clean_attribute,
        source_axis_contract,
    )

    if color_recipe:
        return {
            "name": clean_attribute,
            "role": "customization",
            "values": clean_values,
            "selector_type": "multi_color_recipe_builder",
            "source": "combined",
            "status": "ready",
            "allows_multiple_values": True,
            "notes": (
                "Source/ProductPatternContract marks this color axis as a multi-color recipe.",
                "ERPNext variant lookup remains a representative-price bridge, not the payload target.",
            ),
        }

    notes = ["Live ERPNext required variant axis targets selected_options."]
    if color_axis:
        notes.append(
            "Balloon-color attribute stays sale_unit because no source recipe contract marks it as customization."
        )

    return {
        "name": clean_attribute,
        "role": "sale_unit",
        "values": clean_values,
        "selector_type": _sale_unit_selector_type(clean_values),
        "source": "combined" if source_axis_contract else "erpnext_variant",
        "status": "ready",
        "allows_multiple_values": False,
        "notes": tuple(notes),
    }


def source_color_axis_requires_recipe(axis_name: str, source_axis_contract: Mapping[str, Any]) -> bool:
    """Return true only when the source contract marks a color axis as recipe customization."""

    if not is_balloon_color_axis(axis_name):
        return False
    if source_axis_is_explicit_single_color_sale_unit(source_axis_contract):
        return False
    patterns = {str(pattern) for pattern in source_axis_contract.get("patterns") or ()}
    return bool(patterns & COLOR_RECIPE_PATTERNS)


def source_axis_is_explicit_single_color_sale_unit(source_axis_contract: Mapping[str, Any]) -> bool:
    patterns = {str(pattern) for pattern in source_axis_contract.get("patterns") or ()}
    return bool(
        patterns & SINGLE_COLOR_SALE_UNIT_PATTERNS
        or _clean(source_axis_contract.get("sale_unit_mode")) == "single_color"
        or _clean(source_axis_contract.get("pricing_strategy")) == "single_color_sale_unit"
    )


def _sale_unit_selector_type(values: Sequence[str]) -> str:
    return "chip_group" if len(values) <= 8 else "single_select"


def _clean(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("name") or value.get("attribute_value") or value.get("value")
    return " ".join(str(value or "").strip().split())
