"""Guard owner-like users from direct public catalog mutations.

The safe owner workflow is Product Blueprint -> preview -> guarded apply.
Direct Desk edits to Item, Website Item, Item Price, variant attributes, item
groups, Webshop gallery records, and Webshop Settings can desync public pages,
pricing, media, or checkout.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import frappe
from frappe import _


TITLE = "Protected Owner Catalog Guard"
OWNER_ACCESS_ROLE = "LT Owner Access"
OWNER_USERS = {"locallytwisted@gmail.com"}

ALLOWED_CONTEXTS = {
    "blueprint_local_apply",
    "classification_contract_apply",
    "catalog_import_rehearsal",
    "price_repair_contract",
    "ecommerce_break_lab_restore",
}

PROTECTED_DOCTYPES = {
    "Item": "product records",
    "Website Item": "public product pages",
    "Item Price": "public product prices",
    "Item Attribute": "product option axes",
    "Item Attribute Value": "product option values",
    "Item Variant Attribute": "product variant options",
    "Item Group": "shop categories",
    "Website Slideshow": "public product gallery records",
    "Website Slideshow Item": "public product gallery photos",
    "Webshop Settings": "storefront settings",
}

OWNER_COPY = {
    "Item": "This product record is protected because it can change public pages, prices, or checkout.",
    "Website Item": "This product page is protected because it is connected to the public shop.",
    "Item Price": "Price changes need a guarded product update so the website, cart, and checkout use the same price.",
    "Item Attribute": "Product option axes need a guarded update so variants and prices stay matched.",
    "Item Attribute Value": "Product option values need a guarded update so variants and prices stay matched.",
    "Item Variant Attribute": "Variant option changes need a guarded update so customer choices resolve to exactly one price.",
    "Item Group": "Shop category changes need a guarded update so navigation, routes, and breadcrumbs stay coherent.",
    "Website Slideshow": "Product gallery changes need a guarded product update so public photos stay tied to the right product.",
    "Website Slideshow Item": "Product gallery photo changes need a guarded product update so public photos stay tied to the right product.",
    "Webshop Settings": "Store settings are protected because they can hide prices, block guests, or change checkout.",
}


@contextmanager
def catalog_guard_context(context: str) -> Iterator[None]:
    """Temporarily allow a named server-side guarded catalog operation."""
    if context not in ALLOWED_CONTEXTS:
        frappe.throw(_(f"Unknown catalog guard context: {context}"))

    previous = getattr(frappe.flags, "lt_owner_catalog_guard_context", None)
    frappe.flags.lt_owner_catalog_guard_context = context
    try:
        yield
    finally:
        if previous is None:
            frappe.flags.pop("lt_owner_catalog_guard_context", None)
        else:
            frappe.flags.lt_owner_catalog_guard_context = previous


def validate_owner_catalog_mutation(doc, method: str | None = None, *args, **kwargs) -> None:
    """Block owner-like direct edits to protected catalog records."""
    doctype = getattr(doc, "doctype", None)
    if doctype not in PROTECTED_DOCTYPES:
        return
    if _has_allowed_context():
        return
    if not _is_owner_like_user():
        return

    message = _blocked_message(doctype, doc, method)
    _log_block(doc, method, message)
    frappe.throw(_(message), frappe.PermissionError, title=TITLE)


def _has_allowed_context() -> bool:
    return getattr(frappe.flags, "lt_owner_catalog_guard_context", None) in ALLOWED_CONTEXTS


def _is_owner_like_user() -> bool:
    user = frappe.session.user
    if user in {"Administrator", "Guest"}:
        return False
    if user in OWNER_USERS:
        return True
    return OWNER_ACCESS_ROLE in set(frappe.get_roles(user))


def _blocked_message(doctype: str, doc, method: str | None) -> str:
    action = _action_label(method)
    record = getattr(doc, "name", None) or getattr(doc, "item_code", None) or "this record"
    owner_copy = OWNER_COPY.get(
        doctype,
        "This catalog change is protected because it can affect public products.",
    )
    return (
        f"{owner_copy} Please use Product Setup or a guarded product update. "
        f"Blocked {action} on {doctype} {record}."
    )


def _action_label(method: str | None) -> str:
    method = str(method or "").strip()
    labels = {
        "before_insert": "create",
        "before_save": "save",
        "validate": "save",
        "on_change": "change",
        "on_update": "update",
        "on_trash": "delete",
        "before_rename": "rename",
    }
    return labels.get(method, method or "change")


def _log_block(doc, method: str | None, message: str) -> None:
    try:
        frappe.log_error(
            title=TITLE,
            message="\n".join(
                [
                    message,
                    f"doctype={getattr(doc, 'doctype', '')}",
                    f"name={getattr(doc, 'name', '')}",
                    f"method={method or ''}",
                    f"user={frappe.session.user}",
                    f"context={getattr(frappe.flags, 'lt_owner_catalog_guard_context', '')}",
                ]
            ),
        )
    except Exception:
        # The guard itself must not fail open because Error Log had a problem.
        pass
