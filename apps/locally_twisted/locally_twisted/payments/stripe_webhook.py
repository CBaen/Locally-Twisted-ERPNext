"""Stripe webhook receiver for guest checkout completion.

Stripe POSTs events to this endpoint. We care about
`checkout.session.completed` — that's our cue to mark the linked Payment
Request paid, create/submit the Sales Invoice, and queue the paid-order
emails. This mirrors the browser `/payment-success` path so the order
still reconciles if the customer closes the tab before returning.

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
        from locally_twisted.www.payment_success import reconcile_paid_sales_order

        result = reconcile_paid_sales_order(
            so_name,
            payment_request=pr_name,
            source="stripe_webhook",
            raise_on_error=True,
        )
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Stripe webhook: paid-order reconciliation failed for PR {pr_name}",
        )
        frappe.local.response.http_status_code = 500
        return {"error": "internal error — Stripe will retry"}

    return {"ok": True, "payment_request": pr_name, "sales_order": result.get("sales_order")}
