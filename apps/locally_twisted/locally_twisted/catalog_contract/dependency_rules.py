"""Executable option dependency helpers for product-page contracts."""
from __future__ import annotations

from collections.abc import Mapping

from locally_twisted.catalog_contract.models import OptionDependencyMatrixContract


def available_options_for_selection(
    matrix: OptionDependencyMatrixContract,
    selection: Mapping[str, str] | None,
) -> dict[str, tuple[str, ...]]:
    """Return still-available axis values for a partial option selection.

    Raises ValueError when a selection names an unknown axis or cannot match any
    source-backed combination. This keeps dependency gaps loud instead of
    silently showing impossible choices.
    """
    axes = tuple(matrix.axes or ())
    selected = _clean_selection(selection)
    unknown = sorted(axis for axis in selected if axis not in axes)
    if unknown:
        raise ValueError(f"Unknown dependency axis: {', '.join(unknown)}")

    combinations = tuple(matrix.valid_combinations or ())
    matches = [
        combo
        for combo in combinations
        if _combo_matches_selection(combo, selected)
    ]
    if selected and not matches:
        raise ValueError("No valid option combination matches the selected product options.")

    return {
        axis: tuple(_ordered_values(axis, matches))
        for axis in axes
    }


def _clean_selection(selection: Mapping[str, str] | None) -> dict[str, str]:
    if not selection:
        return {}
    return {
        str(axis).strip(): str(value).strip()
        for axis, value in selection.items()
        if str(axis).strip() and str(value).strip()
    }


def _combo_matches_selection(combo: dict[str, str], selection: dict[str, str]) -> bool:
    return all(str(combo.get(axis) or "").strip() == value for axis, value in selection.items())


def _ordered_values(axis: str, combinations: list[dict[str, str]]) -> list[str]:
    seen = set()
    values = []
    for combo in combinations:
        value = str(combo.get(axis) or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values
