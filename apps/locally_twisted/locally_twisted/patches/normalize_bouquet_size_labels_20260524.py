"""Replace supplier shorthand bouquet-size labels with customer-safe labels."""
from __future__ import annotations

import frappe

from locally_twisted.catalog_variant_rules import BOUQUET_SIZE_LABELS


def execute():
    for old_value, new_value in BOUQUET_SIZE_LABELS.items():
        frappe.db.sql(
            """
            UPDATE `tabItem Attribute Value`
               SET attribute_value = %s
             WHERE parent = %s
               AND attribute_value = %s
            """,
            (new_value, "Bouquet Size", old_value),
        )
        frappe.db.sql(
            """
            UPDATE `tabItem Variant Attribute`
               SET attribute_value = %s
             WHERE attribute = %s
               AND attribute_value = %s
            """,
            (new_value, "Bouquet Size", old_value),
        )

    _rebuild_bouquet_variant_caches()


def _rebuild_bouquet_variant_caches() -> None:
    try:
        from webshop.webshop.variant_selector.utils import ItemVariantsCacheManager
    except Exception:
        return

    rows = frappe.db.sql(
        """
        SELECT DISTINCT item.variant_of AS template
          FROM `tabItem Variant Attribute` attr
          JOIN `tabItem` item ON item.name = attr.parent
         WHERE attr.attribute = %s
           AND item.variant_of IS NOT NULL
           AND item.variant_of != ''
        """,
        ("Bouquet Size",),
        as_dict=True,
    )
    for row in rows:
        template = row.get("template")
        if template:
            ItemVariantsCacheManager(template).rebuild_cache()
