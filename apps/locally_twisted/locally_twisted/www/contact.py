"""Contact page controller and form-submit endpoint.

Renders /contact as a portal page and accepts inquiries via the
whitelisted `submit_contact` method, creating a Lead record + a
linked Communication for the message body. Loud-failure compliant:
all exceptions propagate to the caller as 500 + JSON error so the
client-side script can surface them visibly to the user.

Source of truth for content/structure: the prior Odoo project's
addons/locally_twisted/views/pages/page_contact.xml — captured
verbatim 2026-04-26 per the standing rule on customer-facing copy.
"""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html, validate_email_address

no_cache = 1
sitemap = 1


EVENT_TYPES = [
    ("birthday", "Birthday Party"),
    ("wedding", "Wedding"),
    ("baby_shower", "Baby Shower"),
    ("corporate", "Corporate Event"),
    ("grand_opening", "Grand Opening"),
    ("other", "Other"),
]


PAGE_CSS = """
.lt-contact__intro {
    background-color: var(--lt-blue-tint);
    padding: 3rem 1rem 2.5rem;
    text-align: center;
}
.lt-contact__intro h1 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
    line-height: 1.15;
}
.lt-contact__intro-lede {
    font-size: 1.125rem;
    color: var(--lt-soft-gray);
    margin: 0;
    font-weight: 300;
}

.lt-contact {
    padding: 3rem 1rem;
}
.lt-contact__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2.5rem;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 992px) {
    .lt-contact__grid {
        grid-template-columns: 1.4fr 1fr;
        gap: 3rem;
    }
}

.lt-contact__form-wrap h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.625rem;
    color: var(--lt-near-black);
    margin: 0 0 1.25rem;
    line-height: 1.2;
}

.lt-contact__form .row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}
@media (min-width: 768px) {
    .lt-contact__form .row {
        grid-template-columns: 1fr 1fr;
    }
}

.lt-contact__field {
    display: flex;
    flex-direction: column;
}
.lt-contact__field label {
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin-bottom: 0.35rem;
}
.lt-contact__required {
    color: #c0392b;
    margin-left: 0.15rem;
}
.lt-contact__input,
.lt-contact__select,
.lt-contact__textarea {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    padding: 0.65rem 0.85rem;
    border: 1px solid rgba(26, 26, 26, 0.18);
    border-radius: 0.375rem;
    background-color: var(--lt-white);
    color: var(--lt-near-black);
    width: 100%;
    min-height: 44px;
}
.lt-contact__input:focus,
.lt-contact__select:focus,
.lt-contact__textarea:focus {
    outline: 2px solid var(--lt-teal);
    outline-offset: 1px;
    border-color: var(--lt-teal);
}
.lt-contact__textarea {
    min-height: 120px;
    resize: vertical;
}

.lt-contact__privacy {
    font-size: 0.8125rem;
    color: var(--lt-soft-gray);
    margin: 0.75rem 0 1.25rem;
}
.lt-contact__privacy a {
    color: var(--lt-soft-gray);
    text-decoration: underline;
}

.lt-contact__submit {
    background-color: var(--lt-teal);
    color: var(--lt-white);
    border: none;
    border-radius: 0.375rem;
    padding: 0.875rem 2rem;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    min-height: 48px;
    min-width: 160px;
}
.lt-contact__submit:hover,
.lt-contact__submit:focus-visible {
    background-color: #006666;
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-contact__submit[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
}

.lt-contact__feedback {
    margin-top: 1rem;
    padding: 0.85rem 1rem;
    border-radius: 0.375rem;
    font-size: 0.95rem;
    display: none;
}
.lt-contact__feedback.is-success {
    display: block;
    background-color: #e8f6ee;
    border: 1px solid #198754;
    color: #0e5732;
}
.lt-contact__feedback.is-error {
    display: block;
    background-color: #fdecec;
    border: 1px solid #c0392b;
    color: #842424;
}

.lt-contact__info-card {
    background-color: var(--lt-blush-tint);
    border-radius: 0.5rem;
    padding: 1.75rem;
}
.lt-contact__info-card h3 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.375rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
}
.lt-contact__info-list {
    list-style: none;
    margin: 0 0 1.25rem;
    padding: 0;
}
.lt-contact__info-list li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.45rem;
    font-size: 1rem;
    color: var(--lt-soft-gray);
}
.lt-contact__info-list a {
    color: var(--lt-near-black);
    text-decoration: none;
    font-weight: 600;
}
.lt-contact__info-list a:hover,
.lt-contact__info-list a:focus-visible {
    text-decoration: underline;
}
.lt-contact__icon {
    display: inline-flex;
    width: 1.25rem;
    font-size: 1rem;
}

.lt-contact__divider {
    border: none;
    border-top: 1px solid rgba(26, 26, 26, 0.1);
    margin: 1rem 0;
}
.lt-contact__info-card h4 {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.4rem;
}
.lt-contact__info-card p {
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0 0 0.85rem;
}
.lt-contact__call-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.55rem 1.1rem;
    background-color: transparent;
    border: 1px solid var(--lt-near-black);
    color: var(--lt-near-black);
    border-radius: 0.375rem;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.875rem;
}
.lt-contact__call-btn:hover,
.lt-contact__call-btn:focus-visible {
    background-color: var(--lt-near-black);
    color: var(--lt-white);
}

.lt-contact__social-block {
    margin-top: 1.5rem;
}
.lt-contact__social-block h4 {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.6rem;
}
.lt-contact__social-row {
    display: inline-flex;
    gap: 0.65rem;
}
.lt-contact__social-row a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.1);
}
.lt-contact__social-row a:hover,
.lt-contact__social-row a:focus-visible {
    outline: 2px solid var(--lt-teal);
    outline-offset: 2px;
}
.lt-contact__social-row img {
    width: 22px;
    height: 22px;
    display: block;
}

/* Locations section */
.lt-locations {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem;
}
.lt-locations h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.875rem;
    text-align: center;
    margin: 0 0 0.5rem;
    color: var(--lt-near-black);
}
.lt-locations__subtitle {
    text-align: center;
    font-size: 1rem;
    color: var(--lt-soft-gray);
    margin: 0 auto 2rem;
    max-width: 540px;
}
.lt-locations__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-locations__grid {
        grid-template-columns: 1fr 1fr;
    }
}
.lt-location-card {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.75rem;
}
.lt-location-card__badge {
    display: inline-block;
    background-color: var(--lt-blue-tint);
    color: var(--lt-near-black);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    margin-bottom: 0.75rem;
}
.lt-location-card h3 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    margin: 0 0 0.5rem;
    color: var(--lt-near-black);
}
.lt-location-card__desc {
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0 0 1rem;
    line-height: 1.55;
}
.lt-location-card__details {
    list-style: none;
    margin: 0 0 1rem;
    padding: 0;
}
.lt-location-card__details li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.35rem;
    font-size: 0.9375rem;
    color: var(--lt-soft-gray);
}
.lt-location-card__details a {
    color: var(--lt-near-black);
    text-decoration: none;
    font-weight: 600;
}
.lt-location-card__directions {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 1rem;
    border: 1px solid var(--lt-near-black);
    color: var(--lt-near-black);
    border-radius: 0.375rem;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.875rem;
}
.lt-location-card__directions:hover,
.lt-location-card__directions:focus-visible {
    background-color: var(--lt-near-black);
    color: var(--lt-white);
}
"""


def get_context(context):
    context.title = "Contact — Locally Twisted | Book Your Balloon Event"
    context.metatags = {
        "description": (
            "Get a quote for custom balloon decor in Utah. "
            "Arches, garlands, drops, twisting, and face painting for any celebration."
        ),
        "og:title": "Contact Locally Twisted",
        "og:description": "Tell us about your celebration. We'll get back to you with a quote.",
        "og:type": "website",
    }
    context.event_types = EVENT_TYPES
    context.colocated_css = PAGE_CSS
    return context


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=20, seconds=60 * 60)
def submit_contact(name="", email="", phone="", event_type="", event_date="", message=""):
    """Receive a contact form submission from /contact and create a Lead.

    Required: name, email. Everything else optional.
    Returns JSON with ok=True and the created Lead's name on success.
    Raises (Frappe handles 4xx/5xx + JSON body) on validation or
    persistence failure so the client-side script can show a visible
    error state to the user. Loud-failure compliant.
    """
    name = (name or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()
    event_type = (event_type or "").strip()
    event_date = (event_date or "").strip()
    message = (message or "").strip()

    if not name:
        frappe.throw(_("Please tell us your name."), frappe.ValidationError)
    if not email:
        frappe.throw(_("Please give us an email so we can reply."), frappe.ValidationError)

    # Will throw frappe.InvalidEmailAddressError on bad input.
    email = validate_email_address(email, throw=True)

    safe_name = escape_html(name)
    safe_phone = escape_html(phone)
    safe_message = escape_html(message)

    # Create the Lead
    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": safe_name,
        "email_id": email,
        "mobile_no": safe_phone,
        "source": "Website",
        "status": "Open",
    })
    lead.insert(ignore_permissions=True)

    # Build a readable communication body from the optional fields.
    parts = []
    if event_type:
        label = dict(EVENT_TYPES).get(event_type, event_type)
        parts.append(f"<strong>Event type:</strong> {escape_html(label)}")
    if event_date:
        parts.append(f"<strong>Event date:</strong> {escape_html(event_date)}")
    if safe_phone:
        parts.append(f"<strong>Phone:</strong> {safe_phone}")
    if safe_message:
        parts.append("")
        parts.append(safe_message.replace("\n", "<br>"))
    body_html = "<br>".join(parts) if parts else "(no additional details provided)"

    # Attach a Communication so the message lives on the Lead's timeline.
    frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "sender": email,
        "subject": f"New inquiry from {safe_name}",
        "content": body_html,
        "sent_or_received": "Received",
        "status": "Open",
        "reference_doctype": "Lead",
        "reference_name": lead.name,
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"ok": True, "lead": lead.name}
