"""Verify the Locally Twisted public navigation and key IA links.

This is intentionally a source-level check: Frappe template rendering is
covered separately by route screenshots/cache smoke tests, while this catches
the regression where the template order itself drifts or a homepage CTA points
at a route that is no longer part of the launch surface.
"""
from __future__ import annotations

from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
NAVBAR = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html"
FOOTER = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html"
HOME = ROOT / "apps/locally_twisted/locally_twisted/www/home.html"
SEARCH_ROUTE = ROOT / "apps/locally_twisted/locally_twisted/www/search.py"


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
        'lt-mega-nav__link--quote" href="/contact">Free Event Quote',
        "/portfolio",
        "/faq",
    ]
    positions = [_line_index(primary_nav, needle) for needle in expected]
    if positions != sorted(positions):
        raise AssertionError(
            "Primary nav order must be Event Balloons, Free Event Quote, "
            "Portfolio, FAQ, with deliberate event mega-menu trigger"
        )
    if "lt-mega-products" in primary_nav or "Ready-to-Order" in primary_nav:
        raise AssertionError("Primary nav must not expose ecommerce while the shop is paused")


def test_quote_cta_is_contact(navbar: str) -> None:
    required = (
        'lt-mega-nav__link--quote" href="/contact">Free Event Quote',
        'class="lt-mega-header__cta" href="/contact">Contact Us</a>',
        'class="lt-mega-drawer__single lt-mega-drawer__single--quote" href="/contact">Free Event Quote</a>',
        'class="lt-mega-drawer__cta" href="/contact">Contact Us</a>',
    )
    for needle in required:
        if needle not in navbar:
            raise AssertionError(f"Header/menu must keep Contact Us and Free Event Quote pointed at /contact: {needle}")
    if 'class="lt-mega-header__cta" href="/contact">Free Event Quote</a>' in navbar:
        raise AssertionError("Header CTA label must be Contact Us, not Free Event Quote")


def test_nav_does_not_link_to_retired_book_route(navbar: str) -> None:
    if 'href="/book"' in navbar:
        raise AssertionError("Navigation must use /contact, not retired /book links")


def test_nav_does_not_link_to_retired_category_index(navbar: str, footer: str) -> None:
    combined = f"{navbar}\n{footer}"
    if "shop-by-category" in combined:
        raise AssertionError("Header/footer navigation must use /shop, not retired /shop-by-category links")


def test_nav_does_not_expose_process_page(navbar: str, footer: str) -> None:
    combined = f"{navbar}\n{footer}"
    retired = (
        'href="/process"',
        '"route": "process"',
        "How the Process Works",
        "How It Works",
        ">Process<",
    )
    for needle in retired:
        if needle in combined:
            raise AssertionError(f"Public nav/footer must not expose the unapproved Process page: {needle}")


def test_search_is_overlay_not_public_page(navbar: str, footer: str, search_route: str) -> None:
    combined = f"{navbar}\n{footer}"
    if 'href="/search"' in combined:
        raise AssertionError("Public navigation must not link to Frappe's bundled /search page")
    required = (
        "data-lt-search-toggle",
        'id="lt-site-search-panel"',
        'action="/contact"',
        'name="q"',
    )
    for needle in required:
        if needle not in navbar:
            raise AssertionError(f"Header search overlay contract is missing: {needle}")
    if "lt-mega-header__mobile-search" in navbar:
        raise AssertionError("Mobile search must live in the drawer, not the crowded header action row")
    if "/shop-items" in navbar or "data-lt-search-product-entry" in navbar:
        raise AssertionError("Search overlay must not expose product links while ecommerce is paused")
    if "context.http_status_code = 404" not in search_route or "no_cache = 1" not in search_route:
        raise AssertionError("/search must override Frappe's bundled page with a no-cache 404")


def test_mega_menu_contract(navbar: str) -> None:
    required = (
        'src="/assets/locally_twisted/icons/lt-logo.png"',
        'class="lt-mega-brand__logo"',
        'aria-label="Navigation menu"',
        'id="lt-mega-events"',
        'class="lt-megamenu__panel"',
        '"route": "civic-community"',
        '"route": "corporate-events"',
        '"route": "schools-campuses"',
        '"route": "private-celebrations"',
        "Corporate Events",
        'lt-mega-nav__link--quote" href="/contact">Free Event Quote',
        'class="lt-mega-header__cta" href="/contact">Contact Us</a>',
        'id="lt-mobile-toggle"',
        'id="lt-mobile-nav"',
        'data-lt-search-toggle',
        'aria-expanded="false"',
        "hidden",
    )
    for needle in required:
        if needle not in navbar:
            raise AssertionError(f"Missing deliberate mega-menu contract markup: {needle}")
    retired_event_menu = (
        "Corporate Entrances",
        'class="lt-megamenu__card" href="/portfolio"',
        'class="lt-megamenu__card" href="/event-balloons"',
    )
    for needle in retired_event_menu:
        if needle in navbar:
            raise AssertionError(f"Event mega menu still exposes generic or wrong route: {needle}")


def test_mobile_nav_matches_primary_order(navbar: str) -> None:
    drawer_start = _line_index(navbar, '<aside class="lt-header__mobile-nav-collapse')
    drawer = navbar[drawer_start:]
    expected = [
        'data-lt-drawer-accordion-trigger="lt-mobile-events"',
        "Event Balloons",
        'class="lt-mega-drawer__single lt-mega-drawer__single--quote" href="/contact">Free Event Quote',
        'href="/portfolio"',
        'href="/faq"',
        'class="lt-mega-drawer__cta" href="/contact">Contact Us',
        'class="lt-mega-drawer__search"',
    ]
    positions = [_line_index(drawer, needle) for needle in expected]
    if positions != sorted(positions):
        raise AssertionError(
            "Mobile drawer must follow desktop primary order: Event Balloons, "
            "Free Event Quote, Portfolio, FAQ, Contact Us, Search"
        )
    if 'href="/search"' in drawer:
        raise AssertionError("Mobile drawer must not expose the retired /search page")
    if "lt-mobile-help" in drawer or "Help and Details" in drawer:
        raise AssertionError("Mobile drawer must not hide FAQ behind the retired Help and Details panel")
    if "lt-mobile-nav-heading" in drawer or ">Locally Twisted</span>" in drawer:
        raise AssertionError("Mobile drawer brand must show the logo only, without duplicate Locally Twisted text")
    if "Ready-to-Order" in drawer or "/shop" in drawer or "/cart" in drawer:
        raise AssertionError("Mobile drawer must not expose ecommerce while the shop is paused")


def test_ecommerce_entry_points_are_paused(navbar: str, footer: str) -> None:
    combined = f"{navbar}\n{footer}"
    forbidden = (
        "Ready-to-Order",
        'href="/shop"',
        "/shop-items",
        'href="/cart"',
        "Shopping cart",
    )
    for needle in forbidden:
        if needle in combined:
            raise AssertionError(f"Public header/footer still exposes paused ecommerce: {needle}")


def test_no_retired_nav_contract(navbar: str) -> None:
    retired = (
        "Plan by Occasion",
        "/blog",
        "lt-shop-trigger",
        "lt-shop-mega",
        "lt-mobile-drawer",
        "current ERPNext shop",
        "item-group routes",
        "lt-mega-nav__link--btfp",
        "Twisting &amp; Face Painting",
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
        ROOT / "apps/locally_twisted/locally_twisted/www/event_type_pages.py",
        ROOT / "apps/locally_twisted/locally_twisted/templates/includes/event_type_page.html",
        ROOT / "apps/locally_twisted/locally_twisted/www/civic_community.py",
        ROOT / "apps/locally_twisted/locally_twisted/www/corporate_events.py",
        ROOT / "apps/locally_twisted/locally_twisted/www/schools_campuses.py",
        ROOT / "apps/locally_twisted/locally_twisted/www/private_celebrations.py",
    )
    for path in expected:
        if not path.exists():
            raise AssertionError(f"Missing nav support asset: {path.relative_to(ROOT)}")


def test_homepage_launch_links(home: str) -> None:
    if "/customizable-event-decor" in home:
        raise AssertionError("Homepage must not link to retired /customizable-event-decor route")
    if 'href="/event-balloons"' not in home:
        raise AssertionError("Homepage Custom Event Decor heading must point at /event-balloons")
    retired_exact_counts = (
        "4.9 Google rating",
        "100+ Google reviews",
        "The full portfolio is coming",
        "design your event",
    )
    for text in retired_exact_counts:
        if text in home:
            raise AssertionError(f"Homepage still contains stale launch copy: {text}")


def main() -> None:
    parse_noop_args(__doc__)
    navbar = NAVBAR.read_text(encoding="utf-8")
    footer = FOOTER.read_text(encoding="utf-8")
    home = HOME.read_text(encoding="utf-8")
    search_route = SEARCH_ROUTE.read_text(encoding="utf-8")
    test_desktop_nav_order(navbar)
    test_quote_cta_is_contact(navbar)
    test_nav_does_not_link_to_retired_book_route(navbar)
    test_nav_does_not_link_to_retired_category_index(navbar, footer)
    test_nav_does_not_expose_process_page(navbar, footer)
    test_search_is_overlay_not_public_page(navbar, footer, search_route)
    test_mega_menu_contract(navbar)
    test_mobile_nav_matches_primary_order(navbar)
    test_ecommerce_entry_points_are_paused(navbar, footer)
    test_no_retired_nav_contract(navbar)
    test_supporting_assets_exist()
    test_homepage_launch_links(home)
    print("Nav IA checks passed")


if __name__ == "__main__":
    main()
