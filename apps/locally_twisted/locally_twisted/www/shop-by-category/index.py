"""
shop-by-category override controller.

Replaces apps/webshop/webshop/www/shop-by-category/index.py via same-path
resolution (locally_twisted is last in installed_apps so its www/ wins).

What changed vs webshop's stock controller:
  - Stock controller renders only when Webshop Settings.enable_field_filters=1
    AND filter_fields child table is populated. Out of the box that's empty,
    producing the "empty page" GL flagged.
  - LT controller renders the 11 Shop Items child Item Groups directly as a
    grid of cards. Each card links to /<route> for that category.
"""
import frappe

sitemap = 1


def get_context(context):
    context.body_class = "product-page lt-shop-by-category"
    context.no_cache = 0  # cacheable: this list changes only on Item Group fixture re-deploy

    children = frappe.db.get_all(
        "Item Group",
        filters={
            "parent_item_group": "Shop Items",
            "show_in_website": 1,
        },
        fields=["name", "item_group_name", "route", "image", "weightage"],
        order_by="weightage asc, item_group_name asc",
    )

    # Per-category product counts so the cards can show "10 items" honestly.
    for cat in children:
        cat["product_count"] = frappe.db.count(
            "Website Item",
            filters={"item_group": cat["name"], "published": 1},
        )

    context.shop_categories = children
    context.title = "Shop by Category"
    context.metatags = {
        "title": "Shop by Category — Locally Twisted",
        "description": "Browse balloon decor by what we make: arches, columns, bouquets, garlands, and more. Pickup or delivery along the Wasatch Front.",
    }
    return context
