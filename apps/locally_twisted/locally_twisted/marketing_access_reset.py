"""Fail-loud Locally Twisted account access password reset helper.

Frappe's public reset_password endpoint intentionally returns the same success
message even when no user exists or email delivery fails. That is good for
public security, but dangerous for operator workflows where a known vendor must
actually receive access. This helper is an operator-only bench method that
turns silent/no-op reset attempts into explicit PASS/FAIL reports and uses a
Locally Twisted-branded email instead of Frappe's generic reset template.
"""
from __future__ import annotations

import html
import json
import quopri
import time
from typing import Any
from urllib.parse import urljoin

import frappe
from frappe.utils import add_to_date, cstr, get_url, now_datetime

from locally_twisted.external_marketing_builder_access import EXTERNAL_MARKETING_BUILDER_ROLE
from locally_twisted.marketing_review_access import MARKETING_REVIEW_ROLE


DEFAULT_MARKETING_EMAIL = "marketing@exploringnotboring.com"
DEFAULT_LIVE_SITE_URL = "https://locallytwisted.com"
MODE_ROLE = {
    "review": MARKETING_REVIEW_ROLE,
    "builder": EXTERNAL_MARKETING_BUILDER_ROLE,
}
MODE_USER_TYPE = {
    "review": "Website User",
    "builder": "System User",
}
FAILED_QUEUE_STATUSES = {"Error", "Expired", "Cancelled"}
SUCCESS_QUEUE_STATUS = "Sent"
FORBIDDEN_EMAIL_TEXT = (
    "Built by Cameron",
    "Dear Marketing,",
    "marketing access",
)


class MarketingAccessResetFailure(Exception):
    """Raised when a password reset would otherwise fail silently."""


@frappe.whitelist()
def execute(
    email: str = DEFAULT_MARKETING_EMAIL,
    mode: str = "review",
    send: bool | str | int = False,
    wait_seconds: int | str = 0,
    poll_interval: int | str = 3,
    expected_site_url: str = "",
) -> str:
    """Validate and optionally send a fail-loud LT account reset email.

    Args:
        email: Known external account email.
        mode: ``review`` for website-only review access, or ``builder`` for the
            Desk-bound external marketing builder role.
        send: False by default. When false, this is a no-email readiness check.
        wait_seconds: Optional queue polling window after sending.
        poll_interval: Polling interval when wait_seconds > 0.
        expected_site_url: Optional live URL guard. If provided, a real send
            fails if the generated reset link does not start with this URL.

    Returns:
        JSON string. Does not expose the real password-reset token/link.
    """
    _require_operator_if_http_request()
    send_bool = _as_bool(send)
    wait = max(0, int(wait_seconds or 0))
    interval = max(1, int(poll_interval or 3))
    mode = cstr(mode or "review").strip().lower()
    email = cstr(email or "").strip().lower()
    expected_site_url = _normalize_site_url(expected_site_url)
    started_at = add_to_date(now_datetime(), seconds=-5)

    report: dict[str, Any] = _base_report(
        email=email,
        mode=mode,
        send_requested=send_bool,
        expected_site_url=expected_site_url,
    )

    try:
        _validate_mode(mode)
        _validate_email(email)
        user_doc = _load_and_validate_user(email=email, mode=mode, report=report)
        report["outgoing_email"] = _outgoing_email_report()
        _assert_outgoing_email_ready(report)
        report["sender"] = _default_sender(report)
        report["current_site_url"] = get_url(allow_header_override=False)

        if not send_bool:
            report["email_contract"] = _render_contract_preview(
                account_email=email,
                reset_link=_join_site_url(expected_site_url or report["current_site_url"], "/update-password?key=PREVIEW-NOT-A-REAL-RESET-LINK"),
                preview=True,
                expected_site_url=expected_site_url or report["current_site_url"],
            )
            report["ok"] = True
            report["dry_run"] = True
            print(json.dumps(report, sort_keys=True))
            return json.dumps(report, sort_keys=True)

        _send_reset(user_doc, report, expected_site_url=expected_site_url)
        frappe.db.commit()
        report["sent"] = True
        report["reset_key_written"] = bool(frappe.db.get_value("User", email, "reset_password_key"))
        queue_rows = _wait_for_queue(email=email, started_at=started_at, wait_seconds=wait, poll_interval=interval)
        report["queue"] = [_sanitize_queue_row(row) for row in queue_rows]
        _assert_queue_loud(queue_rows)
        _assert_queue_content_contract(
            queue_rows=queue_rows,
            account_email=email,
            expected_site_url=expected_site_url,
            preview=False,
            report=report,
        )
        report["ok"] = True
    except Exception as exc:
        frappe.db.rollback()
        failure = cstr(exc)
        report["failures"].append(failure)
        _log_loud_failure(report)
    print(json.dumps(report, sort_keys=True))
    return json.dumps(report, sort_keys=True)


@frappe.whitelist()
def send_preview(
    preview_email: str,
    access_email: str = DEFAULT_MARKETING_EMAIL,
    mode: str = "builder",
    wait_seconds: int | str = 20,
    poll_interval: int | str = 3,
    site_url: str = DEFAULT_LIVE_SITE_URL,
) -> str:
    """Send a safe preview of the Locally Twisted reset email to an internal reviewer.

    The preview uses the same LT-branded email body as the real reset, addressed
    to the external account email so the owner can see exactly how it will read.
    The button uses a clearly fake preview key and does not send, reveal, or
    consume the vendor's real reset token.
    """
    _require_operator_if_http_request()
    preview_email = cstr(preview_email or "").strip().lower()
    access_email = cstr(access_email or "").strip().lower()
    mode = cstr(mode or "builder").strip().lower()
    site_url = _normalize_site_url(site_url or DEFAULT_LIVE_SITE_URL) or DEFAULT_LIVE_SITE_URL
    wait = max(0, int(wait_seconds or 20))
    interval = max(1, int(poll_interval or 3))
    started_at = add_to_date(now_datetime(), seconds=-5)

    report: dict[str, Any] = _base_report(
        email=access_email,
        mode=mode,
        send_requested=False,
        expected_site_url=site_url,
    )
    report.update(
        {
            "preview_only": True,
            "preview_email": preview_email,
            "visible_greeting": access_email,
        }
    )

    try:
        _validate_email(preview_email)
        _validate_email(access_email)
        _validate_mode(mode)
        _load_and_validate_user(email=access_email, mode=mode, report=report)
        report["outgoing_email"] = _outgoing_email_report()
        _assert_outgoing_email_ready(report)
        report["sender"] = _default_sender(report)
        preview_link = _join_site_url(site_url, "/update-password?key=PREVIEW-NOT-A-REAL-RESET-LINK")
        rendered = _render_reset_email(account_email=access_email, reset_link=preview_link, preview=True)
        _assert_rendered_content_contract(
            rendered=rendered,
            account_email=access_email,
            expected_site_url=site_url,
            preview=True,
        )
        report["email_contract"] = _contract_report(
            rendered=rendered,
            account_email=access_email,
            expected_site_url=site_url,
            preview=True,
        )
        q = frappe.sendmail(
            recipients=[preview_email],
            sender=report["sender"],
            subject=rendered["subject"],
            content=rendered["html"],
            delayed=False,
            retry=3,
            add_unsubscribe_link=0,
            with_container=False,
        )
        frappe.db.commit()
        report["preview_queue_name"] = getattr(q, "name", None)
        queue_rows = _wait_for_queue(
            email=preview_email,
            started_at=started_at,
            wait_seconds=wait,
            poll_interval=interval,
        )
        report["queue"] = [_sanitize_queue_row(row) for row in queue_rows]
        _assert_queue_loud(queue_rows)
        _assert_queue_content_contract(
            queue_rows=queue_rows,
            account_email=access_email,
            expected_site_url=site_url,
            preview=True,
            report=report,
        )
        report["ok"] = True
    except Exception as exc:
        frappe.db.rollback()
        report["failures"].append(cstr(exc))
        _log_loud_failure(report)
    print(json.dumps(report, sort_keys=True))
    return json.dumps(report, sort_keys=True)


def _base_report(email: str, mode: str, send_requested: bool, expected_site_url: str) -> dict[str, Any]:
    return {
        "ok": False,
        "email": email,
        "mode": mode,
        "expected_role": MODE_ROLE.get(mode),
        "expected_user_type": MODE_USER_TYPE.get(mode),
        "expected_site_url": expected_site_url,
        "send_requested": send_requested,
        "sent": False,
        "reset_key_written": False,
        "queue": [],
        "failures": [],
    }


def _require_operator_if_http_request() -> None:
    """Require a trusted operator for HTTP/API calls, while keeping bench execute usable."""
    if not getattr(getattr(frappe, "local", None), "request", None):
        return
    user = cstr(getattr(frappe.session, "user", "") or "")
    if not user or user == "Guest":
        frappe.throw("System Manager login required for account reset operations", frappe.PermissionError)
    roles = set(frappe.get_roles(user) or [])
    if user != "Administrator" and "System Manager" not in roles:
        frappe.throw("System Manager role required for account reset operations", frappe.PermissionError)


def _validate_mode(mode: str) -> None:
    if mode not in MODE_ROLE:
        raise MarketingAccessResetFailure(f"unsupported mode {mode!r}; expected one of {sorted(MODE_ROLE)}")


def _validate_email(email: str) -> None:
    if not email or "@" not in email:
        raise MarketingAccessResetFailure("a concrete account email address is required")


def _load_and_validate_user(email: str, mode: str, report: dict[str, Any]):
    if not frappe.db.exists("User", email):
        raise MarketingAccessResetFailure(f"User {email} does not exist")

    user_doc = frappe.get_doc("User", email)
    roles = sorted(row.role for row in user_doc.get("roles") or [])
    report["user"] = {
        "name": user_doc.name,
        "enabled": int(user_doc.enabled or 0),
        "user_type": user_doc.user_type,
        "roles": roles,
        "last_login": cstr(user_doc.last_login or ""),
        "last_password_reset_date": cstr(user_doc.last_password_reset_date or ""),
    }

    if not int(user_doc.enabled or 0):
        raise MarketingAccessResetFailure(f"User {email} is disabled")

    expected_user_type = MODE_USER_TYPE[mode]
    if user_doc.user_type != expected_user_type:
        raise MarketingAccessResetFailure(
            f"User {email} has user_type {user_doc.user_type!r}; expected {expected_user_type!r} for {mode} access"
        )

    expected_role = MODE_ROLE[mode]
    if expected_role not in roles:
        raise MarketingAccessResetFailure(f"User {email} is missing expected role {expected_role}")

    wrong_mode_role = MODE_ROLE["builder" if mode == "review" else "review"]
    if wrong_mode_role in roles:
        raise MarketingAccessResetFailure(
            f"User {email} has both marketing access modes; remove {wrong_mode_role} before sending"
        )

    if user_doc.name == "Administrator":
        raise MarketingAccessResetFailure("refusing to send reset email for Administrator")

    user_doc.validate_reset_password()
    return user_doc


def _outgoing_email_report() -> dict[str, Any]:
    accounts = frappe.db.get_all(
        "Email Account",
        filters={"enable_outgoing": 1},
        fields=[
            "name",
            "email_id",
            "default_outgoing",
            "enable_outgoing",
            "smtp_server",
            "smtp_port",
            "use_tls",
            "use_ssl_for_outgoing",
            "awaiting_password",
            "no_smtp_authentication",
        ],
        order_by="default_outgoing desc, modified desc",
        limit_page_length=10,
    )
    sanitized = []
    for account in accounts:
        sanitized.append(
            {
                "name": account.name,
                "email_id": account.email_id,
                "default_outgoing": int(account.default_outgoing or 0),
                "enable_outgoing": int(account.enable_outgoing or 0),
                "smtp_server": account.smtp_server,
                "smtp_port": account.smtp_port,
                "use_tls": int(account.use_tls or 0),
                "use_ssl_for_outgoing": int(account.use_ssl_for_outgoing or 0),
                "awaiting_password": int(account.awaiting_password or 0),
                "no_smtp_authentication": int(account.no_smtp_authentication or 0),
            }
        )
    return {"accounts": sanitized}


def _assert_outgoing_email_ready(report: dict[str, Any]) -> None:
    accounts = report.get("outgoing_email", {}).get("accounts") or []
    if not accounts:
        raise MarketingAccessResetFailure("no enabled outgoing Email Account is configured")
    default_accounts = [row for row in accounts if row.get("default_outgoing")]
    if not default_accounts:
        raise MarketingAccessResetFailure("no default outgoing Email Account is configured")
    awaiting = [row for row in default_accounts if row.get("awaiting_password")]
    if awaiting:
        names = ", ".join(row.get("name") or "unknown" for row in awaiting)
        raise MarketingAccessResetFailure(f"default outgoing Email Account awaiting password: {names}")
    sender_ready = any(
        "locally twisted" in cstr(row.get("name")).lower()
        or "locallytwisted" in cstr(row.get("email_id")).lower()
        for row in default_accounts
    )
    if not sender_ready:
        raise MarketingAccessResetFailure("default outgoing Email Account is not branded as Locally Twisted")


def _default_sender(report: dict[str, Any]) -> str:
    accounts = (report.get("outgoing_email") or {}).get("accounts") or []
    account = next((row for row in accounts if row.get("default_outgoing")), accounts[0] if accounts else {})
    name = cstr(account.get("name") or "Locally Twisted").strip() or "Locally Twisted"
    email_id = cstr(account.get("email_id") or "").strip()
    return f"{name} <{email_id}>" if email_id else name


def _send_reset(user_doc, report: dict[str, Any], expected_site_url: str) -> None:
    try:
        reset_link = user_doc._reset_password(send_email=False)
        if expected_site_url and not reset_link.startswith(expected_site_url.rstrip("/") + "/"):
            raise MarketingAccessResetFailure(
                f"generated reset link host is wrong: expected {expected_site_url}, got {reset_link.split('/update-password')[0]}"
            )
        rendered = _render_reset_email(account_email=user_doc.email, reset_link=reset_link, preview=False)
        _assert_rendered_content_contract(
            rendered=rendered,
            account_email=user_doc.email,
            expected_site_url=expected_site_url,
            preview=False,
        )
        report["email_contract"] = _contract_report(
            rendered=rendered,
            account_email=user_doc.email,
            expected_site_url=expected_site_url,
            preview=False,
        )
        q = frappe.sendmail(
            recipients=[user_doc.email],
            sender=report["sender"],
            subject=rendered["subject"],
            content=rendered["html"],
            delayed=False,
            retry=3,
            add_unsubscribe_link=0,
            with_container=False,
        )
        report["queue_name"] = getattr(q, "name", None)
    except Exception as exc:
        if isinstance(exc, MarketingAccessResetFailure):
            raise
        raise MarketingAccessResetFailure(f"password reset email send raised {type(exc).__name__}: {exc}") from exc


def _render_contract_preview(account_email: str, reset_link: str, preview: bool, expected_site_url: str) -> dict[str, Any]:
    rendered = _render_reset_email(account_email=account_email, reset_link=reset_link, preview=preview)
    _assert_rendered_content_contract(
        rendered=rendered,
        account_email=account_email,
        expected_site_url=expected_site_url,
        preview=preview,
    )
    return _contract_report(
        rendered=rendered,
        account_email=account_email,
        expected_site_url=expected_site_url,
        preview=preview,
    )


def _render_reset_email(account_email: str, reset_link: str, preview: bool) -> dict[str, str]:
    account_email_html = html.escape(account_email)
    reset_link_html = html.escape(reset_link, quote=True)
    preview_notice = ""
    subject = "Reset your Locally Twisted password"
    if preview:
        subject = "[PREVIEW] Reset your Locally Twisted password"
        preview_notice = """
        <div style="margin:0 0 22px 0;padding:14px 16px;border-left:4px solid #b08d57;background:#fff7e6;color:#1c2837;font-family:Lato, Arial, sans-serif;font-size:14px;line-height:1.5;">
          <strong>Preview only.</strong> This shows the Locally Twisted reset email style. The button uses a fake preview link and will not reset any account.
        </div>
        """

    html_body = f"""
<!doctype html>
<html>
  <body style="margin:0;padding:0;background:#f6f1e8;color:#162033;font-family:Lato, Arial, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f6f1e8;margin:0;padding:0;width:100%;">
      <tr>
        <td align="center" style="padding:32px 16px;">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;border-collapse:collapse;background:#ffffff;border:1px solid #ded2be;box-shadow:0 18px 44px rgba(11,22,38,.14);">
            <tr>
              <td style="background:#101b2d;padding:30px 32px 26px 32px;border-bottom:4px solid #b08d57;">
                <div style="font-family:Lato, Arial, sans-serif;letter-spacing:.18em;text-transform:uppercase;color:#d9bf82;font-size:12px;font-weight:700;">Locally Twisted</div>
                <h1 style="margin:10px 0 0 0;color:#fffaf0;font-family:'Cormorant Garamond', Georgia, serif;font-size:34px;line-height:1.08;font-weight:600;">Reset your password</h1>
                <p style="margin:10px 0 0 0;color:#d9e1ea;font-size:15px;line-height:1.5;">Secure account access for locallytwisted.com</p>
              </td>
            </tr>
            <tr>
              <td style="padding:30px 32px 34px 32px;">
                {preview_notice}
                <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#162033;">Dear {account_email_html},</p>
                <p style="margin:0 0 16px 0;font-size:16px;line-height:1.6;color:#162033;">A password reset was requested for your Locally Twisted website account.</p>
                <p style="margin:0 0 24px 0;font-size:16px;line-height:1.6;color:#162033;">Use the secure button below to choose your password and sign in.</p>
                <p style="margin:0 0 26px 0;">
                  <a href="{reset_link_html}" style="display:inline-block;background:#8f1f3b;color:#fffaf0;text-decoration:none;font-family:Lato, Arial, sans-serif;font-size:15px;font-weight:700;letter-spacing:.02em;padding:13px 20px;border:1px solid #8f1f3b;">Reset your Locally Twisted password</a>
                </p>
                <p style="margin:0 0 16px 0;font-size:14px;line-height:1.6;color:#44546a;">If the button does not open, copy and paste this link into your browser:</p>
                <p style="margin:0 0 24px 0;font-size:13px;line-height:1.5;word-break:break-all;color:#44546a;">{reset_link_html}</p>
                <p style="margin:0 0 18px 0;font-size:14px;line-height:1.6;color:#44546a;">If you did not expect this email, you can ignore it or contact Locally Twisted before taking action.</p>
                <p style="margin:0;font-size:16px;line-height:1.6;color:#162033;">Thank you,<br>Locally Twisted</p>
              </td>
            </tr>
            <tr>
              <td style="background:#101b2d;padding:18px 32px;color:#d9e1ea;font-family:Lato, Arial, sans-serif;font-size:12px;line-height:1.5;">
                This message was sent by Locally Twisted for locallytwisted.com account access.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
    return {"subject": subject, "html": html_body}


def _assert_rendered_content_contract(rendered: dict[str, str], account_email: str, expected_site_url: str, preview: bool) -> None:
    combined = f"{rendered.get('subject', '')}\n{rendered.get('html', '')}"
    for forbidden in FORBIDDEN_EMAIL_TEXT:
        if forbidden.lower() in combined.lower():
            raise MarketingAccessResetFailure(f"reset email content contains forbidden text: {forbidden}")
    required = ["Locally Twisted", f"Dear {account_email},", "locallytwisted.com", "Reset your Locally Twisted password"]
    for token in required:
        if token.lower() not in combined.lower():
            raise MarketingAccessResetFailure(f"reset email content missing required text: {token}")
    if expected_site_url and expected_site_url.lower() not in combined.lower():
        raise MarketingAccessResetFailure(f"reset email link does not include expected site URL {expected_site_url}")
    if preview and "Preview only" not in combined:
        raise MarketingAccessResetFailure("preview email is missing the preview-only warning")


def _contract_report(rendered: dict[str, str], account_email: str, expected_site_url: str, preview: bool) -> dict[str, Any]:
    return {
        "subject": rendered.get("subject"),
        "greeting": f"Dear {account_email},",
        "brand": "Locally Twisted",
        "style": "deep navy / brass / berry LT email shell",
        "preview_only": bool(preview),
        "expected_site_url": expected_site_url,
        "forbidden_text_absent": list(FORBIDDEN_EMAIL_TEXT),
    }


def _wait_for_queue(email: str, started_at, wait_seconds: int, poll_interval: int) -> list[dict[str, Any]]:
    deadline = time.time() + wait_seconds
    rows = _queue_rows(email=email, started_at=started_at)
    while wait_seconds and time.time() < deadline:
        if rows and any(row.get("status") == SUCCESS_QUEUE_STATUS for row in rows):
            break
        if rows and any(row.get("status") in FAILED_QUEUE_STATUSES for row in rows):
            break
        time.sleep(poll_interval)
        rows = _queue_rows(email=email, started_at=started_at)
    return rows


def _queue_rows(email: str, started_at) -> list[dict[str, Any]]:
    return frappe.db.sql(
        """
        select
            q.name,
            q.status,
            q.creation,
            q.modified,
            q.send_after,
            q.email_account,
            q.sender,
            q.error,
            r.recipient,
            r.status as recipient_status,
            r.error as recipient_error
        from `tabEmail Queue` q
        join `tabEmail Queue Recipient` r on r.parent = q.name
        where r.recipient = %(email)s
          and q.creation >= %(started_at)s
        order by q.creation desc
        limit 10
        """,
        {"email": email, "started_at": started_at},
        as_dict=True,
    )


def _assert_queue_loud(queue_rows: list[dict[str, Any]]) -> None:
    if not queue_rows:
        raise MarketingAccessResetFailure("password reset produced no Email Queue row for the recipient")

    statuses = {cstr(row.get("status")) for row in queue_rows}
    recipient_statuses = {cstr(row.get("recipient_status")) for row in queue_rows}
    failed = [row for row in queue_rows if row.get("status") in FAILED_QUEUE_STATUSES or row.get("recipient_status") in FAILED_QUEUE_STATUSES]
    if failed:
        details = "; ".join(_queue_failure_text(row) for row in failed)
        raise MarketingAccessResetFailure(f"password reset Email Queue failed: {details}")

    if SUCCESS_QUEUE_STATUS not in statuses and SUCCESS_QUEUE_STATUS not in recipient_statuses:
        raise MarketingAccessResetFailure(
            "password reset Email Queue was created but not marked Sent "
            f"(queue statuses={sorted(statuses)}, recipient statuses={sorted(recipient_statuses)})"
        )


def _assert_queue_content_contract(
    queue_rows: list[dict[str, Any]],
    account_email: str,
    expected_site_url: str,
    preview: bool,
    report: dict[str, Any],
) -> None:
    sent_row = next((row for row in queue_rows if row.get("status") == SUCCESS_QUEUE_STATUS), queue_rows[0])
    message = frappe.db.get_value("Email Queue", sent_row.get("name"), "message") or ""
    decoded = _decode_email_message(message)
    for forbidden in FORBIDDEN_EMAIL_TEXT:
        if forbidden.lower() in decoded.lower():
            raise MarketingAccessResetFailure(f"sent Email Queue content contains forbidden text: {forbidden}")
    for required in ["Locally Twisted", f"Dear {account_email},", "locallytwisted.com"]:
        if required.lower() not in decoded.lower():
            raise MarketingAccessResetFailure(f"sent Email Queue content missing required text: {required}")
    if expected_site_url and expected_site_url.lower() not in decoded.lower():
        raise MarketingAccessResetFailure(f"sent Email Queue content missing expected site URL {expected_site_url}")
    if preview and "Preview only" not in decoded:
        raise MarketingAccessResetFailure("sent preview email missing preview-only warning")
    sender = cstr(sent_row.get("sender") or "")
    if "locally twisted" not in sender.lower() and "locallytwisted" not in sender.lower():
        raise MarketingAccessResetFailure(f"sent Email Queue sender is not Locally Twisted branded: {sender}")
    report["sent_email_contract"] = {
        "queue_name": sent_row.get("name"),
        "sender": sender,
        "greeting_verified": f"Dear {account_email},",
        "forbidden_text_absent": list(FORBIDDEN_EMAIL_TEXT),
        "expected_site_url": expected_site_url,
    }


def _decode_email_message(message: str) -> str:
    try:
        return quopri.decodestring(cstr(message)).decode("utf-8", "ignore")
    except Exception:
        return cstr(message)


def _queue_failure_text(row: dict[str, Any]) -> str:
    error = cstr(row.get("recipient_error") or row.get("error") or "").replace("\n", " ")[:400]
    return f"{row.get('name')} status={row.get('status')} recipient_status={row.get('recipient_status')} error={error}"


def _sanitize_queue_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": row.get("name"),
        "status": row.get("status"),
        "recipient": row.get("recipient"),
        "recipient_status": row.get("recipient_status"),
        "creation": cstr(row.get("creation") or ""),
        "modified": cstr(row.get("modified") or ""),
        "send_after": cstr(row.get("send_after") or ""),
        "email_account": row.get("email_account"),
        "sender": row.get("sender"),
        "error_excerpt": cstr(row.get("recipient_error") or row.get("error") or "").replace("\n", " ")[:400],
    }


def _normalize_site_url(site_url: str) -> str:
    value = cstr(site_url or "").strip().rstrip("/")
    return value


def _join_site_url(site_url: str, path: str) -> str:
    base = _normalize_site_url(site_url) + "/"
    return urljoin(base, path.lstrip("/"))


def _log_loud_failure(report: dict[str, Any]) -> None:
    try:
        frappe.log_error(
            title="Marketing access reset failed loudly",
            message=json.dumps(report, indent=2, sort_keys=True, default=str),
        )
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()


def _as_bool(value: bool | str | int) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return cstr(value).strip().lower() in {"1", "true", "yes", "y", "send"}
