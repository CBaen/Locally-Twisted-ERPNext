"""Stripe webhook behavior verifier.

This exercises the webhook controller with mocked Stripe signature parsing so
we can verify event routing without posting real Stripe events.
"""
from __future__ import annotations

import frappe


class ContractFail(Exception):
    pass


def run():
    try:
        return _run_contract()
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}


def _run_contract():
    failures = []

    unpaid = _invoke_webhook(
        {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_probe_unpaid",
                    "payment_status": "unpaid",
                    "client_reference_id": "SO-PROBE",
                    "metadata": {"payment_request": "PR-PROBE", "sales_order": "SO-PROBE"},
                }
            },
        }
    )
    if unpaid["status_code"] >= 500:
        failures.append(f"unpaid checkout.session.completed returned HTTP {unpaid['status_code']}")
    if unpaid["result"].get("skipped") != "payment_status unpaid":
        failures.append(f"unpaid checkout.session.completed was not skipped: {unpaid['result']}")

    async_success_calls = []
    async_success = _invoke_webhook(
        {
            "type": "checkout.session.async_payment_succeeded",
            "data": {
                "object": {
                    "id": "cs_probe_async_paid",
                    "payment_status": "paid",
                    "client_reference_id": "SO-PROBE-ASYNC",
                    "metadata": {
                        "payment_request": "PR-PROBE-ASYNC",
                        "sales_order": "SO-PROBE-ASYNC",
                    },
                }
            },
        },
        reconcile_calls=async_success_calls,
    )
    if async_success["status_code"] >= 500:
        failures.append(
            f"async_payment_succeeded returned HTTP {async_success['status_code']}: {async_success['result']}"
        )
    if len(async_success_calls) != 1:
        failures.append(
            f"async_payment_succeeded should reconcile once, reconciled {len(async_success_calls)} times"
        )

    ignored = _invoke_webhook({"type": "payment_intent.succeeded", "data": {"object": {}}})
    if ignored["result"].get("ignored") != "payment_intent.succeeded":
        failures.append(f"unexpected event was not ignored cleanly: {ignored['result']}")

    if failures:
        return {"ok": False, "failures": failures}

    return {
        "ok": True,
        "unpaid_completed": unpaid["result"],
        "async_payment_succeeded_calls": len(async_success_calls),
        "ignored_event": ignored["result"].get("ignored"),
    }


def _invoke_webhook(event, reconcile_calls=None):
    import stripe

    import locally_twisted.payments.stripe_webhook as webhook_module
    import locally_twisted.www.payment_success as payment_success

    original_construct_event = stripe.Webhook.construct_event
    original_request = getattr(frappe, "request", None)
    original_secret = frappe.conf.get("stripe_webhook_signing_secret")
    original_response = getattr(frappe.local, "response", None)
    original_reconcile = payment_success.reconcile_paid_sales_order

    class Request:
        data = b"{}"
        headers = {"Stripe-Signature": "probe-signature"}

    def construct_event(payload, sig_header, secret):
        return event

    def reconcile_paid_sales_order(*args, **kwargs):
        if reconcile_calls is not None:
            reconcile_calls.append({"args": args, "kwargs": kwargs})
        return {
            "ok": True,
            "sales_order": kwargs.get("so_name") or (args[0] if args else None),
            "payment_request": kwargs.get("payment_request"),
            "errors": [],
        }

    try:
        frappe.request = Request()
        frappe.local.response = frappe._dict()
        frappe.conf.stripe_webhook_signing_secret = "whsec_probe"
        stripe.Webhook.construct_event = construct_event
        payment_success.reconcile_paid_sales_order = reconcile_paid_sales_order

        result = webhook_module.stripe_webhook()
        return {
            "result": result or {},
            "status_code": int(frappe.local.response.get("http_status_code") or 200),
        }
    finally:
        stripe.Webhook.construct_event = original_construct_event
        payment_success.reconcile_paid_sales_order = original_reconcile
        if original_request is None:
            try:
                delattr(frappe, "request")
            except AttributeError:
                pass
        else:
            frappe.request = original_request
        if original_secret is None:
            frappe.conf.pop("stripe_webhook_signing_secret", None)
        else:
            frappe.conf.stripe_webhook_signing_secret = original_secret
        frappe.local.response = original_response or frappe._dict()
