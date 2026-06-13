"""Locally Twisted branded password-reset email setup and verification."""
from __future__ import annotations

import html
import json
import re
import quopri
from email import policy
from email.parser import Parser
from types import SimpleNamespace
from typing import Any

import frappe
from frappe.email.doctype.email_template.email_template import get_email_template
from frappe.utils import cstr


TEMPLATE_NAME = "Locally Twisted Password Reset"
TEMPLATE_SUBJECT = "Reset your Locally Twisted website password"
DEFAULT_SITE_URL = "https://locallytwisted.com"
DEFAULT_ACCOUNT_EMAIL = "marketing@exploringnotboring.com"
PREVIEW_RESET_KEY = "PREVIEW-NOT-A-REAL-RESET-LINK"

GENERIC_RESET_SNIPPETS = (
    "Please click on the following link to set your new password",
    "Dear Jeff,",
    "Thank you, Administrator",
    "Built by Cameron",
)

TEMPLATE_RESPONSE_HTML = """
<div style="margin:0;padding:0;background:#f6f1ea;color:#162033;font-family:Lato, Arial, sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;background:#f6f1ea;margin:0;padding:28px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;max-width:620px;background:#fffaf0;border:1px solid #e4d5bf;border-radius:18px;overflow:hidden;">
          <tr>
            <td style="background:#132033;padding:28px 32px;text-align:left;">
              <div style="color:#d9b36c;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Locally Twisted</div>
              <h1 style="margin:10px 0 0 0;color:#fffaf0;font-family:'Cormorant Garamond', Georgia, serif;font-size:32px;line-height:1.1;font-weight:600;">Reset your Locally Twisted website password</h1>
            </td>
          </tr>
          <tr>
            <td style="padding:30px 32px 34px 32px;">
              <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#162033;">Dear {{ user }},</p>
              <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#162033;">A password reset was requested for your <strong>Locally Twisted website account</strong>.</p>
              <table role="presentation" cellspacing="0" cellpadding="0" style="border-collapse:collapse;width:100%;margin:0 0 22px 0;background:#f6f1ea;border:1px solid #e8dac4;border-radius:12px;">
                <tr>
                  <td style="padding:14px 16px;font-size:15px;line-height:1.5;color:#162033;">
                    <strong>Account email:</strong> {{ user }}<br>
                    <strong>Website:</strong> Locally Twisted<br>
                    <strong>Sign-in page:</strong> {{ login_url }}
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 18px 0;font-size:16px;line-height:1.6;color:#162033;">Use the secure button below to choose a new password for this Locally Twisted website account.</p>
              <p style="margin:0 0 24px 0;">
                <a href="{{ link }}" style="display:inline-block;background:#8b2854;color:#ffffff;text-decoration:none;border-radius:999px;padding:13px 22px;font-weight:700;font-size:15px;">Choose a new password</a>
              </p>
              <p style="margin:0 0 14px 0;font-size:14px;line-height:1.6;color:#4b5563;">This link only resets your Locally Twisted website password. It does not reset your email inbox, Google account, Facebook account, Exploring Not Boring account, or any other login.</p>
              <p style="margin:0 0 18px 0;font-size:14px;line-height:1.6;color:#4b5563;">If you did not request this, you can ignore this email or contact Locally Twisted before clicking the button.</p>
              <p style="margin:22px 0 0 0;font-size:16px;line-height:1.6;color:#162033;">Thank you,<br>Locally Twisted</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</div>
""".strip()


class PasswordResetEmailFailure(Exception):
    """Raised when the branded password-reset contract is not satisfied."""


@frappe.whitelist()
def sync_password_reset_template(commit: bool | str | int = True) -> str:
    """Install the LT password reset Email Template and set System Settings."""
    _require_operator_if_http_request()
    report = ensure_password_reset_template(commit=_as_bool(commit))
    print(json.dumps(report, sort_keys=True))
    return json.dumps(report, sort_keys=True)


@frappe.whitelist()
def verify_password_reset_template(
    account_email: str = DEFAULT_ACCOUNT_EMAIL,
    site_url: str = DEFAULT_SITE_URL,
) -> str:
    """Verify the configured reset template without sending email."""
    _require_operator_if_http_request()
    report = _verify_password_reset_template(account_email=account_email, site_url=site_url)
    print(json.dumps(report, sort_keys=True))
    return json.dumps(report, sort_keys=True)


def ensure_password_reset_template(commit: bool = True) -> dict[str, Any]:
    """Create/update template, point System Settings at it, and verify output."""
    report: dict[str, Any] = {
        "ok": False,
        "template_name": TEMPLATE_NAME,
        "template_subject": TEMPLATE_SUBJECT,
        "commit_requested": bool(commit),
        "created": False,
        "updated": False,
        "system_setting_before": frappe.db.get_single_value("System Settings", "reset_password_template"),
        "system_setting_after": None,
        "failures": [],
    }
    try:
        if frappe.db.exists("Email Template", TEMPLATE_NAME):
            doc = frappe.get_doc("Email Template", TEMPLATE_NAME)
        else:
            doc = frappe.new_doc("Email Template")
            doc.__newname = TEMPLATE_NAME
            report["created"] = True

        desired = {
            "subject": TEMPLATE_SUBJECT,
            "use_html": 1,
            "response_html": TEMPLATE_RESPONSE_HTML,
            "response": "",
        }
        changed = False
        for field, value in desired.items():
            if doc.get(field) != value:
                doc.set(field, value)
                changed = True
        report["updated"] = changed

        if doc.is_new():
            doc.insert(ignore_permissions=True)
        elif changed:
            doc.save(ignore_permissions=True)

        if report["system_setting_before"] != TEMPLATE_NAME:
            frappe.db.set_single_value("System Settings", "reset_password_template", TEMPLATE_NAME)
        report["system_setting_after"] = frappe.db.get_single_value("System Settings", "reset_password_template")

        verify_report = _verify_password_reset_template(
            account_email=DEFAULT_ACCOUNT_EMAIL,
            site_url=DEFAULT_SITE_URL,
        )
        report["verification"] = verify_report
        report["failures"].extend(verify_report.get("failures") or [])
        report["ok"] = not report["failures"]
        if not report["ok"]:
            raise PasswordResetEmailFailure("; ".join(report["failures"]))
        if commit:
            frappe.db.commit()
    except Exception as exc:
        frappe.db.rollback()
        if not report["failures"]:
            report["failures"].append(cstr(exc))
        report["ok"] = False
    return report


def validate_password_reset_email_queue(doc: Any) -> None:
    """Block Frappe's generic password-reset email before Email Queue insert."""
    subject = _normalize_spaces(getattr(doc, "subject", "") or "")
    message = cstr(getattr(doc, "message", "") or getattr(doc, "content", "") or "")
    plain = _plain_text(message)
    recipients = _queue_recipients(doc)

    if not _looks_like_password_reset(subject, plain, message):
        return

    generic_reasons = _generic_password_reset_reasons(subject, plain, message, recipients)
    if not generic_reasons:
        return

    reason_text = "; ".join(generic_reasons)
    frappe.throw(
        "Blocked generic password reset email before delivery. "
        "Locally Twisted reset emails must identify the Locally Twisted website account, "
        f"show the account email, and sign as Locally Twisted. Reasons: {reason_text}. "
        f"Run sync_password_reset_template for {TEMPLATE_NAME}.",
        title="Blocked Generic Password Reset Email",
    )


def _verify_password_reset_template(account_email: str, site_url: str) -> dict[str, Any]:
    account_email = cstr(account_email or DEFAULT_ACCOUNT_EMAIL).strip().lower()
    site_url = _normalize_site_url(site_url or DEFAULT_SITE_URL)
    failures: list[str] = []
    report: dict[str, Any] = {
        "ok": False,
        "template_name": TEMPLATE_NAME,
        "configured_template": frappe.db.get_single_value("System Settings", "reset_password_template"),
        "account_email": account_email,
        "site_url": site_url,
        "subject": None,
        "greeting": f"Dear {account_email},",
        "required_meaning": [
            "Locally Twisted website password",
            "account email",
            "this does not reset other accounts",
        ],
        "forbidden_generic_copy": list(GENERIC_RESET_SNIPPETS),
        "generic_fallback_blocked": False,
        "failures": failures,
    }

    if report["configured_template"] != TEMPLATE_NAME:
        failures.append(
            f"System Settings reset_password_template is {report['configured_template']!r}, expected {TEMPLATE_NAME!r}"
        )
    if not frappe.db.exists("Email Template", TEMPLATE_NAME):
        failures.append(f"Email Template {TEMPLATE_NAME!r} does not exist")
        return report

    link = f"{site_url}/update-password?key={PREVIEW_RESET_KEY}"
    rendered = get_email_template(
        TEMPLATE_NAME,
        {
            "first_name": "Jeff",
            "last_name": "",
            "user": account_email,
            "title": "Password Reset",
            "login_url": site_url,
            "created_by": "Administrator",
            "link": link,
        },
    )
    subject = cstr(rendered.get("subject") or "")
    message = cstr(rendered.get("message") or "")
    plain = _plain_text(message)
    report["subject"] = subject
    report["message_excerpt"] = plain[:350]

    if subject != TEMPLATE_SUBJECT:
        failures.append(f"subject is {subject!r}, expected {TEMPLATE_SUBJECT!r}")
    for required in (
        "Locally Twisted website password",
        f"Dear {account_email},",
        f"Account email: {account_email}",
        "This link only resets your Locally Twisted website password",
        "It does not reset your email inbox",
        site_url,
        "Choose a new password",
    ):
        if required.lower() not in plain.lower() and required.lower() not in message.lower():
            failures.append(f"rendered reset email missing required copy: {required}")
    for forbidden in GENERIC_RESET_SNIPPETS:
        if forbidden.lower() in plain.lower() or forbidden.lower() in message.lower():
            failures.append(f"rendered reset email contains forbidden generic copy: {forbidden}")
    if "Administrator" in plain:
        failures.append("rendered reset email still exposes Administrator")

    report["generic_fallback_blocked"] = _generic_guard_blocks_preview()
    if not report["generic_fallback_blocked"]:
        failures.append("generic Frappe password reset fallback was not blocked by Email Queue guard")

    report["ok"] = not failures
    return report


def _generic_guard_blocks_preview() -> bool:
    fake = SimpleNamespace(
        subject="Password Reset",
        message="""
            <p>Dear Jeff,</p>
            <p>Please click on the following link to set your new password:</p>
            <p><a href="https://locallytwisted.com/update-password?key=fake">Reset your password</a></p>
            <p>Thank you,<br>Administrator</p>
        """,
        content="",
    )
    try:
        validate_password_reset_email_queue(fake)
    except Exception:
        frappe.clear_messages()
        return True
    return False


def _looks_like_password_reset(subject: str, plain: str, message: str) -> bool:
    combined = f"{subject}\n{plain}\n{message}".lower()
    return (
        "password reset" in subject.lower()
        or "reset your password" in combined
        or "/update-password?key=" in combined
    )


def _generic_password_reset_reasons(
    subject: str, plain: str, message: str, recipients: list[str] | None = None
) -> list[str]:
    reasons: list[str] = []
    clean_subject = _strip_subject_prefix(subject)
    if clean_subject.strip().lower() == "password reset":
        reasons.append("subject is generic 'Password Reset'")
    combined = f"{plain}\n{message}"
    combined_lower = combined.lower()
    for snippet in GENERIC_RESET_SNIPPETS:
        if snippet.lower() in combined_lower:
            reasons.append(f"contains generic/forbidden copy {snippet!r}")
    if "locally twisted" not in combined_lower:
        reasons.append("does not identify Locally Twisted")
    account_visible = "account email" in combined_lower or any(
        cstr(recipient or "").strip().lower() and cstr(recipient).strip().lower() in combined_lower
        for recipient in (recipients or [])
    )
    if not account_visible:
        reasons.append("does not show the account email")
    return reasons


def _strip_subject_prefix(subject: str) -> str:
    prefix = cstr(frappe.conf.get("lt_email_subject_prefix") or "").strip()
    if prefix and subject.startswith(prefix):
        return subject[len(prefix) :].strip()
    return subject


def _plain_text(value: str) -> str:
    variants = _message_text_variants(value)
    text = "\n".join(variants)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return _normalize_spaces(text)


def _message_text_variants(value: str) -> list[str]:
    raw = cstr(value or "")
    variants = [raw]
    try:
        decoded = quopri.decodestring(raw).decode("utf-8", "replace")
        if decoded and decoded not in variants:
            variants.append(decoded)
    except Exception:
        pass
    if "content-type:" in raw.lower() or "mime-version:" in raw.lower():
        try:
            msg = Parser(policy=policy.default).parsestr(raw)
            parts = msg.walk() if msg.is_multipart() else [msg]
            for part in parts:
                if part.get_content_maintype() == "multipart":
                    continue
                content_type = part.get_content_type()
                if content_type not in {"text/plain", "text/html"}:
                    continue
                try:
                    content = part.get_content()
                except Exception:
                    payload = part.get_payload(decode=True)
                    content = payload.decode(part.get_content_charset() or "utf-8", "replace") if payload else ""
                if content and content not in variants:
                    variants.append(content)
        except Exception:
            pass
    return variants


def _queue_recipients(doc: Any) -> list[str]:
    recipients: list[str] = []
    for row in getattr(doc, "recipients", None) or []:
        recipient = getattr(row, "recipient", None) or getattr(row, "email", None)
        if recipient:
            recipients.append(cstr(recipient).strip().lower())
    return recipients


def _normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", cstr(value or "")).strip()


def _normalize_site_url(value: str) -> str:
    value = cstr(value or DEFAULT_SITE_URL).strip().rstrip("/")
    return value or DEFAULT_SITE_URL


def _as_bool(value: bool | str | int) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return cstr(value).strip().lower() in {"1", "true", "yes", "y", "commit"}


def _require_operator_if_http_request() -> None:
    if not getattr(frappe.local, "request", None):
        return
    frappe.only_for("System Manager")
