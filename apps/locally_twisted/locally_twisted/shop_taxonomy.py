"""Approved shop taxonomy for public product grouping."""
from __future__ import annotations

from dataclasses import dataclass

import frappe


@dataclass(frozen=True)
class CategorySpec:
    name: str
    parent: str
    route: str
    weightage: int
    show_in_website: int
    is_group: int = 0
    icon: str = "balloon-pair"
    summary: str = "Browse ready-to-order balloon decor by category."


SHOP_ROOT = "Shop Items"
OCCASION_ROOT = "Shop Occasions"

PRIMARY_CATEGORY_SPECS: tuple[CategorySpec, ...] = (
    CategorySpec(
        name="Arches",
        parent=SHOP_ROOT,
        route="shop-items/arches",
        weightage=10,
        show_in_website=1,
        icon="balloon-arch",
        summary="Entry moments, photo frames, and room-defining balloon statements.",
    ),
    CategorySpec(
        name="Balloon Drops",
        parent=SHOP_ROOT,
        route="shop-items/balloon-drops",
        weightage=20,
        show_in_website=1,
        icon="event-stage",
        summary="Ceiling drops and reveal moments for dances, parties, and big announcements.",
    ),
    CategorySpec(
        name="Bouquets",
        parent=SHOP_ROOT,
        route="shop-items/bouquets",
        weightage=30,
        show_in_website=1,
        icon="balloon-bouquet",
        summary="Themed balloon bundles for birthdays, teams, holidays, and quick gifts.",
    ),
    CategorySpec(
        name="Columns",
        parent=SHOP_ROOT,
        route="shop-items/columns",
        weightage=40,
        show_in_website=1,
        icon="balloon-column",
        summary="Freestanding color and height for doors, stages, and focal points.",
    ),
    CategorySpec(
        name="Garlands",
        parent=SHOP_ROOT,
        route="shop-items/garlands",
        weightage=50,
        show_in_website=1,
        icon="organic-garland",
        summary="Organic balloon runs for backdrops, mantels, entrances, and install moments.",
    ),
    CategorySpec(
        name="Photo Ops & Backdrops",
        parent=SHOP_ROOT,
        route="shop-items/photo-ops-backdrops",
        weightage=60,
        show_in_website=1,
        icon="event-stage",
        summary="Photo-ready frames, backdrop moments, and display pieces.",
    ),
    CategorySpec(
        name="Stands & Easels",
        parent=SHOP_ROOT,
        route="shop-items/stands-easels",
        weightage=70,
        show_in_website=1,
        icon="event-stage",
        summary="Freestanding display pieces for signs, graduations, entrances, and school moments.",
    ),
    CategorySpec(
        name="Table Decor",
        parent=SHOP_ROOT,
        route="shop-items/table-decor",
        weightage=80,
        show_in_website=1,
        icon="balloon-cluster",
        summary="Centerpieces and smaller pieces for tables, counters, and welcome areas.",
    ),
)

SECONDARY_CATEGORY_SPECS: tuple[CategorySpec, ...] = (
    CategorySpec("Any Occasion", OCCASION_ROOT, "shop-occasions/any-occasion", 10, 0),
    CategorySpec("Birthday", OCCASION_ROOT, "shop-occasions/birthday", 20, 0),
    CategorySpec("Holiday", OCCASION_ROOT, "shop-occasions/holiday", 30, 0),
    CategorySpec("Graduation", OCCASION_ROOT, "shop-occasions/graduation", 40, 0),
    CategorySpec("Baby Shower", OCCASION_ROOT, "shop-occasions/baby-shower", 50, 0),
    CategorySpec("Sports", OCCASION_ROOT, "shop-occasions/sports", 60, 0),
    CategorySpec("Get Well", OCCASION_ROOT, "shop-occasions/get-well", 70, 0),
    CategorySpec("Religious", OCCASION_ROOT, "shop-occasions/religious", 80, 0),
    CategorySpec("Corporate", OCCASION_ROOT, "shop-occasions/corporate", 90, 0),
)

LEGACY_PRIMARY_GROUPS: tuple[str, ...] = (
    "Deliveries",
    "Drops",
    "Get-Well Bouquets",
    "Grab & Go",
    "Seasonal & Specialty",
)

LEGACY_CATEGORY_ROUTES: dict[str, str] = {
    "Deliveries": "shop-items/deliveries",
    "Drops": "shop-items/drops",
    "Get-Well Bouquets": "shop-items/get-well-bouquets",
    "Grab & Go": "shop-items/grab-go",
    "Seasonal & Specialty": "shop-items/seasonal-specialty",
}

INVALID_VISIBLE_CATEGORY_TERMS: tuple[str, ...] = (
    *LEGACY_PRIMARY_GROUPS,
    "Latex-free",
    "Latex Free",
    "Delivery",
    "Pickup",
    "Easter",
    "Halloween",
    "Mother's Day",
    "Pride",
)

PRODUCT_TAXONOMY: dict[str, dict[str, str]] = {
    "6-color-rainbow-arch": {"primary": "Arches", "secondary": "Any Occasion"},
    "6-graduation-stands": {"primary": "Stands & Easels", "secondary": "Graduation"},
    "7-butterfly-column": {"primary": "Columns", "secondary": "Any Occasion"},
    "7-epic-column": {"primary": "Columns", "secondary": "Any Occasion"},
    "baby-shower-combination-photo-opt": {"primary": "Photo Ops & Backdrops", "secondary": "Baby Shower"},
    "baby-shower-garland": {"primary": "Garlands", "secondary": "Baby Shower"},
    "baby-table-decor": {"primary": "Table Decor", "secondary": "Baby Shower"},
    "balloon-drop": {"primary": "Balloon Drops", "secondary": "Any Occasion"},
    "bandage-get-well-bouquet-latex-free": {"primary": "Bouquets", "secondary": "Get Well"},
    "basketball-arch": {"primary": "Arches", "secondary": "Sports"},
    "birthday-deliveries": {"primary": "Bouquets", "secondary": "Birthday"},
    "butterfly-get-well-bouquet-latex-free": {"primary": "Bouquets", "secondary": "Get Well"},
    "classic-arch": {"primary": "Arches", "secondary": "Any Occasion"},
    "classic-column": {"primary": "Columns", "secondary": "Any Occasion"},
    "classic-organic-arch": {"primary": "Arches", "secondary": "Any Occasion"},
    "classic-organic-balloon-garland": {"primary": "Garlands", "secondary": "Any Occasion"},
    "classic-organic-columns": {"primary": "Columns", "secondary": "Any Occasion"},
    "classic-organic-for-easel": {"primary": "Stands & Easels", "secondary": "Any Occasion"},
    "easter-balloon-arch-bunny-ear": {"primary": "Arches", "secondary": "Holiday"},
    "easter-balloon-cups": {"primary": "Table Decor", "secondary": "Holiday"},
    "elsa-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "encanto-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "flamingo-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "football-bouquet": {"primary": "Bouquets", "secondary": "Sports"},
    "graduation-grab-n-go": {"primary": "Garlands", "secondary": "Graduation"},
    "halloween-arch": {"primary": "Arches", "secondary": "Holiday"},
    "holy-cow-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "large-head-missionary": {"primary": "Bouquets", "secondary": "Religious"},
    "logo-3-layered-bouquet": {"primary": "Bouquets", "secondary": "Corporate"},
    "marble-table-decor": {"primary": "Table Decor", "secondary": "Any Occasion"},
    "mickey-mouse-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "minion-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "mothers-day-front-yard-7-column": {"primary": "Columns", "secondary": "Holiday"},
    "number-balloon-columns": {"primary": "Columns", "secondary": "Birthday"},
    "organic-grab-n-go": {"primary": "Garlands", "secondary": "Any Occasion"},
    "over-the-hill-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "paw-patrol-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "pemium-organic-column": {"primary": "Columns", "secondary": "Any Occasion"},
    "premium-organic-arch": {"primary": "Arches", "secondary": "Any Occasion"},
    "premium-organic-garland": {"primary": "Garlands", "secondary": "Any Occasion"},
    "shooting-star-get-well-bouquet-latex-free": {"primary": "Bouquets", "secondary": "Get Well"},
    "sleepy-baby-column": {"primary": "Columns", "secondary": "Baby Shower"},
    "soccer-bouquet": {"primary": "Bouquets", "secondary": "Sports"},
    "space-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "star-column": {"primary": "Columns", "secondary": "Any Occasion"},
    "stitch-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
    "unicorn-bouquet": {"primary": "Bouquets", "secondary": "Birthday"},
}

RETIRED_PRODUCT_CODES = (
    "large-garland",
    "mothers-day-bouquet",
    "large-organic-column",
    "pride-progress-rainbow-balloon-arch",
)

PRIMARY_CATEGORY_NAMES = tuple(spec.name for spec in PRIMARY_CATEGORY_SPECS)
SECONDARY_CATEGORY_NAMES = tuple(spec.name for spec in SECONDARY_CATEGORY_SPECS)
PRIMARY_CATEGORY_BY_NAME = {spec.name: spec for spec in PRIMARY_CATEGORY_SPECS}
SECONDARY_CATEGORY_BY_NAME = {spec.name: spec for spec in SECONDARY_CATEGORY_SPECS}
CATEGORY_ICON_BY_NAME = {spec.name: spec.icon for spec in PRIMARY_CATEGORY_SPECS}
CATEGORY_SUMMARY_BY_NAME = {spec.name: spec.summary for spec in PRIMARY_CATEGORY_SPECS}


def product_route(item_code: str) -> str:
    taxonomy = PRODUCT_TAXONOMY[item_code]
    primary = taxonomy["primary"]
    return f"{PRIMARY_CATEGORY_BY_NAME[primary].route}/{item_code}"


def category_slug(category: str) -> str:
    return frappe.scrub(category).replace("_", "-")
