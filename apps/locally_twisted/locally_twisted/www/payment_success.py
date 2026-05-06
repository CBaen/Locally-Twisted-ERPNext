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

from locally_twisted import policy_documents
from locally_twisted.payments.settings import (
    DEFAULT_OPERATOR_EMAIL,
    get_operator_email,
)


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

    reconcile_paid_sales_order(
        sales_order,
        payment_request=(session.get("metadata") or {}).get("payment_request"),
        source="payment_success",
        raise_on_error=False,
    )

    _redirect(f"/thank-you?order={sales_order}")


class PaidOrderReconciliationError(Exception):
    """Raised when the paid-order cascade fails in a retryable path."""


def reconcile_paid_sales_order(
    so_name=None,
    *,
    payment_request=None,
    source="paid_order",
    raise_on_error=False,
):
    """Run the idempotent paid-order cascade for a completed payment.

    Browser redirects should call this with ``raise_on_error=False`` so the
    customer still lands on /thank-you. Webhooks should call it with
    ``raise_on_error=True`` so Stripe retries invoice/email failures.
    """
    errors = []

    def run(label, func, *args):
        try:
            return func(*args)
        except Exception:
            message = f"{source}: {label} failed"
            if args:
                message = f"{message} for {', '.join(str(arg) for arg in args if arg)}"
            frappe.log_error(frappe.get_traceback(), message)
            errors.append(message)
            return None

    if payment_request:
        run("marking Payment Request paid", _mark_payment_request_paid, payment_request)

    if not so_name and payment_request:
        so_name = frappe.db.get_value("Payment Request", payment_request, "reference_name")

    if not so_name:
        errors.append(f"{source}: missing Sales Order for paid-order cascade")
    else:
        run("Sales Invoice creation", _ensure_sales_invoice, so_name)
        run("receipt email", _send_receipt_email, so_name)
        run("operator notification", _send_operator_notification, so_name)
        run("welcome email", _send_welcome_email_if_first_order, so_name)

    if errors and raise_on_error:
        raise PaidOrderReconciliationError("; ".join(errors))

    return {
        "ok": not errors,
        "sales_order": so_name,
        "payment_request": payment_request,
        "errors": errors,
    }


def _mark_payment_request_paid(pr_name):
    """Mark a Payment Request paid + create Payment Entry. Idempotent."""
    if not frappe.db.exists("Payment Request", pr_name):
        raise ValueError(f"Payment Request not found: {pr_name}")
    if frappe.db.get_value("Payment Request", pr_name, "status") == "Paid":
        return

    pr = frappe.get_doc("Payment Request", pr_name)
    pr.flags.ignore_permissions = True
    pr.flags.mute_email = True
    pr.set_as_paid()
    frappe.db.commit()


def _message_already_queued_or_sent(reference_doctype, reference_name, subject):
    filters = {
        "reference_doctype": reference_doctype,
        "reference_name": reference_name,
    }
    email_queue_subject_probe = _email_queue_subject_probe(subject)
    return bool(
        frappe.get_all("Communication", filters={**filters, "subject": subject}, limit=1)
        or frappe.get_all(
            "Email Queue",
            filters={**filters, "message": ("like", f"%Subject: {email_queue_subject_probe}%")},
            limit=1,
        )
    )


def _email_queue_subject_probe(subject):
    """Return the stable part of a subject as stored in Email Queue MIME."""
    for separator in (" — ", " - "):
        if separator in subject:
            return subject.split(separator, 1)[0]
    return subject


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

    # Idempotency: check both Communication and Email Queue because this
    # ERPNext install may queue mail without creating a Communication row.
    if _message_already_queued_or_sent("Sales Order", so_name, subject):
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
<div style="font-family: Lato, Helvetica, Arial, sans-serif; max-width:560px; margin:0 auto; color:#1a1a1a; line-height:1.55;">
  <h1 style="font-family: 'Cormorant Garamond', Georgia, serif; font-size:28px; margin:0 0 12px;">
    Thank you for your order.
  </h1>
  <p style="font-size:15px; color:#5a5a5a; margin:0 0 24px;">
    We&rsquo;ve received your payment and we&rsquo;ll be in touch about delivery.
    This email is your receipt.
  </p>

  <div style="background:#fffcfc; border:1px solid rgba(26,26,26,0.08); border-radius:6px; padding:20px; margin:0 0 24px;">
    <p style="font-family:'Lato',sans-serif; font-size:11px; letter-spacing:0.1em; text-transform:uppercase; color:#7a7a7a; margin:0 0 6px;">
      Order
    </p>
    <p style="font-family:'Cormorant Garamond', Georgia, serif; font-size:22px; margin:0 0 16px; word-break:break-all;">
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

  {policy_documents.customer_policy_block([policy_documents.LANE_READY_TO_ORDER], include_privacy=True)}

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


OPERATOR_EMAIL = DEFAULT_OPERATOR_EMAIL
# Jeff's operator inbox. Update via site_config.json
# (`bench --site frontend set-config lt_operator_email <addr>`) when LT
# wants to route notifications elsewhere; the lookup falls through to
# this constant if no override is set.


def _send_operator_notification(so_name):
    """Email Jeff (or whoever owns the operator inbox) when a new paid
    order lands. Plain HTML body — no PDF attachment (wkhtmltopdf trap).
    Idempotent: looks for an existing Communication or Email Queue row with
    the same subject on this SO.
    """
    so = frappe.get_doc("Sales Order", so_name)
    recipient = get_operator_email()

    subject = f"New paid order — {so.name} — ${flt(so.grand_total):,.2f}"

    if _message_already_queued_or_sent("Sales Order", so_name, subject):
        return

    customer_email = None
    if so.shipping_address_name:
        customer_email = frappe.db.get_value(
            "Address", so.shipping_address_name, "email_id"
        )

    customer_phone = None
    if so.shipping_address_name:
        customer_phone = frappe.db.get_value(
            "Address", so.shipping_address_name, "phone"
        )

    # Pull the address components and assemble a multi-line block.
    # `address_display` is a computed HTML field stored on the SO
    # (so.shipping_address) but not on the Address row itself, so we
    # read the components and format ourselves to keep this email-safe.
    shipping_addr = ""
    if so.shipping_address_name:
        addr = frappe.db.get_value(
            "Address",
            so.shipping_address_name,
            ["address_line1", "address_line2", "city", "state", "pincode", "country"],
            as_dict=True,
        ) or {}
        parts = []
        if addr.get("address_line1"):
            parts.append(addr["address_line1"])
        if addr.get("address_line2"):
            parts.append(addr["address_line2"])
        city_state_zip = ", ".join(filter(None, [
            addr.get("city"),
            " ".join(filter(None, [addr.get("state"), addr.get("pincode")])),
        ]))
        if city_state_zip:
            parts.append(city_state_zip)
        if addr.get("country") and addr.get("country") != "United States":
            parts.append(addr["country"])
        shipping_addr = "\n".join(parts)

    lines_html = ""
    for item in so.items:
        name = item.item_name or item.item_code
        lines_html += (
            f'<tr>'
            f'<td style="padding:6px 12px 6px 0;">{escape_html(name)}</td>'
            f'<td style="padding:6px 12px;text-align:center;">{int(item.qty)}</td>'
            f'<td style="padding:6px 0;text-align:right;">${flt(item.amount):,.2f}</td>'
            f'</tr>'
        )

    site_url = frappe.utils.get_url().rstrip("/")
    desk_link = f"{site_url}/app/sales-order/{so.name}"
    order_notes = _get_customer_order_notes_html(so.name)

    body = f"""
<div style="font-family: Lato, Helvetica, Arial, sans-serif; max-width:600px; color:#1a1a1a; line-height:1.55;">
  <h1 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:22px; margin:0 0 4px;">
    A new paid order just landed.
  </h1>
  <p style="margin:0 0 16px; color:#5a5a5a;">{escape_html(so.name)} &middot; ${flt(so.grand_total):,.2f} {escape_html(so.currency or "USD")}</p>

  <table style="width:100%; border-collapse:collapse; font-size:14px; margin:0 0 16px;">
    <thead>
      <tr style="border-bottom:1px solid #ddd;">
        <th style="text-align:left; padding:6px 12px 6px 0;">Item</th>
        <th style="text-align:center; padding:6px 12px;">Qty</th>
        <th style="text-align:right; padding:6px 0;">Amount</th>
      </tr>
    </thead>
    <tbody>{lines_html}</tbody>
  </table>

  <p style="margin:0 0 6px;"><strong>Customer:</strong> {escape_html(so.customer_name or so.customer or "")}</p>
  {f'<p style="margin:0 0 6px;"><strong>Email:</strong> {escape_html(customer_email)}</p>' if customer_email else ''}
  {f'<p style="margin:0 0 6px;"><strong>Phone:</strong> {escape_html(customer_phone)}</p>' if customer_phone else ''}
  {f'<p style="margin:0 0 16px; white-space:pre-line;"><strong>Shipping:</strong><br>{shipping_addr}</p>' if shipping_addr else ''}
  {f'<p style="margin:0 0 16px; white-space:pre-line;"><strong>Customer notes:</strong><br>{order_notes}</p>' if order_notes else ''}

  <p style="margin:24px 0 0;">
    <a href="{desk_link}" style="display:inline-block; padding:8px 16px; background:#107373; color:#fff; text-decoration:none; border-radius:4px; font-weight:600;">
      Open order in desk
    </a>
  </p>
</div>
"""

    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=body,
        reference_doctype="Sales Order",
        reference_name=so_name,
        now=False,
    )
    frappe.db.commit()


def _get_customer_order_notes_html(so_name):
    subject = f"Customer checkout notes - {so_name}"
    return frappe.db.get_value(
        "Communication",
        {
            "reference_doctype": "Sales Order",
            "reference_name": so_name,
            "subject": subject,
        },
        "content",
    )


def _send_welcome_email_if_first_order(so_name):
    """Send a one-time welcome email to first-time customers.

    Definition of first-time: this SO is the customer's only submitted
    Sales Order. If they have any other submitted SO (this one or
    earlier), they're a returning customer and we skip welcome.

    Idempotent via Communication/Email Queue subject lookup.
    """
    so = frappe.get_doc("Sales Order", so_name)
    if not so.customer:
        return

    # Look for any OTHER submitted SO on this customer.
    other_orders = frappe.get_all(
        "Sales Order",
        filters={
            "customer": so.customer,
            "docstatus": 1,
            "name": ("!=", so_name),
        },
        limit=1,
    )
    if other_orders:
        return  # Returning customer; skip welcome

    email = None
    if so.shipping_address_name:
        email = frappe.db.get_value("Address", so.shipping_address_name, "email_id")
    if not email:
        return

    subject = "Welcome to Locally Twisted"

    if _message_already_queued_or_sent("Customer", so.customer, subject):
        return

    body = f"""
<div style="font-family: Lato, Helvetica, Arial, sans-serif; max-width:560px; margin:0 auto; color:#1a1a1a; line-height:1.6;">
  <h1 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:30px; margin:0 0 16px;">
    Welcome to Locally Twisted.
  </h1>
  <p style="font-size:16px; color:#3a3a3a; margin:0 0 20px;">
    Thanks for your first order with us. We&rsquo;ve been making celebrations
    along the Wasatch Front since 1998, and we&rsquo;re glad you&rsquo;re part of it now.
  </p>

  <h2 style="font-family:'Cormorant Garamond', Georgia, serif; font-size:20px; margin:24px 0 8px;">
    What happens next
  </h2>
  <ul style="font-size:15px; color:#3a3a3a; padding-left:20px; margin:0 0 20px;">
    <li style="margin-bottom:6px;">You&rsquo;ll get a separate receipt email with your order details.</li>
    <li style="margin-bottom:6px;">We&rsquo;ll be in touch about delivery timing for your event.</li>
    <li style="margin-bottom:6px;">If anything changes on your end, just reply to this email.</li>
  </ul>

  <p style="font-size:14px; color:#5a5a5a; margin:24px 0 0;">
    Questions, color preferences, or last-minute additions?
    Reply here or call (801) 285-0860.
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
        reference_doctype="Customer",
        reference_name=so.customer,
        now=False,
    )
    frappe.db.commit()


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect
