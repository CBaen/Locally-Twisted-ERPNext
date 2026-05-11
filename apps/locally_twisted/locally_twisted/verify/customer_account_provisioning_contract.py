"""Verify invite-only customer account provisioning boundaries."""
from __future__ import annotations

import time

import frappe


class ContractFail(Exception):
    pass


def run() -> dict:
    try:
        result = _run_contract()
        return {"ok": True, **result}
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.rollback()


def _run_contract() -> dict:
    from locally_twisted.customer_account_provisioning import provision_customer_account

    before = _side_effect_counts()
    valid_contact = _make_customer_contact("valid")
    missing_customer_contact = _make_standalone_contact("missing-customer")
    missing_email_contact = _make_customer_contact("missing-email", include_email=False)

    provisioned = provision_customer_account(valid_contact)
    if provisioned.get("created") is not True:
        raise ContractFail(f"valid contact should create a Customer Website User: {provisioned}")
    user = frappe.get_doc("User", provisioned["user"])
    if user.user_type != "Website User":
        raise ContractFail(f"provisioned user should be Website User, found {user.user_type}")
    if "Customer" not in {row.role for row in user.roles}:
        raise ContractFail("provisioned user is missing Customer role")
    if user.enabled != 1:
        raise ContractFail("provisioned user should be enabled")
    if frappe.db.get_value("Contact", valid_contact, "user") != user.name:
        raise ContractFail("provisioning should link Contact.user to the created User")

    second = provision_customer_account(valid_contact)
    if second.get("created") is not False or second.get("user") != user.name:
        raise ContractFail(f"second provisioning run should reuse the existing user: {second}")

    _assert_blocks("missing Customer link", lambda: provision_customer_account(missing_customer_contact))
    _assert_blocks("missing primary email", lambda: provision_customer_account(missing_email_contact))

    system_user_email = _make_backend_user_customer_role()
    backend_contact = _make_customer_contact("backend-user", email=system_user_email)
    _assert_blocks("existing System User collision", lambda: provision_customer_account(backend_contact))

    after = _side_effect_counts()
    if before != after:
        raise ContractFail(f"provisioning should not queue/send messages: before={before} after={after}")

    return {
        "valid_contact": valid_contact,
        "user": user.name,
        "created": True,
        "second_run_reused": True,
        "blocked_cases": [
            "missing Customer link",
            "missing primary email",
            "existing System User collision",
        ],
        "side_effect_counts": after,
        "rolled_back": True,
    }


def _make_customer_contact(slug: str, *, include_email: bool = True, email: str | None = None) -> str:
    stamp = int(time.time() * 1000)
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT Account Contract {slug} {stamp}",
            "customer_type": "Individual",
        }
    ).insert(ignore_permissions=True)
    contact = {
        "doctype": "Contact",
        "first_name": "Account",
        "last_name": slug.title(),
        "links": [{"link_doctype": "Customer", "link_name": customer.name}],
    }
    if include_email:
        contact["email_ids"] = [
            {
                "email_id": email or f"lt-account-{slug}-{stamp}@example.invalid",
                "is_primary": 1,
            }
        ]
    return frappe.get_doc(contact).insert(ignore_permissions=True).name


def _make_standalone_contact(slug: str) -> str:
    stamp = int(time.time() * 1000)
    return frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": "Account",
            "last_name": slug.title(),
            "email_ids": [{"email_id": f"lt-account-{slug}-{stamp}@example.invalid", "is_primary": 1}],
        }
    ).insert(ignore_permissions=True).name


def _make_backend_user_customer_role() -> str:
    email = f"lt-account-backend-{int(time.time() * 1000)}@example.invalid"
    frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Backend",
            "last_name": "Collision",
            "enabled": 1,
            "user_type": "System User",
            "send_welcome_email": 0,
            "roles": [{"role": "System Manager"}, {"role": "Customer"}],
        }
    ).insert(ignore_permissions=True)
    return email


def _assert_blocks(label: str, action) -> None:
    try:
        action()
    except frappe.ValidationError:
        return
    except Exception as exc:
        if exc.__class__.__name__.endswith("Error"):
            return
        raise
    raise ContractFail(f"{label} should fail loudly")


def _side_effect_counts() -> dict[str, int]:
    return {
        "Email Queue": frappe.db.count("Email Queue"),
        "Communication": frappe.db.count("Communication"),
    }
