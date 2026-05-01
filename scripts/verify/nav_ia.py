"""Verify the Locally Twisted primary nav information architecture.

This is intentionally a source-level check: Frappe template rendering is
covered separately by route screenshots/cache smoke tests, while this catches
the regression where the template order itself drifts.
"""
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NAVBAR = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html"
CONTEXT = ROOT / "apps/locally_twisted/locally_twisted/navbar_context.py"


def _line_index(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx == -1:
        raise AssertionError(f"Missing expected nav text: {needle}")
    return idx


def test_desktop_nav_order(navbar: str) -> None:
    expected = [
        "Shop Balloon Decor",
        "Plan by Occasion",
        "Balloon Twisting &amp; Face Painting",
        "/faq",
        "/blog",
    ]
    positions = [_line_index(navbar, needle) for needle in expected]
    if positions != sorted(positions):
        raise AssertionError(
            "Primary nav order must be Shop Balloon Decor, Plan by Occasion, "
            "Balloon Twisting & Face Painting, FAQ, Blog"
        )


def test_no_duplicate_contact_in_mobile_drawer(navbar: str) -> None:
    mobile_drawer = navbar.split('<aside class="lt-header__mobile-nav-collapse"', 1)[1]
    if 'href="/contact"' in mobile_drawer or "Contact Us" in mobile_drawer:
        raise AssertionError("Mobile drawer must not duplicate the top-row Contact Us CTA")


def test_nav_does_not_link_to_retired_book_route(navbar: str, context: str) -> None:
    combined = f"{navbar}\n{context}"
    if 'href="/book"' in combined or '"route": "book?' in combined:
        raise AssertionError("Navigation must use /contact, not retired /book links")


def test_context_exports_real_menu_groups(context: str) -> None:
    for name in ("mega_shop_balloon_decor", "mega_plan_by_occasion"):
        if f'context["{name}"]' not in context:
            raise AssertionError(f"Missing context export: {name}")
    for legacy in ("mega_special_occasions", "mega_holidays_seasons"):
        if re.search(rf'context\["{legacy}"\]\s*=', context):
            raise AssertionError(f"Legacy menu context should not drive the navbar: {legacy}")


def test_occasion_menu_links_to_product_discovery(context: str) -> None:
    contact_occasion_links = re.findall(r'"route":\s*"contact\?occasion=', context)
    if contact_occasion_links:
        raise AssertionError("Plan by Occasion must route to product discovery, not contact form shortcuts")

    expected_product_routes = (
        "shop-items/deliveries/birthday-deliveries",
        "shop-items/garlands/baby-shower-garland",
        "shop-items/grab-go/graduation-grab-n-go",
        "shop-items/get-well-bouquets",
        "shop-items/bouquets/large-head-missionary",
    )
    for route in expected_product_routes:
        if route not in context:
            raise AssertionError(f"Missing product-backed occasion route: {route}")


def main() -> None:
    navbar = NAVBAR.read_text(encoding="utf-8")
    context = CONTEXT.read_text(encoding="utf-8")
    test_desktop_nav_order(navbar)
    test_no_duplicate_contact_in_mobile_drawer(navbar)
    test_nav_does_not_link_to_retired_book_route(navbar, context)
    test_context_exports_real_menu_groups(context)
    test_occasion_menu_links_to_product_discovery(context)
    print("Nav IA checks passed")


if __name__ == "__main__":
    main()
