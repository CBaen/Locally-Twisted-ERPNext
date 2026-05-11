"""Verify the Locally Twisted public navigation and key IA links.

This is intentionally a source-level check: Frappe template rendering is
covered separately by route screenshots/cache smoke tests, while this catches
the regression where the template order itself drifts or a homepage CTA points
at a route that is no longer part of the launch surface.
"""
from __future__ import annotations

import re
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
NAVBAR = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html"
FOOTER = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html"
HOME = ROOT / "apps/locally_twisted/locally_twisted/www/home.html"
PORTFOLIO = ROOT / "apps/locally_twisted/locally_twisted/www/portfolio.html"
HOOKS = ROOT / "apps/locally_twisted/locally_twisted/hooks.py"
SEARCH_ROUTE = ROOT / "apps/locally_twisted/locally_twisted/www/search.py"
MEGA_MENU_CSS = ROOT / "apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css"
NAV_SERVICE_REMOVAL_APPROVALS = ROOT / "workstreams/nav-service-removal-approvals.md"

CANONICAL_SERVICE_NAV_LINKS = (
    {
        "label": "Twisting & Face Painting",
        "html_label": "Twisting &amp; Face Painting",
        "href": "/balloon-twisting-and-face-painting",
        "approval_marker": "APPROVED_NAV_SERVICE_REMOVAL: Twisting & Face Painting -> /balloon-twisting-and-face-painting",
    },
)


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
        "data-lt-megamenu-trigger=\"lt-mega-products\"",
        "Ready-to-Order",
        'lt-mega-nav__link--btfp" href="/balloon-twisting-and-face-painting">Twisting &amp; Face Painting',
        "/portfolio",
        "/about",
        "/faq",
    ]
    positions = [_line_index(primary_nav, needle) for needle in expected]
    if positions != sorted(positions):
        raise AssertionError(
            "Primary nav order must be Event Balloons, Ready-to-Order, Twisting & Face Painting, "
            "Portfolio, About Us, FAQ, with deliberate mega-menu triggers"
        )


def test_quote_cta_is_contact(navbar: str) -> None:
    required = (
        '<li><a href="/contact">Free Event Quote</a></li>',
        'class="lt-mega-header__cta" href="/contact">Contact Us</a>',
        'class="lt-mega-drawer__cta" href="/contact">Contact Us</a>',
    )
    for needle in required:
        if needle not in navbar:
            raise AssertionError(f"Header/menu must keep Contact Us and Free Event Quote pointed at /contact: {needle}")
    forbidden = (
        'lt-mega-nav__link--quote" href="/contact">Free Event Quote',
        'lt-mega-drawer__single--quote" href="/contact">Free Event Quote',
        '<strong>Free Event Quote</strong>',
    )
    for needle in forbidden:
        if needle in navbar:
            raise AssertionError(f"Free Event Quote belongs only in the top header banner, not in menus/search: {needle}")
    if 'class="lt-mega-header__cta" href="/contact">Free Event Quote</a>' in navbar:
        raise AssertionError("Header CTA label must be Contact Us, not Free Event Quote")


def test_top_banner_links_are_owner_approved(navbar: str) -> None:
    top_row_start = _line_index(navbar, '<div class="container lt-mega-header__top-row">')
    top_row_end = _line_index(navbar[top_row_start:], '</div>') + top_row_start
    top_row = navbar[top_row_start:top_row_end]
    top_start = _line_index(navbar, '<ul class="lt-mega-header__top-links">')
    top_end = _line_index(navbar[top_start:], '</ul>') + top_start
    top_links = navbar[top_start:top_end]
    short_notice = "SHORT NOTICE? LET US KNOW. WE CAN OFTEN HELP WITH 24 HOURS NOTICE!"
    row_required = (
        f'<a class="lt-mega-header__top-message" href="/contact">{short_notice}</a>',
    )
    mobile_required = (
        f'<a class="lt-mega-header__mobile-message" href="/contact">{short_notice}</a>',
    )
    link_required = (
        'href="/contact">Free Event Quote</a>',
    )
    forbidden = (
        'href="/shop">Ready-to-Order</a>',
        'href="/cart">Cart</a>',
        'href="/portfolio">Recent Work</a>',
        "Prepared design, clean installs, and invoiced event support across Utah.",
        "delivery-install.svg",
    )
    for needle in row_required:
        if needle not in top_row:
            raise AssertionError(f"Header top banner must keep the linked short-notice message: {needle}")
    for needle in mobile_required:
        if needle not in navbar:
            raise AssertionError(f"Mobile header must keep the linked short-notice message: {needle}")
    if "lt-mega-header__top-alert" in top_links:
        raise AssertionError("Short-notice message belongs in the old proof slot, not inside the utility links")
    for needle in link_required:
        if needle not in top_links:
            raise AssertionError(f"Header top links must keep the approved quote link: {needle}")
    for needle in forbidden:
        if needle in top_row:
            raise AssertionError(f"Header banner exposes removed proof/utility content: {needle}")


def _css_rule(css: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>[^}}]+)\}}", css)
    if not match:
        raise AssertionError(f"Missing expected CSS rule: {selector}")
    return match.group("body")


def test_top_banner_accessibility_css(css: str) -> None:
    desktop_top = _css_rule(css, ".lt-mega-header__top")
    if "background: var(--lt-mega-navy);" not in desktop_top:
        raise AssertionError("Desktop top banner must use the deep-navy authority band, not brass/yellow")
    if "color: var(--lt-mega-warm);" not in desktop_top:
        raise AssertionError("Desktop top banner text must stay warm-white on navy")

    top_message = _css_rule(css, ".lt-mega-header__top-message")
    if "color: var(--lt-mega-warm);" not in top_message:
        raise AssertionError("Desktop top banner message must stay warm-white on navy")

    top_links = _css_rule(css, ".lt-mega-header__top-links a")
    if "color: var(--lt-mega-warm);" not in top_links:
        raise AssertionError("Desktop top banner links must stay warm-white on navy")

    hover_required = (
        ".lt-mega-header__top-message:hover,\n.lt-mega-header__top-message:focus-visible,\n.lt-mega-header__top-links a:hover,\n.lt-mega-header__top-links a:focus-visible",
        ".lt-mega-header__mobile-message:hover,\n.lt-mega-header__mobile-message:focus-visible",
    )
    for selector in hover_required:
        body = _css_rule(css, selector)
        if "color: var(--lt-mega-warm);" not in body:
            raise AssertionError(f"Header banner hover/focus text must stay warm-white on navy: {selector}")
        if "text-decoration-color: var(--lt-mega-brass);" not in body:
            raise AssertionError(f"Header banner hover/focus underline should use brass as accent only: {selector}")

    mobile_top = _css_rule(css, ".lt-mega-header__mobile-top")
    if "background: var(--lt-mega-navy);" not in mobile_top:
        raise AssertionError("Mobile top banner must use the deep-navy authority band, not brass/yellow")
    if "color: var(--lt-mega-warm);" not in mobile_top:
        raise AssertionError("Mobile top banner container must set warm-white text so inherited links stay readable")
    expected_padding = "padding: 0 max(0.85rem, env(safe-area-inset-right)) 0 max(0.85rem, env(safe-area-inset-left));"
    if expected_padding not in mobile_top:
        raise AssertionError("Mobile top banner padding must map right inset to right padding and left inset to left padding")


def _active_nav_service_removal_approval_lines() -> set[str]:
    """Return approval marker lines that are active records, not examples.

    The approvals file documents the required marker inside a fenced example.
    Example text must never count as GL approval, or the guard can silently
    bypass itself.
    """
    if not NAV_SERVICE_REMOVAL_APPROVALS.exists():
        return set()

    active_lines: set[str] = set()
    in_fenced_block = False
    for raw_line in NAV_SERVICE_REMOVAL_APPROVALS.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block or not stripped:
            continue
        active_lines.add(stripped)
    return active_lines


def test_canonical_service_nav_requires_explicit_removal_approval(navbar: str, footer: str) -> None:
    """Fail loudly if an approved live service disappears from public navigation.

    Removing a major service lane is a business decision, not a copy tweak. If GL
    explicitly approves removing one, record the exact approval marker in
    workstreams/nav-service-removal-approvals.md before changing the nav.
    """
    combined = f"{navbar}\n{footer}"
    approval_lines = _active_nav_service_removal_approval_lines()
    for service in CANONICAL_SERVICE_NAV_LINKS:
        expected_href = f'href="{service["href"]}"'
        expected_html_label = service["html_label"]
        is_present = expected_href in combined and expected_html_label in combined
        if is_present:
            continue
        if service["approval_marker"] in approval_lines:
            continue
        raise AssertionError(
            "Canonical service nav item disappeared without explicit GL approval: "
            f"{service['label']} ({service['href']}). Add the service back, or record "
            f"the exact approval marker in {NAV_SERVICE_REMOVAL_APPROVALS.relative_to(ROOT)} as an active approval, not an example."
        )


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
        'action="{% if ecommerce_paused %}/contact{% else %}/shop{% endif %}"',
        'name="q"',
    )
    for needle in required:
        if needle not in navbar:
            raise AssertionError(f"Header search overlay contract is missing: {needle}")
    if "lt-mega-header__mobile-search" in navbar:
        raise AssertionError("Mobile search must live in the drawer, not the crowded header action row")
    if "data-lt-search-product-entry" not in navbar or "{% if not ecommerce_paused %}" not in navbar:
        raise AssertionError("Search overlay product links must exist only behind the open-commerce guard")
    if 'href="/about"' not in navbar or "About Us" not in navbar:
        raise AssertionError("Search overlay and public nav must expose the source-owned /about page")
    if '<strong>Free Event Quote</strong>' in navbar:
        raise AssertionError("Search quick results must not duplicate the header-banner-only Free Event Quote label")
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
        'class="lt-mega-nav__link" href="/about">About Us</a>',
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
        'data-lt-drawer-accordion-trigger="lt-mobile-products"',
        "Ready-to-Order",
        'class="lt-mega-drawer__single lt-mega-drawer__single--btfp" href="/balloon-twisting-and-face-painting">Twisting &amp; Face Painting',
        'href="/portfolio"',
        'href="/about"',
        'href="/faq"',
        'class="lt-mega-drawer__cta" href="/contact">Contact Us',
        'class="lt-mega-drawer__search"',
    ]
    positions = [_line_index(drawer, needle) for needle in expected]
    if positions != sorted(positions):
        raise AssertionError(
            "Mobile drawer must follow desktop primary order: Event Balloons, "
            "Ready-to-Order, Twisting & Face Painting, Portfolio, About Us, FAQ, Contact Us, Search"
        )
    if 'href="/search"' in drawer:
        raise AssertionError("Mobile drawer must not expose the retired /search page")
    if "lt-mobile-help" in drawer or "Help and Details" in drawer:
        raise AssertionError("Mobile drawer must not hide FAQ behind the retired Help and Details panel")
    if "lt-mobile-nav-heading" in drawer or ">Locally Twisted</span>" in drawer:
        raise AssertionError("Mobile drawer brand must show the logo only, without duplicate Locally Twisted text")
    if 'data-lt-drawer-accordion-trigger="lt-mobile-products"' not in drawer:
        raise AssertionError("Mobile drawer must expose the open-commerce product panel when commerce is unpaused")


def test_ecommerce_entry_points_are_config_guarded(navbar: str, footer: str) -> None:
    combined = f"{navbar}\n{footer}"
    required = (
        "{% if not ecommerce_paused %}",
        "Ready-to-Order",
        'href="/shop"',
        "data-lt-search-product-entry",
        'href="/cart"',
        "Shopping cart",
    )
    for needle in required:
        if needle not in combined:
            raise AssertionError(f"Open-commerce source guard is missing expected ecommerce marker: {needle}")


def test_no_retired_nav_contract(navbar: str) -> None:
    retired = (
        "Plan by Occasion",
        "/blog",
        "lt-shop-trigger",
        "lt-shop-mega",
        "lt-mobile-drawer",
        "current ERPNext shop",
        "item-group routes",
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
        ROOT / "apps/locally_twisted/locally_twisted/www/about.py",
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
    retired_exact_counts = (
        "4.9 Google rating",
        "100+ Google reviews",
        "The full portfolio is coming",
        "design your event",
    )
    for text in retired_exact_counts:
        if text in home:
            raise AssertionError(f"Homepage still contains stale launch copy: {text}")


def test_event_balloons_hub_is_removed(navbar: str, footer: str, home: str, portfolio: str, hooks: str) -> None:
    combined = f"{navbar}\n{footer}\n{home}\n{portfolio}\n{hooks}"
    forbidden = (
        'href="/event-balloons"',
        "'/event-balloons'",
        '"/event-balloons"',
        '"to_route": "event_balloons"',
    )
    for needle in forbidden:
        if needle in combined:
            raise AssertionError(f"Removed /event-balloons page must not be linked or routed: {needle}")
    for path in (
        ROOT / "apps/locally_twisted/locally_twisted/www/event_balloons.html",
        ROOT / "apps/locally_twisted/locally_twisted/www/event_balloons.py",
    ):
        if path.exists():
            raise AssertionError(f"Removed /event-balloons route file still exists: {path.relative_to(ROOT)}")


def main() -> None:
    parse_noop_args(__doc__)
    navbar = NAVBAR.read_text(encoding="utf-8")
    footer = FOOTER.read_text(encoding="utf-8")
    home = HOME.read_text(encoding="utf-8")
    portfolio = PORTFOLIO.read_text(encoding="utf-8")
    hooks = HOOKS.read_text(encoding="utf-8")
    search_route = SEARCH_ROUTE.read_text(encoding="utf-8")
    mega_menu_css = MEGA_MENU_CSS.read_text(encoding="utf-8")
    test_desktop_nav_order(navbar)
    test_quote_cta_is_contact(navbar)
    test_top_banner_links_are_owner_approved(navbar)
    test_top_banner_accessibility_css(mega_menu_css)
    test_canonical_service_nav_requires_explicit_removal_approval(navbar, footer)
    test_nav_does_not_link_to_retired_book_route(navbar)
    test_nav_does_not_link_to_retired_category_index(navbar, footer)
    test_nav_does_not_expose_process_page(navbar, footer)
    test_search_is_overlay_not_public_page(navbar, footer, search_route)
    test_mega_menu_contract(navbar)
    test_mobile_nav_matches_primary_order(navbar)
    test_ecommerce_entry_points_are_config_guarded(navbar, footer)
    test_no_retired_nav_contract(navbar)
    test_supporting_assets_exist()
    test_homepage_launch_links(home)
    test_event_balloons_hub_is_removed(navbar, footer, home, portfolio, hooks)
    print("Nav IA checks passed")


if __name__ == "__main__":
    main()
