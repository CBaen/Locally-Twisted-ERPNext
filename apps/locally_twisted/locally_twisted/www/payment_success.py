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
follow-up. Browser-return reconciliation errors add a
`reconciliation=pending` flag to the thank-you URL so the customer sees
payment received without being told final receipt paperwork is already done.
"""
from urllib.parse import urlencode

import frappe
from frappe.utils import escape_html, flt

from locally_twisted import policy_documents
from locally_twisted.communication_copy_policy import document_copy_kwargs
from locally_twisted.crm_pipeline import PIPELINE_FIELD
from locally_twisted.customer_email_theme import (
    BILLING_INBOX,
    GENERAL_INBOX,
    formal_email_inline_images,
    render_formal_customer_email,
    render_operator_email,
)
from locally_twisted.failure_recorder import record_backend_failure
from locally_twisted.payments.settings import (
    DEFAULT_OPERATOR_EMAIL,
    get_operator_email,
)
from locally_twisted.product_page_runtime import customer_facing_line_label


no_cache = 1
sitemap = 0
PAYMENT_CHECK_ROUTE = "/thank-you?status=payment-check"


def get_context(context):
    session_id = (frappe.form_dict.get("session_id") or "").strip()
    if session_id:
        _handle_stripe_session(session_id)

    docname_raw = (frappe.form_dict.get("docname") or "").strip()
    doctype = (frappe.form_dict.get("doctype") or "").strip()
    docname = docname_raw.split("?", 1)[0] if docname_raw else ""

    if doctype != "Payment Request" or not docname:
        _redirect(PAYMENT_CHECK_ROUTE)

    integration_status = frappe.db.get_value(
        "Integration Request",
        {"reference_doctype": "Payment Request", "reference_docname": docname},
        "status",
    )
    if integration_status != "Completed":
        _redirect(PAYMENT_CHECK_ROUTE)

    sales_order = frappe.db.get_value("Payment Request", docname, "reference_name")
    if not sales_order:
        _redirect(PAYMENT_CHECK_ROUTE)

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
        _redirect(PAYMENT_CHECK_ROUTE)

    if (session.get("payment_status") or "").lower() != "paid":
        _redirect(PAYMENT_CHECK_ROUTE)

    sales_order = (
        session.get("client_reference_id")
        or (session.get("metadata") or {}).get("sales_order")
    )
    if not sales_order:
        _redirect(PAYMENT_CHECK_ROUTE)

    result = reconcile_paid_sales_order(
        sales_order,
        payment_request=(session.get("metadata") or {}).get("payment_request"),
        source="payment_success",
        raise_on_error=False,
    )

    query = {"order": sales_order}
    if not result.get("ok"):
        query["reconciliation"] = "pending"
    _redirect(f"/thank-you?{urlencode(query)}")


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
        run("Lead conversion", _convert_checkout_leads_after_payment, so_name)
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


def _convert_checkout_leads_after_payment(so_name):
    """Convert Contact-linked inquiry Leads only after payment is verified."""
    so = frappe.get_doc("Sales Order", so_name)
    if not so.customer:
        return []

    lead_names = _lead_names_for_customer(so.customer)
    converted = []
    failures = []

    for lead_name in lead_names:
        try:
            lead = frappe.get_doc("Lead", lead_name)
            changed = False
            if lead.status != "Converted":
                lead.status = "Converted"
                changed = True
            if not lead.get("customer"):
                lead.customer = so.customer
                changed = True
            if lead.meta.has_field(PIPELINE_FIELD) and lead.get(PIPELINE_FIELD) != "Approved":
                lead.set(PIPELINE_FIELD, "Approved")
                changed = True
            if changed:
                lead.flags.ignore_permissions = True
                lead.save(ignore_permissions=True)
            converted.append(lead.name)
        except Exception as exc:
            failures.append(f"{lead_name}: {type(exc).__name__}: {exc}")
            record_backend_failure(
                surface="payment_success_paid_order_cascade",
                step="lead_conversion",
                severity="error",
                primary_doctype="Sales Order",
                primary_name=so_name,
                linked_doctype="Lead",
                linked_name=lead_name,
                customer_visible_impact="Payment was received, but the earlier inquiry did not fully move into the paid-order workflow.",
                internal_next_action="Review the linked Lead, mark it converted, and connect it to the checkout Customer.",
                exception=exc,
                grouping_key=f"payment_success_paid_order_cascade:lead_conversion:{so_name}:{lead_name}",
            )

    if failures:
        raise PaidOrderReconciliationError("; ".join(failures))
    return converted


def _lead_names_for_customer(customer_name):
    contact_links = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Customer",
            "link_name": customer_name,
            "parenttype": "Contact",
        },
        fields=["parent"],
        limit_page_length=100,
    )
    contact_names = sorted({row["parent"] for row in contact_links if row.get("parent")})
    if not contact_names:
        return []

    lead_links = frappe.get_all(
        "Dynamic Link",
        filters={
            "link_doctype": "Lead",
            "parenttype": "Contact",
            "parent": ("in", contact_names),
        },
        fields=["link_name"],
        limit_page_length=100,
    )
    return sorted({row["link_name"] for row in lead_links if row.get("link_name")})


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
    from locally_twisted.product_page_runtime import copy_sales_order_line_configuration_to_invoice

    si = make_sales_invoice(so_name, ignore_permissions=True)
    si.flags.ignore_permissions = True
    si.flags.mute_email = True
    si.set_missing_values()
    copy_sales_order_line_configuration_to_invoice(si, so_name)
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
        message = f"No email found for Sales Order {so_name}; receipt email cannot be sent."
        record_backend_failure(
            surface="payment_success_paid_order_cascade",
            step="receipt_email_missing_recipient",
            severity="error",
            primary_doctype="Sales Order",
            primary_name=so_name,
            customer_visible_impact="Payment was received, but the customer receipt email could not be sent.",
            internal_next_action="Add or repair the customer email on the Sales Order/Customer/Contact and resend the receipt.",
            exception=message,
            grouping_key=f"payment_success_paid_order_cascade:receipt_email_missing_recipient:{so_name}",
        )
        frappe.log_error(
            f"No email found for SO {so_name} — skipping receipt",
            "payment_success: receipt email skipped",
        )
        raise PaidOrderReconciliationError(message)

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
        name = customer_facing_line_label(item)
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

    body_content = f"""
<p style="margin:0 0 10px;">
  We&rsquo;ve received your payment and we&rsquo;ll be in touch about delivery.
  This email is your receipt.
</p>
<div style="background:#FAF7F2;border:1px solid #E7E5E1;border-left:4px solid #B89A5B;padding:12px 14px;margin:0 0 14px;">
  <p style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:#595A5C;margin:0 0 4px;">
    Order
  </p>
  <p style="font-family:Georgia,'Times New Roman',serif;font-size:20px;margin:0 0 10px;color:#0E2240;word-break:break-all;">
    {escape_html(so.name)}
  </p>
  <table style="width:100%;border-collapse:collapse;font-size:13px;">
    {lines_html}
    <tr>
      <td style="padding:10px 0 0;font-weight:700;color:#0A0A0B;">Total</td>
      <td style="padding:10px 0 0;text-align:right;font-weight:700;color:#0A0A0B;">
        ${flt(so.grand_total):,.2f} {escape_html(so.currency or "USD")}
      </td>
    </tr>
  </table>
</div>
{policy_documents.customer_policy_block([policy_documents.LANE_READY_TO_ORDER], include_privacy=True)}
<p style="font-size:13px;color:#595A5C;margin:0;">
  Questions about your order or payment? Reply to this email or contact
  <a href="mailto:{BILLING_INBOX}" style="color:#0E2240;text-decoration:underline;">{BILLING_INBOX}</a>.
</p>
""".strip()
    body = render_formal_customer_email(
        title="Your Locally Twisted order is confirmed",
        preheader=f"Payment received for {so.name}. This email is your receipt.",
        body_html=body_content,
        support_email=BILLING_INBOX,
    )

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=body,
        reference_doctype="Sales Order",
        reference_name=so_name,
        reply_to=BILLING_INBOX,
        inline_images=formal_email_inline_images(),
        # attach_print intentionally omitted — we never want to attach a
        # PDF render (wkhtmltopdf-in-Docker trap). The HTML body is the
        # receipt.
        now=False,
        **document_copy_kwargs(external_audience=True, primary_recipients=[email]),
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
        name = customer_facing_line_label(item)
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

    body_content = f"""
  <p style="margin:0 0 10px;"><strong>Order:</strong> {escape_html(so.name)}<br>
  <strong>Total:</strong> ${flt(so.grand_total):,.2f} {escape_html(so.currency or "USD")}</p>
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

  <div style="background:#F7F7F5;border:1px solid #E1DED8;padding:10px 12px;margin:0 0 14px;">
  <p style="margin:0 0 6px;"><strong>Customer:</strong> {escape_html(so.customer_name or so.customer or "")}</p>
  {f'<p style="margin:0 0 6px;"><strong>Email:</strong> {escape_html(customer_email)}</p>' if customer_email else ''}
  {f'<p style="margin:0 0 6px;"><strong>Phone:</strong> {escape_html(customer_phone)}</p>' if customer_phone else ''}
  {f'<p style="margin:0 0 6px; white-space:pre-line;"><strong>Shipping:</strong><br>{escape_html(shipping_addr)}</p>' if shipping_addr else ''}
  {f'<p style="margin:0; white-space:pre-line;"><strong>Customer notes:</strong><br>{order_notes}</p>' if order_notes else ''}
  </div>

  <p style="margin:14px 0 0;">
    <a href="{desk_link}" style="display:inline-block; padding:8px 16px; background:#107373; color:#fff; text-decoration:none; border-radius:4px; font-weight:600;">
      Open order in desk
    </a>
  </p>
"""
    body = render_operator_email(
        title="New paid order",
        preheader=f"{so.name} - ${flt(so.grand_total):,.2f} {so.currency or 'USD'}",
        body_html=body_content,
    )

    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=body,
        reference_doctype="Sales Order",
        reference_name=so_name,
        now=False,
        **document_copy_kwargs(external_audience=False, primary_recipients=[recipient]),
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

    body_content = """
<p style="margin:0 0 10px;">
  Thanks for your first order with us. We&rsquo;ve been making celebrations
  along the Wasatch Front since 1998, and we&rsquo;re glad you&rsquo;re part of it now.
</p>
<p style="font-family:Georgia,'Times New Roman',serif;font-size:18px;color:#0E2240;margin:14px 0 6px;">
  What happens next
</p>
<ul style="font-size:14px;color:#30343A;padding-left:18px;margin:0 0 12px;">
  <li style="margin-bottom:5px;">You&rsquo;ll get a separate receipt email with your order details.</li>
  <li style="margin-bottom:5px;">We&rsquo;ll be in touch about delivery timing for your event.</li>
  <li style="margin-bottom:5px;">If anything changes on your end, just reply to this email.</li>
</ul>
<p style="font-size:13px;color:#595A5C;margin:0;">
  Questions, color preferences, or last-minute additions? Reply here or contact
  <a href="mailto:hi@locallytwisted.com" style="color:#0E2240;text-decoration:underline;">hi@locallytwisted.com</a>.
</p>
""".strip()
    body = render_formal_customer_email(
        title="Welcome to Locally Twisted",
        preheader="Thanks for your first order. Here is what happens next.",
        body_html=body_content,
        support_email=GENERAL_INBOX,
    )

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=body,
        reference_doctype="Customer",
        reference_name=so.customer,
        reply_to=GENERAL_INBOX,
        inline_images=formal_email_inline_images(),
        now=False,
        **document_copy_kwargs(external_audience=True, primary_recipients=[email]),
    )
    frappe.db.commit()


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect
