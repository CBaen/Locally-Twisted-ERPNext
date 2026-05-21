"""Verify the Webshop Guest party infrastructure that public shopping depends on."""
from __future__ import annotations

from typing import Any

import frappe


EXPECTED_METHOD_OVERRIDES = {
    "webshop.webshop.shopping_cart.product_info.get_product_info_for_website": (
        "locally_twisted.overrides.website_item.get_guest_safe_product_info_for_website"
    ),
    "webshop.webshop.variant_selector.utils.get_next_attribute_and_values": (
        "locally_twisted.api.variant_selector.get_next_attribute_and_values"
    ),
}
EXPECTED_DOCTYPE_OVERRIDES = {
    "Website Item": "locally_twisted.overrides.website_item.LocallyTwistedWebsiteItem",
}
EXPECTED_GUARD_HANDLER = "locally_twisted.webshop_guest_party_guard.validate_guest_party_record"
EXPECTED_DELETE_GUARD_HANDLER = "locally_twisted.webshop_guest_party_guard.block_guest_party_delete"
EXPECTED_RENAME_GUARD_HANDLER = "locally_twisted.webshop_guest_party_guard.block_guest_party_rename"
EXPECTED_GUARD_EVENTS = {
    "User": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
        "on_trash": EXPECTED_DELETE_GUARD_HANDLER,
        "before_rename": EXPECTED_RENAME_GUARD_HANDLER,
    },
    "Customer": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
        "on_trash": EXPECTED_DELETE_GUARD_HANDLER,
        "before_rename": EXPECTED_RENAME_GUARD_HANDLER,
    },
    "Contact": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
        "on_trash": EXPECTED_DELETE_GUARD_HANDLER,
        "before_rename": EXPECTED_RENAME_GUARD_HANDLER,
    },
    "Has Role": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_insert": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
        "on_trash": EXPECTED_DELETE_GUARD_HANDLER,
    },
    "Portal User": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_insert": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
        "on_trash": EXPECTED_DELETE_GUARD_HANDLER,
    },
    "Dynamic Link": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_insert": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
        "on_trash": EXPECTED_DELETE_GUARD_HANDLER,
    },
    "Contact Email": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_insert": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
    },
    "Contact Phone": {
        "validate": EXPECTED_GUARD_HANDLER,
        "before_insert": EXPECTED_GUARD_HANDLER,
        "before_save": EXPECTED_GUARD_HANDLER,
        "on_change": EXPECTED_GUARD_HANDLER,
    },
}
EXPECTED_WEBSHOP_SETTINGS = {
    "enabled": 1,
    "show_price": 1,
    "login_required_to_view_products": 0,
    "hide_price_for_guest": 0,
    "enable_checkout": 1,
    "price_list": "Standard Selling",
    "default_customer_group": "Individual",
}


def run() -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {}

    _check_guest_user(failures, evidence)
    _check_guest_party(failures, evidence)
    _check_webshop_settings(failures, evidence)
    _check_hooks(failures, evidence)
    _check_public_pricing_paths(failures, warnings, evidence)
    _check_runtime_guard(failures, evidence)

    return {
        "ok": not failures,
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "warnings": warnings,
        "evidence": evidence,
    }


def _check_guest_user(failures: list[str], evidence: dict[str, Any]) -> None:
    guest_user = frappe.db.get_value(
        "User",
        "Guest",
        ["name", "user_type", "enabled"],
        as_dict=True,
    )
    roles = sorted(
        row.role
        for row in frappe.get_all(
            "Has Role",
            filters={"parent": "Guest"},
            fields=["role"],
        )
    )
    evidence["guest_user"] = dict(guest_user or {})
    evidence["guest_roles"] = roles

    if not guest_user:
        failures.append("User Guest is missing")
        return
    if guest_user.user_type != "Website User":
        failures.append(f"User Guest must stay Website User, found {guest_user.user_type!r}")
    if int(guest_user.enabled or 0) != 1:
        failures.append("User Guest must stay enabled for public sessions")
    forbidden_roles = sorted(set(roles) - {"Guest"})
    if forbidden_roles:
        failures.append(f"User Guest must not gain extra roles: {forbidden_roles}")


def _check_guest_party(failures: list[str], evidence: dict[str, Any]) -> None:
    customer = frappe.db.get_value(
        "Customer",
        "Guest",
        ["name", "customer_name", "customer_type", "customer_group", "disabled"],
        as_dict=True,
    )
    contact = frappe.db.get_value(
        "Contact",
        "Guest-Guest",
        ["name", "first_name", "status"],
        as_dict=True,
    )
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parent": "Guest-Guest", "link_doctype": "Customer", "link_name": "Guest"},
        fields=["parent", "parenttype", "link_doctype", "link_name"],
    )
    portal_users = frappe.get_all(
        "Portal User",
        filters={"user": "Guest", "parent": "Guest"},
        fields=["parent", "parenttype", "user"],
    )

    evidence["guest_customer"] = dict(customer or {})
    evidence["guest_contact"] = dict(contact or {})
    evidence["guest_dynamic_links"] = [dict(row) for row in links]
    evidence["guest_portal_users"] = [dict(row) for row in portal_users]

    if not customer:
        failures.append("Customer Guest is missing; anonymous Webshop party lookup can collapse")
    else:
        if customer.customer_group != "Individual":
            failures.append(f"Customer Guest customer_group expected 'Individual', found {customer.customer_group!r}")
        if int(customer.disabled or 0) != 0:
            failures.append("Customer Guest must not be disabled")

    if not contact:
        failures.append("Contact Guest-Guest is missing; Guest party link is incomplete")
    if not links:
        failures.append("Dynamic Link Guest-Guest -> Customer Guest is missing")
    if not portal_users:
        failures.append("Portal User link Guest -> Customer Guest is missing")


def _check_webshop_settings(failures: list[str], evidence: dict[str, Any]) -> None:
    settings = frappe.get_single("Webshop Settings")
    observed = {field: settings.get(field) for field in EXPECTED_WEBSHOP_SETTINGS}
    observed["company"] = settings.get("company")
    observed["payment_gateway_account"] = settings.get("payment_gateway_account")
    evidence["webshop_settings"] = observed

    for field, expected in EXPECTED_WEBSHOP_SETTINGS.items():
        actual = settings.get(field)
        if isinstance(expected, int):
            actual = int(actual or 0)
        if actual != expected:
            failures.append(f"Webshop Settings.{field} expected {expected!r}, found {settings.get(field)!r}")


def _check_hooks(failures: list[str], evidence: dict[str, Any]) -> None:
    method_overrides = frappe.get_hooks("override_whitelisted_methods") or {}
    doctype_overrides = frappe.get_hooks("override_doctype_class") or {}
    doc_events = frappe.get_doc_hooks()

    observed_methods: dict[str, list[str]] = {}
    for dotted_path, expected in EXPECTED_METHOD_OVERRIDES.items():
        values = _hook_values(method_overrides.get(dotted_path))
        observed_methods[dotted_path] = values
        if expected not in values:
            failures.append(f"Missing guest-safe method override for {dotted_path}: expected {expected}")

    observed_doctypes: dict[str, list[str]] = {}
    for doctype, expected in EXPECTED_DOCTYPE_OVERRIDES.items():
        values = _hook_values(doctype_overrides.get(doctype))
        observed_doctypes[doctype] = values
        if expected not in values:
            failures.append(f"Missing guest-safe doctype override for {doctype}: expected {expected}")

    evidence["hook_overrides"] = {
        "methods": observed_methods,
        "doctypes": observed_doctypes,
    }

    observed_doc_events: dict[str, dict[str, list[str]]] = {}
    for doctype, expected_events in EXPECTED_GUARD_EVENTS.items():
        observed_doc_events[doctype] = {}
        for event, expected in expected_events.items():
            values = _hook_values((doc_events.get(doctype) or {}).get(event))
            observed_doc_events[doctype][event] = values
            if expected not in values:
                failures.append(f"Missing Guest infrastructure guard for {doctype}.{event}: expected {expected}")
    evidence["guest_guard_doc_events"] = observed_doc_events


def _check_runtime_guard(failures: list[str], evidence: dict[str, Any]) -> None:
    probes = []
    for label, attempt in _guard_probe_attempts():
        try:
            attempt()
        except Exception as exc:
            if _is_expected_guard_exception(exc):
                probes.append({"label": label, "blocked": True, "message": _clean_exception_message(exc)})
            else:
                failures.append(f"{label} failed with an unexpected exception: {_clean_exception_message(exc)}")
                probes.append({"label": label, "blocked": False, "unexpected": _clean_exception_message(exc)})
        else:
            failures.append(f"{label} was allowed; Guest infrastructure is not protected")
            probes.append({"label": label, "blocked": False, "unexpected": "mutation allowed"})
        finally:
            frappe.db.rollback()
            _clear_guest_document_cache()

    evidence["runtime_guard_probes"] = probes


def _guard_probe_attempts():
    return [
        ("delete Customer:Guest", lambda: frappe.delete_doc("Customer", "Guest", ignore_permissions=True, force=True)),
        ("delete Contact:Guest-Guest", lambda: frappe.delete_doc("Contact", "Guest-Guest", ignore_permissions=True, force=True)),
        ("delete User:Guest", lambda: frappe.delete_doc("User", "Guest", ignore_permissions=True, force=True)),
        ("rename Customer:Guest", _attempt_rename_guest_customer),
        ("rename Contact:Guest-Guest", _attempt_rename_guest_contact),
        ("disable User:Guest", _attempt_disable_guest_user),
        ("disable Customer:Guest", _attempt_disable_guest_customer),
        ("remove Customer:Guest Portal User row", _attempt_remove_guest_portal_user),
        ("add extra User:Guest role", _attempt_add_guest_role),
        ("remove Contact:Guest-Guest Dynamic Link", _attempt_remove_guest_dynamic_link),
        ("add Contact:Guest-Guest email row", _attempt_add_guest_email),
    ]


def _attempt_rename_guest_customer() -> None:
    frappe.rename_doc("Customer", "Guest", "Guest-Rename-Probe", force=True)


def _attempt_rename_guest_contact() -> None:
    frappe.rename_doc("Contact", "Guest-Guest", "Guest-Guest-Rename-Probe", force=True)


def _attempt_disable_guest_user() -> None:
    doc = frappe.get_doc("User", "Guest")
    doc.enabled = 0
    doc.save(ignore_permissions=True)


def _attempt_disable_guest_customer() -> None:
    doc = frappe.get_doc("Customer", "Guest")
    doc.disabled = 1
    doc.save(ignore_permissions=True)


def _attempt_remove_guest_portal_user() -> None:
    doc = frappe.get_doc("Customer", "Guest")
    doc.set("portal_users", [])
    doc.save(ignore_permissions=True)


def _attempt_add_guest_role() -> None:
    doc = frappe.get_doc("User", "Guest")
    doc.append("roles", {"role": "System Manager"})
    doc.save(ignore_permissions=True)


def _attempt_remove_guest_dynamic_link() -> None:
    doc = frappe.get_doc("Contact", "Guest-Guest")
    doc.set("links", [])
    doc.save(ignore_permissions=True)


def _attempt_add_guest_email() -> None:
    doc = frappe.get_doc("Contact", "Guest-Guest")
    doc.append("email_ids", {"email_id": "guest-tamper-probe@example.invalid", "is_primary": 1})
    doc.save(ignore_permissions=True)


def _is_expected_guard_exception(exc: Exception) -> bool:
    from locally_twisted.webshop_guest_party_guard import WebshopGuestPartyProtectionError

    text = _clean_exception_message(exc)
    return (
        isinstance(exc, WebshopGuestPartyProtectionError)
        or "Webshop Guest" in text
        or "User Guest cannot be deleted" in text
        or "User Guest cannot be disabled" in text
    )


def _clean_exception_message(exc: Exception) -> str:
    return " ".join(str(exc).split())


def _clear_guest_document_cache() -> None:
    for doctype, name in (("User", "Guest"), ("Customer", "Guest"), ("Contact", "Guest-Guest")):
        try:
            frappe.clear_document_cache(doctype, name)
        except Exception:
            pass


def _check_public_pricing_paths(
    failures: list[str],
    warnings: list[str],
    evidence: dict[str, Any],
) -> None:
    proof = _find_variant_probe()
    evidence["variant_probe_candidate"] = proof
    if not proof:
        failures.append("Could not find a published variant Website Item to probe Guest pricing")
        return

    previous_user = frappe.session.user
    try:
        frappe.set_user("Guest")
        from locally_twisted.api.variant_selector import get_next_attribute_and_values
        from locally_twisted.overrides.website_item import get_guest_safe_product_info_for_website

        product_info = get_guest_safe_product_info_for_website(proof["variant_item_code"])
        variant_info = get_next_attribute_and_values(
            proof["template_item_code"],
            proof["selected_attributes"],
        )
    except Exception:
        failures.append(f"Guest product pricing probe crashed:\n{frappe.get_traceback()}")
        return
    finally:
        frappe.set_user(previous_user or "Administrator")

    price = (product_info.get("product_info") or {}).get("price") or {}
    selected_product_info = variant_info.get("product_info") or {}
    evidence["guest_product_info_probe"] = {
        "item_code": proof["variant_item_code"],
        "price": price,
    }
    evidence["guest_variant_selector_probe"] = {
        "template_item_code": proof["template_item_code"],
        "exact_match": variant_info.get("exact_match"),
        "filtered_items_count": variant_info.get("filtered_items_count"),
        "has_product_info": bool(selected_product_info),
    }

    if not price:
        warnings.append(f"Guest product info probe returned no price for {proof['variant_item_code']}")
    if not selected_product_info:
        failures.append("Guest variant selector returned no product_info for the exact variant probe")


def _find_variant_probe() -> dict[str, Any] | None:
    preferred = _probe_for_template("unicorn-bouquet")
    if preferred:
        return preferred

    candidates = frappe.get_all(
        "Website Item",
        filters={"published": 1},
        fields=["item_code", "route"],
        order_by="name asc",
        limit_page_length=100,
    )
    for candidate in candidates:
        probe = _probe_for_template(candidate.item_code)
        if probe:
            probe["route"] = candidate.route
            return probe
    return None


def _probe_for_template(template_item_code: str) -> dict[str, Any] | None:
    template = frappe.db.get_value(
        "Item",
        {"name": template_item_code, "has_variants": 1, "disabled": 0},
        ["name", "item_name"],
        as_dict=True,
    )
    if not template:
        return None

    variant = frappe.db.get_value(
        "Item",
        {"variant_of": template_item_code, "disabled": 0},
        ["name", "item_code"],
        as_dict=True,
    )
    if not variant:
        return None

    attrs = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": variant.name},
        fields=["attribute", "attribute_value"],
        order_by="idx asc",
    )
    selected = {
        row.attribute: row.attribute_value
        for row in attrs
        if row.attribute and row.attribute_value
    }
    if not selected:
        return None

    return {
        "template_item_code": template_item_code,
        "variant_item_code": variant.name,
        "selected_attributes": selected,
    }


def _hook_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]
