"""School, seasonal, and quote-request color preset rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


COLLEGE_COLOR_PRESET_ATTRIBUTE = "College Color Preset"


@dataclass(frozen=True)
class ColorPreset:
    key: str
    label: str
    abbr: str
    category: str
    organization: str
    brand_hex_values: tuple[str, ...]
    balloon_color_values: tuple[str, ...]
    source_note: str


COLLEGE_COLOR_PRESETS: tuple[ColorPreset, ...] = (
    ColorPreset(
        key="weber_state",
        label="Weber State Purple and White",
        abbr="WSU",
        category="college",
        organization="Weber State University",
        brand_hex_values=("#4B2682", "#FFFFFF"),
        balloon_color_values=("Violet", "White"),
        source_note="Weber State brand color reference verified 2026-05-18.",
    ),
    ColorPreset(
        key="university_of_utah",
        label="University of Utah Red, Black, and White",
        abbr="UTU",
        category="college",
        organization="University of Utah",
        brand_hex_values=("#CC0000", "#000000", "#FFFFFF"),
        balloon_color_values=("Red", "black", "White"),
        source_note="University of Utah brand color reference verified 2026-05-18.",
    ),
    ColorPreset(
        key="byu",
        label="BYU Blue and White",
        abbr="BYU",
        category="college",
        organization="Brigham Young University",
        brand_hex_values=("#002E5D", "#FFFFFF"),
        balloon_color_values=("Royal Blue", "White"),
        source_note="BYU brand color reference verified 2026-05-18.",
    ),
    ColorPreset(
        key="utah_state",
        label="Utah State Aggie Blue and White",
        abbr="USU",
        category="college",
        organization="Utah State University",
        brand_hex_values=("#0F2439", "#FFFFFF"),
        balloon_color_values=("Blue Slate", "White"),
        source_note="Utah State web identity reference verified 2026-05-18.",
    ),
)

COLLEGE_PRESET_LABELS: tuple[str, ...] = tuple(preset.label for preset in COLLEGE_COLOR_PRESETS)

GRADUATION_PRESET_CHECKOUT_PRODUCTS = frozenset(
    {
        "graduation-grab-n-go",
        "6-graduation-stands",
    }
)

QUOTE_REQUEST_COLOR_PRODUCTS = frozenset(
    {
        "7-butterfly-column",
        "7-epic-column",
        "baby-shower-combination-photo-opt",
        "baby-shower-garland",
        "balloon-drop",
        "classic-arch",
        "classic-column",
        "classic-organic-arch",
        "classic-organic-balloon-garland",
        "classic-organic-columns",
        "classic-organic-for-easel",
        "halloween-arch",
        "logo-3-layered-bouquet",
        "number-balloon-columns",
        "organic-grab-n-go",
        "pemium-organic-column",
        "premium-organic-arch",
        "premium-organic-garland",
        "sleepy-baby-column",
    }
)

SEASONAL_BABY_QUOTE_PRESET_PRODUCTS = frozenset(
    {
        "baby-shower-combination-photo-opt",
        "baby-shower-garland",
        "halloween-arch",
        "sleepy-baby-column",
    }
)

SCHOOL_CORPORATE_QUOTE_PRODUCTS = QUOTE_REQUEST_COLOR_PRODUCTS - SEASONAL_BABY_QUOTE_PRESET_PRODUCTS


def college_preset_by_label(label: str | None) -> ColorPreset | None:
    clean = " ".join(str(label or "").split())
    for preset in COLLEGE_COLOR_PRESETS:
        if preset.label == clean:
            return preset
    return None


def college_preset_values() -> list[dict[str, Any]]:
    return [
        {
            "key": preset.key,
            "label": preset.label,
            "abbr": preset.abbr,
            "category": preset.category,
            "organization": preset.organization,
            "brand_hex_values": list(preset.brand_hex_values),
            "balloon_color_values": list(preset.balloon_color_values),
            "source_note": preset.source_note,
        }
        for preset in COLLEGE_COLOR_PRESETS
    ]


def is_quote_request_color_product(item_code: str | None) -> bool:
    return str(item_code or "").strip() in QUOTE_REQUEST_COLOR_PRODUCTS


def is_graduation_preset_checkout_product(item_code: str | None) -> bool:
    return str(item_code or "").strip() in GRADUATION_PRESET_CHECKOUT_PRODUCTS
