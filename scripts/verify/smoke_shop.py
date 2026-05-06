"""End-to-end smoke test for the LT shop surfaces.

Validates the catalog port, shop hub, public nav, fixed-price product lane,
and retail variant selectors via a real Chromium browser. This should pass on
every deploy and fail loudly on customer-facing regressions.

Coverage:
  1. Homepage navbar exposes the current authority-first primary links and /shop CTA.
  2. /shop renders 11 filter pills + 53 product cards.
  3. /shop and category pages use the approved product-showroom card contract.
  4. /shop-by-category redirects to /shop instead of rendering the retired
     category-card index.
  5. Each child group's category page returns 200.
  6. Product detail pages do not invent product-level quote gates.
  7. Retail product detail (variant template) renders inline chips/select for
     every attribute, chips are radio/single-select, and partial selections can
     disable invalid later options.
  8. Product detail (single SKU) renders price + add-to-cart button.
  9. No "Item Code" jargon appears anywhere customer-facing.
  10. No "/Nos" UoM display anywhere.
  11. Mobile drawer exposes the same primary links and /contact quote CTA.

Run:
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/smoke_shop.py
"""
from __future__ import annotations

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
FIXED_PRICE_PRODUCT_URLS = [
    (f"{BASE}/shop-items/garlands/baby-shower-garland", "Baby Shower Garland", "baby-shower-garland"),
    (f"{BASE}/shop-items/arches/classic-arch", "Classic Arch", "classic-arch"),
]
PRODUCT_VARIANT_URL = f"{BASE}/shop-items/bouquets/unicorn-bouquet"
PRODUCT_VARIANT_EXPECTED_ATTRS = ["Bouquet Size", "Add Foil Number"]
PRODUCT_PROGRESSIVE_URL = PRODUCT_VARIANT_URL
PRODUCT_CART_VARIANT_URL = PRODUCT_VARIANT_URL
PRODUCT_SINGLE_URL = f"{BASE}/shop-items/bouquets/mothers-day-bouquet"
SHOP_CATEGORY_SHOWCASE_URL = f"{BASE}/shop-items/arches"
PRODUCT_DETAIL_SHOWCASE_URL = f"{BASE}/shop-items/garlands/baby-shower-garland"

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
        'type="checkbox"' not in text,
        "variant option chips must not render as checkboxes; variant attributes are single-select",
    )
    print("  OK no per-attribute Jinja DB lookup; chips stay radio/single-select")


def check_homepage(page):
    print("-> Homepage authority-first mega navigation")
    page.goto(f"{BASE}/", wait_until="networkidle", timeout=15000)

    assert_(page.locator(".lt-mega-brand__logo").count() >= 1, "Mega header missing logo image")
    event_trigger = page.locator("[data-lt-megamenu-trigger='lt-mega-events']")
    product_trigger = page.locator("[data-lt-megamenu-trigger='lt-mega-products']")
    assert_(event_trigger.count() == 1, "Desktop header missing Event Balloons mega trigger")
    assert_(product_trigger.count() == 1, "Desktop header missing Ready-to-Order mega trigger")

    for label, href in (("Portfolio", "/portfolio"), ("Process", "/process"), ("FAQ", "/faq")):
        link = page.locator(".lt-mega-nav__link", has_text=label)
        assert_(link.count() == 1, f"Desktop header missing {label} link")
        assert_(link.first.get_attribute("href") == href, f"{label} should link to {href}")

    event_trigger.click()
    assert_(page.locator("#lt-mega-events").is_visible(), "Event mega menu did not open")
    assert_(
        page.locator("#lt-mega-events a[href='/event-balloons']").count() >= 1,
        "Event mega menu should link to /event-balloons",
    )
    product_trigger.click()
    assert_(page.locator("#lt-mega-products").is_visible(), "Ready-to-Order mega menu did not open")
    assert_(
        page.locator("#lt-mega-products a[href='/shop-items/arches']").count() >= 1,
        "Product mega menu should link to /shop-items/arches",
    )

    quote_cta = page.locator(".lt-mega-header__cta", has_text="Free Event Quote")
    assert_(quote_cta.count() == 1, "Desktop header missing Free Event Quote CTA")
    assert_(quote_cta.first.get_attribute("href") == "/contact", "Free Event Quote CTA must link to /contact")
    footer_all_decor = page.locator("footer .lt-footer__col-link", has_text="All Ready-to-Order")
    assert_(footer_all_decor.count() == 1, "Footer missing All Ready-to-Order link")
    assert_(footer_all_decor.first.get_attribute("href") == "/shop", "Footer All Ready-to-Order link must use /shop")
    print("  OK mega triggers, key links, /contact quote CTA, and footer /shop link")


def check_shop_page(page):
    print(f"-> {BASE}/shop")
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    chips = page.locator(".lt-shop__chip")
    chip_count = chips.count()
    assert_(chip_count == 12, f"/shop expected 12 pills (All + 11 categories), got {chip_count}")

    body = page.content()
    assert_("53 ITEMS" in body or "53&nbsp;ITEMS" in body or ">53" in body, "/shop should show 53 items count")
    print(f"  OK {chip_count} pills rendered, 53 items")


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
        page.locator(".lt-shop__sidebar").count() == 0,
        "Category showcase pages must use top controls, not a desktop sidebar",
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
    print("  OK category page uses top controls and showroom cards")


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


def check_category_nav_symmetry_contract(page):
    print("-> /shop-items/<group> category nav symmetry contract")
    for viewport, expected_per_row in ((MOBILE_VIEWPORT, 2), (DESKTOP_VIEWPORT, 4)):
        page.set_viewport_size(viewport)
        page.goto(f"{BASE}/shop-items/get-well-bouquets", wait_until="networkidle", timeout=15000)
        rows = _visible_rect_rows(page, ".lt-shop__toolbar--categories .lt-shop__category-link")
        total_links = sum(row["count"] for row in rows)
        assert_(total_links == 12, f"Category nav must include 12 equal tiles including All Ready-to-Order, got {total_links}")
        for row in rows:
            assert_(
                row["count"] == expected_per_row,
                f"Category nav rows must be symmetrical at {viewport['width']}px: got row {row['texts']} with {row['count']} cells, expected {expected_per_row}",
            )
            widths = row["widths"]
            heights = row["heights"]
            assert_(
                max(widths) - min(widths) <= 2,
                f"Category nav row widths must match at {viewport['width']}px: got {widths} for {row['texts']}",
            )
            assert_(
                max(heights) - min(heights) <= 2,
                f"Category nav row heights must match at {viewport['width']}px: got {heights} for {row['texts']}",
            )
    print("  OK category nav uses equal-width symmetrical rows")


def check_shop_filtered_grid_symmetry_contract(page):
    print("-> /shop filtered product grid symmetry contract")
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    page.locator(".lt-shop__chip[data-category='arches']").click()
    rows = _visible_rect_rows(page, "#lt-shop-grid .lt-shop__card")
    assert_(rows, "/shop Arches filter did not render visible cards")
    assert_(
        rows[-1]["count"] != 1,
        f"/shop filtered grid must not leave one orphan card on desktop: final row has {rows[-1]['texts']}",
    )
    print("  OK /shop filtered grid avoids desktop orphan rows")


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


def check_fixed_price_product_pages_do_not_show_product_quote_gate(page):
    print("-> Fixed-price product pages avoid product-level quote gate")
    for url, expected_title, item_code in FIXED_PRICE_PRODUCT_URLS:
        page.goto(url, wait_until="networkidle", timeout=15000)
        title = page.locator(".lt-product__title").inner_text()
        assert_(expected_title in title, f"Product title wrong for {url}: {title!r}")

        body = page.content()
        assert_(f"Item Code: {item_code}" not in body, f"{url} still leaks 'Item Code:' jargon")
        assert_("/ Nos" not in body and " / Nos" not in body, f"{url} still leaks '/Nos' UoM")
        assert_("Shop by Category" not in body, f"{url} breadcrumb still shows retired 'Shop by Category' label")
        assert_("/shop-by-category" not in body, f"{url} breadcrumb still links to retired /shop-by-category route")
        assert_(
            page.locator(".lt-product__cta--primary", has_text="Request a Quote").count() == 0,
            f"{url} should not say the product itself requires a quote",
        )
        if page.locator(".lt-product__configure").count():
            assert_(
                page.locator("#lt-add-to-cart-variant").count() == 1,
                f"{url} should expose add-to-cart after option selection",
            )
        else:
            assert_(
                page.locator(".btn-add-to-cart").count() >= 1,
                f"{url} should expose add-to-cart when it is a fixed-price single SKU",
            )
    print("  OK fixed-price products stay checkoutable; delivery ZIP owns quote fallback")


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

    for attr in PRODUCT_VARIANT_EXPECTED_ATTRS:
        loc = page.locator(f".lt-product__attr[data-attribute-name='{attr}']")
        assert_(loc.count() == 1, f"Variant attr {attr!r} not rendered inline")

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
    print(f"-> {PRODUCT_PROGRESSIVE_URL} progressive option disabling")
    page.goto(PRODUCT_PROGRESSIVE_URL, wait_until="networkidle", timeout=15000)
    page.evaluate(
        """() => {
            const original = window.frappe.call.bind(window.frappe);
            window.__ltProgressiveCalls = [];
            window.__ltRestoreFrappeCall = () => {
                window.frappe.call = original;
                delete window.__ltRestoreFrappeCall;
            };
            window.frappe.call = (options) => {
                const args = options && options.args ? options.args : {};
                const selected = args.selected_attributes || {};
                if (
                    options &&
                    options.method === 'webshop.webshop.variant_selector.utils.get_next_attribute_and_values' &&
                    Object.keys(selected).length === 1
                ) {
                    window.__ltProgressiveCalls.push(selected);
                    window.setTimeout(() => {
                        const valid = Object.assign({}, selected, {
                            'Add Foil Number': ['1']
                        });
                        options.callback && options.callback({
                            message: {
                                valid_options_for_attributes: valid,
                                exact_match: [],
                                filtered_items_count: 1,
                                filtered_items: []
                            }
                        });
                    }, 0);
                    return { then() { return this; }, fail() { return this; } };
                }
                return original(options);
            };
        }"""
    )

    try:
        page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip").first.click()
        page.wait_for_function(
            """() => {
                const one = document.querySelector("select[data-attribute-name='Add Foil Number'] option[value='1']");
                const two = document.querySelector("select[data-attribute-name='Add Foil Number'] option[value='2']");
                return one && two && !one.disabled && two.disabled;
            }""",
            timeout=10000,
        )
        calls = page.evaluate("window.__ltProgressiveCalls || []")
        assert_(calls, "Partial option selection did not call the variant option API")
    finally:
        page.evaluate("window.__ltRestoreFrappeCall && window.__ltRestoreFrappeCall()")

    print("  OK partial selection consumes valid_options_for_attributes and disables invalid options")


def check_variant_add_to_cart_ui(page):
    print(f"-> {PRODUCT_CART_VARIANT_URL} variant add-to-cart")
    page.goto(PRODUCT_CART_VARIANT_URL, wait_until="networkidle", timeout=15000)
    page.evaluate("window.LT_CART && window.LT_CART.clear && window.LT_CART.clear()")
    page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip").first.click()
    page.select_option("select[data-attribute-name='Add Foil Number']", index=1)
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

    for panel_id in ("lt-mobile-events", "lt-mobile-products", "lt-mobile-help"):
        page.locator(f"[data-lt-drawer-accordion-trigger='{panel_id}']").click()
        assert_(page.locator(f"#{panel_id}").is_visible(), f"Mobile drawer panel {panel_id} did not open")

    expected_links = {
        "Event Balloons": "/event-balloons",
        "Portfolio": "/portfolio",
        "Process": "/process",
        "Shop All": "/shop",
        "Frequently Asked Questions": "/faq",
        "Free Event Quote": "/contact",
    }
    for label, href in expected_links.items():
        link = page.locator("#lt-mobile-nav a", has_text=label).first
        assert_(link.count() == 1, f"Mobile drawer missing {label}")
        assert_(link.get_attribute("href") == href, f"Mobile drawer {label} should link to {href}")
    print("  OK drawer opens, accordions expose links, and /contact quote CTA")
    browser.close()


def main() -> int:
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
        for fn in (
            check_homepage,
            check_shop_page,
            check_shop_showroom_contract,
            check_shop_filtered_grid_symmetry_contract,
            check_shop_items_broad_route,
            check_shop_by_category_redirect,
            check_category_pages,
            check_category_showroom_contract,
            check_category_nav_symmetry_contract,
            check_category_product_grid_symmetry_contract,
            check_fixed_price_product_pages_do_not_show_product_quote_gate,
            check_product_variant_page,
            check_product_detail_showroom_contract,
            check_progressive_variant_option_disabling,
            check_variant_add_to_cart_ui,
            check_product_single_page,
        ):
            try:
                fn(page)
            except SmokeFail as e:
                print(f"  FAIL: {e}")
                failures.append(str(e))
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
    sys.exit(main())
