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
   "we got your message, 24 hours" copy. Idempotent via Communication-
   by-subject lookup so a manual rerun never double-sends.

ALL helpers wrapped in try/except so a backend hiccup never blocks the
form's success response. The customer's experience comes first; backend
reconciliation can be backfilled by a re-run if anything fails.

Wired in `hooks.py` `doc_events`. Source-of-truth for the cascade GL
named: "everything should cascade" (2026-04-29 cart session) -> here
applied to Leads on customer-form submission.
"""
import frappe
from frappe.utils import escape_html

from locally_twisted import stage_cascade


WEBSITE_LEAD_SOURCE = "Website"

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
    customer_name = (doc.lead_name or "").strip()
    if customer_name and customer_name not in placeholder_titles:
        return  # already meaningful, don't overwrite

    # The form posts contact_name in `lead_name`; if `lead_name` was
    # the literal placeholder, pull the real name from `first_name` /
    # `company_name` etc. Frappe's Lead doesn't have contact_name as a
    # standard field; the customer name comes in via lead_name.
    parts = []
    real_name = doc.get("first_name") or doc.get("company_name") or ""
    real_name = real_name.strip() if real_name else ""
    if real_name:
        parts.append(real_name)

    services_label = _format_services_label(doc)
    if services_label:
        parts.append(services_label)

    if parts:
        doc.lead_name = " - ".join(parts)


def after_insert(doc, method=None):
    """Run the cascade. Each helper isolated in try/except."""
    try:
        _ensure_contact_link(doc)
    except Exception as e:
        frappe.log_error(
            title=f"Lead cascade: Contact dedup failed for {doc.name}",
            message=f"{type(e).__name__}: {e}\nLead: {doc.name}\nemail: {doc.email_id}\nphone: {doc.mobile_no or doc.phone}",
        )

    try:
        if (doc.source or "").strip() == WEBSITE_LEAD_SOURCE:
            _send_auto_ack_email(doc)
    except Exception as e:
        frappe.log_error(
            title=f"Lead cascade: Auto-ack email failed for {doc.name}",
            message=f"{type(e).__name__}: {e}\nLead: {doc.name}\nemail: {doc.email_id}",
        )

    stage_cascade.after_insert(doc)


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

    Copy ported from the Odoo `template_form_acknowledgment` mail.template:
    subject "We got your message", body "Thank you for reaching out...
    24 hours... browse our shop for inspiration."
    """
    email = (doc.email_id or "").strip()
    if not email:
        return

    subject = "We got your message"
    customer_name = (doc.lead_name or doc.first_name or "Hello").split(" - ")[0]

    # Idempotency: skip if a Communication with this subject already
    # exists on this Lead.
    existing = frappe.get_all(
        "Communication",
        filters={
            "reference_doctype": "Lead",
            "reference_name": doc.name,
            "subject": subject,
        },
        limit=1,
    )
    if existing:
        return

    safe_name = escape_html(customer_name)
    body_html = f"""
<div style="max-width: 600px; margin: 0 auto; font-family: 'Lato', Arial, sans-serif; color: #595A5C;">
    <div style="background-color: #FBF5F2; padding: 24px 32px; text-align: center;">
        <h2 style="font-family: Georgia, 'Cormorant Garamond', serif; color: #1A1A1A; margin: 0; font-size: 24px;">
            Locally Twisted
        </h2>
    </div>
    <div style="padding: 32px; background-color: #FBFBFB;">
        <p style="font-size: 15px; line-height: 1.6;">{safe_name},</p>
        <p style="font-size: 15px; line-height: 1.6;">
            Thank you for reaching out. We've received your message and
            we'll be in touch within 24 hours.
        </p>
        <p style="font-size: 15px; line-height: 1.6;">
            In the meantime, feel free to browse our
            <a href="/shop" style="color: #1A1A1A; text-decoration: underline;">shop</a>
            for inspiration.
        </p>
        <p style="font-size: 15px; line-height: 1.6; margin-top: 24px;">
            Warmly,<br/>
            The Locally Twisted Family
        </p>
    </div>
    <div style="text-align: center; padding: 16px; font-size: 12px; color: #999;">
        Locally Twisted &mdash; Utah's Balloon Specialists<br/>
        8969 S 2700 W, West Jordan, UT 84088
    </div>
</div>
""".strip()

    frappe.sendmail(
        recipients=[email],
        subject=subject,
        message=body_html,
        reference_doctype="Lead",
        reference_name=doc.name,
        now=False,  # queue async
    )
