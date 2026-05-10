"""Customer delivery for reviewed product-page quote approval links."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from locally_twisted.communication_copy_policy import (
    BUSINESS_DOCUMENT_COPY,
    routed_alias_copy_risks,
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
    return f"""
<p>Hi there,</p>
<p>Your Locally Twisted quote is ready for review.</p>
<p><strong>Quote:</strong> {frappe.utils.escape_html(quotation.name)}<br>
<strong>Scope:</strong> {frappe.utils.escape_html(summary)}<br>
<strong>Total:</strong> {total:.2f} {frappe.utils.escape_html(currency)}</p>
<p><a href="{frappe.utils.escape_html(acceptance_url)}">Review and approve your quote</a></p>
<p>Approving the quote creates a draft order for our team to review. It does not charge a card or create an invoice.</p>
<p>If anything looks off, reply to this email and we will help.</p>
"""
