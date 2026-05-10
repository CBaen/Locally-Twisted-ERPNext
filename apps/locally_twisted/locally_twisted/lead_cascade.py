"""Lead create cascade — what happens immediately when a Lead lands.

Mirrors the Odoo `crm.lead` create() override behavior plus the
`automation_form_ack` base.automation that fired on Hetzner. Three things
fire on Lead insert from a customer-facing form:

1. before_insert: build a useful Lead title from contact_name + service
   list, so Jeff's pipeline shows "Sarah Smith - Balloon Twisting + Face
   Painting" instead of the form's literal "Booking Request".

2. after_insert: dedup-or-create a Contact (Frappe's "Contact" doctype,
   the equivalent of Odoo's res.partner), attach it to the Lead via
   the standard `customer_id` link is wrong for Lead -> we use the
   built-in mechanism: a dynamic-link Contact pointing at the Lead via
   Contact's `links` child table.

3. after_insert: send an auto-acknowledgment email to the customer with
   the LT-branded 24-hour response-time promise. Idempotent via Communication-
   by-subject lookup so a manual rerun never double-sends.

4. after_insert: if the Lead came from a product-page quote handoff, create
   an internal draft Quotation so operator review starts in the right ERPNext
   record instead of stopping at a raw Lead note.

Helpers are isolated so the Lead can still exist for the customer, but partial
failures must leave record-level evidence on the Lead. Error Log-only evidence
is not enough for customer-intent handoffs.

Wired in `hooks.py` `doc_events`. Source-of-truth for the cascade GL
named: "everything should cascade" (2026-04-29 cart session) -> here
applied to Leads on customer-form submission.
"""
import frappe
from frappe.utils import escape_html

from locally_twisted import policy_documents
from locally_twisted import stage_cascade
from locally_twisted.communication_copy_policy import document_copy_kwargs
from locally_twisted.customer_email_theme import (
    AUTO_ACK_SUBJECT,
    GENERAL_INBOX,
    customer_email_inline_images,
    render_customer_email,
)
from locally_twisted.failure_recorder import record_backend_failure


WEBSITE_LEAD_SOURCE = "Website"
LEGACY_AUTO_ACK_SUBJECTS = (
    "We got your message",
    "Locally Twisted Message Sent - 24 Hour or Less Response Time",
)

# Map service-checkbox values (matching Hetzner /book) to the labels we
# join into the Lead title. Keep aligned with `book.py` SERVICE_OPTIONS.
SERVICE_LABEL_MAP = {
    "Balloon Decor": "Balloon Decor",
    "Balloon Twisting": "Balloon Twisting",
    "Face Painting": "Face Painting",
    "Delivery": "Delivery",
    "Pickup": "Pickup",
    "Events Inquiry": "Event Inquiry",
    "Something Else": "Other",
}


def before_insert(doc, method=None):
    """Auto-build a useful Lead title.

    `lead_name` on the Lead doctype is the contact's name. The Lead's
    *display title* (`name1` in the standard Frappe doctype, the
    auto-name) is built differently. We populate `lead_name` with the
    full "Customer - Service" form so Jeff's pipeline shows it.

    Skips work if `lead_name` already holds something more useful than
    a placeholder (e.g. the form's hidden "Booking Request" sentinel).
    """
    placeholder_titles = {"Booking Request", "Quick Booking Request", ""}
    current_title = (doc.lead_name or "").strip()
    services_label = _format_services_label(doc)
    formatted_title = _format_useful_lead_title(doc, current_title, services_label, placeholder_titles)
    if formatted_title:
        doc.lead_name = formatted_title


def _format_useful_lead_title(doc, current_title, services_label, placeholder_titles):
    if current_title and current_title not in placeholder_titles:
        if services_label and current_title in _real_name_candidates(doc):
            return f"{current_title} - {services_label}"
        return None

    parts = []
    real_name = doc.get("first_name") or doc.get("company_name") or ""
    real_name = real_name.strip() if real_name else ""
    if real_name:
        parts.append(real_name)

    if services_label:
        parts.append(services_label)

    if parts:
        return " - ".join(parts)
    return None


def _real_name_candidates(doc):
    candidates = []
    for fieldname in ("first_name", "company_name"):
        value = (doc.get(fieldname) or "").strip()
        if value:
            candidates.append(value)
    first_name = (doc.get("first_name") or "").strip()
    last_name = (doc.get("last_name") or "").strip()
    if first_name and last_name:
        candidates.append(f"{first_name} {last_name}")
    return set(candidates)


def after_insert(doc, method=None):
    """Run the cascade. Each helper isolated in try/except."""
    try:
        _ensure_useful_title_after_insert(doc)
    except Exception as e:
        record_backend_failure(
            surface="lead_contact_ack_cascade",
            step="lead_title_format",
            severity="error",
            primary_doctype="Lead",
            primary_name=doc.name,
            customer_visible_impact="The inquiry was received, but the internal Lead title did not include all useful details.",
            internal_next_action="Review the Lead title and service selections before follow-up.",
            exception=e,
            grouping_key=f"lead_contact_ack_cascade:lead_title_format:{doc.name}",
        )

    try:
        _ensure_contact_link(doc)
    except Exception as e:
        record_backend_failure(
            surface="lead_contact_ack_cascade",
            step="contact_dedup_link",
            severity="error",
            primary_doctype="Lead",
            primary_name=doc.name,
            customer_visible_impact="The inquiry was received, but Contact linking failed.",
            internal_next_action="Review the Lead and link/create the Contact before follow-up.",
            exception=e,
            grouping_key=f"lead_contact_ack_cascade:contact_dedup_link:{doc.name}",
        )

    try:
        if (doc.source or "").strip() == WEBSITE_LEAD_SOURCE:
            _send_auto_ack_email(doc)
    except Exception as e:
        record_backend_failure(
            surface="lead_contact_ack_cascade",
            step="customer_ack_email",
            severity="error",
            primary_doctype="Lead",
            primary_name=doc.name,
            customer_visible_impact="The inquiry was received, but the acknowledgment email did not queue.",
            internal_next_action="Confirm the customer email and send or requeue the acknowledgment.",
            exception=e,
            grouping_key=f"lead_contact_ack_cascade:customer_ack_email:{doc.name}",
        )

    try:
        _ensure_product_quote_draft(doc)
    except Exception as e:
        record_backend_failure(
            surface="lead_product_quote_cascade",
            step="draft_quotation",
            severity="error",
            primary_doctype="Lead",
            primary_name=doc.name,
            customer_visible_impact="The inquiry was received, but the internal product quote draft did not finish.",
            internal_next_action="Open the Lead, review the Product Quote Items table, and create or repair the draft Quotation before quoting.",
            exception=e,
            grouping_key=f"lead_product_quote_cascade:draft_quotation:{doc.name}",
        )

    try:
        stage_cascade.after_insert(doc)
    except Exception as e:
        record_backend_failure(
            surface="lead_contact_ack_cascade",
            step="initial_task_cascade",
            severity="error",
            primary_doctype="Lead",
            primary_name=doc.name,
            customer_visible_impact="The inquiry was received, but the internal follow-up task did not finish.",
            internal_next_action="Create or repair the first operational Task for this Lead.",
            exception=e,
            grouping_key=f"lead_contact_ack_cascade:initial_task_cascade:{doc.name}",
        )


def _ensure_product_quote_draft(doc):
    if not _has_product_quote_payload(doc):
        return None
    from locally_twisted.product_quote_runtime import create_product_page_draft_quotation_from_lead

    return create_product_page_draft_quotation_from_lead(doc.name)


def _has_product_quote_payload(doc) -> bool:
    if doc.get("custom_lt_product_quote_payload"):
        return True
    return bool(doc.get("custom_lt_product_quote_items"))


def _ensure_useful_title_after_insert(doc):
    saved_doc = frappe.get_doc("Lead", doc.name)
    placeholder_titles = {"Booking Request", "Quick Booking Request", ""}
    current_title = (saved_doc.lead_name or "").strip()
    services_label = _format_services_label(saved_doc)
    formatted_title = _format_useful_lead_title(saved_doc, current_title, services_label, placeholder_titles)
    if not formatted_title or formatted_title == current_title:
        return

    frappe.db.set_value("Lead", saved_doc.name, "lead_name", formatted_title, update_modified=False)
    doc.lead_name = formatted_title
    saved_doc.lead_name = formatted_title


def _format_services_label(doc):
    """Pull the multi-select services from the Lead and format them
    for the title.

    custom_event_type is the Desk Table MultiSelect on Lead. The public
    /contact submit handler populates this child table directly so Desk
    conditional sections open from a real website inquiry.

    Returns a comma-joined string like "Balloon Decor + Twisting" or "".
    """
    rows = doc.get("custom_event_type") or []
    if not rows:
        # Legacy fallback for older test records / schema attempts where
        # services were stored as a CSV instead of child rows.
        services_csv = (doc.get("custom_services") or "").strip()
        if not services_csv:
            return ""
        labels = [s.strip() for s in services_csv.split(",") if s.strip()]
    else:
        labels = []
        for row in rows:
            label = (
                row.get("service_type")
                or row.get("service_type_name")
                or row.get("name1")
                or ""
            )
            if label:
                labels.append(label.strip())

    short_labels = [SERVICE_LABEL_MAP.get(l, l) for l in labels]
    if not short_labels:
        return ""
    if len(short_labels) == 1:
        return short_labels[0]
    if len(short_labels) == 2:
        return f"{short_labels[0]} + {short_labels[1]}"
    return f"{short_labels[0]} + {len(short_labels) - 1} more"


def _ensure_contact_link(doc):
    """Find an existing Contact by email/phone or create one. Link it
    to the Lead via Contact.links (Dynamic Link child table).

    Frappe's Contact uses a dynamic-link pattern: a Contact can link to
    multiple parent doctypes (Customer, Supplier, Lead) via the
    `links` child table on Contact. The Lead-side has no FK; the join
    direction is Contact -> Lead.
    """
    email = (doc.email_id or "").strip().lower()
    phone = (doc.mobile_no or doc.phone or "").strip()
    digits = "".join(c for c in phone if c.isdigit())

    contact = None

    # Search by email first
    if email:
        existing = frappe.get_all(
            "Contact Email",
            filters={"email_id": email},
            fields=["parent"],
            limit=1,
        )
        if existing:
            contact = frappe.get_doc("Contact", existing[0].parent)

    # Then by phone (last 10 digits, US numbers)
    if not contact and len(digits) >= 7:
        suffix = digits[-10:]
        existing = frappe.db.sql(
            """
            SELECT cp.parent
            FROM `tabContact Phone` cp
            WHERE REPLACE(REPLACE(REPLACE(REPLACE(cp.phone, ' ', ''), '-', ''), '(', ''), ')', '')
                  LIKE %(suffix)s
            LIMIT 1
            """,
            {"suffix": f"%{suffix}"},
            as_dict=True,
        )
        if existing:
            contact = frappe.get_doc("Contact", existing[0].parent)

    # Fresh: create a new Contact
    if not contact:
        first_name = (doc.first_name or doc.lead_name or "Website Lead").strip()
        last_name = (doc.last_name or "").strip()
        contact = frappe.get_doc({
            "doctype": "Contact",
            "first_name": first_name,
            "last_name": last_name or None,
            "company_name": (doc.company_name or "").strip() or None,
        })
        if email:
            contact.append("email_ids", {
                "email_id": email,
                "is_primary": 1,
            })
        if phone:
            contact.append("phone_nos", {
                "phone": phone,
                "is_primary_mobile_no": 1,
                "is_primary_phone": 1,
            })
        contact.insert(ignore_permissions=True)

    # Attach Contact to this Lead (via Contact.links). Avoid duplicate
    # link rows if the Contact was already linked to this Lead from a
    # prior submission.
    already_linked = any(
        link.link_doctype == "Lead" and link.link_name == doc.name
        for link in (contact.links or [])
    )
    if not already_linked:
        contact.append("links", {
            "link_doctype": "Lead",
            "link_name": doc.name,
        })
        contact.save(ignore_permissions=True)


def _send_auto_ack_email(doc):
    """Send the customer auto-acknowledgment email. Idempotent via
    Communication-by-subject lookup -> safe to retry.
    """
    email = (doc.email_id or "").strip()
    if not email:
        return

    subject = AUTO_ACK_SUBJECT
    customer_name = (doc.lead_name or doc.first_name or "Hello").split(" - ")[0]

    # Idempotency: skip if a Communication with the current subject or the
    # retired launch subject already exists on this Lead.
    existing = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Lead",
            "reference_name": doc.name,
            "subject": ["in", [subject, *LEGACY_AUTO_ACK_SUBJECTS]],
        },
        limit=1,
    )
    if existing:
        return

    safe_name = escape_html(customer_name)
    policy_block = policy_documents.customer_policy_block(
        policy_documents.lanes_for_lead(doc),
        include_privacy=True,
        heading="Before you book",
    )
    body_html = f"""
<p style="margin:0 0 10px;">{safe_name},</p>
<p style="margin:0 0 10px;">
  Thanks for sending your event details to Locally Twisted.
</p>
<p style="margin:0 0 12px;padding:10px 12px;background:#FAF7F2;border-left:4px solid #B31B34;color:#0A0A0B;">
  <strong>Response time:</strong> We will reply in 24 hours or less.
</p>
<p style="margin:0 0 12px;">
  We will review the request and send the next useful step. For ideas while you wait,
  browse our <a href="https://locallytwisted.com/portfolio" style="color:#0E2240;text-decoration:underline;">recent work</a>.
</p>
{policy_block}
""".strip()
    message = render_customer_email(
        title=subject,
        preheader="We got your message and will be in touch soon.",
        body_html=body_html,
        support_email=GENERAL_INBOX,
    )

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=message,
        reference_doctype="Lead",
        reference_name=doc.name,
        reply_to=GENERAL_INBOX,
        inline_images=customer_email_inline_images(),
        now=False,  # queue async
        **document_copy_kwargs(external_audience=True, primary_recipients=[email]),
    )
