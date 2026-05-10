"""Verify code-owned customer-facing policy lanes for pages and emails."""
from __future__ import annotations

import time
from html import unescape
from quopri import decodestring

import frappe


class ContractFail(Exception):
    pass


REQUIRED_ANCHORS = (
    "event-balloon-decor",
    "ready-to-order-pickup-delivery",
    "face-painting-balloon-twisting",
    "corporate-invoicing",
)


def run():
    original_commit = frappe.db.commit
    original_in_test = frappe.flags.get("in_test")
    original_testing_email = frappe.flags.get("testing_email")
    intercepted_commits = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        frappe.flags.in_test = True
        frappe.flags.testing_email = False
        result = _run_contract()
        result["commit_calls_intercepted"] = len(intercepted_commits)
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        _restore_flag("in_test", original_in_test)
        _restore_flag("testing_email", original_testing_email)
        frappe.db.rollback()


def _run_contract():
    failures: list[str] = []
    failures.extend(_check_policy_helper())
    failures.extend(_check_routed_alias_guard())
    failures.extend(_check_routed_alias_sendmail_hook())
    failures.extend(_check_page_anchors())
    failures.extend(_check_lead_auto_ack_lane_links())

    if failures:
        raise ContractFail("; ".join(failures))

    return {"ok": True, "checked_anchors": list(REQUIRED_ANCHORS)}


def _check_policy_helper() -> list[str]:
    from locally_twisted import policy_documents

    failures = []
    ready = policy_documents.customer_policy_block(["ready_to_order"], include_privacy=True)
    for expected in (
        "/terms-of-service#ready-to-order-pickup-delivery",
        "/refund-policy#ready-to-order-pickup-delivery",
        "/privacy",
        "not returnable once they are prepared, delivered, or picked up",
    ):
        if expected not in ready:
            failures.append(f"ready-to-order helper missing {expected}")

    artist = policy_documents.customer_policy_block(["artist_service"], include_privacy=False)
    for expected in ("$50 per artist", "72 hours before your event", "#face-painting-balloon-twisting"):
        if expected not in artist:
            failures.append(f"artist helper missing {expected}")

    forbidden = ("service tax", "tax on services", "taxable service", "taxable deposit")
    combined = (ready + artist).lower()
    for phrase in forbidden:
        if phrase in combined:
            failures.append(f"policy helper should not imply service/deposit taxability: {phrase}")
    return failures


def _check_page_anchors() -> list[str]:
    failures = []
    for route, path in {
        "/terms-of-service": "terms_of_service.html",
        "/refund-policy": "refund_policy.html",
    }.items():
        text = frappe.get_app_path("locally_twisted", "www", path)
        with open(text, encoding="utf-8") as handle:
            content = handle.read()
        for anchor in REQUIRED_ANCHORS:
            if f'id="{anchor}"' not in content:
                failures.append(f"{route} missing #{anchor} anchor")
    return failures


def _check_routed_alias_guard() -> list[str]:
    from locally_twisted.email_delivery_guard import validate_email_queue_delivery

    failures = []
    unsafe_doc = frappe._dict(
        sender="Locally Twisted <locallytwisted@gmail.com>",
        recipients=[frappe._dict(recipient="hi@locallytwisted.com")],
    )
    try:
        validate_email_queue_delivery(unsafe_doc)
    except Exception as exc:
        if "routed-alias loop" not in str(exc):
            failures.append(f"routed alias guard raised the wrong error: {exc}")
    else:
        failures.append("routed alias guard did not block hi@locallytwisted.com")

    for safe_doc in (
        frappe._dict(
            sender="Locally Twisted <locallytwisted@gmail.com>",
            recipients=[frappe._dict(recipient="locallytwisted@gmail.com")],
        ),
        frappe._dict(
            sender="QA Sender <qa@example.invalid>",
            recipients=[frappe._dict(recipient="hi@locallytwisted.com")],
        ),
    ):
        try:
            validate_email_queue_delivery(safe_doc)
        except Exception as exc:
            failures.append(f"routed alias guard blocked a safe path: {exc}")
    return failures


def _check_routed_alias_sendmail_hook() -> list[str]:
    failures = []
    subject = f"LT routed alias guard probe {int(time.time())}"
    try:
        frappe.sendmail(
            recipients=["hi@locallytwisted.com"],
            subject=subject,
            message="This should be blocked before Email Queue insert.",
            now=False,
        )
    except Exception as exc:
        if "routed-alias loop" not in str(exc):
            failures.append(f"routed alias sendmail hook raised the wrong error: {exc}")
    else:
        failures.append("routed alias sendmail hook did not block hi@locallytwisted.com")

    if frappe.db.exists("Email Queue", {"message": ("like", f"%Subject: {subject}%")}):
        failures.append("routed alias sendmail hook left an Email Queue row behind")
    return failures


def _check_lead_auto_ack_lane_links() -> list[str]:
    from locally_twisted.communication_copy_policy import BUSINESS_DOCUMENT_COPY, routed_alias_copy_risks

    token = str(int(time.time()))
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": f"LT Doc Test {token}",
            "email_id": f"lt-doc-{token}@example.invalid",
            "source": "Website",
            "status": "Open",
            "custom_pipeline_stage": "New Inquiry",
            "custom_event_type": [
                {"service_type": "Balloon Decor"},
                {"service_type": "Face Painting"},
            ],
        }
    )
    lead.insert(ignore_permissions=True)

    rows = frappe.get_all(
        "Email Queue",
        filters={
            "reference_doctype": "Lead",
            "reference_name": lead.name,
            "message": ("like", "%Subject: We got your message%"),
        },
        fields=["name", "message"],
        limit=1,
    )
    if not rows:
        return ["missing customer inquiry auto-ack Email Queue row"]

    message = _readable_message(rows[0]["message"] or "")
    recipients = _email_queue_recipients(rows[0]["name"])
    failures = []
    for expected in (
        "/terms-of-service#event-balloon-decor",
        "/terms-of-service#face-painting-balloon-twisting",
        "/refund-policy#event-balloon-decor",
        "/refund-policy#face-painting-balloon-twisting",
    ):
        if expected not in message:
            failures.append(f"auto-ack email missing lane link: {expected}")
    if BUSINESS_DOCUMENT_COPY not in recipients:
        failures.append(f"auto-ack email missing required copy recipient: {BUSINESS_DOCUMENT_COPY}")
    for alias in routed_alias_copy_risks(recipients):
        failures.append(f"auto-ack email should not copy routed alias loop: {alias}")
    return failures


def _restore_flag(flag_name: str, original_value) -> None:
    if original_value is None:
        frappe.flags.pop(flag_name, None)
    else:
        frappe.flags[flag_name] = original_value


def _email_queue_recipients(queue_name: str) -> set[str]:
    rows = frappe.get_all(
        "Email Queue Recipient",
        filters={"parent": queue_name},
        fields=["recipient"],
    )
    return {
        (row.get("recipient") or "").strip().lower()
        for row in rows
        if row.get("recipient")
    }


def _readable_message(message: str) -> str:
    decoded = decodestring(message.encode("utf-8", errors="ignore")).decode("utf-8", errors="ignore")
    return unescape(f"{message}\n{decoded}")
