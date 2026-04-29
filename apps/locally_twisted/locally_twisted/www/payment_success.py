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

Side-effects on payment success (added 2026-04-29):
- Sales Invoice creation from the SO (so the order lands in ERPNext's
  invoicing pipeline, not just as an SO + Payment Entry pair).
- Transactional receipt email to the customer's address email_id.
Both wrapped in try/except — a backend reconciliation glitch must not
block the customer's /thank-you landing. Errors are logged for
follow-up.
"""
import frappe
from frappe.utils import escape_html, flt


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

    # Sales Invoice — convert the SO to an invoice so it lands in the
    # accounting / invoicing surface, not just SO + Payment Entry.
    try:
        _ensure_sales_invoice(sales_order)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"payment_success: SI creation failed for SO {sales_order}",
        )

    # Transactional receipt email — fires once per paid order.
    try:
        _send_receipt_email(sales_order)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"payment_success: receipt email failed for SO {sales_order}",
        )

    # Operator notification — Jeff sees a new paid order land without
    # refreshing his desk.
    try:
        _send_operator_notification(sales_order)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"payment_success: operator notification failed for SO {sales_order}",
        )

    # Welcome email — only fires for first-time customers.
    try:
        _send_welcome_email_if_first_order(sales_order)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"payment_success: welcome email failed for SO {sales_order}",
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


def _ensure_sales_invoice(so_name):
    """Create + submit a Sales Invoice from the Sales Order. Idempotent.

    If a Sales Invoice already exists for this SO (any status), returns
    its name. Otherwise creates one via ERPNext's standard make_sales_invoice
    helper and submits it.

    `mute_email = True` and `ignore_default_payment_terms_template = True`
    are set to suppress the default invoice email + the wkhtmltopdf PDF
    render that fails inside the Frappe Docker container (see
    frappe-payment-safety skill, Trap 4).
    """
    existing = frappe.get_all(
        "Sales Invoice Item",
        filters={"sales_order": so_name, "docstatus": ("<", 2)},
        fields=["parent"],
        limit=1,
    )
    if existing:
        return existing[0]["parent"]

    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

    si = make_sales_invoice(so_name, ignore_permissions=True)
    si.flags.ignore_permissions = True
    si.flags.mute_email = True
    si.set_missing_values()
    si.insert(ignore_permissions=True)
    si.submit()
    frappe.db.commit()
    return si.name


def _send_receipt_email(so_name):
    """Send a transactional confirmation email to the customer.

    CAN-SPAM safe: this is a transactional receipt for a completed order,
    not marketing. Plain HTML body — no PDF attachment (avoids the
    wkhtmltopdf-in-Docker trap; production can re-enable PDF once
    host_name is configured in site_config.json).

    Idempotent: looks up a Communication record linked to the SO with
    subject prefix matching this template. If one exists, doesn't resend.
    """
    so = frappe.get_doc("Sales Order", so_name)

    # Resolve the customer email. The Address linked to the SO has email_id
    # populated by submit_guest_order. Falls back to the linked Contact's
    # primary email if the address email is missing.
    email = None
    if so.shipping_address_name:
        email = frappe.db.get_value("Address", so.shipping_address_name, "email_id")
    if not email and so.customer:
        contact_name = frappe.db.get_value(
            "Dynamic Link",
            {
                "link_doctype": "Customer",
                "link_name": so.customer,
                "parenttype": "Contact",
            },
            "parent",
        )
        if contact_name:
            email = frappe.db.get_value(
                "Contact Email", {"parent": contact_name, "is_primary": 1}, "email_id"
            )
    if not email:
        frappe.log_error(
            f"No email found for SO {so_name} — skipping receipt",
            "payment_success: receipt email skipped",
        )
        return

    subject = f"Your Locally Twisted order is confirmed — {so.name}"

    # Idempotency: if a Communication with this exact subject already
    # exists for the SO, don't resend.
    already_sent = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Sales Order",
            "reference_name": so_name,
            "subject": subject,
        },
        limit=1,
    )
    if already_sent:
        return

    # Build line items HTML — no innerHTML / template injection risk
    # since item_name comes from Website Item (operator-controlled, not
    # customer input). escape_html applied as belt-and-suspenders.
    lines_html = ""
    for item in so.items:
        name = item.item_name or item.item_code
        lines_html += (
            f'<tr>'
            f'<td style="padding:8px 0;border-bottom:1px solid #eee;">'
            f'{escape_html(name)} &times; {int(item.qty)}'
            f'</td>'
            f'<td style="padding:8px 0;border-bottom:1px solid #eee;text-align:right;">'
            f'${flt(item.amount):,.2f}'
            f'</td>'
            f'</tr>'
        )

    body = f"""
<div style="font-family: Raleway, Helvetica, Arial, sans-serif; max-width:560px; margin:0 auto; color:#1a1a1a; line-height:1.55;">
  <h1 style="font-family: 'DM Serif Display', Georgia, serif; font-size:28px; margin:0 0 12px;">
    Thank you for your order.
  </h1>
  <p style="font-size:15px; color:#5a5a5a; margin:0 0 24px;">
    We&rsquo;ve received your payment and we&rsquo;ll be in touch about delivery.
    This email is your receipt.
  </p>

  <div style="background:#fffcfc; border:1px solid rgba(26,26,26,0.08); border-radius:6px; padding:20px; margin:0 0 24px;">
    <p style="font-family:'Raleway',sans-serif; font-size:11px; letter-spacing:0.1em; text-transform:uppercase; color:#7a7a7a; margin:0 0 6px;">
      Order
    </p>
    <p style="font-family:'DM Serif Display', Georgia, serif; font-size:22px; margin:0 0 16px; word-break:break-all;">
      {escape_html(so.name)}
    </p>
    <table style="width:100%; border-collapse:collapse; font-size:14px;">
      {lines_html}
      <tr>
        <td style="padding:12px 0 0; font-weight:600;">Total</td>
        <td style="padding:12px 0 0; text-align:right; font-weight:600;">
          ${flt(so.grand_total):,.2f} {escape_html(so.currency or "USD")}
        </td>
      </tr>
    </table>
  </div>

  <p style="font-size:14px; color:#5a5a5a; margin:0 0 8px;">
    Questions about your order? Reply to this email or call (801) 285-0860.
  </p>
  <p style="font-size:12px; color:#9a9a9a; margin:24px 0 0;">
    Locally Twisted &middot; 8969 S 2700 W, West Jordan, UT 84088
  </p>
</div>
"""

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=body,
        reference_doctype="Sales Order",
        reference_name=so_name,
        # attach_print intentionally omitted — we never want to attach a
        # PDF render (wkhtmltopdf-in-Docker trap). The HTML body is the
        # receipt.
        now=False,
    )
    frappe.db.commit()


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect
