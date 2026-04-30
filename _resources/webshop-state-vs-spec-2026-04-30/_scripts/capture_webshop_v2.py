#!/usr/bin/env python3
"""
Capture current ERPNext webshop + mirror spec pages for state-vs-spec comparison.
Using the correct URL patterns discovered by probing the live site.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
MIRROR_DIR = Path("C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/odoo-live-mirror/pages")
NOW_DIR = Path("C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/webshop-state-vs-spec-2026-04-30/screenshots/now")
SPEC_DIR = Path("C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/_resources/webshop-state-vs-spec-2026-04-30/screenshots/spec")

# Correct live URLs
LIVE_PAGES = [
    ("/shop", "shop"),
    ("/all-products", "all-products"),
    ("/shop-by-category", "shop-by-category"),
    ("/shop-items/arches", "category-arches"),
    ("/shop-items/arches/6-color-rainbow-arch", "product-detail"),
    ("/cart", "cart"),
]

# Spec mirror pages
MIRROR_PAGES = [
    ("shop.html", "shop"),
    ("shop_category_what-we-make-balloon-arches-26.html", "category-arches"),
    ("shop_baby-shower-garland-71.html", "product-detail"),
    ("shop_cart.html", "cart"),
]

DESKTOP = {"width": 1366, "height": 900}
MOBILE = {"width": 375, "height": 812}


def scroll_and_wait(page):
    """Scroll to trigger lazy loads."""
    page.evaluate("""async () => {
        const dist = 300;
        const delay = 80;
        for (let y = 0; y < document.body.scrollHeight; y += dist) {
            window.scrollTo(0, y);
            await new Promise(r => setTimeout(r, delay));
        }
        window.scrollTo(0, 0);
    }""")
    page.wait_for_timeout(600)


def capture_live(page, url, label, vp_name):
    full_url = BASE_URL + url
    page.goto(full_url, wait_until="networkidle", timeout=25000)
    page.wait_for_timeout(1200)
    scroll_and_wait(page)
    out = NOW_DIR / f"{label}-{vp_name}.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"  saved: {out.name}")


def capture_mirror(page, filename, label, vp_name):
    path = MIRROR_DIR / filename
    if not path.exists():
        print(f"  skip (not found): {filename}")
        return
    file_url = "file:///" + str(path).replace("\\", "/")
    page.goto(file_url, wait_until="domcontentloaded", timeout=15000)
    page.wait_for_timeout(800)
    out = SPEC_DIR / f"{label}-{vp_name}.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"  saved: {out.name}")


def main():
    with sync_playwright() as p:
        print("\n--- Desktop (1366x900) LIVE ---")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=DESKTOP)
        page = ctx.new_page()
        for url, label in LIVE_PAGES:
            capture_live(page, url, label, "desktop")
        browser.close()

        print("\n--- Mobile (375x812) LIVE ---")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=MOBILE, is_mobile=True)
        page = ctx.new_page()
        for url, label in LIVE_PAGES:
            capture_live(page, url, label, "mobile")
        browser.close()

        print("\n--- Desktop (1366x900) SPEC MIRROR ---")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=DESKTOP)
        page = ctx.new_page()
        for filename, label in MIRROR_PAGES:
            capture_mirror(page, filename, label, "desktop")
        browser.close()

        print("\n--- Mobile (375x812) SPEC MIRROR ---")
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=MOBILE, is_mobile=True)
        page = ctx.new_page()
        for filename, label in MIRROR_PAGES:
            capture_mirror(page, filename, label, "mobile")
        browser.close()

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
