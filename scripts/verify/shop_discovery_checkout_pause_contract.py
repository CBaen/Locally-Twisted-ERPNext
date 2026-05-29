#!/usr/bin/env python3
"""Verify shop discovery can open without opening checkout."""
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


FILES = {
    "pause": ROOT / "apps/locally_twisted/locally_twisted/ecommerce_pause.py",
    "seo": ROOT / "apps/locally_twisted/locally_twisted/seo.py",
    "sitemap": ROOT / "apps/locally_twisted/locally_twisted/www/sitemap.py",
    "website_context": ROOT / "apps/locally_twisted/locally_twisted/website_context.py",
    "navbar_context": ROOT / "apps/locally_twisted/locally_twisted/navbar_context.py",
    "checkout": ROOT / "apps/locally_twisted/locally_twisted/www/checkout.py",
    "navbar": ROOT / "apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html",
    "footer": ROOT / "apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html",
    "shop": ROOT / "apps/locally_twisted/locally_twisted/www/shop.html",
    "item_add": ROOT / "apps/locally_twisted/locally_twisted/templates/generators/item/item_add_to_cart.html",
    "item_configure": ROOT / "apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html",
    "item_details": ROOT / "apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html",
}


class ContractFail(Exception):
    pass


def read(key: str) -> str:
    return FILES[key].read_text(encoding="utf-8")


def require(key: str, needle: str, message: str) -> None:
    if needle not in read(key):
        raise ContractFail(f"{FILES[key].relative_to(ROOT)}: {message}")


def forbid(key: str, needle: str, message: str) -> None:
    if needle in read(key):
        raise ContractFail(f"{FILES[key].relative_to(ROOT)}: {message}")


def require_order(key: str, first: str, second: str, message: str) -> None:
    text = read(key)
    first_pos = text.find(first)
    second_pos = text.find(second)
    if first_pos == -1 or second_pos == -1 or first_pos >= second_pos:
        raise ContractFail(f"{FILES[key].relative_to(ROOT)}: {message}")


def verify_pause_controls() -> None:
    for needle in (
        "SHOP_DISCOVERY_OPEN_DEFAULT = False",
        "CHECKOUT_PAUSED_DEFAULT = True",
        "SHOP_DISCOVERY_PUBLIC_PATHS",
        "CHECKOUT_PUBLIC_PATHS",
        "lt_shop_discovery_open",
        "lt_checkout_paused",
        "def is_shop_discovery_open",
        "def is_checkout_paused",
        "def is_shop_discovery_path",
        "def is_checkout_path",
    ):
        require("pause", needle, f"missing pause-control marker {needle!r}")
    require(
        "pause",
        "if is_ecommerce_paused():\n        return True",
        "broad ecommerce pause must force checkout paused",
    )
    require_order(
        "pause",
        "if is_checkout_path(path):",
        "if is_shop_discovery_path(path):",
        "checkout path must be tested before shop discovery path",
    )


def verify_indexing_and_sitemap() -> None:
    for key in ("seo", "sitemap"):
        require(key, "is_checkout_path", "must treat checkout/cart separately")
        require(key, "is_shop_discovery_open", "must read shop-discovery state")
        require(key, "is_shop_discovery_path", "must treat shop/category/product paths separately")
    require("seo", "if is_checkout_path(path):", "checkout/cart must remain noindex")
    require("seo", "not is_shop_discovery_open()", "shop pages must noindex while discovery is closed")
    require("sitemap", "if is_checkout_path(canonical):", "checkout/cart must stay out of sitemap")
    require("sitemap", "canonical == PAUSE_ROUTE", "pause route must stay out of sitemap")


def verify_context_and_navigation() -> None:
    for needle in ("lt_shop_discovery_open", "lt_checkout_paused"):
        require("website_context", needle, f"website context must expose {needle}")
    require("navbar_context", "is_shop_discovery_open", "navbar categories must follow shop discovery")
    require("navbar", "shop_discovery_open", "navbar must separate shop discovery from broad ecommerce pause")
    require("navbar", "checkout_paused", "navbar must hide cart by checkout pause")
    require("navbar", "action=\"{% if shop_discovery_open %}/shop{% else %}/contact{% endif %}\"", "search action must follow shop discovery")
    require("footer", "shop_discovery_open", "footer shop link must follow shop discovery")


def verify_checkout_blocking() -> None:
    require("checkout", "from locally_twisted.ecommerce_pause import is_checkout_paused", "checkout APIs must use checkout pause guard")
    require("checkout", "if not is_checkout_paused():", "checkout API guard must open only when checkout pause is false")
    forbid("checkout", "from locally_twisted.ecommerce_pause import is_ecommerce_paused", "checkout API guard must not use broad ecommerce pause")


def verify_customer_controls() -> None:
    require("shop", "checkout_paused", "shop cards must know whether checkout is paused")
    require("shop", "{% elif checkout_paused %}", "shop cards must avoid add-to-cart while checkout is paused")
    require("shop", "View details", "shop cards should send paused shoppers to product detail")
    require("item_add", "or checkout_paused", "simple product controls must show quote CTA while checkout is paused")
    require("item_add", "{% if not checkout_paused %}", "simple product add-to-cart script must not bind while checkout is paused")
    require("item_configure", "var checkoutPaused =", "variant controls must expose checkout pause to JS")
    require("item_configure", "disableAdd(msgCheckoutPaused)", "variant controls must keep add-to-cart disabled while checkout is paused")
    require("item_configure", "if (!checkoutPaused)", "variant add-to-cart click must not bind while checkout is paused")
    require("item_details", "Ready to browse", "product note must explain browse-only mode")


def main() -> int:
    verify_pause_controls()
    verify_indexing_and_sitemap()
    verify_context_and_navigation()
    verify_checkout_blocking()
    verify_customer_controls()
    print("[SHOP DISCOVERY CHECKOUT PAUSE] PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ContractFail as exc:
        print(f"[SHOP DISCOVERY CHECKOUT PAUSE] FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
