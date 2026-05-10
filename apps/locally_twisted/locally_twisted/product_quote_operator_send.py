"""Operator-owned control for sending reviewed product-page quote links."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from locally_twisted.product_quote_acceptance import product_quote_acceptance_blockers
from locally_twisted.product_quote_customer_delivery import (
    DEFAULT_BUSINESS_BCC,
    send_product_quote_customer_review,
)
from locally_twisted.product_quote_operator_review import STATUS_READY
from locally_twisted.product_quote_runtime import QUOTATION_FIELDNAMES


@frappe.whitelist()
def send_reviewed_product_quote_to_customer(
    quotation_name: str | None = None,
    recipient_email: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Desk action for sending a reviewed product-page quote approval link."""
    quotation_name = str(quotation_name or "").strip()
    if not quotation_name:
        frappe.throw(
            _("Tiny snag: choose the reviewed quote before sending the approval link."),
            frappe.ValidationError,
        )

    quotation = frappe.get_doc("Quotation", quotation_name)
    quotation.check_permission("email")
    _assert_ready_for_operator_send(quotation)

    result = send_product_quote_customer_review(
        quotation.name,
        recipient_email=recipient_email,
        business_bcc=DEFAULT_BUSINESS_BCC,
        base_url=base_url,
    )
    result.update(
        {
            "operator_control": True,
            "customer_delivery_enabled": True,
            "review_status": STATUS_READY,
            "sales_order_creation_allowed": False,
            "invoice_creation_allowed": False,
            "payment_request_allowed": False,
        }
    )
    return result


def _assert_ready_for_operator_send(quotation) -> None:
    status = str(quotation.get(QUOTATION_FIELDNAMES["status"]) or "").strip()
    if status != STATUS_READY:
        frappe.throw(
            _(
                "Tiny snag: this product quote is not marked Ready For Customer Review yet. "
                "Please finish the review before sending an approval link."
            ),
            frappe.ValidationError,
        )

    blockers = product_quote_acceptance_blockers(quotation)
    if blockers:
        frappe.throw(
            _(
                "Tiny snag: this product quote is not ready for a customer approval link yet. "
                "Please clear these review items first: "
            )
            + "; ".join(blockers),
            frappe.ValidationError,
        )
