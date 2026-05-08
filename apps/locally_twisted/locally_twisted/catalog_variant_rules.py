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


def is_required_variant_attribute(attribute: str | None) -> bool:
    return bool(attribute) and attribute not in OPTIONAL_ADDON_ATTRIBUTES


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
        str(attribute): value
        for attribute, value in combo.items()
        if not drop_optional_addons or is_required_variant_attribute(str(attribute))
    }


def dedupe_required_variant_rows(rows: Iterable[Mapping[str, Any]] | None) -> list[dict[str, Any]]:
    """Project scraped Odoo rows to required attrs and remove add-on duplicates."""
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
