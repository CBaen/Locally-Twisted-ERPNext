"""Customer delivery for reviewed product-page quote approval links."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from locally_twisted.communication_copy_policy import (
    BUSINESS_DOCUMENT_COPY,
    routed_alias_copy_risks,
)
from locally_twisted.customer_email_theme import (
    GENERAL_INBOX,
    formal_email_inline_images,
    render_formal_customer_email,
)
from locally_twisted.product_quote_acceptance import issue_product_quote_acceptance_token
from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES


DEFAULT_BUSINESS_BCC = BUSINESS_DOCUMENT_COPY


def send_product_quote_customer_review(
    quotation_name: str,
    *,
    recipient_email: str | None = None,
    business_bcc: str | None = DEFAULT_BUSINESS_BCC,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Send a reviewed product quote approval link with required business BCC.

    This queues a customer review email only. It must not create Sales Orders,
    Sales Invoices, Payment Requests, or any payment path.
    """
    quotation_name = str(quotation_name or "").strip()
    if not quotation_name:
        frappe.throw(
            _("Tiny snag: we need the reviewed quote before sending the approval link."),
            frappe.ValidationError,
        )
    quotation = frappe.get_doc("Quotation", quotation_name)
    recipient = _recipient_email(quotation, recipient_email)
    bcc = _business_bcc(business_bcc)
    token = issue_product_quote_acceptance_token(quotation.name, base_url=base_url)
    subject = f"Your Locally Twisted quote is ready: {quotation.name}"
    message = _customer_message(quotation, token["acceptance_url"])
    frappe.sendmail(
        recipients=[recipient],
        bcc=[bcc],
        subject=subject,
        message=message,
        reference_doctype="Quotation",
        reference_name=quotation.name,
        reply_to=GENERAL_INBOX,
        inline_images=formal_email_inline_images(),
        now=False,
        delayed=True,
    )
    return {
        "ok": True,
        "quotation": quotation.name,
        "recipient": recipient,
        "business_bcc": bcc,
        "acceptance_url": token["acceptance_url"],
        "email_send_allowed": True,
        "sales_order_creation_allowed": False,
        "invoice_creation_allowed": False,
        "payment_request_allowed": False,
    }


def _recipient_email(quotation, explicit: str | None) -> str:
    email = str(explicit or "").strip()
    if not email:
        for fieldname in ("contact_email", "email_id", "customer_email"):
            email = str(quotation.get(fieldname) or "").strip()
            if email:
                break
    if not email and quotation.get("quotation_to") == "Lead" and quotation.get("party_name"):
        email = str(frappe.db.get_value("Lead", quotation.get("party_name"), "email_id") or "").strip()
    if not email and quotation.get("quotation_to") == "Customer" and quotation.get("party_name"):
        email = _linked_customer_contact_email(str(quotation.get("party_name")).strip())
    if "@" not in email:
        frappe.throw(
            _("Tiny snag: this quote needs a customer email before we can send the approval link."),
            frappe.ValidationError,
        )
    return email


def _linked_customer_contact_email(customer_name: str) -> str:
    if not customer_name:
        return ""
    rows = frappe.get_all(
        "Dynamic Link",
        filters={"link_doctype": "Customer", "link_name": customer_name, "parenttype": "Contact"},
        fields=["parent"],
    )
    for row in rows:
        contact_name = row.get("parent")
        if not contact_name:
            continue
        email = str(
            frappe.db.get_value("Contact Email", {"parent": contact_name, "is_primary": 1}, "email_id")
            or frappe.db.get_value("Contact", contact_name, "email_id")
            or frappe.db.get_value("Contact Email", {"parent": contact_name}, "email_id")
            or ""
        ).strip()
        if email:
            return email
    return ""


def _business_bcc(value: str | None) -> str:
    bcc = str(value or "").strip()
    if "@" not in bcc:
        frappe.throw(
            _(
                "Tiny snag: this quote email needs a business copy before it can send. "
                "Please add the Locally Twisted copy address and try again."
            ),
            frappe.ValidationError,
        )
    risks = routed_alias_copy_risks([bcc])
    if risks:
        frappe.throw(
            _(
                "Tiny snag: this quote email copy address loops back into the sending mailbox. "
                "Please use the delivery-safe business copy address before sending."
            ),
            frappe.ValidationError,
        )
    return bcc


def _customer_message(quotation, acceptance_url: str) -> str:
    summary = quotation.get(QUOTATION_FIELDNAMES["summary"]) or "your reviewed quote"
    total = float(quotation.get("grand_total") or 0)
    currency = quotation.get("currency") or "USD"
    body_html = f"""
<p style="margin:0 0 10px;">Your Locally Twisted quote is ready for review.</p>
<div style="background:#F7F7F5;border:1px solid #E1DED8;padding:10px 12px;margin:0 0 12px;">
  <p style="margin:0 0 5px;"><strong>Quote:</strong> {frappe.utils.escape_html(quotation.name)}</p>
  <p style="margin:0 0 5px;"><strong>Scope:</strong> {frappe.utils.escape_html(summary)}</p>
  <p style="margin:0;"><strong>Total:</strong> {total:.2f} {frappe.utils.escape_html(currency)}</p>
</div>
<p style="margin:0 0 12px;">
  <a href="{frappe.utils.escape_html(acceptance_url)}" style="display:inline-block;padding:8px 14px;background:#1F2933;color:#FFFFFF;text-decoration:none;border-radius:4px;font-weight:700;">Review and approve your quote</a>
</p>
<p style="margin:0 0 10px;">Approving the quote creates a draft order for our team to review. It does not charge a card or create an invoice.</p>
<p style="margin:0;">Reply to this email if anything looks off and we will help.</p>
""".strip()
    return render_formal_customer_email(
        title="Your Locally Twisted quote is ready for review",
        preheader=f"Review quote {quotation.name}. No card will be charged by approving.",
        body_html=body_html,
        support_email=GENERAL_INBOX,
    )
