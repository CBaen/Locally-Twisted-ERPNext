"""Newsletter sign-up endpoint.

Public surface: locally_twisted.api.newsletter.signup(email)

Loud-failure compliance (per project CLAUDE.md + global loud-failure rule):
  - User-facing: frappe.throw with user-safe messages (Frappe surfaces these
    to the client as _server_messages; lt-newsletter.js renders them in the
    visible error banner).
  - Developer-facing: frappe.log_error on any unexpected exception, with
    sanitized payload (no raw email after validation pass — privacy-safe).
  - Monitor: add to scripts/verify/smoke_forms.py (flagged as TODO — not yet
    covered; tracked in builder-js-build.md self-review concerns).

Rate-limiting: 10 requests per IP per hour via @rate_limit decorator.

Notes on privacy:
  - If the email passes format validation we do NOT log the raw email in the
    error branch.  We log hash(email) to allow correlation queries without
    leaking the address.
  - If validation fails we don't log at all — the frappe.throw response itself
    is the only signal, and it contains no PII.
"""
import re

import frappe
from frappe.rate_limiter import rate_limit


# RFC 5322-light pattern: local@domain.tld
# Deliberately permissive (no punycoding, no length limits beyond the
# Database column limit) because real-world valid addresses can be unusual.
# The server-side check is primarily a sanity gate; real validation happens
# on first attempted email send (Frappe mail queue will bounce).
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Cap input lengths before hitting the DB.  Frappe's Data field truncates at
# the column length (200 for email, 500 for source_url) but we enforce earlier
# to avoid wasted DB calls and for clarity.
_MAX_EMAIL_LEN = 200
_MAX_SOURCE_URL_LEN = 500


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=10, seconds=60 * 60)
def signup(email=None):
    """Sign up a newsletter email address.

    Returns:
        {"ok": True, "message": "<user-facing confirmation>"}

    Raises:
        frappe.ValidationError  — when email is missing or malformed
        Any other exception     — logged + re-raised so Frappe's error
                                  handler returns a 500 with _server_messages

    The try/except around record creation ensures loud failure per project
    rules: the error is always logged with sanitized context, never swallowed.
    """
    # ── Input validation ───────────────────────────────────────────────
    if not email or not isinstance(email, str):
        frappe.throw("Email is required.", frappe.ValidationError)

    email = email.strip().lower()

    if len(email) > _MAX_EMAIL_LEN:
        frappe.throw("That email address is too long.", frappe.ValidationError)

    if not _EMAIL_RE.match(email):
        frappe.throw("That doesn't look like a valid email.", frappe.ValidationError)

    # ── Idempotent insert ──────────────────────────────────────────────
    try:
        if frappe.db.exists("LT Newsletter Signup", {"email": email}):
            return {"ok": True, "message": "You're already on the list — thanks!"}

        # Pull source_url from the HTTP request for analytics (which page
        # the visitor signed up from).  None if not available.
        request = getattr(frappe.local, "request", None)
        source_url = getattr(request, "url", None)
        if source_url and len(source_url) > _MAX_SOURCE_URL_LEN:
            source_url = source_url[:_MAX_SOURCE_URL_LEN]

        doc = frappe.get_doc({
            "doctype": "LT Newsletter Signup",
            "email": email,
            "source_url": source_url,
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"ok": True, "message": "Thanks — we'll be in touch."}

    except Exception as exc:
        # Loud-failure: log dev-channel detail before re-raising.
        # We DO NOT log the raw email after it passed validation —
        # instead we log its hash so issues can be correlated without
        # leaking the address.
        frappe.log_error(
            title="Newsletter signup failed",
            message=(
                "{exc_type}: {exc}\n"
                "email_hash: {email_hash}\n"
                "remote_ip: {remote_ip}"
            ).format(
                exc_type=type(exc).__name__,
                exc=exc,
                email_hash=hash(email),
                remote_ip=getattr(frappe.local, "request_ip", "unknown"),
            ),
        )
        raise
