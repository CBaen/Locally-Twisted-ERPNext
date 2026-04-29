"""Stripe webhook receiver for guest checkout completion.

Stripe POSTs events to this endpoint. We care about
`checkout.session.completed` — that's our cue to mark the linked Payment
Request paid (which in turn creates a Payment Entry and updates the SO).

URL Stripe sends to:
    /api/method/locally_twisted.payments.stripe_webhook.stripe_webhook

Local dev: run Stripe CLI's `stripe listen --forward-to ...` to forward
events to this URL and get a temporary signing secret.

Production: configure the endpoint in Stripe Dashboard → Developers →
Webhooks. Stripe shows the signing secret once; store it in the site's
site_config.json under `stripe_webhook_signing_secret`.

Security:
- Signature verification is mandatory (rejects unsigned + replayed events)
- Idempotent: if the linked PR is already Paid, we return 200 without
  re-processing
- Loud-failure: signature failures log + 400; internal errors log + 500
  (Stripe will retry — that's the design)
"""
from __future__ import annotations

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True, methods=["POST"])
def stripe_webhook():
    """Receive a Stripe webhook event."""
    import stripe

    payload = frappe.request.data
    sig_header = frappe.request.headers.get("Stripe-Signature", "")

    secret = frappe.conf.get("stripe_webhook_signing_secret")
    if not secret:
        frappe.log_error(
            "stripe_webhook_signing_secret not set in site_config.json — "
            "rejecting webhook to avoid processing unverified events.",
            "Stripe webhook: missing signing secret",
        )
        frappe.local.response.http_status_code = 503
        return {"error": "webhook signing secret not configured"}

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        frappe.log_error(
            f"Stripe webhook signature verification failed: {e}",
            "Stripe webhook: invalid signature",
        )
        frappe.local.response.http_status_code = 400
        return {"error": "invalid signature"}

    event_type = event.get("type", "")
    if event_type != "checkout.session.completed":
        return {"ok": True, "ignored": event_type}

    session = (event.get("data") or {}).get("object") or {}
    metadata = session.get("metadata") or {}
    pr_name = metadata.get("payment_request")
    so_name = session.get("client_reference_id") or metadata.get("sales_order")

    if not pr_name:
        frappe.log_error(
            f"checkout.session.completed without payment_request metadata: {session.get('id')}",
            "Stripe webhook: missing PR metadata",
        )
        return {"ok": True, "skipped": "no payment_request metadata"}

    try:
        _mark_payment_request_paid(pr_name, so_name, session)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Stripe webhook: marking PR {pr_name} paid failed")
        frappe.local.response.http_status_code = 500
        return {"error": "internal error — Stripe will retry"}

    return {"ok": True, "payment_request": pr_name}


def _mark_payment_request_paid(pr_name: str, so_name: str | None, session: dict):
    """Idempotently mark the Payment Request paid + create Payment Entry."""
    if not frappe.db.exists("Payment Request", pr_name):
        frappe.log_error(
            f"Stripe webhook references non-existent Payment Request: {pr_name}",
            "Stripe webhook: PR not found",
        )
        return

    pr_status = frappe.db.get_value("Payment Request", pr_name, "status")
    if pr_status == "Paid":
        return

    pr = frappe.get_doc("Payment Request", pr_name)

    pr.flags.ignore_permissions = True
    pr.flags.mute_email = True
    pr.set_as_paid()

    frappe.db.commit()
