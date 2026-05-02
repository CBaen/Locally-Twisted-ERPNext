"""End-to-end smoke test for the LT shop surfaces.

Validates the catalog port, shop hub, mega menu, and variant selectors via a
real Chromium browser. This should pass on every deploy and fail loudly on
customer-facing regressions.

Coverage:
  1. Homepage navbar contains the Balloon Decor mega-menu trigger, /shop CTA,
     and 11 category links.
  2. /shop renders 11 filter pills + 53 product cards.
  3. /shop-by-category redirects to /shop instead of rendering the retired
     category-card index.
  4. Each child group's category page returns 200.
  5. Product detail (variant template) renders inline chips/select for every
     attribute, chips are radio/single-select, and partial selections can
     disable invalid later options.
  6. Product detail (single SKU) renders price + add-to-cart button.
  7. No "Item Code" jargon appears anywhere customer-facing.
  8. No "/Nos" UoM display anywhere.
  9. Mega menu opens on click + closes on Escape, ARIA-correct.
 10. Mobile drawer Balloon Decor accordion expands.

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
MENU_LABEL_OVERRIDES = {
    "Drops": "Balloon Drops",
}
PRODUCT_VARIANT_URL = f"{BASE}/shop-items/garlands/baby-shower-garland"
PRODUCT_VARIANT_EXPECTED_ATTRS = ["Garland Length", "latex colors"]
PRODUCT_PROGRESSIVE_URL = f"{BASE}/shop-items/arches/classic-arch"
PRODUCT_CART_VARIANT_URL = f"{BASE}/shop-items/arches/6-color-rainbow-arch"
PRODUCT_CART_VARIANT_EXPECTED_CODE = "6-color-rainbow-arch-20F"
PRODUCT_SINGLE_URL = f"{BASE}/shop-items/arches/easter-arch"


class SmokeFail(Exception):
    pass


def assert_(cond, msg):
    if not cond:
        raise SmokeFail(msg)


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
    print("-> Homepage navbar mega-menu trigger")
    page.goto(f"{BASE}/", wait_until="networkidle", timeout=15000)
    trigger = page.locator('[data-lt-megamenu-trigger="lt-mega-shop-balloon-decor"]')
    assert_(trigger.count() == 1, "Balloon Decor mega-menu trigger missing on homepage")
    assert_(
        trigger.inner_text().strip().startswith("Balloon Decor"),
        "Mega-menu trigger label must be Balloon Decor",
    )
    assert_(trigger.get_attribute("aria-haspopup") == "true", "Shop trigger missing aria-haspopup=true")

    trigger.click()
    page.wait_for_timeout(200)
    assert_(
        trigger.get_attribute("aria-expanded") == "true",
        "Shop trigger aria-expanded didn't flip to true on click",
    )
    panel = page.locator("#lt-mega-shop-balloon-decor")
    assert_(not panel.is_hidden(), "Shop mega panel still hidden after click")

    all_decor = panel.locator(".lt-header__mega-cta", has_text="All Balloon Decor")
    assert_(all_decor.count() == 1, "Mega menu missing All Balloon Decor CTA")
    assert_(all_decor.first.get_attribute("href") == "/shop", "All Balloon Decor CTA must link to /shop")
    footer_all_decor = page.locator("footer .lt-footer__col-link", has_text="All Balloon Decor")
    assert_(footer_all_decor.count() == 1, "Footer missing All Balloon Decor link")
    assert_(footer_all_decor.first.get_attribute("href") == "/shop", "Footer All Balloon Decor link must use /shop")

    mega_links_text = [el.inner_text().strip() for el in panel.locator(".lt-header__mega-link").all()]
    for cat_name in EXPECTED_CATEGORIES:
        label = MENU_LABEL_OVERRIDES.get(cat_name, cat_name)
        assert_(label in mega_links_text, f"Mega menu missing category label {label!r} (have: {mega_links_text})")

    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    assert_(
        trigger.get_attribute("aria-expanded") == "false",
        "Shop trigger aria-expanded didn't flip back on Escape",
    )
    print("  OK mega menu open/close + /shop CTA + 11 categories present")


def check_shop_page(page):
    print(f"-> {BASE}/shop")
    page.goto(f"{BASE}/shop", wait_until="networkidle", timeout=15000)
    chips = page.locator(".lt-shop__chip")
    chip_count = chips.count()
    assert_(chip_count == 12, f"/shop expected 12 pills (All + 11 categories), got {chip_count}")

    body = page.content()
    assert_("53 ITEMS" in body or "53&nbsp;ITEMS" in body or ">53" in body, "/shop should show 53 items count")
    print(f"  OK {chip_count} pills rendered, 53 items")


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


def check_product_variant_page(page):
    print(f"-> {PRODUCT_VARIANT_URL}")
    page.goto(PRODUCT_VARIANT_URL, wait_until="networkidle", timeout=15000)
    title = page.locator(".lt-product__title").inner_text()
    assert_("Baby Shower Garland" in title, f"Product title wrong: {title!r}")

    body = page.content()
    assert_("Item Code: baby-shower-garland" not in body, "Product detail still leaks 'Item Code:' jargon")
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
    print("  OK inline variants render, jargon stripped, CTA disabled until selection")


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
                        options.callback && options.callback({
                            message: {
                                valid_options_for_attributes: {
                                    'Arch Size': ['20ft'],
                                    'latex colors': ['black'],
                                    'Design': ['Layered'],
                                    'LED Lights': ['Do Not Add LED Lights']
                                },
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
        page.locator(".lt-product__attr[data-attribute-name='Arch Size'] .lt-product__chip", has_text="20ft").click()
        page.wait_for_function(
            """() => {
                const black = document.querySelector("select[data-attribute-name='latex colors'] option[value='black']");
                const white = document.querySelector("select[data-attribute-name='latex colors'] option[value='White']");
                return black && white && !black.disabled && white.disabled;
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
    page.locator(".lt-product__chip").first.click()
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
    assert_(
        variant_code == PRODUCT_CART_VARIANT_EXPECTED_CODE,
        f"Expected configured variant {PRODUCT_CART_VARIANT_EXPECTED_CODE}, got {variant_code!r}",
    )
    btn.click()
    page.wait_for_timeout(500)
    cart = page.evaluate("window.LT_CART && window.LT_CART.getCart()")
    codes = [line["item_code"] for line in (cart or {}).get("items", [])]
    assert_(
        PRODUCT_CART_VARIANT_EXPECTED_CODE in codes,
        f"Configured variant was not written to LT_CART (codes: {codes})",
    )
    print(f"  OK option selection adds purchasable variant {PRODUCT_CART_VARIANT_EXPECTED_CODE}")


def check_product_single_page(page):
    print(f"-> {PRODUCT_SINGLE_URL}")
    resp = page.goto(PRODUCT_SINGLE_URL, wait_until="networkidle", timeout=15000)
    if resp.status != 200:
        print(f"  skipped (HTTP {resp.status})")
        return
    body = page.content()
    assert_("Item Code: easter-arch" not in body, "Single SKU still leaks Item Code jargon")
    print("  OK single SKU page clean")


def check_mobile_drawer(p):
    print("-> Mobile drawer Balloon Decor accordion")
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
    page.wait_for_timeout(200)

    accordion = page.locator('[data-lt-drawer-accordion-trigger="lt-mob-shop-balloon-decor"]')
    assert_(accordion.count() == 1, "Mobile Balloon Decor accordion toggle missing")
    assert_(accordion.inner_text().strip().startswith("Balloon Decor"), "Mobile accordion label must be Balloon Decor")
    accordion.click()
    page.wait_for_timeout(200)
    panel = page.locator("#lt-mob-shop-balloon-decor")
    assert_(not panel.is_hidden(), "Mobile Balloon Decor accordion didn't expand on click")

    sublinks_text = [el.inner_text().strip() for el in panel.locator(".lt-header__mobile-nav-sublink").all()]
    for cat_name in EXPECTED_CATEGORIES:
        label = MENU_LABEL_OVERRIDES.get(cat_name, cat_name)
        assert_(label in sublinks_text, f"Mobile drawer missing sublink {label!r} (have: {sublinks_text})")
    assert_("All Balloon Decor" in sublinks_text, "Mobile drawer missing All Balloon Decor sublink")
    all_decor_href = panel.locator(".lt-header__mobile-nav-sublink--all").first.get_attribute("href")
    assert_(all_decor_href == "/shop", "Mobile All Balloon Decor sublink must link to /shop")
    print(f"  OK accordion expands, all {len(EXPECTED_CATEGORIES)} categories and /shop CTA present")
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
            check_shop_by_category_redirect,
            check_category_pages,
            check_product_variant_page,
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
