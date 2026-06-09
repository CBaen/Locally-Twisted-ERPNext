"""Fail-loud guards for LT outbound email delivery traps."""
from __future__ import annotations

from email.utils import parseaddr
from typing import Any

import frappe

from locally_twisted.communication_copy_policy import routed_alias_copy_risks


SMTP_SENDER_WITH_ROUTED_ALIAS_RISK = "locallytwisted@gmail.com"


def validate_email_queue_delivery(doc: Any, method: str | None = None) -> None:
    """Block known Cloudflare Email Routing alias loops before SMTP handoff."""
    apply_site_email_subject_prefix(doc)

    sender = _sender_email(doc)
    if sender != SMTP_SENDER_WITH_ROUTED_ALIAS_RISK:
        return

    risks = routed_alias_copy_risks(_queue_recipients(doc))
    if not risks:
        return

    aliases = ", ".join(risks)
    frappe.throw(
        "Blocked email routed-alias loop: "
        f"{sender} cannot send to {aliases} while those aliases route back "
        "into the same Gmail account. Use a non-LT mailbox for QA review or "
        "a delivery-safe business mailbox.",
        title="Blocked Unsafe Email Route",
    )


def apply_site_email_subject_prefix(doc: Any) -> None:
    """Apply a site-local QA subject prefix before email queue insertion."""
    prefix = str(frappe.conf.get("lt_email_subject_prefix") or "").strip()
    if not prefix:
        return

    subject = str(getattr(doc, "subject", "") or "")
    if subject.startswith(prefix):
        return

    doc.subject = f"{prefix} {subject}".strip()


def _sender_email(doc: Any) -> str:
    sender = _normalize_email(getattr(doc, "sender", None))
    if sender:
        return sender

    email_account = getattr(doc, "email_account", None)
    if email_account:
        account_email = frappe.db.get_value("Email Account", email_account, "email_id")
        sender = _normalize_email(account_email)
        if sender:
            return sender

    return ""


def _queue_recipients(doc: Any) -> list[str]:
    recipients = []
    for row in getattr(doc, "recipients", None) or []:
        recipient = getattr(row, "recipient", None)
        if recipient:
            recipients.append(str(recipient))
    return recipients


def _normalize_email(value: str | None) -> str:
    return parseaddr(str(value or ""))[1].strip().lower()
