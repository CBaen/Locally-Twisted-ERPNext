"""Balloon color grouping and metadata rules for product-page contracts."""

from __future__ import annotations

from dataclasses import dataclass

COLOR_STYLE_ORDER = (
    "Reflex",
    "Dusk",
    "Pastels",
    "Blues + Teals",
    "Greens",
    "Pinks + Purples",
    "Neutrals",
    "Brights",
    "Review Needed",
)


@dataclass(frozen=True)
class ClassifiedColor:
    name: str
    group: str
    vendor_name: str
    hex_value: str = ""
    swatch_url: str = ""
    status: str = "needs_color_asset_review"


def _color_key(name: str) -> str:
    return " ".join(str(name or "").replace("-", " ").strip().lower().split())


COLOR_NAME_ALIASES = {
    "blue slate": "Blue Slate",
    "reflex champage": "Reflex Champagne",
    "smoke grey": "Smoke Grey",
}


def canonical_color_name(name: str) -> str:
    clean = " ".join(str(name or "").strip().split())
    return COLOR_NAME_ALIASES.get(_color_key(clean), clean)


# Approximate values sampled visually from the provided Qualatex guide image.
# These are customer-facing aids, not official vendor color science values.
QUALATEX_GUIDE_APPROX_HEX = {
    "white": "#f3f2e9",
    "black": "#111111",
    "red": "#e73543",
    "raspberry": "#d64b68",
    "fuchsia": "#cf5fa0",
    "bubble gum": "#e7a6cb",
    "orange": "#ef7b32",
    "golden rod": "#f3d35c",
    "yellow": "#f3d94f",
    "forest": "#2f7c4d",
    "wintergreen": "#66bc9a",
    "lime": "#a0cf6a",
    "navy": "#142b55",
    "naval": "#2b4668",
    "royal blue": "#2562a8",
    "light blue": "#53b7e4",
    "caribbean": "#75c9c7",
    "teal": "#5ebdb8",
    "violet": "#55318b",
    "orchid": "#9a2b8f",
    "lilac": "#a699c8",
    "chocolate": "#3b241e",
    "coffee": "#95633e",
    "latte": "#c7a46a",
    "blush": "#f2d8ad",
    "ivory": "#f7f4c9",
    "grey": "#b7bcc0",
    "gray": "#b7bcc0",
    "grey smoke": "#8d9290",
    "gray smoke": "#8d9290",
    "sangria": "#934058",
    "samba": "#8f3f5f",
    "cranberry": "#ac4d4d",
    "rosewood": "#c68991",
    "canyon rose": "#d9b0c9",
    "cameo": "#ead5d4",
    "aloha": "#eb8d9e",
    "coral": "#e85b55",
    "burnt orange": "#c97857",
    "mustard": "#e5bd2d",
    "cocoa": "#92756e",
    "sand": "#cfc1ba",
    "stone": "#d7d5cd",
    "willow": "#8aa194",
    "eucalyptus": "#99aa89",
    "empower mint": "#c3d7cc",
    "empowermint": "#c3d7cc",
    "blue slate": "#93b7c5",
    "seaglass": "#9ad8e7",
    "fog": "#d2d9dc",
    "neon green": "#a9d64c",
    "neon yellow": "#e9e84e",
    "neon blue": "#5aa7df",
    "neon orange": "#e88272",
    "neon pink": "#d85b93",
    "dusk blue": "#7496a0",
    "dusk green": "#829386",
    "dusk cream": "#d7d4cf",
    "dusk lavender": "#ad8eb4",
    "dusk rose": "#cfc4c4",
    "pastel pink": "#efd9df",
    "pastel yellow": "#f7f2c4",
    "pastel green": "#cddfd5",
    "pastel blue": "#bee2eb",
    "pastel lilac": "#d8d2e3",
    "pastel melon": "#f2beb1",
}


def approximate_hex_for_color(name: str) -> str:
    """Approximate Qualatex-like swatch hex for customer-facing color metadata."""
    key = _color_key(canonical_color_name(name))
    if key in QUALATEX_GUIDE_APPROX_HEX:
        return QUALATEX_GUIDE_APPROX_HEX[key]

    rules = [
        ("champagne", "#b8a08f"), ("truffle", "#5b3f3c"),
        ("cream", "#eee8dc"), ("green tea", "#9bcbb3"),
        ("reflex blue", "#1f6f8d"), ("periwinkle", "#8ea4dc"),
        ("robin", "#86c5d8"), ("deep teal", "#006f73"),
        ("shamrock", "#1f9d55"), ("honey", "#d7a12f"),
        ("brown", "#7a5237"), ("clear", "#dcecf2"),
    ]
    for token, value in rules:
        if token in key:
            return value
    return ""


def classify_color_name(name: str) -> ClassifiedColor:
    clean = canonical_color_name(name)
    lower = clean.lower()

    if lower.startswith("reflex"):
        return ClassifiedColor(clean, "Reflex", clean, approximate_hex_for_color(clean), status="approximate_review")
    if lower.startswith("dusk"):
        return ClassifiedColor(clean, "Dusk", clean, approximate_hex_for_color(clean), status="approximate_review")
    if lower.startswith("pastel"):
        return ClassifiedColor(clean, "Pastels", clean, approximate_hex_for_color(clean), status="approximate_review")

    if any(token in lower for token in ["blue", "teal", "periwinkle", "robin"]):
        return ClassifiedColor(clean, "Blues + Teals", clean, approximate_hex_for_color(clean), status="approximate_review")
    if any(token in lower for token in ["green", "eucalyptus", "forest", "shamrock", "wintergreen", "lime", "empowermint"]):
        return ClassifiedColor(clean, "Greens", clean, approximate_hex_for_color(clean), status="approximate_review")
    if any(token in lower for token in ["pink", "raspberry", "fuchsia", "bubble gum", "violet", "orchid", "lilac", "blush"]):
        return ClassifiedColor(clean, "Pinks + Purples", clean, approximate_hex_for_color(clean), status="approximate_review")
    if any(token in lower for token in ["white", "black", "grey", "gray", "smoke", "chocolate", "brown", "latte", "clear"]):
        return ClassifiedColor(clean, "Neutrals", clean, approximate_hex_for_color(clean), status="approximate_review")
    if any(token in lower for token in ["red", "orange", "yellow", "honey"]):
        return ClassifiedColor(clean, "Brights", clean, approximate_hex_for_color(clean), status="approximate_review")

    return ClassifiedColor(clean, "Review Needed", clean, approximate_hex_for_color(clean), status="approximate_review")


def grouped_colors(values: list[str] | tuple[str, ...]) -> list[dict]:
    buckets: dict[str, list[dict]] = {group: [] for group in COLOR_STYLE_ORDER}
    for value in values:
        color = classify_color_name(value)
        buckets.setdefault(color.group, []).append(
            {
                "name": color.name,
                "vendor_name": color.vendor_name,
                "hex_value": color.hex_value,
                "swatch_url": color.swatch_url,
                "status": color.status,
            }
        )

    result = []
    for group in COLOR_STYLE_ORDER:
        options = buckets.get(group) or []
        if options:
            result.append({"group": group, "options": options})
    return result


def is_balloon_color_axis(axis_name: str | None) -> bool:
    return str(axis_name or "").strip().lower() in {"latex colors", "color palette", "number colors", "baby color"}
