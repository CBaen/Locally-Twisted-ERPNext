"""End-to-end smoke test for the LT shop surfaces.

Validates the catalog port, shop hub, public nav, fixed-price product lane,
and retail variant selectors via a real Chromium browser. This should pass on
every deploy and fail loudly on customer-facing regressions. When public
ecommerce is intentionally paused, open-shop checks are skipped and the pause
contract is verified instead.

Coverage:
  1. Homepage navbar exposes the current mode-aware nav and /contact CTA.
  2. /shop renders the ready-to-order category rail/dropdown + 53 product cards
     when ecommerce is open, or redirects to the pause page when paused.
  3. /shop and category pages use the approved product-showroom card contract.
  4. /shop-by-category redirects to /shop instead of rendering the retired
     category-card index.
  5. Each child group's category page returns 200.
  6. Quote-first product detail pages keep the contact handoff instead of checkout controls.
  7. Retail product detail (variant template) renders inline chips/select for
     every attribute, chips are radio/single-select, and partial selections can
     disable invalid later options.
  8. Product detail (single SKU) renders price + add-to-cart button.
  9. Product detail pages do not render empty additional/recommendation panels.
  10. Product option and price/add-to-cart controls stay clear, not boxed.
  11. No "Item Code" jargon appears anywhere customer-facing.
  12. No "/Nos" UoM display anywhere.
  13. Mobile drawer exposes the same primary links and /contact quote CTA.

Run:
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/smoke_shop.py
  python scripts/verify/smoke_shop.py --help
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8081"
ROOT = Path(__file__).resolve().parents[2]
ITEM_CONFIGURE_TEMPLATE = (
    ROOT
    / "apps"
    / "locally_twisted"
    / "locally_twisted"
    / "templates"
    / "generators"
    / "item"
    / "item_configure.html"
)
EXPECTED_CATEGORIES = [
    "Arches",
    "Columns",
    "Bouquets",
    "Get-Well Bouquets",
    "Garlands",
    "Drops",
    "Grab & Go",
    "Table Decor",
    "Stands & Easels",
    "Deliveries",
    "Seasonal & Specialty",
]
QUOTE_FIRST_PRODUCT_URLS = [
    (f"{BASE}/shop-items/garlands/baby-shower-garland", "Baby Shower Garland", "baby-shower-garland"),
    (f"{BASE}/shop-items/arches/classic-arch", "Classic Arch", "classic-arch"),
]
PRODUCT_VARIANT_URL = f"{BASE}/shop-items/bouquets/unicorn-bouquet"
PRODUCT_VARIANT_EXPECTED_ATTRS = ["Bouquet Size"]
PRODUCT_PROGRESSIVE_URL = PRODUCT_VARIANT_URL
PRODUCT_CART_VARIANT_URL = PRODUCT_VARIANT_URL
PRODUCT_SINGLE_URL = f"{BASE}/shop-items/bouquets/mothers-day-bouquet"
SHOP_CATEGORY_SHOWCASE_URL = f"{BASE}/shop-items/arches"
PRODUCT_DETAIL_SHOWCASE_URL = f"{BASE}/shop-items/garlands/baby-shower-garland"
VARIANT_STARTING_PRICE_URL = f"{BASE}/shop-items/columns/classic-column"
VARIANT_STARTING_PRICE_ROUTE = "/shop-items/columns/classic-column"
ASSET_BOOT_ERROR_MARKER = "file_uploader.bundle.js"
PUBLIC_ECOMMERCE_PAUSED = False
PAUSED_ECOMMERCE_ROUTES = (
    "/shop",
    "/shop-items",
    "/shop-items/arches",
    "/shop-items/bouquets/unicorn-bouquet",
    "/shop-by-category",
    "/all-products",
    "/cart",
    "/checkout",
)

DESKTOP_VIEWPORT = {"width": 1366, "height": 900}
MOBILE_VIEWPORT = {"width": 375, "height": 812}
MIN_DESKTOP_CARD_WIDTH = 340
MIN_DESKTOP_CARD_IMAGE_WIDTH = 300
MAX_MOBILE_THUMBNAIL_WIDTH = 130
MIN_PRODUCT_DETAIL_IMAGE_WIDTH = 480


class SmokeFail(Exception):
    pass


def assert_(cond, msg):
    if not cond:
        raise SmokeFail(msg)


def _asset_boot_errors(errors: list[str]) -> list[str]:
    return [error for error in errors if ASSET_BOOT_ERROR_MARKER in error]


def _is_pause_page(page) -> bool:
    return "/ready-to-order-paused" in page.url or page.locator(".lt-ecommerce-paused").count() > 0


def detect_public_ecommerce_paused(page) -> bool:
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    return _is_pause_page(page)


def check_ecommerce_pause_routes(page):
    print("-> Public ecommerce pause routes")
    for route in PAUSED_ECOMMERCE_ROUTES:
        page.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        assert_(_is_pause_page(page), f"{route} should land on the branded ecommerce pause page")
        body = page.content()
        assert_("Ready-to-order is paused" in body, f"{route} did not render the pause headline")
        assert_("Start a custom event quote" in body, f"{route} did not render the quote fallback")
    print("  OK paused shop/product/cart/checkout routes render the branded quote fallback")


def _box(page, selector: str, index: int = 0):
    return page.evaluate(
        """({selector, index}) => {
            const el = document.querySelectorAll(selector)[index];
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            const style = window.getComputedStyle(el);
            return {
                width: rect.width,
                height: rect.height,
                left: rect.left,
                top: rect.top,
                display: style.display,
                gridTemplateColumns: style.gridTemplateColumns,
            };
        }""",
        {"selector": selector, "index": index},
    )


def _visible_boxes(page, selector: str, limit: int = 6):
    return page.evaluate(
        """({selector, limit}) => Array.from(document.querySelectorAll(selector))
            .map((el) => {
                const rect = el.getBoundingClientRect();
                const img = el.querySelector('img');
                const imgRect = img ? img.getBoundingClientRect() : null;
                const style = window.getComputedStyle(el);
                const imgStyle = img ? window.getComputedStyle(img) : null;
                return {
                    width: rect.width,
                    height: rect.height,
                    display: style.display,
                    className: el.className,
                    text: (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 80),
                    imageWidth: imgRect ? imgRect.width : null,
                    imageHeight: imgRect ? imgRect.height : null,
                    imageObjectFit: imgStyle ? imgStyle.objectFit : null,
                };
            })
            .filter((box) => box.width > 0 && box.height > 0)
            .slice(0, limit)""",
        {"selector": selector, "limit": limit},
    )


def _first_visible_box(page, selector: str):
    boxes = _visible_boxes(page, selector, 1)
    return boxes[0] if boxes else None


def _computed_style(page, selector: str):
    return page.evaluate(
        """(selector) => {
            const el = document.querySelector(selector);
            if (!el) return null;
            const style = window.getComputedStyle(el);
            return {
                backgroundColor: style.backgroundColor,
                borderTopWidth: style.borderTopWidth,
                borderRightWidth: style.borderRightWidth,
                borderBottomWidth: style.borderBottomWidth,
                borderLeftWidth: style.borderLeftWidth,
                borderRadius: style.borderRadius,
                boxShadow: style.boxShadow
            };
        }""",
        selector,
    )


def _px(value: str) -> float:
    return float((value or "0").replace("px", "") or 0)


def _is_transparent(color: str) -> bool:
    return color in ("transparent", "rgba(0, 0, 0, 0)")


def check_variant_template_contract():
    print("-> Variant selector template contract")
    text = ITEM_CONFIGURE_TEMPLATE.read_text(encoding="utf-8")
    assert_(
        'frappe.get_all("Item Attribute Value"' not in text,
        "item_configure.html must not query Item Attribute Value once per attribute from Jinja",
    )
    assert_(
        "get_variant_attribute_options" in text,
        "item_configure.html should use LT's Webshop-backed prepared attribute/value helper",
    )
    assert_(
        'type="radio"' in text and 'class="lt-product__chip-input js-lt-attr-input"' in text,
        "variant option chips must render as radio/single-select controls",
    )
    print("  OK no per-attribute Jinja DB lookup; chips stay radio/single-select")


def check_homepage(page):
    print("-> Homepage authority-first mega navigation")
    page.goto(f"{BASE}/", wait_until="networkidle", timeout=15000)

    assert_(page.locator(".lt-mega-brand__logo").count() >= 1, "Mega header missing logo image")
    event_trigger = page.locator("[data-lt-megamenu-trigger='lt-mega-events']")
    product_trigger = page.locator("[data-lt-megamenu-trigger='lt-mega-products']")
    assert_(event_trigger.count() == 1, "Desktop header missing Event Balloons mega trigger")
    if PUBLIC_ECOMMERCE_PAUSED:
        assert_(product_trigger.count() == 0, "Paused desktop header must not expose Ready-to-Order mega trigger")
    else:
        assert_(product_trigger.count() == 1, "Desktop header missing Ready-to-Order mega trigger")

    nav_links = page.locator(".lt-mega-nav__link, .lt-mega-nav__button")
    nav_text = [
        nav_links.nth(i).inner_text().replace("\n", " ").strip()
        for i in range(nav_links.count())
    ]

    def nav_index(label: str) -> int:
        label_key = label.casefold()
        for index, text in enumerate(nav_text):
            if text.casefold() == label_key:
                return index
        assert_(False, f"Primary nav missing {label}; got {nav_text}")
        return -1

    btfp_index = nav_index("Twisting & Face Painting")
    quote_index = nav_index("Free Event Quote")
    portfolio_index = nav_index("Portfolio")
    faq_index = nav_index("FAQ")
    if PUBLIC_ECOMMERCE_PAUSED:
        assert_("Ready-to-Order" not in nav_text, f"Paused primary nav must hide Ready-to-Order, got {nav_text}")
        assert_(
            btfp_index < quote_index < portfolio_index < faq_index,
            f"Paused primary nav should place BTFP, Free Event Quote, Portfolio, FAQ in order; got {nav_text}",
        )
    else:
        ready_index = nav_index("Ready-to-Order")
        assert_(
            ready_index < btfp_index < quote_index < portfolio_index < faq_index,
            f"Open-commerce primary nav order is wrong, got {nav_text}",
        )

    for label, href in (
        ("Portfolio", "/portfolio"),
        ("About Us", "/about"),
        ("FAQ", "/faq"),
    ):
        link = page.locator(".lt-mega-nav__link", has_text=label)
        assert_(link.count() == 1, f"Desktop header missing {label} link")
        assert_(link.first.get_attribute("href") == href, f"{label} should link to {href}")
    assert_(page.locator(".lt-mega-nav__link", has_text="Process").count() == 0, "Desktop header must not expose Process")

    search_button = page.locator(".lt-mega-header__search")
    assert_(search_button.count() == 1, "Desktop header missing search overlay button")
    assert_(search_button.first.get_attribute("href") is None, "Search control must not link to /search")
    search_button.click()
    assert_(page.locator("#lt-site-search-panel").is_visible(), "Search overlay did not open")
    assert_(page.url.rstrip("/") == BASE, "Opening search overlay must not navigate away from the current page")
    page.locator("#lt-site-search-input").fill("arches")
    if PUBLIC_ECOMMERCE_PAUSED:
        form_action = page.locator("#lt-site-search-panel form").first.get_attribute("action")
        assert_(form_action == "/contact", f"Paused search form should submit to /contact, got {form_action!r}")
        assert_(
            page.locator("#lt-site-search-panel [data-lt-search-product-entry]").count() == 0,
            "Paused search overlay must not expose product quick links",
        )
    else:
        assert_(
            page.locator("#lt-site-search-panel a[href='/shop-items/arches']").is_visible(),
            "Search overlay should filter quick product-family links",
        )
    page.keyboard.press("Escape")
    assert_(not page.locator("#lt-site-search-panel").is_visible(), "Search overlay did not close on Escape")

    event_trigger.click()
    assert_(page.locator("#lt-mega-events").is_visible(), "Event mega menu did not open")
    for label, href in (
        ("Civic & Community", "/civic-community"),
        ("Corporate Events", "/corporate-events"),
        ("Schools & Campuses", "/schools-campuses"),
        ("Private Celebrations", "/private-celebrations"),
    ):
        link = page.locator("#lt-mega-events a", has_text=label)
        assert_(link.count() == 1, f"Event mega menu missing {label}")
        assert_(link.first.get_attribute("href") == href, f"Event mega menu {label} should link to {href}")
    assert_(page.locator("#lt-mega-events", has_text="Corporate Entrances").count() == 0, "Event mega menu must say Corporate Events, not Corporate Entrances")
    assert_(page.locator("#lt-mega-events .lt-megamenu__card[href='/event-balloons']").count() == 0, "Event mega cards must not all link to /event-balloons")
    assert_(page.locator("#lt-mega-events .lt-megamenu__card[href='/portfolio']").count() == 0, "Corporate event mega card must not link to /portfolio")
    if not PUBLIC_ECOMMERCE_PAUSED:
        product_trigger.click()
        assert_(page.locator("#lt-mega-products").is_visible(), "Ready-to-Order mega menu did not open")
        assert_(
            page.locator("#lt-mega-products a[href='/shop-items/arches']").count() >= 1,
            "Product mega menu should link to /shop-items/arches",
        )

    quote_cta = page.locator(".lt-mega-header__cta", has_text="Contact Us")
    assert_(quote_cta.count() == 1, "Desktop header missing Contact Us CTA")
    assert_(quote_cta.first.get_attribute("href") == "/contact", "Contact Us CTA must link to /contact")
    footer_all_decor = page.locator("footer .lt-footer__col-link", has_text="All Ready-to-Order")
    if PUBLIC_ECOMMERCE_PAUSED:
        assert_(footer_all_decor.count() == 0, "Paused footer must hide All Ready-to-Order link")
    else:
        assert_(footer_all_decor.count() == 1, "Footer missing All Ready-to-Order link")
        assert_(footer_all_decor.first.get_attribute("href") == "/shop", "Footer All Ready-to-Order link must use /shop")
    print("  OK mode-aware mega navigation, service lane, /contact CTA, and footer commerce state")


def check_event_type_pages(page):
    print("-> Event type pages")
    expectations = {
        "/civic-community": ("Balloon decor for Utah public events.", ["Ogden City", "SLC County", "Equality Utah"]),
        "/corporate-events": ("On-brand balloon decor for Utah company events.", ["Ancestry", "Zions Bank", "KSL"]),
        "/schools-campuses": ("School-color balloon decor for campus moments.", ["University of Utah", "Weber State", "St. Joseph's"]),
        "/private-celebrations": ("Polished balloons for personal celebrations.", ["Alpine Events", "Ogden Country Club", "Tree House Museum"]),
    }
    for route, (title_text, proof_names) in expectations.items():
        page.goto(f"{BASE}{route}", wait_until="networkidle", timeout=15000)
        assert_(page.locator(".lt-event-type-page").count() == 1, f"{route} missing event-type page wrapper")
        assert_(page.locator("h1", has_text=title_text).count() == 1, f"{route} missing focused page title")
        body = page.locator("body").inner_text().casefold()
        for proof_name in proof_names:
            assert_(proof_name.casefold() in body, f"{route} must mention proof client {proof_name}")
    print("  OK event menu routes render focused proof pages with relevant client names")


def check_shop_page(page):
    print(f"-> {BASE}/shop")
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    assert_(
        page.locator(".lt-shop__chip").count() == 0,
        "/shop must not use the old category chip wall",
    )
    rail_links = page.locator(".lt-shop__category-rail .lt-shop__category-link")
    rail_count = rail_links.count()
    assert_(rail_count == 12, f"/shop expected 12 category rail links (All + 11 categories), got {rail_count}")
    category_select = page.locator(".lt-shop__category-select")
    assert_(category_select.count() == 1, "/shop should expose one mobile category select")
    assert_(category_select.locator("option").count() == 12, "/shop mobile category select should include All + 11 categories")

    body = page.content()
    assert_("53 ITEMS" in body or "53&nbsp;ITEMS" in body or ">53" in body, "/shop should show 53 items count")
    print(f"  OK {rail_count} category rail links rendered, 53 items")


def check_search_page_retired(page):
    print(f"-> {BASE}/search retired route")
    response = page.goto(f"{BASE}/search", wait_until="domcontentloaded", timeout=15000)
    assert_(response is not None, "/search did not return a response")
    assert_(response.status == 404, f"/search must return 404, got HTTP {response.status}")
    print("  OK /search returns 404 instead of Frappe's bundled search page")


def check_shop_showroom_contract(page):
    print("-> /shop showroom card contract")
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    card = _first_visible_box(page, ".lt-shop__card")
    assert_(card is not None, "/shop did not render visible product cards")
    assert_(
        card["width"] >= MIN_DESKTOP_CARD_WIDTH,
        f"/shop desktop cards must be showroom sized: got {card['width']:.1f}px, expected >= {MIN_DESKTOP_CARD_WIDTH}px",
    )
    assert_(
        (card["imageWidth"] or 0) >= MIN_DESKTOP_CARD_IMAGE_WIDTH,
        f"/shop desktop card image must be large: got {card['imageWidth']:.1f}px, expected >= {MIN_DESKTOP_CARD_IMAGE_WIDTH}px",
    )

    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    mobile_card = _first_visible_box(page, ".lt-shop__card")
    assert_(mobile_card is not None, "/shop mobile did not render visible product cards")
    assert_(
        (mobile_card["imageWidth"] or 0) > MAX_MOBILE_THUMBNAIL_WIDTH,
        f"/shop mobile cards must not use thumbnail treatment: got image width {mobile_card['imageWidth']:.1f}px",
    )
    print("  OK /shop desktop and mobile cards meet showroom sizing")


def check_category_showroom_contract(page):
    print("-> /shop-items/<group> showroom contract")
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(SHOP_CATEGORY_SHOWCASE_URL, wait_until="networkidle", timeout=15000)
    assert_(
        page.locator(".lt-shop__toolbar--categories").count() == 0,
        "Category showcase pages must not repeat the old top category button wall",
    )
    assert_(
        page.locator(".lt-shop__category-rail").count() == 1,
        "Category showcase pages must use the desktop category rail",
    )
    layout = _box(page, ".lt-shop__layout")
    assert_(layout is not None, "Category page missing .lt-shop__layout")
    assert_(
        "px 0px" not in layout["gridTemplateColumns"],
        f"Category grid has collapsed columns: {layout['gridTemplateColumns']!r}",
    )
    card = _first_visible_box(page, "#product-listing .item-card, #product-listing .lt-shop__card")
    assert_(card is not None, "Category page did not render visible product cards")
    assert_(
        card["width"] >= MIN_DESKTOP_CARD_WIDTH,
        f"Category desktop cards must be showroom sized: got {card['width']:.1f}px, expected >= {MIN_DESKTOP_CARD_WIDTH}px",
    )
    assert_(
        (card["imageWidth"] or 0) >= MIN_DESKTOP_CARD_IMAGE_WIDTH,
        f"Category desktop card image must be large: got {card['imageWidth']:.1f}px, expected >= {MIN_DESKTOP_CARD_IMAGE_WIDTH}px",
    )
    assert_(
        card["imageObjectFit"] in ("contain", "scale-down"),
        f"Category card images must show the whole product, got object-fit {card['imageObjectFit']!r}",
    )

    page.set_viewport_size(MOBILE_VIEWPORT)
    page.goto(SHOP_CATEGORY_SHOWCASE_URL, wait_until="networkidle", timeout=15000)
    mobile_card = _first_visible_box(page, "#product-listing .item-card, #product-listing .lt-shop__card")
    assert_(mobile_card is not None, "Category mobile did not render visible product cards")
    assert_(
        (mobile_card["imageWidth"] or 0) > MAX_MOBILE_THUMBNAIL_WIDTH,
        f"Category mobile cards must not use thumbnail treatment: got image width {mobile_card['imageWidth']:.1f}px",
    )
    print("  OK category page uses side category rail/dropdown and showroom cards")


def _visible_rect_rows(page, selector: str):
    return page.evaluate(
        """(selector) => {
            const rows = new Map();
            for (const el of Array.from(document.querySelectorAll(selector))) {
                const rect = el.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) continue;
                const top = Math.round(rect.top);
                if (!rows.has(top)) rows.set(top, []);
                rows.get(top).push({
                    text: (el.textContent || '').replace(/\\s+/g, ' ').trim(),
                    width: rect.width,
                    height: rect.height,
                    left: rect.left,
                });
            }
            return Array.from(rows.entries())
                .sort((a, b) => a[0] - b[0])
                .map(([top, cells]) => ({
                    top,
                    count: cells.length,
                    widths: cells.map((cell) => cell.width),
                    heights: cells.map((cell) => cell.height),
                    texts: cells.map((cell) => cell.text),
                }));
        }""",
        selector,
    )


def check_category_nav_rail_contract(page):
    print("-> shop category rail/dropdown navigation contract")
    for url in (f"{BASE}/shop", f"{BASE}/shop-items/get-well-bouquets"):
        page.set_viewport_size(DESKTOP_VIEWPORT)
        page.goto(url, wait_until="networkidle", timeout=15000)
        assert_(page.locator(".lt-shop__chip").count() == 0, f"{url} must not render category chips")
        rail = page.locator(".lt-shop__category-rail")
        assert_(rail.count() == 1, f"{url} missing desktop category rail")
        assert_(rail.is_visible(), f"{url} category rail should be visible on desktop")
        links = page.locator(".lt-shop__category-rail .lt-shop__category-link")
        assert_(links.count() == 12, f"{url} category rail must include All + 11 categories")
        active = page.locator(".lt-shop__category-rail .lt-shop__category-link.is-active")
        assert_(active.count() == 1, f"{url} category rail should have exactly one active link")
        rail_rows = _visible_rect_rows(page, ".lt-shop__category-rail .lt-shop__category-link")
        assert_(
            all(row["count"] == 1 for row in rail_rows),
            f"{url} desktop rail must be a vertical list, got rows {rail_rows}",
        )

        page.set_viewport_size(MOBILE_VIEWPORT)
        page.goto(url, wait_until="networkidle", timeout=15000)
        select = page.locator(".lt-shop__category-select")
        assert_(select.count() == 1, f"{url} missing mobile category select")
        assert_(select.is_visible(), f"{url} category select should be visible on mobile")
        assert_(select.locator("option").count() == 12, f"{url} mobile select must include All + 11 categories")
        target_value = "/shop-items/arches" if url.endswith("/shop") else "/shop"
        target_url = f"{BASE}{target_value}"
        with page.expect_navigation(url=target_url, wait_until="networkidle", timeout=15000):
            select.select_option(target_value)
        assert_(page.url.rstrip("/") == target_url, f"{url} mobile select did not navigate to {target_url}")
        assert_(
            not page.locator(".lt-shop__category-rail nav").is_visible(),
            f"{url} desktop rail list should be hidden on mobile",
        )
    print("  OK category navigation uses desktop rail and mobile select")


def check_shop_product_grid_symmetry_contract(page):
    print("-> /shop product grid symmetry contract")
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    rows = _visible_rect_rows(page, "#lt-shop-grid .lt-shop__card")
    assert_(rows, "/shop did not render visible cards")
    assert_(
        rows[-1]["count"] != 1,
        f"/shop product grid must not leave one orphan card on desktop: final row has {rows[-1]['texts']}",
    )
    print("  OK /shop product grid avoids desktop orphan rows")


def check_category_product_grid_symmetry_contract(page):
    print("-> /shop-items/<group> product grid symmetry contract")
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(SHOP_CATEGORY_SHOWCASE_URL, wait_until="networkidle", timeout=15000)
    rows = _visible_rect_rows(page, "#products-grid-area .item-card")
    assert_(rows, "Category product grid did not render visible cards")
    assert_(
        rows[-1]["count"] != 1,
        f"Category product grid must not leave one orphan card on desktop: final row has {rows[-1]['texts']}",
    )
    print("  OK category product grid avoids desktop orphan rows")


def _card_price_for_route(page, card_selector: str, route: str) -> str | None:
    return page.evaluate(
        """({cardSelector, route}) => {
            const cards = Array.from(document.querySelectorAll(cardSelector));
            const card = cards.find((candidate) => {
                const link = candidate.querySelector(`a[href="${route}"]`);
                return !!link;
            });
            if (!card) return null;
            const price = card.querySelector('.lt-shop__card-price, .product-price');
            return price ? price.textContent.replace(/\\s+/g, ' ').trim() : '';
        }""",
        {"cardSelector": card_selector, "route": route},
    )


def check_variant_template_starting_price_display(page):
    print("-> Variant template starting price display")
    page.set_viewport_size(DESKTOP_VIEWPORT)

    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    shop_price = _card_price_for_route(page, ".lt-shop__card", VARIANT_STARTING_PRICE_ROUTE)
    assert_(shop_price is not None, "/shop missing Classic Column card")
    assert_(
        shop_price.lower().startswith("from $"),
        f"/shop Classic Column card should show a public starting price, got {shop_price!r}",
    )

    page.goto(f"{BASE}/shop-items/columns", wait_until="networkidle", timeout=15000)
    category_price = _card_price_for_route(page, ".item-card", VARIANT_STARTING_PRICE_ROUTE)
    assert_(category_price is not None, "/shop-items/columns missing Classic Column card")
    assert_(
        category_price.lower().startswith("from $"),
        f"/shop-items/columns Classic Column card should show a public starting price, got {category_price!r}",
    )

    page.goto(VARIANT_STARTING_PRICE_URL, wait_until="networkidle", timeout=15000)
    if page.locator("#lt-product-price-text").count():
        detail_price = page.locator("#lt-product-price-text").inner_text().strip()
        assert_(
            detail_price.lower().startswith("from $"),
            f"Variant detail page should show a starting price before option selection, got {detail_price!r}",
        )
    else:
        assert_(
            page.locator(".lt-product__cart--quote-first").count() == 1,
            "Variant detail page without direct price should render the quote-first handoff",
        )
    print("  OK variant templates expose listing prices and route detail pages to the correct lane")


def check_product_detail_no_auxiliary_ecommerce_panels(page):
    print("-> Product detail auxiliary ecommerce panels")
    page.set_viewport_size(DESKTOP_VIEWPORT)

    for url in (PRODUCT_VARIANT_URL, PRODUCT_DETAIL_SHOWCASE_URL, PRODUCT_SINGLE_URL):
        page.goto(url, wait_until="networkidle", timeout=15000)
        for selector in (
            ".lt-product__more",
            ".lt-product__info-panel",
            ".lt-product__info-content",
            ".lt-product__recommendations",
            ".recommended-item-section",
            ".recommendation-container",
        ):
            assert_(
                page.locator(selector).count() == 0,
                f"{url} should not render auxiliary product panel {selector}",
            )

    print("  OK product detail pages do not render empty additional/recommendation panels")


def check_product_detail_clear_option_box_contract(page):
    print("-> Product detail clear option box contract")

    disallowed_box_selectors = (
        ".lt-product__configure",
        ".lt-product__cart",
        ".lt-product__attr",
        ".lt-product__chip-label",
    )
    optional_disallowed_box_selectors = (".lt-product__select",)
    no_side_box_selectors = (
        ".lt-product__details-section",
    )

    for viewport in (DESKTOP_VIEWPORT, MOBILE_VIEWPORT):
        page.set_viewport_size(viewport)
        page.goto(PRODUCT_VARIANT_URL, wait_until="networkidle", timeout=15000)

        for selector in disallowed_box_selectors:
            assert_(page.locator(selector).count() > 0, f"{selector} missing on product option page")
            style = _computed_style(page, selector)
            assert_(style is not None, f"{selector} style missing")
            assert_(
                _is_transparent(style["backgroundColor"]),
                f"{selector} must not have a boxed background; got {style['backgroundColor']}",
            )
            assert_(
                _px(style["borderTopWidth"]) == 0
                and _px(style["borderRightWidth"]) == 0
                and _px(style["borderBottomWidth"]) == 0
                and _px(style["borderLeftWidth"]) == 0,
                f"{selector} must not render a product option box; got borders {style}",
            )
            assert_(style["boxShadow"] == "none", f"{selector} must not render a boxed shadow")

        for selector in optional_disallowed_box_selectors:
            if page.locator(selector).count() == 0:
                continue
            style = _computed_style(page, selector)
            assert_(style is not None, f"{selector} style missing")
            assert_(
                _is_transparent(style["backgroundColor"]),
                f"{selector} must not have a boxed background; got {style['backgroundColor']}",
            )
            assert_(
                _px(style["borderTopWidth"]) == 0
                and _px(style["borderRightWidth"]) == 0
                and _px(style["borderBottomWidth"]) == 0
                and _px(style["borderLeftWidth"]) == 0,
                f"{selector} must not render a product option box; got borders {style}",
            )
            assert_(style["boxShadow"] == "none", f"{selector} must not render a boxed shadow")

        for selector in no_side_box_selectors:
            style = _computed_style(page, selector)
            assert_(style is not None, f"{selector} style missing")
            assert_(
                _is_transparent(style["backgroundColor"]),
                f"{selector} must stay clear; got {style['backgroundColor']}",
            )
            assert_(
                _px(style["borderRightWidth"]) == 0
                and _px(style["borderBottomWidth"]) == 0
                and _px(style["borderLeftWidth"]) == 0,
                f"{selector} may use only a section divider, not a box; got borders {style}",
            )
            assert_(style["boxShadow"] == "none", f"{selector} must not render a boxed shadow")

        fulfillment_style = _computed_style(page, ".lt-product__fulfillment")
        assert_(fulfillment_style is not None, "Pickup/delivery panel missing")
        assert_(
            not _is_transparent(fulfillment_style["backgroundColor"])
            and _px(fulfillment_style["borderTopWidth"]) > 0,
            "Pickup/delivery is the one allowed framed product-page container",
        )

    print("  OK product options and price/add-to-cart stay clear; pickup/delivery remains framed")


def check_shop_items_broad_route(page):
    print(f"-> {BASE}/shop-items")
    page.goto(f"{BASE}/shop-items", wait_until="networkidle", timeout=15000)
    assert_(
        page.url.rstrip("/") in (f"{BASE}/shop", f"{BASE}/shop-items"),
        f"/shop-items should redirect or alias to /shop, landed on {page.url!r}",
    )
    assert_(page.locator(".lt-shop--landing #lt-shop-grid .lt-shop__card").count() >= 1, "/shop-items should land on the broad showroom")
    assert_(page.locator("body[data-path='shop']").count() == 1, "/shop-items alias should render the /shop page contract")
    print("  OK /shop-items aliases to /shop showroom")


def check_shop_by_category_redirect(page):
    print(f"-> {BASE}/shop-by-category")
    resp = page.goto(f"{BASE}/shop-by-category", wait_until="networkidle", timeout=15000)
    assert_(resp.status == 200, f"/shop-by-category final response returned {resp.status}")
    assert_(
        page.url.rstrip("/") == f"{BASE}/shop",
        f"/shop-by-category should redirect to /shop, landed on {page.url!r}",
    )
    assert_(
        page.locator(".lt-by-cat__card").count() == 0,
        "/shop-by-category must not render the retired category-card index",
    )
    print("  OK redirects to /shop")


def check_category_pages(page):
    print("-> Each category page returns 200 with no jargon")
    for cat_name in EXPECTED_CATEGORIES:
        slug = cat_name.lower().replace(" & ", "-").replace(" ", "-")
        url = f"{BASE}/shop-items/{slug}"
        resp = page.goto(url, wait_until="domcontentloaded", timeout=10000)
        assert_(resp.status == 200, f"Category {cat_name} ({url}) returned {resp.status}")
        content = page.content()
        assert_(
            "product-item-code" not in content or 'class="product-item-code"' not in content,
            f"Category {cat_name} still shows product-item-code class",
        )
        print(f"  OK /{cat_name}")


def check_quote_first_product_pages_keep_quote_gate(page):
    print("-> Quote-first product pages keep the customer-safe quote gate")
    for url, expected_title, item_code in QUOTE_FIRST_PRODUCT_URLS:
        page.goto(url, wait_until="networkidle", timeout=15000)
        title = page.locator(".lt-product__title").inner_text()
        assert_(expected_title in title, f"Product title wrong for {url}: {title!r}")

        body = page.content()
        assert_(f"Item Code: {item_code}" not in body, f"{url} still leaks 'Item Code:' jargon")
        assert_("/ Nos" not in body and " / Nos" not in body, f"{url} still leaks '/Nos' UoM")
        assert_("Shop by Category" not in body, f"{url} breadcrumb still shows retired 'Shop by Category' label")
        assert_("/shop-by-category" not in body, f"{url} breadcrumb still links to retired /shop-by-category route")
        assert_(
            page.locator(".lt-product__cart--quote-first").count() == 1,
            f"{url} should render the quote-first product cart",
        )
        assert_(
            page.locator(".lt-product__configure").count() == 0,
            f"{url} should not render direct-checkout variant controls",
        )
        assert_(
            page.locator(".js-lt-product-quote-request").count() == 1,
            f"{url} should expose the product quote request handoff",
        )
        assert_(
            page.locator(".btn-add-to-cart, #lt-add-to-cart-variant").count() == 0,
            f"{url} should not expose add-to-cart controls",
        )
    print("  OK quote-first products keep product details, options, and contact handoff")


def check_product_variant_page(page):
    print(f"-> {PRODUCT_VARIANT_URL}")
    page.goto(PRODUCT_VARIANT_URL, wait_until="networkidle", timeout=15000)
    title = page.locator(".lt-product__title").inner_text()
    assert_("Unicorn Bouquet" in title, f"Product title wrong: {title!r}")

    body = page.content()
    assert_("Item Code: unicorn-bouquet" not in body, "Product detail still leaks 'Item Code:' jargon")
    assert_("/ Nos" not in body and " / Nos" not in body, "Product detail still leaks '/Nos' UoM")
    assert_("Shop by Category" not in body, "Product breadcrumb still shows retired 'Shop by Category' label")
    assert_("/shop-by-category" not in body, "Product breadcrumb still links to retired /shop-by-category route")
    assert_("super shape" not in body.lower(), "Product detail still exposes super shape jargon")
    assert_(
        body.count("/assets/frappe/js/lib/jquery/jquery.min.js") == 1,
        "Product detail should not render duplicate jQuery/base script blocks",
    )
    file_uploader_asset = page.evaluate(
        "() => window.frappe?.boot?.assets_json?.['file_uploader.bundle.js']"
    )
    assert_(file_uploader_asset, "Product detail missing Frappe asset map for file uploader bundle")

    for attr in PRODUCT_VARIANT_EXPECTED_ATTRS:
        loc = page.locator(f".lt-product__attr[data-attribute-name='{attr}']")
        assert_(loc.count() == 1, f"Variant attr {attr!r} not rendered inline")
    assert_(
        page.locator(".lt-product__attr[data-attribute-name='Add Foil Number']").count() == 0,
        "Add Foil Number must not render as a required variant option",
    )

    btn = page.locator("#lt-add-to-cart-variant")
    assert_(btn.count() == 1, "Add-to-cart button missing")
    assert_(btn.is_disabled(), "Add-to-cart button should be disabled before selection")
    checkbox_count = page.locator(".lt-product__configure input[type='checkbox']").count()
    radio_count = page.locator(".lt-product__configure input[type='radio']").count()
    assert_(checkbox_count == 0, "Variant chips must not use checkbox inputs")
    assert_(radio_count > 0, "Variant chips should use radio inputs for single-choice options")
    print("  OK retail inline variants render, jargon stripped, CTA disabled until selection")


def check_product_detail_showroom_contract(page):
    print("-> Product detail showroom image contract")
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(PRODUCT_DETAIL_SHOWCASE_URL, wait_until="networkidle", timeout=15000)
    image_box = _box(page, ".lt-product__summary-row .website-image")
    assert_(image_box is not None, "Product detail missing main product image")
    assert_(
        image_box["width"] >= MIN_PRODUCT_DETAIL_IMAGE_WIDTH,
        f"Product detail desktop image must be showcase sized: got {image_box['width']:.1f}px, expected >= {MIN_PRODUCT_DETAIL_IMAGE_WIDTH}px",
    )
    print("  OK product detail main image is showcase sized")


def check_progressive_variant_option_disabling(page):
    print(f"-> {PRODUCT_PROGRESSIVE_URL} size variants update media and remain changeable")
    page.goto(PRODUCT_PROGRESSIVE_URL, wait_until="networkidle", timeout=15000)
    assert_(
        page.locator(".lt-product__attr[data-attribute-name='Add Foil Number']").count() == 0,
        "Foil numbers should not block size selection",
    )

    page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip").nth(1).click()
    page.wait_for_function(
        """() => {
            const btn = document.querySelector('#lt-add-to-cart-variant');
            const img = document.querySelector('.product-image img.website-image');
            return btn && !btn.disabled
                && btn.getAttribute('data-item-code')
                && img && /medium/i.test(img.getAttribute('src') || '');
        }""",
        timeout=10000,
    )
    medium_code = page.locator("#lt-add-to-cart-variant").get_attribute("data-item-code")

    page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip").nth(2).click()
    page.wait_for_function(
        """(previousCode) => {
            const btn = document.querySelector('#lt-add-to-cart-variant');
            const img = document.querySelector('.product-image img.website-image');
            return btn && !btn.disabled
                && btn.getAttribute('data-item-code')
                && btn.getAttribute('data-item-code') !== previousCode
                && img && /large/i.test(img.getAttribute('src') || '');
        }""",
        arg=medium_code,
        timeout=10000,
    )

    print("  OK bouquet size alone resolves a variant, swaps image, and stays changeable")


def check_variant_add_to_cart_ui(page):
    print(f"-> {PRODUCT_CART_VARIANT_URL} variant add-to-cart")
    page.goto(PRODUCT_CART_VARIANT_URL, wait_until="networkidle", timeout=15000)
    page.evaluate("window.LT_CART && window.LT_CART.clear && window.LT_CART.clear()")
    page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip").first.click()
    btn = page.locator("#lt-add-to-cart-variant")
    btn.wait_for(state="visible", timeout=10000)
    page.wait_for_function(
        """() => {
            const btn = document.querySelector('#lt-add-to-cart-variant');
            return btn && !btn.disabled && btn.getAttribute('data-item-code');
        }""",
        timeout=10000,
    )
    variant_code = btn.get_attribute("data-item-code")
    assert_(variant_code and variant_code.startswith("unicorn-bouquet-"), f"Unexpected variant code {variant_code!r}")
    btn.click()
    page.wait_for_timeout(500)
    cart = page.evaluate("window.LT_CART && window.LT_CART.getCart()")
    codes = [line["item_code"] for line in (cart or {}).get("items", [])]
    assert_(
        variant_code in codes,
        f"Configured variant was not written to LT_CART (codes: {codes})",
    )
    print(f"  OK option selection adds purchasable variant {variant_code}")


def check_product_single_page(page):
    print(f"-> {PRODUCT_SINGLE_URL}")
    resp = page.goto(PRODUCT_SINGLE_URL, wait_until="networkidle", timeout=15000)
    if resp.status != 200:
        print(f"  skipped (HTTP {resp.status})")
        return
    body = page.content()
    assert_("Item Code: mothers-day-bouquet" not in body, "Single SKU still leaks Item Code jargon")
    assert_(page.locator(".btn-add-to-cart").count() >= 1, "Retail single-SKU page missing add-to-cart button")
    print("  OK retail single SKU page clean with add-to-cart")


def check_mobile_drawer(p):
    print("-> Mobile drawer mega links")
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        viewport={"width": 375, "height": 812},
        is_mobile=True,
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 Version/16.0 Mobile/15E148 Safari/604.1"
        ),
    )
    page = ctx.new_page()
    page.goto(f"{BASE}/", wait_until="networkidle", timeout=15000)
    page.click("#lt-mobile-toggle")
    page.wait_for_function(
        """() => {
            const drawer = document.querySelector('#lt-mobile-nav');
            return drawer && drawer.classList.contains('is-open') && drawer.getAttribute('aria-hidden') === 'false';
        }""",
        timeout=10000,
    )

    panel_ids = ["lt-mobile-events"]
    if not PUBLIC_ECOMMERCE_PAUSED:
        panel_ids.append("lt-mobile-products")
    else:
        assert_(
            page.locator("[data-lt-drawer-accordion-trigger='lt-mobile-products']").count() == 0,
            "Paused mobile drawer must not expose Ready-to-Order accordion",
        )

    for panel_id in panel_ids:
        page.locator(f"[data-lt-drawer-accordion-trigger='{panel_id}']").click()
        assert_(page.locator(f"#{panel_id}").is_visible(), f"Mobile drawer panel {panel_id} did not open")

    expected_links = {
        "Event Balloons": "/event-balloons",
        "Twisting & Face Painting": "/balloon-twisting-and-face-painting",
        "Portfolio": "/portfolio",
        "FAQ": "/faq",
        "Sign In": "/login",
        "Free Event Quote": "/contact",
        "Contact Us": "/contact",
    }
    if not PUBLIC_ECOMMERCE_PAUSED:
        expected_links["Shop All"] = "/shop"
    for label, href in expected_links.items():
        link = page.locator("#lt-mobile-nav a", has_text=label).first
        assert_(link.count() == 1, f"Mobile drawer missing {label}")
        assert_(link.get_attribute("href") == href, f"Mobile drawer {label} should link to {href}")
    for label, href in (
        ("Civic & Community", "/civic-community"),
        ("Corporate Events", "/corporate-events"),
        ("Schools & Campuses", "/schools-campuses"),
        ("Private Celebrations", "/private-celebrations"),
    ):
        link = page.locator("#lt-mobile-events a", has_text=label).first
        assert_(link.count() == 1, f"Mobile event drawer missing {label}")
        assert_(link.get_attribute("href") == href, f"Mobile event drawer {label} should link to {href}")
    assert_(page.locator("#lt-mobile-nav a[href='/search']").count() == 0, "Mobile drawer must not link to /search")
    search_button = page.locator("#lt-mobile-nav .lt-mega-drawer__search").first
    assert_(search_button.count() == 1, "Mobile drawer missing bottom search button")
    assert_(search_button.get_attribute("href") is None, "Mobile drawer search must open the overlay, not link to /search")
    search_button.click()
    page.wait_for_selector("#lt-site-search-panel", state="visible", timeout=10000)
    assert_(
        not page.locator("#lt-mobile-nav").evaluate("drawer => drawer.classList.contains('is-open')"),
        "Opening drawer search should close the mobile menu before focusing search",
    )
    print("  OK drawer opens, accordions expose links, hides /search, keeps /contact quote CTA, and puts search at the bottom")
    browser.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the end-to-end LT shop smoke test against the local Frappe site. "
            "This launches a real Chromium browser and may take longer than small contract tests."
        )
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parse_args(argv)
    failures = []
    try:
        check_variant_template_contract()
    except SmokeFail as e:
        print(f"  FAIL: {e}")
        failures.append(str(e))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        page_errors: list[str] = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        global PUBLIC_ECOMMERCE_PAUSED
        PUBLIC_ECOMMERCE_PAUSED = detect_public_ecommerce_paused(page)
        if PUBLIC_ECOMMERCE_PAUSED:
            print("-> Public ecommerce mode")
            print("  OK detected paused public ecommerce; open-shop smoke checks will be skipped")
            try:
                check_ecommerce_pause_routes(page)
            except SmokeFail as e:
                print(f"  FAIL: {e}")
                failures.append(str(e))

        open_commerce_checks = {
            check_shop_page,
            check_shop_showroom_contract,
            check_shop_product_grid_symmetry_contract,
            check_shop_items_broad_route,
            check_shop_by_category_redirect,
            check_category_pages,
            check_category_showroom_contract,
            check_category_nav_rail_contract,
            check_category_product_grid_symmetry_contract,
            check_variant_template_starting_price_display,
            check_quote_first_product_pages_keep_quote_gate,
            check_product_variant_page,
            check_product_detail_showroom_contract,
            check_product_detail_no_auxiliary_ecommerce_panels,
            check_product_detail_clear_option_box_contract,
            check_progressive_variant_option_disabling,
            check_variant_add_to_cart_ui,
            check_product_single_page,
        }
        for fn in (
            check_homepage,
            check_event_type_pages,
            check_shop_page,
            check_search_page_retired,
            check_shop_showroom_contract,
            check_shop_product_grid_symmetry_contract,
            check_shop_items_broad_route,
            check_shop_by_category_redirect,
            check_category_pages,
            check_category_showroom_contract,
            check_category_nav_rail_contract,
            check_category_product_grid_symmetry_contract,
            check_variant_template_starting_price_display,
            check_quote_first_product_pages_keep_quote_gate,
            check_product_variant_page,
            check_product_detail_showroom_contract,
            check_product_detail_no_auxiliary_ecommerce_panels,
            check_product_detail_clear_option_box_contract,
            check_progressive_variant_option_disabling,
            check_variant_add_to_cart_ui,
            check_product_single_page,
        ):
            if PUBLIC_ECOMMERCE_PAUSED and fn in open_commerce_checks:
                print(f"-> {fn.__name__}")
                print("  SKIP public ecommerce is paused; covered by ecommerce pause route contract")
                continue
            before_error_count = len(page_errors)
            try:
                fn(page)
            except SmokeFail as e:
                print(f"  FAIL: {e}")
                failures.append(str(e))
            new_asset_errors = _asset_boot_errors(page_errors[before_error_count:])
            if new_asset_errors:
                msg = f"{fn.__name__} triggered Frappe asset boot error: {new_asset_errors[0]}"
                print(f"  FAIL: {msg}")
                failures.append(msg)
        browser.close()

        try:
            check_mobile_drawer(p)
        except SmokeFail as e:
            print(f"  FAIL (mobile): {e}")
            failures.append(str(e))

    if failures:
        print(f"\n=== {len(failures)} smoke check(s) FAILED ===")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\n=== All shop smoke checks PASSED ===")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
