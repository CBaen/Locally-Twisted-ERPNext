"""Runtime guard for Webshop's required anonymous Guest party records."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _


GUEST_USER = "Guest"
GUEST_CUSTOMER = "Guest"
GUEST_CONTACT = "Guest-Guest"
GUEST_ROLE = "Guest"
GUEST_CUSTOMER_GROUP = "Individual"
PROTECTED_LINK = {
    "parent": GUEST_CONTACT,
    "parenttype": "Contact",
    "link_doctype": "Customer",
    "link_name": GUEST_CUSTOMER,
}
PROTECTED_PORTAL_USER = {
    "parent": GUEST_CUSTOMER,
    "parenttype": "Customer",
    "user": GUEST_USER,
}


class WebshopGuestPartyProtectionError(frappe.ValidationError):
    pass


def validate_guest_party_record(doc: Any, method: str | None = None, *args: Any, **kwargs: Any) -> None:
    """Block unsafe edits to the Guest infrastructure records."""
    if _guard_bypassed():
        return

    doctype = getattr(doc, "doctype", None)
    if doctype == "User" and doc.name == GUEST_USER:
        _validate_guest_user(doc)
    elif doctype == "Customer" and doc.name == GUEST_CUSTOMER:
        _validate_guest_customer(doc)
    elif doctype == "Contact" and doc.name == GUEST_CONTACT:
        _validate_guest_contact(doc)
    elif doctype == "Has Role":
        _validate_has_role_child(doc)
    elif doctype == "Portal User":
        _validate_portal_user_child(doc)
    elif doctype == "Dynamic Link":
        _validate_dynamic_link_child(doc)
    elif doctype in {"Contact Email", "Contact Phone"}:
        _validate_contact_detail_child(doc)


def block_guest_party_delete(doc: Any, method: str | None = None, *args: Any, **kwargs: Any) -> None:
    """Block deleting the required Guest infrastructure records."""
    if _guard_bypassed():
        return

    doctype = getattr(doc, "doctype", None)
    if doctype in {"User", "Customer"} and doc.name == GUEST_USER:
        _throw(f"{doctype}:{doc.name} is required Webshop Guest infrastructure and cannot be deleted.")
    if doctype == "Contact" and doc.name == GUEST_CONTACT:
        _throw("Contact:Guest-Guest is required Webshop Guest infrastructure and cannot be deleted.")
    if doctype == "Has Role" and _is_required_guest_role(doc):
        _throw("User:Guest must keep exactly the Guest role; that role row cannot be deleted.")
    if doctype == "Portal User" and _is_required_portal_user(doc):
        _throw("Customer:Guest must stay linked to User:Guest; that Portal User row cannot be deleted.")
    if doctype == "Dynamic Link" and _is_required_dynamic_link(doc):
        _throw("Contact:Guest-Guest must stay linked to Customer:Guest; that Dynamic Link cannot be deleted.")


def block_guest_party_rename(doc: Any, method: str | None = None, *args: Any, **kwargs: Any) -> None:
    """Block renaming the required Guest identity records."""
    if _guard_bypassed():
        return

    old_name = args[0] if args else getattr(doc, "name", None)
    doctype = getattr(doc, "doctype", None)
    protected_names = {
        "User": GUEST_USER,
        "Customer": GUEST_CUSTOMER,
        "Contact": GUEST_CONTACT,
    }
    if protected_names.get(str(doctype)) == old_name:
        _throw(f"{doctype}:{old_name} is required Webshop Guest infrastructure and cannot be renamed.")


def _validate_guest_user(doc: Any) -> None:
    if int(doc.get("enabled") or 0) != 1:
        _throw("User:Guest must stay enabled for anonymous public Webshop sessions.")
    if doc.get("user_type") != "Website User":
        _throw("User:Guest must stay a Website User.")

    roles = sorted({row.role for row in doc.get("roles") or [] if row.role})
    if roles != [GUEST_ROLE]:
        _throw(f"User:Guest must have exactly the Guest role; found {roles!r}.")


def _validate_guest_customer(doc: Any) -> None:
    expected_values = {
        "customer_name": GUEST_CUSTOMER,
        "customer_type": "Individual",
        "customer_group": GUEST_CUSTOMER_GROUP,
    }
    for fieldname, expected in expected_values.items():
        if doc.get(fieldname) != expected:
            _throw(f"Customer:Guest {fieldname} must stay {expected!r}.")
    if int(doc.get("disabled") or 0) != 0:
        _throw("Customer:Guest must not be disabled.")

    portal_users = [
        {
            "parent": row.parent,
            "parenttype": row.parenttype,
            "user": row.user,
        }
        for row in doc.get("portal_users") or []
        if row.user
    ]
    if portal_users != [PROTECTED_PORTAL_USER]:
        _throw("Customer:Guest must keep exactly one Portal User row linking User:Guest.")


def _validate_guest_contact(doc: Any) -> None:
    if doc.get("first_name") != GUEST_USER:
        _throw("Contact:Guest-Guest first_name must stay 'Guest'.")
    if doc.get("status") != "Passive":
        _throw("Contact:Guest-Guest status must stay Passive.")
    if doc.get("email_ids"):
        _throw("Contact:Guest-Guest must not store real email addresses.")
    if doc.get("phone_nos"):
        _throw("Contact:Guest-Guest must not store real phone numbers.")

    links = [
        {
            "parent": row.parent,
            "parenttype": row.parenttype,
            "link_doctype": row.link_doctype,
            "link_name": row.link_name,
        }
        for row in doc.get("links") or []
        if row.link_doctype or row.link_name
    ]
    if links != [PROTECTED_LINK]:
        _throw("Contact:Guest-Guest must keep exactly one Dynamic Link to Customer:Guest.")


def _validate_has_role_child(doc: Any) -> None:
    if doc.get("parent") == GUEST_USER and not _is_required_guest_role(doc):
        _throw("User:Guest cannot gain roles beyond Guest.")


def _validate_portal_user_child(doc: Any) -> None:
    touches_guest = doc.get("parent") == GUEST_CUSTOMER or doc.get("user") == GUEST_USER
    if touches_guest and not _is_required_portal_user(doc):
        _throw("Only Customer:Guest -> User:Guest is allowed for the Guest Portal User link.")


def _validate_dynamic_link_child(doc: Any) -> None:
    touches_guest = (
        doc.get("parent") == GUEST_CONTACT
        or (doc.get("link_doctype") == "Customer" and doc.get("link_name") == GUEST_CUSTOMER)
    )
    if touches_guest and not _is_required_dynamic_link(doc):
        _throw("Only Contact:Guest-Guest -> Customer:Guest is allowed for the Guest Dynamic Link.")


def _validate_contact_detail_child(doc: Any) -> None:
    if doc.get("parent") == GUEST_CONTACT:
        _throw("Contact:Guest-Guest cannot store email or phone detail rows.")


def _is_required_guest_role(doc: Any) -> bool:
    return doc.get("parent") == GUEST_USER and doc.get("parenttype") == "User" and doc.get("role") == GUEST_ROLE


def _is_required_portal_user(doc: Any) -> bool:
    return (
        doc.get("parent") == GUEST_CUSTOMER
        and doc.get("parenttype") == "Customer"
        and doc.get("user") == GUEST_USER
    )


def _is_required_dynamic_link(doc: Any) -> bool:
    return (
        doc.get("parent") == GUEST_CONTACT
        and doc.get("parenttype") == "Contact"
        and doc.get("link_doctype") == "Customer"
        and doc.get("link_name") == GUEST_CUSTOMER
    )


def _guard_bypassed() -> bool:
    return bool(getattr(frappe.flags, "lt_allow_webshop_guest_party_repair", False))


def _throw(message: str) -> None:
    frappe.throw(
        _(message),
        exc=WebshopGuestPartyProtectionError,
        title=_("Protected Webshop Guest Infrastructure"),
    )
