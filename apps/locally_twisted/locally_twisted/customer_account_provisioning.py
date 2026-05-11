"""Invite-only customer portal account provisioning."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _


CUSTOMER_ROLE = "Customer"
SUPPLIER_ROLE = "Supplier"


@frappe.whitelist()
def provision_customer_account(contact_name: str | None = None, commit: bool | int | str = False) -> dict[str, Any]:
    """Create or repair an invite-only Customer Website User for a Contact.

    This function deliberately does not send email or create a password-reset
    message. A future invite sender can call this first, then handle delivery
    through its own reviewed email gate.
    """
    contact_name = str(contact_name or "").strip()
    if not contact_name:
        _fail(_("Tiny snag: choose a customer contact before creating account access."))

    contact = frappe.get_doc("Contact", contact_name)
    contact.check_permission("write")

    email = _primary_email(contact)
    if not email:
        _fail(_("Tiny snag: this contact needs an email address before account access can be created."))

    customer = _linked_customer(contact)
    if not customer:
        _fail(_("Tiny snag: this contact must be linked to a Customer before account access can be created."))

    user = _get_or_create_customer_user(email, contact)
    changed = _ensure_customer_role(user)
    changed = _link_contact_to_user(contact, user.name) or changed

    if changed:
        user.save(ignore_permissions=True)

    if _as_bool(commit):
        frappe.db.commit()

    return {
        "ok": True,
        "created": bool(getattr(user.flags, "lt_created_customer_account", False)),
        "user": user.name,
        "contact": contact.name,
        "customer": customer,
        "user_type": user.user_type,
        "roles": sorted({row.role for row in user.roles}),
        "email_sent": False,
        "password_setup_required": True,
    }


def _get_or_create_customer_user(email: str, contact) -> Any:
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
        _assert_existing_user_safe_for_customer_portal(user)
        user.check_permission("write")
        return user

    if not frappe.has_permission("User", "create"):
        frappe.throw(
            _("Tiny snag: your account does not have permission to create customer portal users."),
            frappe.PermissionError,
        )

    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": contact.first_name or email.split("@", 1)[0],
            "middle_name": contact.middle_name,
            "last_name": contact.last_name,
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0,
            "roles": [{"role": CUSTOMER_ROLE}],
        }
    )
    user.flags.lt_created_customer_account = True
    user.insert(ignore_permissions=True)
    return user


def _assert_existing_user_safe_for_customer_portal(user) -> None:
    roles = {row.role for row in user.roles}
    if user.user_type != "Website User":
        _fail(
            _(
                "Tiny snag: {0} is already a backend user. Customer portal access must not reuse backend accounts."
            ).format(user.name)
        )
    if SUPPLIER_ROLE in roles:
        _fail(
            _(
                "Tiny snag: {0} already has supplier access. Customer and supplier portals must stay separate."
            ).format(user.name)
        )


def _ensure_customer_role(user) -> bool:
    roles = {row.role for row in user.roles}
    if CUSTOMER_ROLE in roles:
        return False
    user.append("roles", {"role": CUSTOMER_ROLE})
    return True


def _link_contact_to_user(contact, user_name: str) -> bool:
    contact.reload()
    existing = str(contact.get("user") or "").strip()
    if existing and existing != user_name:
        _fail(
            _(
                "Tiny snag: this contact is already linked to {0}. Please review the contact before changing account access."
            ).format(existing)
        )
    if existing == user_name:
        return False
    contact.user = user_name
    contact.save(ignore_permissions=True)
    return True


def _primary_email(contact) -> str:
    rows = [row for row in contact.get("email_ids", []) if str(row.get("email_id") or "").strip()]
    primary = next((row for row in rows if row.get("is_primary")), None)
    row = primary or (rows[0] if rows else None)
    return str(row.get("email_id") or "").strip().lower() if row else ""


def _linked_customer(contact) -> str:
    for row in contact.get("links", []):
        if row.get("link_doctype") == "Customer" and row.get("link_name"):
            return str(row.link_name)
    return ""


def _as_bool(value: bool | int | str) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    return bool(value)


def _fail(message: str) -> None:
    frappe.throw(message, frappe.ValidationError)
