"""Rules for separating required variant axes from optional add-ons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

AxisClassification = Literal["required", "optional_addon", "needs_review"]


@dataclass(frozen=True)
class ClassifiedAxis:
    status: AxisClassification
    note: str = ""


# Confirmed directly by GL on 2026-05-08.
CONFIRMED_ADD_ONS = {
    "Add Foil Number": ClassifiedAxis(
        "optional_addon",
        "Foil numbers are optional upgrades, priced at $12 each, not required variant axes.",
    ),
}

# Odoo axes that smell like add-ons but need product-family review before import.
REVIEW_ADD_ONS = {
    "Add ons": "Potential optional add-ons; needs product-family mapping.",
    "Plush add ons": "Potential optional plush upgrades; needs product-family mapping.",
    "Orbz toppers": "Potential optional topper upgrades; needs product-family mapping.",
    "Add Bouquet": "May be optional companion bouquet on deliveries; needs GL/product-family confirmation.",
}


def classify_axis(axis_name: str | None) -> ClassifiedAxis:
    name = str(axis_name or "").strip()
    if name in CONFIRMED_ADD_ONS:
        return CONFIRMED_ADD_ONS[name]
    if name in REVIEW_ADD_ONS:
        return ClassifiedAxis("needs_review", REVIEW_ADD_ONS[name])
    return ClassifiedAxis("required", "Required product configuration axis unless later reclassified.")


def known_add_on_contracts_for_axis(axis_name: str) -> list[dict]:
    """Return initial add-on contracts for confirmed source axes.

    This is deliberately conservative: only GL-confirmed add-ons become real
    add-on contracts automatically. Ambiguous axes stay review warnings.
    """
    if axis_name == "Add Foil Number":
        return [
            {
                "key": "foil_number",
                "label": "Foil number",
                "pricing_rule": "$12 each selected number",
                "unit_price": 12.0,
                "source_attribute": axis_name,
                "status": "confirmed",
                "note": "Colors coordinate with the selected theme/artist design.",
            }
        ]
    return []
