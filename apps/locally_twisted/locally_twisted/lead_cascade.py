"""Lead create cascade — what happens immediately when a Lead lands.

Mirrors the catalog_data `crm.lead` create() override behavior plus the
`automation_form_ack` base.automation that fired on current import capture. Three things
fire on Lead insert from a customer-facing form:

1. before_insert: build a useful Lead title from contact_name + service
   list, so Jeff's pipeline shows "Sarah Smith - Balloon Twisting + Face
   Painting" instead of the form's literal "Booking Request".

2. after_insert: dedup-or-create a Contact (Frappe's "Contact" doctype,
   the equivalent of catalog_data's res.partner), attach it to the Lead via
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
from frappe.utils import get_datetime, get_url
from frappe.utils import escape_html

from locally_twisted import policy_documents
from locally_twisted import stage_cascade
from locally_twisted.communication_copy_policy import BUSINESS_DOCUMENT_COPY, document_copy_kwargs
from locally_twisted.customer_email_theme import (
    GENERAL_INBOX,
    customer_email_inline_images,
    form_confirmation_subject,
    render_customer_email,
    render_operator_email,
)
from locally_twisted.failure_recorder import record_backend_failure


WEBSITE_LEAD_SOURCE = "Website"
CUSTOMER_EMAIL_FLAG = "lt_customer_email"
CUSTOMER_EMAIL_NOTE_PREFIX = "Customer email:"
BUSINESS_INQUIRY_SUBJECT_PREFIX = "New website inquiry"
LEGACY_AUTO_ACK_SUBJECTS = (
    "We got your message",
    "Locally Twisted Message Sent - 24 Hour or Less Response Time",
    "\U0001F388Locally Twisted\U0001F388 We Got Your Message! Be in Touch Soon!",
)

# Map service-checkbox values (matching current import capture /book) to the labels we
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


def customer_email_for(doc) -> str:
    """Return the real customer email even when Lead.email_id had to stay blank."""
    flagged_email = (getattr(getattr(doc, "flags", None), CUSTOMER_EMAIL_FLAG, "") or "").strip()
    if flagged_email:
        return flagged_email
    lead_email = (doc.get("email_id") or "").strip()
    if lead_email:
        return lead_email
    return _customer_email_from_note(doc.get("custom_anything_else"))


def customer_email_note(email: str) -> str:
    return f"{CUSTOMER_EMAIL_NOTE_PREFIX} {email.strip()}"


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
            if not getattr(getattr(doc, "flags", None), "lt_defer_customer_ack", False):
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
    email = customer_email_for(doc).lower()
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
        # Permission bypass is guarded by Lead hook context and only creates the matching Contact.
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
        # Permission bypass is guarded by duplicate-link checks for this Lead and Contact pair.
        contact.save(ignore_permissions=True)


def send_customer_inquiry_confirmation(doc, *, photo_uploads=None):
    """Queue the customer-facing confirmation email for a Website inquiry."""
    return _send_auto_ack_email(doc, photo_uploads=photo_uploads)


def _business_inquiry_photo_attachments(doc) -> list[dict[str, str]]:
    photo_urls = {
        row.get("photo")
        for row in (doc.get("custom_inspiration_photos") or [])
        if row.get("photo")
    }
    if not photo_urls:
        return []

    rows = frappe.get_all(
        "File",
        filters={
            "attached_to_doctype": "Lead",
            "attached_to_name": doc.name,
            "file_url": ["in", sorted(photo_urls)],
        },
        fields=["name"],
        order_by="creation asc",
        limit_page_length=20,
    )
    return [{"fid": row["name"]} for row in rows if row.get("name")]


def send_business_inquiry_notification(doc, *, photo_uploads=None):
    """Queue the internal business notification for a Website inquiry."""
    if _has_current_business_notification_queue(doc):
        return {"ok": True, "queued": False, "skipped_existing": True}

    customer_email = customer_email_for(doc)
    customer_name = (doc.lead_name or doc.first_name or "Website inquiry").split(" - ")[0]
    subject = f"{BUSINESS_INQUIRY_SUBJECT_PREFIX} from {customer_name}"
    desk_link = f"{get_url()}/app/lead/{doc.name}"
    body_html = _operator_inquiry_details_block(
        doc,
        customer_email=customer_email,
        photo_uploads=photo_uploads,
        desk_link=desk_link,
    )
    attachments = _business_inquiry_photo_attachments(doc)
    message = render_operator_email(
        title="New website inquiry",
        preheader=f"{customer_name} submitted a Locally Twisted form.",
        body_html=body_html,
    )

    frappe.sendmail(
        recipients=[BUSINESS_DOCUMENT_COPY],
        subject=subject,
        message=message,
        reference_doctype="Lead",
        reference_name=doc.name,
        reply_to=customer_email or GENERAL_INBOX,
        attachments=attachments,
        now=False,
        **document_copy_kwargs(
            external_audience=False,
            primary_recipients=[BUSINESS_DOCUMENT_COPY],
        ),
    )
    if not _has_current_business_notification_queue(doc):
        frappe.throw(
            "We saved your request, but the business notification email did not queue. "
            "Please call (801) 285-0860 or email hi@locallytwisted.com and we will help.",
            frappe.ValidationError,
        )
    return {"ok": True, "queued": True, "skipped_existing": False}


def _send_auto_ack_email(doc, *, photo_uploads=None):
    """Send the customer auto-acknowledgment email. Idempotent via
    Lead-scoped Communication/Email Queue lookup -> safe to retry.
    """
    email = customer_email_for(doc)
    if not email:
        return

    customer_name = (doc.lead_name or doc.first_name or "Hello").split(" - ")[0]
    subject = form_confirmation_subject(customer_name)

    # Idempotency: skip if a Communication with the current subject or the
    # retired launch subject already exists on this Lead.
    existing = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Lead",
            "reference_name": doc.name,
            "subject": ["in", [subject, *LEGACY_AUTO_ACK_SUBJECTS]],
            **_current_lead_creation_filter(doc),
        },
        limit=1,
    )
    queued = _has_current_confirmation_email_queue(doc, recipient=email)
    if existing or queued:
        return {"ok": True, "queued": False, "skipped_existing": True}

    safe_name = escape_html(customer_name)
    details_block = _customer_submitted_details_block(doc, photo_uploads=photo_uploads)
    policy_block = _compact_policy_link_block(policy_documents.lanes_for_lead(doc))
    body_html = f"""
<p style="margin:0 0 7px;">{safe_name},</p>
<p style="margin:0 0 8px;">Thanks for choosing Locally Twisted!</p>
<p style="margin:0 0 8px;">
  If anything you submitted appears incorrect, please reply to this email so we can make it right!
</p>
{details_block}
<p style="margin:8px 0;">
  We will get back to you as soon as possible. Generally within less than 24 hours, no matter the day.
</p>
{policy_block}
""".strip()
    message = render_customer_email(
        title="Here is what we received",
        preheader="Please review your event details and reply if anything needs a fix.",
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
    if not _has_current_confirmation_email_queue(doc, recipient=email):
        frappe.throw(
            "We saved your request, but the confirmation email did not queue. "
            "Please call (801) 285-0860 or email hi@locallytwisted.com and we will help.",
            frappe.ValidationError,
        )
    return {"ok": True, "queued": True, "skipped_existing": False}


def _has_current_confirmation_email_queue(doc, *, recipient=None) -> bool:
    """Return true only for queue rows that belong to this Lead incarnation.

    Test cleanup can remove and recreate Leads with the same autoname. Old
    Email Queue rows with the same reference_name must not suppress the new
    customer's confirmation email.
    """
    return _has_current_email_queue(doc, recipient=recipient or customer_email_for(doc))


def _has_current_business_notification_queue(doc) -> bool:
    return _has_current_email_queue(
        doc,
        recipient=BUSINESS_DOCUMENT_COPY,
        required_message_text=BUSINESS_INQUIRY_SUBJECT_PREFIX,
    )


def _has_current_email_queue(doc, *, recipient=None, required_message_text=None) -> bool:
    filters = {
        "reference_doctype": "Lead",
        "reference_name": doc.name,
        **_current_lead_creation_filter(doc),
    }
    rows = frappe.get_all(
        "Email Queue",
        filters=filters,
        fields=["name", "message"],
        limit_page_length=20,
    )
    normalized_recipient = _normalize_email(recipient)
    for row in rows:
        if normalized_recipient and normalized_recipient not in _email_queue_recipients(row["name"]):
            continue
        if required_message_text and required_message_text not in (row.get("message") or ""):
            continue
        return True
    return False


def _email_queue_recipients(queue_name: str) -> set[str]:
    rows = frappe.get_all(
        "Email Queue Recipient",
        filters={"parent": queue_name},
        fields=["recipient"],
    )
    return {
        _normalize_email(row.get("recipient"))
        for row in rows
        if row.get("recipient")
    }


def _normalize_email(value) -> str:
    return str(value or "").strip().lower()


def _customer_email_from_note(note) -> str:
    text = str(note or "")
    marker_index = text.lower().find(CUSTOMER_EMAIL_NOTE_PREFIX.lower())
    if marker_index < 0:
        return ""
    value = text[marker_index + len(CUSTOMER_EMAIL_NOTE_PREFIX):].strip()
    for separator in (";", "\n", "\r", "<", " "):
        value = value.split(separator, 1)[0].strip()
    return value


def _current_lead_creation_filter(doc) -> dict:
    created_at = get_datetime(doc.get("creation")) if doc.get("creation") else None
    if not created_at:
        return {}
    return {"creation": [">=", created_at]}


def _operator_inquiry_details_block(doc, *, customer_email, photo_uploads=None, desk_link=None) -> str:
    rows: list[tuple[str, str]] = []

    def line(label, value):
        if value is None or value == "" or value == 0:
            return
        rows.append((label, str(value)))

    line("Lead", doc.name)
    line("Name", (doc.get("first_name") or doc.get("lead_name") or "").split(" - ")[0])
    line("Email", customer_email)
    line("Phone", doc.get("mobile_no") or doc.get("phone"))
    line("Preferred contact method", doc.get("custom_preferred_contact_method"))
    line("Company", doc.get("company_name"))
    line("Occasion", doc.get("custom_occasion_type"))
    line("Event date", doc.get("custom_event_date"))
    line("Event start time", doc.get("custom_event_time"))
    line("Event end time", doc.get("custom_event_end_time"))
    line("Location", doc.get("custom_event_location"))
    line("Estimated guests", doc.get("custom_guest_count"))
    services = _services_for_confirmation(doc)
    if services:
        line("Services requested", ", ".join(services))
    line("Indoor / Outdoor", doc.get("custom_indoor_outdoor"))
    if doc.get("custom_shade_required"):
        line("Shade", "Required")
    line("Colors", doc.get("custom_colors"))
    line("Decor types", doc.get("custom_decor_types"))
    line("Setup arrival", doc.get("custom_setup_time_arrival"))
    line("Decor notes", doc.get("custom_decor_notes"))
    line("Twisters", doc.get("custom_num_twisters"))
    line("Twister start", doc.get("custom_artist_start"))
    line("Twister end", doc.get("custom_artist_end"))
    line("Twisting notes", doc.get("custom_twisting_notes"))
    line("Face painters", doc.get("custom_num_painters"))
    line("Painter start", doc.get("custom_painter_start"))
    line("Painter end", doc.get("custom_painter_end"))
    line("Painting notes", doc.get("custom_painting_notes"))
    line("Delivery notes", doc.get("custom_delivery_notes"))
    line("Events inquiry notes", doc.get("custom_package_notes"))
    line("Other notes", doc.get("custom_other_notes"))
    line("Anything else", _customer_note_for_display(doc.get("custom_anything_else")))

    if photo_uploads:
        submitted = int(photo_uploads.get("submitted") or 0)
        attached = int(photo_uploads.get("attached") or 0)
        if submitted:
            line("Reference files", f"{attached} of {submitted} attached")
        upload_issues = _photo_upload_issue_summary(photo_uploads)
        if upload_issues:
            line("Reference file notes", upload_issues)

    rows_html = "".join(
        "<tr>"
        f"<td style=\"padding:4px 10px 4px 0;color:#5B616A;white-space:nowrap;vertical-align:top;\">{escape_html(label)}</td>"
        f"<td style=\"padding:4px 0;color:#1F2933;vertical-align:top;\">{escape_html(value).replace(chr(10), '<br>')}</td>"
        "</tr>"
        for label, value in rows
    )
    open_link = ""
    if desk_link:
        safe_link = escape_html(desk_link)
        open_link = f"""
<p style="margin:14px 0 0;">
  <a href="{safe_link}" style="display:inline-block;padding:8px 14px;background:#111111;color:#ffffff;text-decoration:none;border-radius:4px;font-weight:600;">
    Open Lead in desk
  </a>
</p>
""".strip()

    return f"""
<p style="margin:0 0 8px;">A customer submitted this website inquiry. Review the details below, then follow up from the Lead.</p>
<p style="font-size:13px;font-weight:700;color:#111111;margin:0 0 6px;">Customer-submitted details</p>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:13px;line-height:1.35;">
  {rows_html}
</table>
{open_link}
""".strip()


def _customer_submitted_details_block(doc, *, photo_uploads=None) -> str:
    rows: list[tuple[str, str]] = []

    def line(label, value):
        if value is None or value == "" or value == 0:
            return
        rows.append((label, str(value)))

    line("Name", (doc.get("first_name") or doc.get("lead_name") or "").split(" - ")[0])
    line("Email", customer_email_for(doc))
    line("Phone", doc.get("mobile_no") or doc.get("phone"))
    line("Preferred contact method", doc.get("custom_preferred_contact_method"))
    line("Company", doc.get("company_name"))
    line("Occasion", doc.get("custom_occasion_type"))
    line("Event date", doc.get("custom_event_date"))
    line("Event start time", doc.get("custom_event_time"))
    line("Event end time", doc.get("custom_event_end_time"))
    line("Location", doc.get("custom_event_location"))
    line("Estimated guests", doc.get("custom_guest_count"))
    services = _services_for_confirmation(doc)
    if services:
        line("Services requested", ", ".join(services))
    line("Indoor / Outdoor", doc.get("custom_indoor_outdoor"))
    if doc.get("custom_shade_required"):
        line("Shade", "Required")
    line("Colors", doc.get("custom_colors"))
    line("Decor types", doc.get("custom_decor_types"))
    line("Setup arrival", doc.get("custom_setup_time_arrival"))
    line("Decor notes", doc.get("custom_decor_notes"))
    line("Twisters", doc.get("custom_num_twisters"))
    line("Twister start", doc.get("custom_artist_start"))
    line("Twister end", doc.get("custom_artist_end"))
    line("Twisting notes", doc.get("custom_twisting_notes"))
    line("Face painters", doc.get("custom_num_painters"))
    line("Painter start", doc.get("custom_painter_start"))
    line("Painter end", doc.get("custom_painter_end"))
    line("Painting notes", doc.get("custom_painting_notes"))
    line("Delivery notes", doc.get("custom_delivery_notes"))
    line("Events inquiry notes", doc.get("custom_package_notes"))
    line("Other notes", doc.get("custom_other_notes"))
    line("Anything else", _customer_note_for_display(doc.get("custom_anything_else")))

    attached = int((photo_uploads or {}).get("attached") or 0)
    if attached:
        line("Reference files", f"We received {attached} files for reference.")
    upload_issues = _photo_upload_issue_summary(photo_uploads)
    if upload_issues:
        line("Reference file notes", upload_issues)

    rows_html = "".join(
        "<tr>"
        f"<td style=\"padding:3px 8px 3px 0;color:#595A5C;white-space:nowrap;vertical-align:top;\">{escape_html(label)}</td>"
        f"<td style=\"padding:3px 0;color:#0A0A0B;vertical-align:top;\">{escape_html(value).replace(chr(10), '<br>')}</td>"
        "</tr>"
        for label, value in rows
    )
    return f"""
<div style="border:1px solid #E7E5E1;border-left:3px solid #B31B34;background:#FAF7F2;padding:8px 10px;margin:8px 0;">
  <p style="font-size:13px;font-weight:700;color:#0A0A0B;margin:0 0 5px;">Here is what we received</p>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;font-size:12px;line-height:1.28;">
    {rows_html}
  </table>
</div>
""".strip()


def _services_for_confirmation(doc) -> list[str]:
    labels = []
    for row in doc.get("custom_event_type") or []:
        label = row.get("service_type") or row.get("service_type_name") or row.get("name1")
        if label:
            labels.append(str(label).strip())
    if not labels and doc.get("custom_services"):
        labels = [part.strip() for part in str(doc.get("custom_services")).split(",") if part.strip()]
    return labels


def _photo_upload_issue_summary(photo_uploads) -> str:
    if not photo_uploads:
        return ""
    issues = []
    for item in (photo_uploads.get("rejected") or []) + (photo_uploads.get("failed") or []):
        filename = item.get("filename") or "unnamed upload"
        message = item.get("message") or item.get("reason") or "needs review"
        issues.append(f"{filename}: {message}")
    return "; ".join(issues)


def _customer_note_for_display(note) -> str:
    text = str(note or "").strip()
    if not text:
        return ""

    marker_index = text.lower().find(CUSTOMER_EMAIL_NOTE_PREFIX.lower())
    if marker_index < 0:
        return text

    before = text[:marker_index].strip(" ;\r\n")
    after = text[marker_index + len(CUSTOMER_EMAIL_NOTE_PREFIX):].strip()
    for separator in (";", "\n", "\r"):
        if separator in after:
            after = after.split(separator, 1)[1].strip(" ;\r\n")
            break
    else:
        after = ""
    return "; ".join(part for part in (before, after) if part)


def _compact_policy_link_block(lanes) -> str:
    items = []
    for lane in policy_documents.normalize_lanes(lanes):
        spec = policy_documents.POLICY_LANES[lane]
        items.append(
            f"{escape_html(spec['label'])}: "
            f"<a href=\"{spec['terms']}\" style=\"color:#0E2240;text-decoration:underline;\">Terms</a> "
            f"&middot; <a href=\"{spec['refund']}\" style=\"color:#0E2240;text-decoration:underline;\">Refund policy</a>"
        )
    return f"""
<div style="border-top:1px solid #E7E5E1;margin:8px 0 0;padding-top:7px;font-size:11px;line-height:1.28;color:#595A5C;">
  <p style="margin:0 0 4px;font-weight:700;color:#0A0A0B;">Before you book</p>
  <p style="margin:0;">{"<br>".join(items)}</p>
  <p style="margin:4px 0 0;"><a href="/privacy" style="color:#0E2240;text-decoration:underline;">Privacy policy</a></p>
</div>
""".strip()
