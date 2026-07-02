"""Shared rules for storefront variant choices.

ERPNext variants are required product choices. Optional companion products
should not be imported or rendered as required variant axes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


OPTIONAL_ADDON_ATTRIBUTES = frozenset(
    {
        "Add Foil Number",
    }
)

OPTIONAL_ADDON_CONTEXT_ATTRIBUTES = frozenset(
    {
        "Bouquet Size",
    }
)

BOUQUET_SIZE_LABELS = {
    "Small — 1 super shape, 2 foils, 7 latex": "Small — 1 featured foil balloon, 2 coordinating foil balloons, 7 latex balloons",
    "Medium — 2 super shapes, 4 foils, 14 latex": "Medium — 2 featured foil balloons, 4 coordinating foil balloons, 14 latex balloons",
    "Large - 3 super shapes, 5 foil 16 latex": "Large — 3 featured foil balloons, 5 coordinating foil balloons, 16 latex balloons",
}


def is_required_variant_attribute(attribute: str | None) -> bool:
    return bool(attribute) and attribute not in OPTIONAL_ADDON_ATTRIBUTES


def normalize_variant_value(attribute: str | None, value: str | None) -> str | None:
    if attribute == "Bouquet Size" and value:
        return BOUQUET_SIZE_LABELS.get(value, value)
    return value


def _should_drop_optional_addons(attribute_names: Iterable[str]) -> bool:
    names = {str(name) for name in attribute_names if name}
    return bool(names & OPTIONAL_ADDON_CONTEXT_ATTRIBUTES)


def required_variant_attribute_names(attributes: Mapping[str, Any] | Iterable[str] | None) -> list[str]:
    if not attributes:
        return []
    names = attributes.keys() if isinstance(attributes, Mapping) else attributes
    names = [str(name) for name in names if name]
    if not _should_drop_optional_addons(names):
        return names
    return [name for name in names if is_required_variant_attribute(name)]


def project_required_variant_combo(combo: Mapping[str, str] | None) -> dict[str, str]:
    if not combo:
        return {}
    drop_optional_addons = _should_drop_optional_addons(combo.keys())
    return {
        str(attribute): normalize_variant_value(str(attribute), value)
        for attribute, value in combo.items()
        if not drop_optional_addons or is_required_variant_attribute(str(attribute))
    }


def dedupe_required_variant_rows(rows: Iterable[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    """Project scraped catalog_data rows to required attrs and remove add-on duplicates."""
    deduped: dict[tuple[tuple[str, str], ...], dict[str, Any]] = {}
    for row in rows or []:
        combo = project_required_variant_combo(row.get("combo") if isinstance(row, Mapping) else None)
        if not combo:
            continue
        key = tuple(sorted(combo.items()))
        if key in deduped:
            continue
        projected = dict(row)
        projected["combo"] = combo
        deduped[key] = projected
    return list(deduped.values())
