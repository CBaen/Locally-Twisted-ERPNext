#!/usr/bin/env python3
"""
Capture current ERPNext webshop pages (live + mirror spec) for state-vs-spec comparison.
Outputs to: _resources/webshop-state-vs-spec-2026-04-30/screenshots/now/
             _resources/webshop-state-vs-spec-2026-04-30/screenshots/spec/
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
MIRROR_DIR = Path("C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/odoo-live-mirror/pages")
NOW_DIR = Path("C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/webshop-state-vs-spec-2026-04-30/screenshots/now")
SPEC_DIR = Path("C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/webshop-state-vs-spec-2026-04-30/screenshots/spec")

LIVE_PAGES = [
    ("/all-products", "all-products"),
    ("/shop", "shop"),
    ("/shop-by-category", "shop-by-category"),
    ("/shop/category/balloon-arches-27", "category-balloon-arches"),
    ("/shop/baby-shower-garland-71", "product-baby-shower-garland"),
    ("/shop/cart", "cart"),
]

MIRROR_PAGES = [
    ("shop.html", "shop"),
    ("shop_baby-shower-garland-71.html", "product-baby-shower-garland"),
    ("shop_category_what-we-make-balloon-arches-26.html", "category-balloon-arches"),
    ("shop_cart.html", "cart"),
]

DESKTOP = {"width": 1366, "height": 900}
MOBILE = {"width": 375, "height": 812}

results = {}


def capture_live(page, url, label, viewport, vp_name):
    try:
        page.goto(BASE_URL + url, wait_until="networkidle", timeout=25000)
        page.wait_for_timeout(1000)
        out = NOW_DIR / f"{label}-{vp_name}.png"
        page.screenshot(path=str(out), full_page=True)
        title = page.title()
        h1_count = page.locator("h1").count()
        h1 = page.locator("h1").first.inner_text() if h1_count else ""
        product_count = page.locator(".oe_product, .o_wsale_product_item, [itemtype*='Product']").count()
        has_sidebar = page.locator("#products_grid_before, .o_wsale_products_sidebar, aside").count() > 0
        has_search = page.locator("input[type=search], .search-query").count() > 0
        has_sort = page.locator("[href*='order='], .o_wsale_sort").count() > 0
        results[f"{label}-{vp_name}"] = {
            "url": BASE_URL + url,
            "title": title,
            "h1": h1,
            "product_cards_visible": product_count,
            "has_sidebar": has_sidebar,
            "has_search": has_search,
            "has_sort": has_sort,
            "screenshot": str(out),
            "status": "ok",
        }
        print(f"  [ok] {label}-{vp_name}: {product_count} product cards, title={title!r}")
    except Exception as e:
        results[f"{label}-{vp_name}"] = {"url": BASE_URL + url, "status": f"error: {e}"}
        print(f"  [err] {label}-{vp_name}: {e}")


def capture_mirror(page, filename, label, viewport, vp_name):
    path = MIRROR_DIR / filename
    if not path.exists():
        print(f"  [skip] mirror {filename} not found")
        return
    file_url = "file:///" + str(path).replace("\\", "/")
    try:
        page.goto(file_url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(800)
        out = SPEC_DIR / f"{label}-{vp_name}.png"
        page.screenshot(path=str(out), full_page=True)
        product_count = page.locator(".oe_product, .o_wsale_product_grid_wrapper").count()
        print(f"  [ok] spec {label}-{vp_name}: {product_count} product cards")
    except Exception as e:
        print(f"  [err] spec {label}-{vp_name}: {e}")


def main():
    with sync_playwright() as p:
        # --- Desktop live pages ---
        print("\n=== Desktop (1366x900) — LIVE ===")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=DESKTOP)
        page = ctx.new_page()
        for url, label in LIVE_PAGES:
            capture_live(page, url, label, DESKTOP, "desktop")
        browser.close()

        # --- Mobile live pages ---
        print("\n=== Mobile (375x812) — LIVE ===")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=MOBILE, is_mobile=True)
        page = ctx.new_page()
        for url, label in LIVE_PAGES:
            capture_live(page, url, label, MOBILE, "mobile")
        browser.close()

        # --- Desktop mirror (spec) ---
        print("\n=== Desktop (1366x900) — SPEC MIRROR ===")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=DESKTOP)
        page = ctx.new_page()
        for filename, label in MIRROR_PAGES:
            capture_mirror(page, filename, label, DESKTOP, "desktop")
        browser.close()

        # --- Mobile mirror (spec) ---
        print("\n=== Mobile (375x812) — SPEC MIRROR ===")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=MOBILE, is_mobile=True)
        page = ctx.new_page()
        for filename, label in MIRROR_PAGES:
            capture_mirror(page, filename, label, MOBILE, "mobile")
        browser.close()

    print("\n=== Captured results ===")
    for k, v in results.items():
        print(f"  {k}: {v.get('status','?')} | products={v.get('product_cards_visible','?')} | h1={v.get('h1','')!r}")


if __name__ == "__main__":
    main()
