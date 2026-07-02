"""Normalize customer-facing Product Setup bouquet-size copy."""
from __future__ import annotations

import frappe

from locally_twisted.catalog_variant_rules import BOUQUET_SIZE_LABELS


TEXT_FIELD_TARGETS = {
    "LT Product Blueprint Gallery Image": ("heading", "description", "operator_note"),
    "LT Product Blueprint Media Rule": ("attribute_value", "label", "operator_note"),
    "LT Product Blueprint Content Rule": ("attribute_value", "heading", "body", "operator_note"),
}


def execute():
    for doctype, fieldnames in TEXT_FIELD_TARGETS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        meta = frappe.get_meta(doctype)
        for fieldname in fieldnames:
            if not meta.has_field(fieldname):
                continue
            for old_value, new_value in BOUQUET_SIZE_LABELS.items():
                frappe.db.sql(
                    f"""
                    UPDATE `tab{doctype}`
                       SET `{fieldname}` = REPLACE(`{fieldname}`, %s, %s)
                     WHERE `{fieldname}` LIKE %s
                    """,
                    (old_value, new_value, f"%{old_value}%"),
                )
    _remove_source_shorthand_note()


def _remove_source_shorthand_note() -> None:
    if not frappe.db.exists("DocType", "LT Product Blueprint Gallery Image"):
        return
    frappe.db.sql(
        """
        UPDATE `tabLT Product Blueprint Gallery Image`
           SET operator_note = %s
         WHERE operator_note = %s
        """,
        (
            "Backfilled from source-approved product gallery media.",
            "Backfilled from source-approved catalog_data product gallery media.",
        ),
    )
