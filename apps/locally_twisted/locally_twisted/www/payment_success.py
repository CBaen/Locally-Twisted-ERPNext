"""Override Frappe's /payment-success page for guest checkouts.

Two paths supported:

1. PRIMARY — Stripe Checkout Session redirect (current flow):
   Stripe's success_url comes back as `/payment-success?session_id=cs_test_...`.
   We retrieve the session, verify payment_status == "paid", read
   client_reference_id (= Sales Order name), and redirect to
   /thank-you?order=<so_name>.

2. LEGACY — Frappe payments redirect (kept for any in-flight charges):
   The bundled payments app builds a redirect URL like
   `/payment-success?doctype=Payment%20Request&docname=ACC-PRQ-...?redirect_to=None`.
   Two upstream bugs make this fail: (a) the malformed double-`?` URL,
   (b) guests can't read Payment Request → 403. We dodge both: clean the
   docname, verify Integration Request status, look up the SO with
   elevated perms, redirect.

Why an override at all: Frappe's payment_success.py loads the Payment
Request via `frappe.get_doc(...)` under the guest session, which 403s.
We never read Payment Request as guest; we verify completion via the
Stripe API or Integration Request status instead.
"""
import frappe


no_cache = 1
sitemap = 0


def get_context(context):
    session_id = (frappe.form_dict.get("session_id") or "").strip()
    if session_id:
        _handle_stripe_session(session_id)

    docname_raw = (frappe.form_dict.get("docname") or "").strip()
    doctype = (frappe.form_dict.get("doctype") or "").strip()
    docname = docname_raw.split("?", 1)[0] if docname_raw else ""

    if doctype != "Payment Request" or not docname:
        _redirect("/")

    integration_status = frappe.db.get_value(
        "Integration Request",
        {"reference_doctype": "Payment Request", "reference_docname": docname},
        "status",
    )
    if integration_status != "Completed":
        _redirect("/")

    sales_order = frappe.db.get_value("Payment Request", docname, "reference_name")
    if not sales_order:
        _redirect("/")

    _redirect(f"/thank-you?order={sales_order}")


def _handle_stripe_session(session_id):
    """Resolve a Stripe Checkout Session → mark PR paid → redirect.

    Verifies payment_status == 'paid' via the Stripe API before exposing
    the order. Then marks the linked Payment Request paid synchronously
    here (the webhook handler in payments/stripe_webhook.py would do the
    same thing async — both paths are idempotent, so whichever fires
    first wins and the second is a no-op). This keeps the demo flow
    working without a webhook listener; in production the webhook is
    still the safety net for browser-closed-before-redirect cases.

    On any failure, redirect home rather than leak existence information.
    """
    from locally_twisted.payments.stripe_session import retrieve_session

    try:
        session = retrieve_session(session_id)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Stripe session retrieval failed")
        _redirect("/")

    if (session.get("payment_status") or "").lower() != "paid":
        _redirect("/")

    sales_order = (
        session.get("client_reference_id")
        or (session.get("metadata") or {}).get("sales_order")
    )
    if not sales_order:
        _redirect("/")

    pr_name = (session.get("metadata") or {}).get("payment_request")
    if pr_name:
        try:
            _mark_payment_request_paid(pr_name)
        except Exception:
            # Don't block the customer's success landing on a backend
            # reconciliation error. Logged for follow-up; the customer
            # still sees /thank-you.
            frappe.log_error(
                frappe.get_traceback(),
                f"payment_success: marking PR {pr_name} paid failed",
            )

    _redirect(f"/thank-you?order={sales_order}")


def _mark_payment_request_paid(pr_name):
    """Mark a Payment Request paid + create Payment Entry. Idempotent."""
    if not frappe.db.exists("Payment Request", pr_name):
        return
    if frappe.db.get_value("Payment Request", pr_name, "status") == "Paid":
        return

    pr = frappe.get_doc("Payment Request", pr_name)
    pr.flags.ignore_permissions = True
    pr.flags.mute_email = True
    pr.set_as_paid()
    frappe.db.commit()


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect
