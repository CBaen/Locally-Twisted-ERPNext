"""Verify owner phone/action access stays provider-neutral and scoped."""
from __future__ import annotations

import json
import time

import frappe

from locally_twisted import owner_business_access
from locally_twisted.seed import owner_demo_data


OWNER_USER = "locallytwisted@gmail.com"
CARD_KEYS = {
    "id",
    "source_doctype",
    "source_name",
    "type",
    "title",
    "subtitle",
    "reason",
    "stage",
    "when",
    "location",
    "preferred_contact_method",
    "email",
    "phone",
    "phone_href",
    "sms_href",
    "message_draft",
    "record_url",
}


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    marker = f"LT-CONTRACT-OWNER-ACTIONS-{int(time.time() * 1000)}"
    original_user = frappe.session.user
    try:
        frappe.set_user("Administrator")
        owner_demo_data.sync(marker)
        _assert_owner_user_exists()

        frappe.set_user(OWNER_USER)
        context = owner_business_access.action_center_context(limit=12)
        _assert_context_boundary(context)
        lead_card = _first_marker_card(context.get("urgent_contacts") or [], marker)
        booking_card = _first_marker_card(context.get("upcoming_bookings") or [], marker)
        _assert_card(lead_card, expected_type="lead")
        _assert_card(booking_card, expected_type="booking")
        _assert_log_contact_attempt(lead_card, marker)
        _assert_non_owner_blocked()

        return {
            "ok": True,
            "marker": marker,
            "owner_user": OWNER_USER,
            "provider_neutral": True,
            "customer_send_allowed": False,
            "read_surfaces": ["action_center", "urgent_contacts", "upcoming_bookings", "search_contacts"],
            "write_surfaces": ["log_contact_attempt"],
            "fake_records_cleaned_up": True,
            "failures": [],
        }
    except ContractFail as exc:
        return {"ok": False, "marker": marker, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "marker": marker, "failures": [frappe.get_traceback()]}
    finally:
        frappe.set_user("Administrator")
        owner_demo_data.cleanup_demo_data(marker)
        frappe.db.commit()
        frappe.set_user(original_user)


def _assert_owner_user_exists() -> None:
    if not frappe.db.exists("User", OWNER_USER):
        raise ContractFail(f"{OWNER_USER} does not exist")
    roles = set(frappe.get_roles(OWNER_USER))
    if "LT Owner Access" not in roles and "System Manager" not in roles:
        raise ContractFail(f"{OWNER_USER} is missing owner access")


def _assert_context_boundary(context: dict[str, object]) -> None:
    if context.get("ok") is not True:
        raise ContractFail("action_center_context did not return ok=True")
    boundaries = context.get("boundaries") or {}
    expected = {
        "provider_neutral": True,
        "raw_erpnext_records": False,
        "customer_send_allowed": False,
        "human_tap_required_for_call_or_text": True,
    }
    for key, value in expected.items():
        if boundaries.get(key) is not value:
            raise ContractFail(f"owner boundary {key} expected {value!r}, found {boundaries.get(key)!r}")
    identity = context.get("identity") or {}
    if "lt.owner.read" not in (identity.get("read_scopes") or []):
        raise ContractFail("owner DTO identity is missing lt.owner.read")
    if "lt.contact-log.write" not in (identity.get("write_scopes") or []):
        raise ContractFail("owner DTO identity is missing lt.contact-log.write")


def _first_marker_card(cards: list[dict[str, object]], marker: str) -> dict[str, object]:
    marker_text = marker.lower()
    for card in cards:
        if marker_text in json.dumps(card, default=str).lower():
            return card
    raise ContractFail(f"No owner action card found for marker {marker}")


def _assert_card(card: dict[str, object], *, expected_type: str) -> None:
    extra_keys = sorted(set(card) - CARD_KEYS)
    if extra_keys:
        raise ContractFail(f"{expected_type} card exposes raw/unapproved keys: {', '.join(extra_keys)}")
    if card.get("type") != expected_type:
        raise ContractFail(f"card type expected {expected_type!r}, found {card.get('type')!r}")
    if not str(card.get("phone_href") or "").startswith("tel:"):
        raise ContractFail(f"{expected_type} card missing tel: link")
    if not str(card.get("sms_href") or "").startswith("sms:"):
        raise ContractFail(f"{expected_type} card missing sms: link")
    if not str(card.get("record_url") or "").startswith("/app/"):
        raise ContractFail(f"{expected_type} card missing Desk record URL")


def _assert_log_contact_attempt(card: dict[str, object], marker: str) -> None:
    before_comments = frappe.db.count("Comment")
    before_email_queue = frappe.db.count("Email Queue") if frappe.db.exists("DocType", "Email Queue") else 0
    result = owner_business_access.log_contact_attempt(
        source_doctype=str(card["source_doctype"]),
        source_name=str(card["source_name"]),
        channel="call",
        note=f"{marker} verifier call note",
    )
    if result.get("ok") is not True:
        raise ContractFail("log_contact_attempt did not return ok=True")
    if frappe.db.count("Comment") != before_comments + 1:
        raise ContractFail("log_contact_attempt did not create exactly one Comment")
    after_email_queue = frappe.db.count("Email Queue") if frappe.db.exists("DocType", "Email Queue") else 0
    if after_email_queue != before_email_queue:
        raise ContractFail("log_contact_attempt created an Email Queue row")


def _assert_non_owner_blocked() -> None:
    frappe.set_user("Guest")
    try:
        owner_business_access.action_center_context(limit=1)
    except frappe.PermissionError:
        return
    finally:
        frappe.set_user(OWNER_USER)
    raise ContractFail("Guest was able to read owner action center data")
