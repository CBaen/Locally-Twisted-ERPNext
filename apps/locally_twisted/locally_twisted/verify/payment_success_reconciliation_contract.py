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
    original_reconcile = payment_success.reconcile_paid_sales_order
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

    try:
        stripe_session.retrieve_session = fake_retrieve_session
        payment_success.reconcile_paid_sales_order = fake_reconcile_paid_sales_order
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
        payment_success.reconcile_paid_sales_order = original_reconcile
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
