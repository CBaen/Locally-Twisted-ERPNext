"""Payment-success browser return fail-loud contract.

This verifier uses only monkeypatched fake Stripe/reconciliation responses.
It proves the customer thank-you redirect does not imply final paperwork is
done when paid-order reconciliation returns errors.
"""
from __future__ import annotations

import frappe


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
    import locally_twisted.payments.stripe_session as stripe_session
    from locally_twisted.www import payment_success, thank_you

    original_retrieve = stripe_session.retrieve_session
    original_verify = payment_success.verify_paid_stripe_session
    original_reconcile = payment_success.reconcile_paid_sales_order
    original_payment_state = thank_you._payment_state_for_sales_order
    original_form_dict = getattr(frappe.local, "form_dict", None)
    original_redirect = getattr(frappe.local.flags, "redirect_location", None)
    calls: list[dict[str, object]] = []

    def fake_retrieve_session(session_id):
        calls.append({"retrieve_session": session_id})
        return {
            "payment_status": "paid",
            "client_reference_id": "SO-RECONCILE-PENDING",
            "metadata": {"payment_request": "PR-RECONCILE-PENDING"},
        }

    def fake_reconcile_paid_sales_order(so_name=None, **kwargs):
        calls.append({"reconcile": so_name, **kwargs})
        return {
            "ok": False,
            "sales_order": so_name,
            "payment_request": kwargs.get("payment_request"),
            "errors": ["receipt email failed"],
        }

    def fake_verify_paid_stripe_session(session, **kwargs):
        calls.append({"verify": session.get("id"), **kwargs})
        return {
            "sales_order": session.get("client_reference_id"),
            "payment_request": (session.get("metadata") or {}).get("payment_request"),
        }

    def fake_payment_state_for_sales_order(so_name):
        return {
            "state": "reconciliation_needed",
            "eyebrow": "Payment Received",
            "lede": (
                "Your payment came through. We have your order, and the final receipt "
                "or invoice check is still finishing in the background."
            ),
            "notice": "Tiny snag: the final receipt or invoice details are still being checked.",
        }

    try:
        stripe_session.retrieve_session = fake_retrieve_session
        payment_success.verify_paid_stripe_session = fake_verify_paid_stripe_session
        payment_success.reconcile_paid_sales_order = fake_reconcile_paid_sales_order
        thank_you._payment_state_for_sales_order = fake_payment_state_for_sales_order
        try:
            payment_success._handle_stripe_session("cs_test_reconcile_pending")
        except frappe.Redirect:
            pass
        redirect_location = getattr(frappe.local.flags, "redirect_location", "")

        context = frappe._dict()
        frappe.local.form_dict = frappe._dict(
            {"order": "SO-RECONCILE-PENDING", "reconciliation": "pending"}
        )
        thank_you.get_context(context)

        failures = []
        if "reconciliation=pending" not in redirect_location:
            failures.append(f"pending redirect missing reconciliation flag: {redirect_location!r}")
        if "order=SO-RECONCILE-PENDING" not in redirect_location:
            failures.append(f"pending redirect missing order: {redirect_location!r}")
        reconcile_calls = [call for call in calls if "reconcile" in call]
        if not reconcile_calls:
            failures.append("paid browser return did not call reconcile_paid_sales_order")
        elif reconcile_calls[0].get("raise_on_error") is not False:
            failures.append("browser return must call reconciliation with raise_on_error=False")
        if context.get("reconciliation_pending") is not True:
            failures.append("thank-you context missing reconciliation_pending state")
        lede = context.get("thank_you_lede") or ""
        if "final receipt" not in lede.lower() and "paperwork" not in lede.lower():
            failures.append(f"thank-you pending lede does not explain receipt/paperwork state: {lede!r}")
        failures.extend(_discounted_session_verification_failures(payment_success, original_verify))

        if failures:
            raise ContractFail("; ".join(failures))

        return {
            "ok": True,
            "redirect_location": redirect_location,
            "reconciliation_pending": context.get("reconciliation_pending"),
            "calls": calls,
        }
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        stripe_session.retrieve_session = original_retrieve
        payment_success.verify_paid_stripe_session = original_verify
        payment_success.reconcile_paid_sales_order = original_reconcile
        thank_you._payment_state_for_sales_order = original_payment_state
        if original_form_dict is None:
            frappe.local.form_dict = frappe._dict()
        else:
            frappe.local.form_dict = original_form_dict
        if original_redirect is None:
            try:
                del frappe.local.flags.redirect_location
            except AttributeError:
                pass
        else:
            frappe.local.flags.redirect_location = original_redirect


def _discounted_session_verification_failures(payment_success, verify_paid_stripe_session):
    failures = []
    original_exists = frappe.db.exists
    original_get_value = frappe.db.get_value

    sales_order = "SO-DISCOUNT-CONTRACT"
    payment_request = "PR-DISCOUNT-CONTRACT"
    expected_cents = 12500

    def fake_exists(doctype, name=None, *args, **kwargs):
        if doctype == "Payment Request" and name == payment_request:
            return True
        if doctype == "Sales Order" and name == sales_order:
            return True
        return original_exists(doctype, name, *args, **kwargs)

    def fake_get_value(doctype, name=None, fieldname=None, *args, **kwargs):
        as_dict = kwargs.get("as_dict")
        if doctype == "Payment Request" and name == payment_request:
            value = {
                "reference_doctype": "Sales Order",
                "reference_name": sales_order,
                "grand_total": expected_cents / 100,
                "currency": "USD",
                "outstanding_amount": expected_cents / 100,
            }
            if as_dict:
                return frappe._dict(value)
            if isinstance(fieldname, (list, tuple)):
                return [value.get(field) for field in fieldname]
            return value.get(fieldname)
        if doctype == "Sales Order" and name == sales_order:
            value = {"grand_total": expected_cents / 100, "currency": "USD"}
            if as_dict:
                return frappe._dict(value)
            if isinstance(fieldname, (list, tuple)):
                return [value.get(field) for field in fieldname]
            return value.get(fieldname)
        return original_get_value(doctype, name, fieldname, *args, **kwargs)

    def session(**overrides):
        data = {
            "payment_status": "paid",
            "client_reference_id": sales_order,
            "amount_total": 2500,
            "currency": "usd",
            "total_details": {"amount_discount": 10000},
            "metadata": {
                "lt_origin": "guest_checkout",
                "sales_order": sales_order,
                "payment_request": payment_request,
                "amount_expected_cents": str(expected_cents),
            },
        }
        data.update(overrides)
        return data

    try:
        frappe.db.exists = fake_exists
        frappe.db.get_value = fake_get_value

        discounted = verify_paid_stripe_session(
            session(),
            source="payment_success_reconciliation_contract",
        )
        if discounted.get("amount_discount_cents") != 10000:
            failures.append(f"discounted Stripe session did not report 10000 discount cents: {discounted}")
        if discounted.get("amount_total_cents") != 2500:
            failures.append(f"discounted Stripe session did not report 2500 amount_total cents: {discounted}")

        fully_discounted = verify_paid_stripe_session(
            session(
                payment_status="no_payment_required",
                amount_total=0,
                total_details={"amount_discount": expected_cents},
            ),
            source="payment_success_reconciliation_contract",
        )
        if fully_discounted.get("amount_total_cents") != 0:
            failures.append(f"fully discounted Stripe session did not report zero total: {fully_discounted}")

        try:
            verify_paid_stripe_session(
                session(amount_total=2500, total_details={"amount_discount": 0}),
                source="payment_success_reconciliation_contract",
            )
            failures.append("underpaid Stripe session without a discount was accepted")
        except payment_success.StripePaymentVerificationError:
            pass
    finally:
        frappe.db.exists = original_exists
        frappe.db.get_value = original_get_value

    return failures
