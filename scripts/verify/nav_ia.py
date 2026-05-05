"""Verify the Locally Twisted primary nav information architecture.

This is intentionally a source-level check: Frappe template rendering is
covered separately by route screenshots/cache smoke tests, while this catches
the regression where the template order itself drifts.
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NAVBAR = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html"
FOOTER = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html"


def _line_index(text: str, needle: str) -> int:
    idx = text.find(needle)
    if idx == -1:
        raise AssertionError(f"Missing expected nav text: {needle}")
    return idx


def test_desktop_nav_order(navbar: str) -> None:
    nav_start = _line_index(navbar, '<nav class="lt-mega-nav"')
    nav_end = _line_index(navbar[nav_start:], '</nav>') + nav_start
    primary_nav = navbar[nav_start:nav_end]
    expected = [
        "data-lt-megamenu-trigger=\"lt-mega-events\"",
        "Event Balloons",
        "/portfolio",
        "/process",
        "data-lt-megamenu-trigger=\"lt-mega-products\"",
        "Ready-to-Order",
        "/faq",
    ]
    positions = [_line_index(primary_nav, needle) for needle in expected]
    if positions != sorted(positions):
        raise AssertionError(
            "Primary nav order must be Event Balloons, Portfolio, Process, "
            "Ready-to-Order, FAQ, with deliberate mega-menu triggers"
        )


def test_quote_cta_is_contact(navbar: str) -> None:
    if 'href="/contact"' not in navbar or "Free Event Quote" not in navbar:
        raise AssertionError("Header must keep Free Event Quote pointed at /contact")


def test_nav_does_not_link_to_retired_book_route(navbar: str) -> None:
    if 'href="/book"' in navbar:
        raise AssertionError("Navigation must use /contact, not retired /book links")


def test_nav_does_not_link_to_retired_category_index(navbar: str, footer: str) -> None:
    combined = f"{navbar}\n{footer}"
    if "shop-by-category" in combined:
        raise AssertionError("Header/footer navigation must use /shop, not retired /shop-by-category links")


def test_mega_menu_contract(navbar: str) -> None:
    required = (
        'src="/assets/locally_twisted/icons/lt-logo.png"',
        'class="lt-mega-brand__logo"',
        'id="lt-mega-events"',
        'id="lt-mega-products"',
        'class="lt-megamenu__panel"',
        'href="/event-balloons"',
        '"route": "shop-items/arches"',
        '"route": "shop-items/garlands"',
        '"route": "shop-items/columns"',
        '"route": "shop-items/bouquets"',
        'id="lt-mobile-toggle"',
        'id="lt-mobile-nav"',
        'data-lt-drawer-accordion-trigger="lt-mobile-products"',
        'aria-expanded="false"',
        "hidden",
    )
    for needle in required:
        if needle not in navbar:
            raise AssertionError(f"Missing deliberate mega-menu contract markup: {needle}")


def test_no_retired_nav_contract(navbar: str) -> None:
    retired = (
        "Plan by Occasion",
        "/blog",
        "lt-shop-trigger",
        "lt-shop-mega",
        "lt-mobile-drawer",
    )
    for label in retired:
        if label in navbar:
            raise AssertionError(f"Retired nav contract still appears in the header: {label}")


def test_supporting_assets_exist() -> None:
    expected = (
        ROOT / "apps/locally_twisted/locally_twisted/navbar_context.py",
        ROOT / "apps/locally_twisted/locally_twisted/public/js/lt-megamenu.js",
        ROOT / "apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css",
        ROOT / "apps/locally_twisted/locally_twisted/public/icons/lt-logo.png",
    )
    for path in expected:
        if not path.exists():
            raise AssertionError(f"Missing nav support asset: {path.relative_to(ROOT)}")


def main() -> None:
    navbar = NAVBAR.read_text(encoding="utf-8")
    footer = FOOTER.read_text(encoding="utf-8")
    test_desktop_nav_order(navbar)
    test_quote_cta_is_contact(navbar)
    test_nav_does_not_link_to_retired_book_route(navbar)
    test_nav_does_not_link_to_retired_category_index(navbar, footer)
    test_mega_menu_contract(navbar)
    test_no_retired_nav_contract(navbar)
    test_supporting_assets_exist()
    print("Nav IA checks passed")


if __name__ == "__main__":
    main()
