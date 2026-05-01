"""Balloon Twisting & Face Painting service page + booking endpoint.

Frappe maps this file to the route /balloon-twisting-and-face-painting
(underscore filename → dash URL automatically, see Frappe's own
www/complete_signup.html → /complete-signup pattern).

Source of truth for content/structure: the prior Odoo project's
addons/locally_twisted/views/pages/page_balloon_twisting.xml — captured
verbatim 2026-04-26 per the standing rule on customer-facing copy.

For first ship the image carousels, event-type crawl, and confirmation
modal are deliberately omitted; the form uses an inline success banner.
"""
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html, validate_email_address

no_cache = 1
sitemap = 1


SERVICE_CHOICES = [
    ("both", "Both — Balloon Twisting & Face Painting"),
    ("twisting", "Balloon Twisting Only"),
    ("painting", "Face Painting Only"),
]
HOURS_OPTIONS = [
    ("1", "1 hour"),
    ("2", "2 hours"),
    ("3", "3 hours"),
    ("4+", "4+ hours"),
]
EVENT_TYPES = [
    ("birthday", "Birthday Party"),
    ("school", "School Event"),
    ("corporate", "Corporate Event"),
    ("festival", "Festival / Fair"),
    ("church", "Church Event"),
    ("reunion", "Family Reunion"),
    ("holiday", "Holiday Party"),
    ("other", "Other"),
]


PAGE_CSS = """
.lt-btfp__intro {
    background-color: var(--lt-blush-tint);
    padding: 4rem 1.5rem 3.5rem;
    text-align: left;
}
.lt-btfp__intro-inner {
    max-width: 1100px;
    margin: 0 auto;
    text-align: left;
}
.lt-btfp__intro-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.25rem;
    color: var(--lt-near-black);
    margin: 0 0 1.25rem;
    line-height: 1.1;
    text-align: left;
    max-width: 30rem;
}
.lt-btfp__intro-lede {
    font-size: 1.0625rem;
    color: var(--lt-soft-gray);
    margin: 0;
    font-weight: 300;
    text-align: left;
    max-width: 32rem;
    line-height: 1.6;
}
@media (min-width: 992px) {
    .lt-btfp__intro {
        padding: 5rem 2rem 4rem;
    }
    .lt-btfp__intro-title {
        font-size: 3.25rem;
    }
}

.lt-btfp__banner {
    background-color: var(--lt-blue-tint);
    padding: 1.25rem 1rem;
    border-top: 1px solid rgba(26, 26, 26, 0.06);
    border-bottom: 1px solid rgba(26, 26, 26, 0.06);
}
.lt-btfp__banner-inner {
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    text-align: center;
}
@media (min-width: 768px) {
    .lt-btfp__banner-inner {
        flex-direction: row;
        gap: 1.5rem;
    }
}
.lt-btfp__banner-copy {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    color: var(--lt-near-black);
    margin: 0;
    line-height: 1.45;
}
.lt-btfp__banner-copy strong {
    font-weight: 600;
}
.lt-btfp__banner-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem 1rem;
    align-items: center;
}
.lt-btfp__banner-link {
    font-family: 'Raleway', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--lt-near-black);
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
.lt-btfp__banner-link:hover,
.lt-btfp__banner-link:focus-visible {
    text-decoration-thickness: 2px;
}
.lt-btfp__banner-link:focus-visible {
    outline: 3px solid var(--lt-teal);
    outline-offset: 3px;
    border-radius: 2px;
}

.lt-btfp__services {
    padding: 2.5rem 1rem;
}
.lt-btfp__services-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 768px) {
    .lt-btfp__services-grid {
        grid-template-columns: 1fr 1fr;
    }
}
.lt-btfp__service-card {
    background-color: var(--lt-white);
    border: 1px solid rgba(26, 26, 26, 0.08);
    border-radius: 0.5rem;
    padding: 1.75rem;
}
.lt-btfp__service-card h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    margin: 0 0 0.85rem;
    color: var(--lt-near-black);
}
.lt-btfp__service-card ul {
    list-style: disc;
    padding-left: 1.25rem;
    margin: 0;
    color: var(--lt-soft-gray);
    line-height: 1.55;
}
.lt-btfp__service-card li {
    margin-bottom: 0.4rem;
}
.lt-btfp__carousel {
    width: 100%;
    /* Portrait 3:4 — matches the dominant source-photo orientation
       (10 of 12 photos are portrait/square iPhone shots). Avoids the
       aggressive cover-crop that made portraits feel "too close-up".
       No max-width cap — let carousels fill their column for presence. */
    aspect-ratio: 3 / 4;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
    background-color: var(--lt-blush-tint);
    position: relative;
    overflow: hidden;
}
.lt-btfp__carousel-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0;
    animation: lt-btfp-carousel-fade 36s infinite;
}
.lt-btfp__carousel-img:nth-child(1) { animation-delay: 0s; }
.lt-btfp__carousel-img:nth-child(2) { animation-delay: 6s; }
.lt-btfp__carousel-img:nth-child(3) { animation-delay: 12s; }
.lt-btfp__carousel-img:nth-child(4) { animation-delay: 18s; }
.lt-btfp__carousel-img:nth-child(5) { animation-delay: 24s; }
.lt-btfp__carousel-img:nth-child(6) { animation-delay: 30s; }
@keyframes lt-btfp-carousel-fade {
    0%   { opacity: 0; }
    3%   { opacity: 1; }
    16%  { opacity: 1; }
    19%  { opacity: 0; }
    100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .lt-btfp__carousel-img { animation: none; opacity: 0; }
    .lt-btfp__carousel-img:first-child { opacity: 1; }
}

.lt-btfp__booking {
    background-color: var(--lt-near-white);
    padding: 3rem 1rem;
}
.lt-btfp__booking-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2.5rem;
    max-width: 1100px;
    margin: 0 auto;
}
@media (min-width: 992px) {
    .lt-btfp__booking-grid {
        grid-template-columns: 1.6fr 1fr;
        gap: 3rem;
    }
}
.lt-btfp__form-wrap h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.75rem;
    color: var(--lt-near-black);
    margin: 0 0 0.4rem;
}
.lt-btfp__form-subtitle {
    color: var(--lt-soft-gray);
    margin: 0 0 1.5rem;
}
.lt-btfp__form .row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}
@media (min-width: 768px) {
    .lt-btfp__form .row {
        grid-template-columns: 1fr 1fr;
    }
}
.lt-btfp__field {
    display: flex;
    flex-direction: column;
}
.lt-btfp__field label {
    font-family: 'Raleway', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin-bottom: 0.35rem;
}
.lt-btfp__required {
    color: #c0392b;
    margin-left: 0.15rem;
}
.lt-btfp__input,
.lt-btfp__select,
.lt-btfp__textarea {
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
.lt-btfp__input:focus,
.lt-btfp__select:focus,
.lt-btfp__textarea:focus {
    outline: 2px solid var(--lt-teal);
    outline-offset: 1px;
    border-color: var(--lt-teal);
}
.lt-btfp__textarea {
    min-height: 90px;
    resize: vertical;
}
.lt-btfp__privacy {
    font-size: 0.8125rem;
    color: var(--lt-soft-gray);
    margin: 0.75rem 0 1.25rem;
}
.lt-btfp__privacy a {
    color: var(--lt-soft-gray);
    text-decoration: underline;
}
.lt-btfp__submit {
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
    min-width: 180px;
}
.lt-btfp__submit:hover,
.lt-btfp__submit:focus-visible {
    background-color: #006666;
    outline: 2px solid var(--lt-near-black);
    outline-offset: 2px;
}
.lt-btfp__submit[disabled] {
    opacity: 0.6;
    cursor: not-allowed;
}
.lt-btfp__feedback {
    margin-top: 1rem;
    padding: 0.85rem 1rem;
    border-radius: 0.375rem;
    font-size: 0.95rem;
    display: none;
}
.lt-btfp__feedback.is-success {
    display: block;
    background-color: #e8f6ee;
    border: 1px solid #198754;
    color: #0e5732;
}
.lt-btfp__feedback.is-error {
    display: block;
    background-color: #fdecec;
    border: 1px solid #c0392b;
    color: #842424;
}

.lt-btfp__expect-card {
    background-color: var(--lt-blush-tint);
    border-radius: 0.5rem;
    padding: 1.75rem;
}
.lt-btfp__expect-card h3 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.375rem;
    color: var(--lt-near-black);
    margin: 0 0 0.85rem;
}
.lt-btfp__expect-card h4 {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.4rem;
}
.lt-btfp__expect-card p {
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0 0 0.85rem;
    line-height: 1.5;
}
.lt-btfp__expect-list {
    list-style: none;
    margin: 0 0 1rem;
    padding: 0;
}
.lt-btfp__expect-list li {
    display: flex;
    align-items: flex-start;
    gap: 0.55rem;
    margin-bottom: 0.55rem;
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    line-height: 1.45;
}
.lt-btfp__expect-icon {
    color: var(--lt-teal);
    flex-shrink: 0;
    width: 1.25rem;
    text-align: center;
}
.lt-btfp__expect-divider {
    border: none;
    border-top: 1px solid rgba(26, 26, 26, 0.1);
    margin: 1rem 0;
}
.lt-btfp__expect-contact {
    list-style: none;
    margin: 0;
    padding: 0;
}
.lt-btfp__expect-contact li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
    font-size: 0.95rem;
}
.lt-btfp__expect-contact a {
    color: var(--lt-near-black);
    text-decoration: none;
    font-weight: 600;
}
.lt-btfp__expect-contact a:hover,
.lt-btfp__expect-contact a:focus-visible {
    text-decoration: underline;
}

.lt-btfp__faq {
    background-color: var(--lt-white);
    padding: 3rem 1rem 4rem;
}
.lt-btfp__faq-inner {
    max-width: 44rem;
    margin: 0 auto;
}
.lt-btfp__faq-heading {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.75rem;
    color: var(--lt-near-black);
    margin: 0 0 1.5rem;
    line-height: 1.2;
}
.lt-btfp__faq-item {
    border-bottom: 1px solid rgba(26, 26, 26, 0.1);
}
.lt-btfp__faq-item summary {
    list-style: none;
    cursor: pointer;
    padding: 1rem 2.5rem 1rem 0;
    position: relative;
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.4;
    color: var(--lt-near-black);
}
.lt-btfp__faq-item summary::-webkit-details-marker {
    display: none;
}
.lt-btfp__faq-item summary::after {
    content: "+";
    position: absolute;
    right: 0.25rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    font-weight: 400;
    line-height: 1;
    color: var(--lt-teal);
    transition: transform 0.2s ease;
}
.lt-btfp__faq-item[open] summary::after {
    content: "\\2212";
}
.lt-btfp__faq-item summary:hover {
    color: var(--lt-teal);
}
.lt-btfp__faq-item summary:focus-visible {
    outline: 3px solid var(--lt-teal);
    outline-offset: 2px;
    border-radius: 2px;
}
.lt-btfp__faq-answer {
    padding: 0 0 1.25rem;
    font-size: 1rem;
    line-height: 1.6;
    color: var(--lt-soft-gray);
}
.lt-btfp__faq-answer p {
    margin: 0 0 0.75rem;
}
.lt-btfp__faq-answer p:last-child {
    margin-bottom: 0;
}
.lt-btfp__faq-answer strong {
    font-weight: 600;
    color: var(--lt-near-black);
}
.lt-btfp__faq-answer a {
    color: var(--lt-near-black);
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.2em;
}
@media (prefers-reduced-motion: reduce) {
    .lt-btfp__faq-item summary::after {
        transition: none;
    }
}
@media (max-width: 480px) {
    .lt-btfp__faq-heading {
        font-size: 1.5rem;
    }
}

/* ============================================================
   Mockup-aligned restructure (2026-04-27 r5)
   Hero kicker, service spec tables, decorative ribbons,
   process section, event-types section.
   ============================================================ */

.lt-btfp__kicker {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    color: var(--lt-soft-gray);
    text-transform: uppercase;
    margin: 0 0 1rem;
    text-align: left;
}

/* Service card — restructured for spec-table layout */
.lt-btfp__service-kicker {
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
}
.lt-btfp__service-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.2;
}
.lt-btfp__service-body {
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0 0 1.5rem;
    font-size: 0.95rem;
}
.lt-btfp__service-spec {
    margin: 0;
    padding-top: 0.5rem;
    border-top: 1px solid rgba(26, 26, 26, 0.1);
}
.lt-btfp__service-spec-row {
    display: grid;
    grid-template-columns: 100px 1fr;
    gap: 1rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(26, 26, 26, 0.05);
}
.lt-btfp__service-spec-row:last-child {
    border-bottom: none;
}
.lt-btfp__service-spec-row dt {
    font-family: 'Raleway', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    color: var(--lt-near-black);
    text-transform: uppercase;
    margin: 0;
    align-self: center;
}
.lt-btfp__service-spec-row dd {
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.5;
    align-self: center;
}

/* Thin decorative ribbons (full-bleed horizontal accent bands).
   Must NOT set margin shorthand — that resets margin-left/right and
   defeats the .lt-fullbleed negative margins. */
.lt-btfp__ribbon {
    height: 40px;
    border: none;
    padding: 0;
    display: block;
    margin-top: 0;
    margin-bottom: 0;
}
.lt-btfp__ribbon--blush {
    background-color: var(--lt-blush);
}
.lt-btfp__ribbon--soft-blue {
    background-color: var(--lt-soft-blue);
}
@media (min-width: 992px) {
    .lt-btfp__ribbon {
        height: 56px;
    }
}

/* Process section — "Booking is straightforward." */
.lt-btfp__process {
    background-color: var(--lt-near-white);
    padding: 4rem 1.5rem;
}
.lt-btfp__process-inner {
    max-width: 760px;
    margin: 0 auto;
}
.lt-btfp__process-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
    margin: 0 0 2rem;
    line-height: 1.15;
}
@media (min-width: 992px) {
    .lt-btfp__process-title {
        font-size: 2.5rem;
    }
}
.lt-btfp__process-list {
    list-style: none;
    padding: 0;
    margin: 0;
}
.lt-btfp__process-item {
    display: grid;
    grid-template-columns: 60px 1fr;
    gap: 1.5rem;
    padding: 1.5rem 0;
    border-bottom: 1px solid rgba(26, 26, 26, 0.08);
    align-items: start;
}
.lt-btfp__process-item:last-child {
    border-bottom: none;
}
.lt-btfp__process-number {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    color: rgba(26, 26, 26, 0.3);
    line-height: 1;
    padding-top: 0.15rem;
}
.lt-btfp__process-step-title {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0 0 0.5rem;
    line-height: 1.3;
}
.lt-btfp__process-content p {
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.6;
}

/* Event types section — "Any Event. Any Size." */
.lt-btfp__events {
    background-color: var(--lt-white);
    padding: 4rem 1.5rem;
}
.lt-btfp__events-inner {
    max-width: 760px;
    margin: 0 auto;
}
.lt-btfp__events-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
    margin: 0 0 2rem;
    line-height: 1.15;
}
@media (min-width: 992px) {
    .lt-btfp__events-title {
        font-size: 2.5rem;
    }
}
.lt-btfp__events-list {
    margin: 0;
    padding: 0;
}
.lt-btfp__events-row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.35rem;
    padding: 1.25rem 0;
    border-bottom: 1px solid rgba(26, 26, 26, 0.08);
}
@media (min-width: 768px) {
    .lt-btfp__events-row {
        grid-template-columns: 14rem 1fr;
        gap: 2rem;
        align-items: baseline;
    }
}
.lt-btfp__events-row:last-child {
    border-bottom: none;
}
.lt-btfp__events-row dt {
    font-family: 'Raleway', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--lt-near-black);
    margin: 0;
}
.lt-btfp__events-row dd {
    font-size: 0.95rem;
    color: var(--lt-soft-gray);
    margin: 0;
    line-height: 1.5;
}
"""


def get_context(context):
    context.title = "Balloon Twisting & Face Painting — Locally Twisted | Utah"
    context.metatags = {
        "description": (
            "Professional balloon twisting and face painting for birthday parties, "
            "school events, corporate family days, and festivals. "
            "Serving Weber, Davis, Salt Lake, and Utah counties."
        ),
        "og:title": "Balloon Twisting & Face Painting — Locally Twisted",
        "og:description": "Live entertainment that keeps every guest smiling.",
        "og:type": "website",
    }
    context.service_choices = SERVICE_CHOICES
    context.hours_options = HOURS_OPTIONS
    context.event_types = EVENT_TYPES
    context.colocated_css = PAGE_CSS
    return context


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=20, seconds=60 * 60)
def submit_btfp_booking(name="", email="", phone="", service_choice="", hours_needed="",
                        event_date="", event_time="", event_type="", guest_count="", notes=""):
    """Receive a BTFP booking inquiry from /balloon-twisting-and-face-painting and create a Lead.

    Required: name, email, phone, service_choice, hours_needed, event_date.
    Loud-failure compliant: validation errors and persistence errors raise so
    the client-side script can show a visible message to the user.
    """
    name = (name or "").strip()
    email = (email or "").strip()
    phone = (phone or "").strip()
    service_choice = (service_choice or "").strip()
    hours_needed = (hours_needed or "").strip()
    event_date = (event_date or "").strip()
    event_time = (event_time or "").strip()
    event_type = (event_type or "").strip()
    guest_count = (guest_count or "").strip()
    notes = (notes or "").strip()

    if not name:
        frappe.throw(_("Please tell us your name."), frappe.ValidationError)
    if not email:
        frappe.throw(_("Please give us an email so we can reply."), frappe.ValidationError)
    if not phone:
        frappe.throw(_("Please give us a phone number for fastest response."), frappe.ValidationError)
    if not service_choice:
        frappe.throw(_("Please pick a service option."), frappe.ValidationError)
    if not hours_needed:
        frappe.throw(_("Please tell us how many hours you need."), frappe.ValidationError)
    if not event_date:
        frappe.throw(_("Please give us your event date."), frappe.ValidationError)

    email = validate_email_address(email, throw=True)

    safe_name = escape_html(name)
    safe_phone = escape_html(phone)
    safe_notes = escape_html(notes)

    # Idempotently ensure the Website Lead Source exists (caught at LT
    # contact-page first smoke test 2026-04-26 — fresh ERPNext has no
    # Lead Source records by default).
    if not frappe.db.exists("Lead Source", "Website"):
        try:
            frappe.get_doc({"doctype": "Lead Source", "source_name": "Website"}) \
                .insert(ignore_permissions=True, ignore_if_duplicate=True)
        except frappe.DuplicateEntryError:
            pass

    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": safe_name,
        "email_id": email,
        "mobile_no": safe_phone,
        "source": "Website",
        "status": "Open",
    })
    lead.insert(ignore_permissions=True)

    # Build a readable communication body packaging the BTFP-specific fields.
    service_label = dict(SERVICE_CHOICES).get(service_choice, service_choice)
    hours_label = dict(HOURS_OPTIONS).get(hours_needed, hours_needed)
    parts = [
        f"<strong>Service:</strong> {escape_html(service_label)}",
        f"<strong>Hours needed:</strong> {escape_html(hours_label)}",
        f"<strong>Event date:</strong> {escape_html(event_date)}",
    ]
    if event_time:
        parts.append(f"<strong>Preferred start time:</strong> {escape_html(event_time)}")
    if event_type:
        parts.append(f"<strong>Event type:</strong> {escape_html(dict(EVENT_TYPES).get(event_type, event_type))}")
    if guest_count:
        parts.append(f"<strong>Estimated guests:</strong> {escape_html(guest_count)}")
    if safe_phone:
        parts.append(f"<strong>Phone:</strong> {safe_phone}")
    if safe_notes:
        parts.append("")
        parts.append(safe_notes.replace("\n", "<br>"))
    body_html = "<br>".join(parts)

    frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "sender": email,
        "subject": f"BTFP booking from {safe_name}",
        "content": body_html,
        "sent_or_received": "Received",
        "status": "Open",
        "reference_doctype": "Lead",
        "reference_name": lead.name,
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    return {"ok": True, "lead": lead.name}
