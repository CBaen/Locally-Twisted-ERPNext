"""
Shop recon — viewport-only screenshots at desktop (1280) and mobile (375)
of the three shop surfaces, plus rendered DOM facts (titles, prices,
counts, descriptions, image srcs, console errors).

NOT full-page (full-page lies at extreme aspect ratios — see HANDOFF).
NOT a verdict — visual reality only after GL opens in their browser.

Outputs:
  scripts/verify/_screenshots/<ts>-shop-recon/
    {url-key}-{viewport}.png
    facts.json
    console.log

Run:
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/_oneshot_shop_recon.py
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8081"
TARGETS = [
    ("shop-by-category", f"{BASE}/shop-by-category"),
    ("shop-items", f"{BASE}/shop-items"),
    ("product-baby-shower-garland", f"{BASE}/shop/baby-shower-garland"),
    ("product-7-butterfly-column", f"{BASE}/shop/7-butterfly-column"),
    ("shop-redirect", f"{BASE}/shop"),
    ("all-products", f"{BASE}/all-products"),
]
VIEWPORTS = [
    ("desktop", {"width": 1280, "height": 800}, False),
    ("mobile", {"width": 375, "height": 812}, True),
]
TS = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
OUT = Path("scripts/verify/_screenshots") / f"{TS}-shop-recon"
OUT.mkdir(parents=True, exist_ok=True)


def grab_facts(page, url_key):
    """Pull what actually rendered, not what should have rendered."""
    facts = {}
    facts["title"] = page.title()
    facts["url_resolved"] = page.url
    facts["h1"] = [h.inner_text() for h in page.locator("h1").all()]
    facts["h2"] = [h.inner_text() for h in page.locator("h2").all()]
    facts["h3"] = [h.inner_text() for h in page.locator("h3").all()][:20]

    # Webshop-specific DOM signals
    facts["product_card_count"] = page.locator(".product-card, .website-list-item, [data-route]").count()
    facts["price_elements"] = [el.inner_text().strip() for el in page.locator(".product-price, .price").all()][:30]
    facts["item_group_links"] = [
        {"text": a.inner_text().strip(), "href": a.get_attribute("href")}
        for a in page.locator("a[href*='/shop-items'], a[href*='/shop-by-category']").all()
    ][:40]
    facts["breadcrumb"] = [a.inner_text().strip() for a in page.locator(".breadcrumb a, nav.breadcrumb a, ol.breadcrumb a").all()]

    # Product detail-specific
    facts["product_detail_image_count"] = page.locator(".product-image img, .website-image img, img[itemprop='image']").count()
    facts["item_code_visible"] = "Item Code" in page.content() or "item_code" in page.content().lower()
    facts["item_code_text_around"] = ""
    if facts["item_code_visible"]:
        # Try to locate the visible element with item-code text
        for sel in [".item-code", "[class*='item-code']", "[class*='item_code']"]:
            loc = page.locator(sel)
            if loc.count():
                facts["item_code_text_around"] = loc.first.inner_text()
                break

    # Variant/attribute UI signals
    facts["variant_form_count"] = page.locator("form.variant-form, .variant-attribute, .item-variants").count()
    facts["select_count"] = page.locator("select").count()
    facts["radio_groups"] = page.locator("input[type=radio]").count()

    # Cart UI
    facts["add_to_cart_button_count"] = page.locator("button:has-text('Add to Cart'), .btn-add-to-cart, [data-action='add-to-cart']").count()
    facts["buy_now_count"] = page.locator("button:has-text('Buy'), a:has-text('Buy')").count()

    # Generic header check
    facts["nav_top_links"] = [a.inner_text().strip() for a in page.locator(".lt-header__nav-link, .lt-header__mobile-nav-link").all()][:20]

    return facts


def main():
    console_log = []

    with sync_playwright() as p:
        for vp_key, vp_size, is_mobile in VIEWPORTS:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport=vp_size,
                is_mobile=is_mobile,
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 Version/16.0 Mobile/15E148 Safari/604.1"
                ) if is_mobile else None,
            )
            page = context.new_page()
            page.on("console", lambda msg: console_log.append(f"{msg.type}: {msg.text}"))
            page.on("pageerror", lambda exc: console_log.append(f"PAGEERROR: {exc}"))

            for url_key, url in TARGETS:
                console_log.append(f"=== {vp_key} :: {url_key} :: {url} ===")
                try:
                    page.goto(url, wait_until="networkidle", timeout=20000)
                    page.wait_for_timeout(800)
                    # Viewport-only screenshot — not full page
                    out_path = OUT / f"{url_key}-{vp_key}.png"
                    page.screenshot(path=str(out_path), full_page=False)
                    facts = grab_facts(page, url_key)
                    facts_path = OUT / f"{url_key}-{vp_key}.facts.json"
                    facts_path.write_text(json.dumps(facts, indent=2, ensure_ascii=False))
                    print(f"  {vp_key:<8} {url_key:<32} -> {out_path.name} ({facts.get('product_card_count', 0)} cards)")
                except Exception as e:
                    console_log.append(f"FAIL {url_key} ({vp_key}): {e}")
                    print(f"  {vp_key:<8} {url_key:<32} FAIL: {e}")

            browser.close()

    (OUT / "console.log").write_text("\n".join(console_log))
    print(f"\nOutputs in: {OUT}")


if __name__ == "__main__":
    main()
