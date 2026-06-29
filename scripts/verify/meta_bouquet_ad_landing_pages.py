#!/usr/bin/env python3
"""Verify the LT missionary Meta ad landing-page source contract."""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "apps" / "locally_twisted" / "locally_twisted"


EXPECTED = {
    "missionary_balloon_gift": {
        "route": "/missionary-balloon-gift",
        "product_url": "/shop-items/bouquets/large-head-missionary",
        "item_code": "large-head-missionary",
        "content": "missionary_gift_ad_v1",
    },
}

MISSIONARY_BLOCKLIST = (
    "are you christian",
    "are you lds",
    "are you mormon",
    "your religion",
    "your faith",
    "your missionary",
    "other christians",
    "other lds",
    "other mormons",
)

MISSIONARY_REQUIRED_CONTEXT = (
    "mission calling",
    "slc airport",
    "homecoming",
    "farewell party",
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def load_pages():
    sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))
    return importlib.import_module("locally_twisted.www.product_ad_pages")


def check_page_data() -> None:
    module = load_pages()
    pages = module.PRODUCT_AD_PAGES
    assert_true(set(EXPECTED).issubset(pages), "expected ad page keys should be present")

    for key, expected in EXPECTED.items():
        page = pages[key]
        assert_true(page["route_path"] == expected["route"], f"{key} route should match customer URL")
        assert_true(page["product_url"] == expected["product_url"], f"{key} should link to the approved product page")
        assert_true("utm_" not in page["product_url"], f"{key} product CTA should not hard-code ad UTMs")
        assert_true(page["item_code"] == expected["item_code"], f"{key} item code should match the live product")
        assert_true(page["hero_image"].startswith("/"), f"{key} hero image should be site-local")
        assert_true(page["primary_label"], f"{key} should have a primary CTA label")

        parsed = urlparse(page["final_url"])
        params = parse_qs(parsed.query)
        assert_true(parsed.path == expected["route"], f"{key} final URL path should be the landing page")
        assert_true(params.get("utm_source") == ["meta"], f"{key} final URL should identify Meta source")
        assert_true(params.get("utm_medium") == ["paid_social"], f"{key} final URL should identify paid social medium")
        assert_true(params.get("utm_campaign") == [module.AD_CAMPAIGN_SLUG], f"{key} final URL campaign should be stable")
        assert_true(params.get("utm_content") == [expected["content"]], f"{key} final URL content should identify the ad")

    missionary_copy = " ".join(
        str(load_pages().PRODUCT_AD_PAGES["missionary_balloon_gift"].get(field, ""))
        for field in ("title", "description", "eyebrow", "lede", "use_lede", "cta_title", "cta_body")
    ).lower()
    for phrase in MISSIONARY_BLOCKLIST:
        assert_true(phrase not in missionary_copy, f"missionary ad copy should avoid personal-attribute phrase {phrase!r}")
    for phrase in MISSIONARY_REQUIRED_CONTEXT:
        assert_true(phrase in missionary_copy, f"missionary ad copy should include local buyer context {phrase!r}")


def check_missionary_product_source_copy() -> None:
    source = read("apps/locally_twisted/locally_twisted/seed/seed_product_copy.py").lower()
    for phrase in ("mission calling", "slc airport", "homecomings", "open houses", "farewell events"):
        assert_true(phrase in source, f"source product copy should include {phrase!r}")
    assert_true(
        "day someone leaves on a mission" not in source,
        "source product copy should not keep the old departure-first framing",
    )


def check_routes_and_seo() -> None:
    hooks = read("apps/locally_twisted/locally_twisted/hooks.py")
    seo = read("apps/locally_twisted/locally_twisted/seo.py")
    layout = read("scripts/verify/layout_helpers.js")
    for expected in EXPECTED.values():
        route = expected["route"]
        module_route = route.strip("/").replace("-", "_")
        assert_true(route in hooks, f"{route} should have a dashed route rule")
        assert_true(module_route in hooks, f"{route} should map to the underscore module")
        assert_true(route in seo, f"{route} should be present in SEO canonical/social mapping")
        assert_true(route in layout, f"{route} should be part of public layout verification")


def check_templates() -> None:
    template = read("apps/locally_twisted/locally_twisted/templates/includes/product_ad_page.html")
    forbidden = ("fbq(", "gtag(", "connect.facebook.net", "googletagmanager.com")
    for marker in forbidden:
        assert_true(marker not in template, f"landing template should not send platform events directly: {marker}")
    assert_true("data-lt-preserve-attribution" in template, "landing CTAs should preserve ad attribution from the URL")
    assert_true("URLSearchParams" in template, "landing page should preserve allowed UTM/fbclid params")
    assert_true("data-lt-ad-primary-cta" in template, "landing page should expose primary CTA markers")

    for key in EXPECTED:
        html = read(f"apps/locally_twisted/locally_twisted/www/{key}.html")
        py = read(f"apps/locally_twisted/locally_twisted/www/{key}.py")
        assert_true("product_ad_page.html" in html, f"{key} should use the shared landing template")
        assert_true("no_cache = 1" in py, f"{key} should avoid stale ad-page rendering")
        assert_true("sitemap = 1" in py, f"{key} should be eligible for normal public indexing")


def check_stale_checkout_pause_copy() -> None:
    faq = read("apps/locally_twisted/locally_twisted/www/faq.html").lower()
    contact = read("apps/locally_twisted/locally_twisted/www/contact.html").lower()
    stale_phrases = (
        "online checkout is paused",
        "while ready-to-order is paused",
        "ready-to-order is paused",
    )
    for phrase in stale_phrases:
        assert_true(phrase not in faq, f"FAQ should not keep stale checkout pause wording: {phrase!r}")
        assert_true(phrase not in contact, f"contact page should not keep stale checkout pause wording: {phrase!r}")
    assert_true(
        "checkout is available on ready-to-order product pages" in faq,
        "FAQ should explain that checkout is available where a product page shows it",
    )


def main() -> int:
    checks = [
        check_page_data,
        check_missionary_product_source_copy,
        check_routes_and_seo,
        check_templates,
        check_stale_checkout_pause_copy,
    ]
    failures: list[str] = []
    for check in checks:
        try:
            check()
            print(f"[PASS] {check.__name__}")
        except Exception as exc:
            failures.append(f"{check.__name__}: {exc}")
            print(f"[FAIL] {check.__name__}: {exc}")
    if failures:
        print("\n[META MISSIONARY AD LANDING PAGE] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\n[META MISSIONARY AD LANDING PAGE] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
