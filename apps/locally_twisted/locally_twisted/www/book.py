"""Inquiry-form submit endpoint and retired /book route.

/contact renders the form partial. /book redirects to /contact?intent=quick.

Spec: Hetzner http://5.78.136.133/book — saved 2026-04-29 to
_resources/odoo-live-snapshot/hetzner-book.html. The local Odoo clone is
stale; do not use it as canonical.

The form mirrors Hetzner's structure with the current /contact consolidation:
event date, city/location, name, email,
phone, and preferred contact method are required on the shared inquiry path.

Submit flow:
  1. Client posts multipart/form-data to submit_book_inquiry
  2. Controller validates + escapes inputs
  3. Controller creates a Lead with custom_* fields routed correctly
  4. Lead `before_insert` hook auto-builds the title
  5. Lead `after_insert` hook deduplicates the Contact and queues the
     auto-acknowledgment email (Quiet Confidence voice, 24-hr promise)
  6. Each uploaded photo becomes a File record attached_to_doctype="Lead"
  7. Controller posts a Communication so the inquiry message lands on
     the Lead's timeline (Frappe's standard "communication on inbound")
  8. Returns JSON {ok: true, lead: <name>, photo_uploads: {...}} -> client
     shows the received modal with any upload notes

Loud-failure compliance (per project CLAUDE.md + global loud-failure rule):
  - User: visible error banner with retry; never blank page on failure
  - Developer: frappe.log_error on every uncaught exception with payload
  - Monitor: scripts/verify/smoke_forms.py covers /contact on every deploy
"""
import copy
import hashlib
import hmac
import json
import time

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html, validate_email_address

from locally_twisted import commerce_rules, lead_cascade
from locally_twisted.failure_recorder import record_backend_failure
from locally_twisted.inquiry_sales_filter import classify_inquiry_sales_solicitation


no_cache = 1
sitemap = 1


# Aligned with Hetzner /book and the Lead Custom Field
# `custom_occasion_type` options. The three new ones (Wedding, Baby Shower,
# Grand Opening) come from /contact's set and were merged in by GL's
# consolidation directive (2026-04-29).
OCCASION_OPTIONS = [
    ("birthday", "Birthday Party"),
    ("wedding", "Wedding"),
    ("baby_shower", "Baby Shower"),
    ("graduation", "Graduation"),
    ("get_well", "Get Well"),
    ("school", "School Event"),
    ("corporate", "Corporate Event"),
    ("grand_opening", "Grand Opening"),
    ("festival", "Festival / Fair"),
    ("church", "Church Event"),
    ("missionary", "Missionary Farewell / Homecoming"),
    ("religious", "Religious Celebration"),
    ("reunion", "Family Reunion"),
    ("holiday", "Holiday Party"),
    ("other", "Other"),
]


# The service checkboxes mirror the current /contact x_services multi-select.
# The visibility-condition values must match these label strings exactly
# because the JS does string-contains matching against the joined list.
SERVICE_OPTIONS = [
    ("svc_decor", "Balloon Decor", "Balloon Decor (arches, garlands, walls, drops)"),
    ("svc_twisting", "Balloon Twisting", "Balloon Twisting"),
    ("svc_painting", "Face Painting", "Face Painting"),
    ("svc_delivery", "Delivery", "Delivery (helium bouquets, balloon pieces)"),
    ("svc_pickup", "Pickup", "Pickup"),
    ("svc_package", "Events Inquiry", "Multiple services or larger event"),
    ("svc_other", "Something Else", "Something Else"),
]
SERVICE_VALUES = {value for _cb_id, value, _label in SERVICE_OPTIONS}

PREFERRED_CONTACT_OPTIONS = [
    ("Email", "Email"),
    ("Phone", "Phone"),
    ("Text", "Text"),
]


PACKAGE_ITEM_OPTIONS = [
    "Balloon Arches",
    "Columns",
    "Garlands",
    "Picture Perfect Backdrops",
    "Balloon Drops",
    "Balloon Bouquets",
    "Centerpieces",
    "Custom Sculptures",
]


# 5 photos x 25 MB each, per GL's spec (2026-04-29) and Hetzner JS
# constants. Server-side validation matches the client-side limits in
# the inline JS.
MAX_PHOTOS = 5
MAX_PHOTO_BYTES = 25 * 1024 * 1024  # 25 MB
ALLOWED_PHOTO_MIMES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/heic", "image/heif",
}
ALLOWED_PHOTO_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif"}
PHOTO_UPLOAD_FAILURE_STEPS = {
    "unsupported_type": "photo_rejected_unsupported_type",
    "too_large": "photo_rejected_too_large",
    "too_many_files": "photo_rejected_too_many_files",
    "upload_failed": "photo_upload_failed",
}
INQUIRY_SPAM_TOKEN_FIELD = "lt_form_token"
INQUIRY_HONEYPOT_FIELD = "website"
INQUIRY_SPAM_TOKEN_MAX_AGE_SECONDS = 4 * 60 * 60
INQUIRY_SPAM_MIN_FILL_SECONDS = 2
INQUIRY_SPAM_RETRY_MESSAGE = _(
    "Tiny pause: please refresh the page and try again before sending this request."
)


def build_inquiry_spam_token(now: int | None = None) -> str:
    """Build a signed, timestamped token for the public inquiry form."""
    timestamp = int(now or time.time())
    signature = _inquiry_spam_signature(timestamp)
    return f"{timestamp}.{signature}"


def get_context(context):
    frappe.local.flags.redirect_location = "/contact?intent=quick"
    raise frappe.Redirect


def _validate_inquiry_spam_gate(fd):
    """Reject common bot submissions before creating Leads or email queues."""
    if (fd.get(INQUIRY_HONEYPOT_FIELD) or "").strip():
        _throw_inquiry_spam_gate()

    timestamp = _inquiry_spam_token_timestamp((fd.get(INQUIRY_SPAM_TOKEN_FIELD) or "").strip())
    if not timestamp:
        _throw_inquiry_spam_gate()

    elapsed = int(time.time()) - timestamp
    if elapsed < INQUIRY_SPAM_MIN_FILL_SECONDS:
        _throw_inquiry_spam_gate()
    if elapsed > INQUIRY_SPAM_TOKEN_MAX_AGE_SECONDS:
        _throw_inquiry_spam_gate()


def _inquiry_spam_token_timestamp(token: str) -> int | None:
    try:
        raw_timestamp, signature = token.split(".", 1)
        timestamp = int(raw_timestamp)
    except (AttributeError, TypeError, ValueError):
        return None

    expected = _inquiry_spam_signature(timestamp)
    if not hmac.compare_digest(signature, expected):
        return None
    return timestamp


def _inquiry_spam_signature(timestamp: int) -> str:
    secret = _inquiry_spam_secret().encode("utf-8")
    payload = str(int(timestamp)).encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def _inquiry_spam_secret() -> str:
    site = getattr(getattr(frappe, "local", None), "site", "") or ""
    return str(
        frappe.conf.get("encryption_key")
        or frappe.conf.get("db_password")
        or site
        or "locally_twisted_inquiry_form"
    )


def _throw_inquiry_spam_gate():
    frappe.throw(INQUIRY_SPAM_RETRY_MESSAGE, frappe.ValidationError)


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=20, seconds=60 * 60)
def submit_book_inquiry():
    """Receive a /book form submission and create a Lead + linked records.

    Reads `frappe.form_dict` for fields and `frappe.request.files` for
    photos. Name, email, phone, preferred contact method, event date, and
    city/location are required. Returns JSON; raises on persistence
    failure so the client-side script can render an error.
    """
    fd = frappe.form_dict
    _validate_inquiry_spam_gate(fd)

    # Event basics
    occasion = (fd.get("x_occasion_type") or "").strip()
    event_date = (fd.get("x_event_date") or "").strip()
    if not event_date:
        frappe.throw(_("Please choose the event date."), frappe.ValidationError)
    event_time = _compose_time_widget_value(fd, "x_event_time", "event start time")
    event_end_time = _compose_time_widget_value(fd, "x_event_end_time", "event end time")
    event_location = (fd.get("x_event_location") or "").strip()
    if not event_location:
        frappe.throw(_("Please tell us the city or location for the event."), frappe.ValidationError)
    guest_count = _parse_int(fd.get("x_guest_count"))

    # Required contact fields
    first_name = (fd.get("contact_name") or "").strip()
    email = (fd.get("email_from") or "").strip()
    if not first_name:
        frappe.throw(_("Please tell us your name."), frappe.ValidationError)
    if not email:
        frappe.throw(_("Please enter a valid email address."), frappe.ValidationError)
    email = _validate_required_email(email)

    phone = (fd.get("phone") or "").strip()
    if not phone:
        frappe.throw(
            _("Please enter a phone number so we have a second way to contact you about your inquiry."),
            frappe.ValidationError,
        )
    preferred_contact_method = _normalize_preferred_contact_method(fd.get("preferred_contact_method"))
    if not preferred_contact_method:
        frappe.throw(
            _("Please choose how you prefer to be contacted."),
            frappe.ValidationError,
        )

    # Optional contact fields
    company = (fd.get("partner_name") or "").strip()

    # Multi-select services (incoming as repeated form field or CSV).
    services = _parse_multivalue(fd.get("x_services"))

    # Per-service notes (only relevant if the matching service was checked)
    decor_types = (fd.get("x_decor_types") or "").strip()
    setup_arrival = (fd.get("x_setup_time_arrival") or "").strip()
    decor_notes = (fd.get("x_decor_notes") or "").strip()
    num_twisters = _parse_int(fd.get("x_num_twisters"))
    artist_start = (fd.get("x_artist_start") or "").strip()
    artist_end = (fd.get("x_artist_end") or "").strip()
    twisting_notes = (fd.get("x_twisting_notes") or "").strip()
    num_painters = _parse_int(fd.get("x_num_painters"))
    painter_start = (fd.get("x_painter_start") or "").strip()
    painter_end = (fd.get("x_painter_end") or "").strip()
    painting_notes = (fd.get("x_painting_notes") or "").strip()
    delivery_notes = (fd.get("x_delivery_notes") or "").strip()
    package_items = _parse_multivalue(fd.get("x_package_items"))
    package_colors = (fd.get("x_package_colors") or "").strip()
    package_notes = _compose_events_inquiry_notes(
        package_items,
        package_colors,
        (fd.get("x_package_notes") or "").strip(),
    )
    other_notes = (fd.get("x_other_notes") or "").strip()

    # Environment (visible when any service is checked)
    indoor_outdoor = (fd.get("x_indoor_outdoor") or "").strip()
    shade_required = 1 if str(fd.get("x_shade_required") or "").lower() in ("true", "on", "1", "yes") else 0
    colors = _combine_text_values((fd.get("x_colors") or "").strip(), package_colors)

    # Free-form catch-all
    description = (fd.get("description") or "").strip()
    requested_item_code = (fd.get("lt_requested_item_code") or "").strip()
    requested_item_name = (fd.get("lt_requested_item_name") or "").strip()
    requested_product_quote_raw = (fd.get("lt_product_quote_payload") or "").strip()
    requested_item = _requested_item_note(requested_item_code, requested_item_name)
    product_quote_payload = _requested_product_quote_payload(requested_item_code, requested_product_quote_raw)
    if requested_item:
        description = _combine_text_values(requested_item, description)
    if product_quote_payload and product_quote_payload.get("summary"):
        description = _combine_text_values(product_quote_payload["summary"], description)
    payment_rule = _payment_rule_for_inquiry(services, num_twisters, num_painters)
    solicitation_filter = classify_inquiry_sales_solicitation({
        "name": first_name,
        "email": email,
        "phone": phone,
        "company": company,
        "occasion": _occasion_label(occasion),
        "event_location": event_location,
        "services": services,
        "decor_notes": decor_notes,
        "twisting_notes": twisting_notes,
        "painting_notes": painting_notes,
        "delivery_notes": delivery_notes,
        "package_notes": package_notes,
        "other_notes": other_notes,
        "description": description,
    })

    # Lead Source: ensure "Website" exists (idempotent)
    _ensure_lead_source("Website")

    # Build the Lead. lead_cascade.before_insert auto-titles it.
    lead_doc = {
        "doctype": "Lead",
        "first_name": first_name,
        "last_name": "",
        "email_id": email,
        "mobile_no": phone,
        "company_name": company or None,
        "source": "Website",
        "status": "Open",
        "custom_pipeline_stage": "New Inquiry",
        "custom_occasion_type": _occasion_label(occasion),
        "custom_event_date": event_date or None,
        "custom_event_time": event_time or None,
        "custom_event_end_time": event_end_time or None,
        "custom_event_location": event_location or None,
        "custom_guest_count": guest_count,
        "custom_preferred_contact_method": preferred_contact_method,
        "custom_event_type": _service_child_rows(services),
        "custom_decor_types": decor_types or None,
        "custom_setup_time_arrival": setup_arrival or None,
        "custom_decor_notes": decor_notes or None,
        "custom_num_twisters": num_twisters,
        "custom_artist_start": artist_start or None,
        "custom_artist_end": artist_end or None,
        "custom_twisting_notes": twisting_notes or None,
        "custom_num_painters": num_painters,
        "custom_painter_start": painter_start or None,
        "custom_painter_end": painter_end or None,
        "custom_painting_notes": painting_notes or None,
        "custom_delivery_notes": delivery_notes or None,
        "custom_package_notes": package_notes or None,
        "custom_other_notes": other_notes or None,
        "custom_indoor_outdoor": _indoor_outdoor_label(indoor_outdoor),
        "custom_shade_required": shade_required,
        "custom_colors": colors or None,
        "custom_anything_else": description or None,
        "custom_source_channel": "Website Form",
    }
    lead_doc.update(_lead_payment_fields(payment_rule))
    lead_doc.update(_lead_product_quote_fields(product_quote_payload))
    product_quote_child_rows = _lead_product_quote_child_rows(product_quote_payload)
    if product_quote_child_rows:
        lead_doc["custom_lt_product_quote_items"] = product_quote_child_rows
    try:
        lead = _insert_lead_with_retry(lead_doc, defer_customer_ack=True, customer_email=email)
    except Exception as e:
        # Loud-failure: log dev-channel detail before re-raising so the
        # framework error handler surfaces the user-facing error banner.
        try:
            payload = json.dumps(
                {k: v for k, v in (frappe.form_dict or {}).items() if k != "cmd"},
                default=str,
            )[:2000]
        except Exception:
            payload = "<payload serialization failed>"
        frappe.log_error(
            title="/book Lead creation failed",
            message=(
                f"{type(e).__name__}: {e}\n"
                f"form_url: {getattr(getattr(frappe.local, 'request', None), 'url', 'unknown')}\n"
                f"remote_ip: {getattr(frappe.local, 'request_ip', 'unknown')}\n"
                f"payload: {payload}"
            ),
        )
        raise

    # Attach photos as File records linked to the Lead. Invalid, oversized,
    # excess, or failed files do not block the inquiry, but they must be visible
    # to the customer response and on the Lead timeline.
    photo_files = _files_from_request("ufile")
    photo_uploads = _photo_upload_summary(len(photo_files))
    attached = 0
    stored_photo_files = []
    for f in photo_files[MAX_PHOTOS:]:
        _record_photo_upload_issue(
            lead,
            photo_uploads,
            f,
            reason="too_many_files",
            message=f"Only the first {MAX_PHOTOS} inspiration photos can be attached.",
        )
    for f in photo_files[:MAX_PHOTOS]:
        if not _is_allowed_photo(f):
            _record_photo_upload_issue(
                lead,
                photo_uploads,
                f,
                reason="unsupported_type",
                message="File type is not one of JPEG, PNG, GIF, WebP, HEIC, or HEIF.",
            )
            continue
        size = _file_size(f)
        if size > MAX_PHOTO_BYTES:
            _record_photo_upload_issue(
                lead,
                photo_uploads,
                f,
                reason="too_large",
                message=f"File is over {MAX_PHOTO_BYTES // (1024 * 1024)} MB.",
            )
            continue
        try:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": f.filename,
                "is_private": 1,
                "content": f.stream.read() if hasattr(f, "stream") else f.read(),
                "attached_to_doctype": "Lead",
                "attached_to_name": lead.name,
            }).insert(ignore_permissions=True)
            attached += 1
            stored_photo_files.append(file_doc)
        except Exception as e:
            _record_photo_upload_issue(
                lead,
                photo_uploads,
                f,
                reason="upload_failed",
                message="File passed validation but could not be attached.",
                exception=e,
                severity="error",
            )
    photo_uploads["attached"] = attached
    photo_uploads["customer_message"] = _photo_upload_customer_message(photo_uploads)
    if stored_photo_files:
        lead.reload()
        for file_doc in stored_photo_files:
            lead.append("custom_inspiration_photos", {
                "photo": file_doc.file_url,
                "caption": file_doc.file_name,
            })
        lead.save(ignore_permissions=True)

    # Inbound Communication on the Lead's timeline. Captures the
    # message body + the structured summary so Jeff has one place to read
    # the customer's submission verbatim.
    _record_inquiry_communication(
        lead, first_name, email, phone, preferred_contact_method, company, occasion, event_date,
        event_time, event_end_time, event_location, guest_count, services, indoor_outdoor,
        shade_required, colors, decor_types, setup_arrival, decor_notes,
        num_twisters, artist_start, artist_end, twisting_notes,
        num_painters, painter_start, painter_end, painting_notes,
        delivery_notes, package_notes, other_notes, description, attached, payment_rule,
        photo_uploads,
    )
    business_notification = _send_deferred_business_notification(
        lead,
        photo_uploads,
        solicitation_filter=solicitation_filter,
    )
    customer_confirmation = _send_deferred_customer_confirmation(lead, photo_uploads)

    frappe.db.commit()
    return {
        "ok": True,
        "lead": lead.name,
        "photos": attached,
        "photo_uploads": photo_uploads,
        "business_notification": business_notification,
        "customer_confirmation": customer_confirmation,
    }


# -------------------------- helpers ---------------------------------- #


def _validate_required_email(email):
    validated = validate_email_address(email, throw=False)
    if not validated:
        frappe.throw(
            _("Please enter a valid email address."),
            frappe.ValidationError,
        )
    return validated


def _normalize_preferred_contact_method(value):
    value = (value or "").strip()
    for option, _label in PREFERRED_CONTACT_OPTIONS:
        if value.lower() == option.lower():
            return option
    return ""


def _compose_time_widget_value(fd, prefix, label):
    value = (fd.get(prefix) or "").strip()
    if value:
        return value

    hour = (fd.get(f"{prefix}_hour") or "").strip()
    minute = (fd.get(f"{prefix}_minute") or "").strip()
    period = (fd.get(f"{prefix}_period") or "").strip().upper()
    parts = [hour, minute, period]
    present_count = len([part for part in parts if part])
    if present_count == 0:
        return ""
    if present_count != 3 or hour not in {str(n) for n in range(1, 13)} or minute not in {"00", "15", "30", "45"} or period not in {"AM", "PM"}:
        frappe.throw(
            _(f"Please choose a complete {label} or leave it blank."),
            frappe.ValidationError,
        )
    return f"{hour}:{minute} {period}"


def _insert_lead_with_retry(lead_doc, *, defer_customer_ack=False, customer_email=None):
    """Retry only transient database contention during public Lead creation."""
    max_attempts = 3
    working_doc = copy.deepcopy(lead_doc)
    stripped_unique_email = False
    for attempt in range(1, max_attempts + 1):
        lead = frappe.get_doc(copy.deepcopy(working_doc))
        if defer_customer_ack:
            lead.flags.lt_defer_customer_ack = True
        if customer_email:
            lead.flags.lt_customer_email = customer_email
        try:
            lead.insert(ignore_permissions=True)
            return lead
        except Exception as exc:
            if (
                not stripped_unique_email
                and working_doc.get("email_id")
                and _is_duplicate_lead_email_error(exc)
            ):
                frappe.db.rollback()
                _clear_frappe_messages()
                working_doc = _lead_doc_without_unique_email(working_doc, customer_email or working_doc.get("email_id"))
                stripped_unique_email = True
                continue
            if attempt >= max_attempts or not _is_transient_lead_insert_error(exc):
                raise
            frappe.db.rollback()
            time.sleep(0.15 * attempt)
    raise RuntimeError("unreachable lead insert retry state")


def _send_deferred_business_notification(lead, photo_uploads, *, solicitation_filter=None):
    if (solicitation_filter or {}).get("is_solicitation"):
        _record_sales_solicitation_note(lead, solicitation_filter)
        return {
            "ok": True,
            "queued": False,
            "skipped_existing": False,
            "suppressed": True,
            "reason": "sales_solicitation",
            "sales_score": solicitation_filter.get("sales_score"),
            "customer_score": solicitation_filter.get("customer_score"),
        }
    try:
        return lead_cascade.send_business_inquiry_notification(lead, photo_uploads=photo_uploads)
    except Exception as e:
        record_backend_failure(
            surface="lead_contact_ack_cascade",
            step="business_notification_email",
            severity="error",
            primary_doctype="Lead",
            primary_name=lead.name,
            customer_visible_impact="The inquiry was received, but the business notification email did not queue.",
            internal_next_action="Open the Lead immediately and confirm the business notification email settings.",
            exception=e,
            grouping_key=f"lead_contact_ack_cascade:business_notification_email:{lead.name}",
        )
        frappe.throw(
            "We saved your request, but the business notification email did not queue. "
            "Please call (801) 285-0860 or email hi@locallytwisted.com and we will help.",
            frappe.ValidationError,
        )


def _record_sales_solicitation_note(lead, solicitation_filter):
    reasons = ", ".join(solicitation_filter.get("sales_reasons") or [])
    customer_reasons = ", ".join(solicitation_filter.get("customer_reasons") or [])
    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Info",
        "reference_doctype": "Lead",
        "reference_name": lead.name,
        "content": (
            "Owner email suppressed: high-confidence sales solicitation. "
            f"Sales score: {solicitation_filter.get('sales_score')}; "
            f"customer/event score: {solicitation_filter.get('customer_score')}; "
            f"sales signals: {frappe.utils.escape_html(reasons) or 'none'}; "
            f"customer signals: {frappe.utils.escape_html(customer_reasons) or 'none'}."
        ),
    }).insert(ignore_permissions=True)


def _send_deferred_customer_confirmation(lead, photo_uploads):
    try:
        return lead_cascade.send_customer_inquiry_confirmation(lead, photo_uploads=photo_uploads)
    except Exception as e:
        record_backend_failure(
            surface="lead_contact_ack_cascade",
            step="customer_ack_email",
            severity="error",
            primary_doctype="Lead",
            primary_name=lead.name,
            customer_visible_impact="The inquiry was received, but the acknowledgment email did not queue.",
            internal_next_action="Confirm the customer email and send or requeue the acknowledgment.",
            exception=e,
            grouping_key=f"lead_contact_ack_cascade:customer_ack_email:{lead.name}",
        )
        frappe.throw(
            "We saved your request, but the confirmation email did not queue. "
            "Please call (801) 285-0860 or email hi@locallytwisted.com and we will help.",
            frappe.ValidationError,
        )


def _is_transient_lead_insert_error(exc):
    query_deadlock_error = getattr(frappe, "QueryDeadlockError", None)
    if query_deadlock_error and isinstance(exc, query_deadlock_error):
        return True

    message = str(exc).lower()
    transient_markers = (
        "deadlock",
        "record has changed since last read",
        "try restarting transaction",
    )
    return any(marker in message for marker in transient_markers)


def _is_duplicate_lead_email_error(exc):
    duplicate_error = getattr(frappe, "DuplicateEntryError", None)
    if duplicate_error and not isinstance(exc, duplicate_error):
        return False
    message = str(exc).lower()
    return "email address" in message and "unique" in message


def _lead_doc_without_unique_email(lead_doc, customer_email):
    retry_doc = copy.deepcopy(lead_doc)
    retry_doc["email_id"] = None
    note = lead_cascade.customer_email_note(customer_email)
    current_note = retry_doc.get("custom_anything_else") or ""
    if note not in current_note:
        retry_doc["custom_anything_else"] = _combine_text_values(note, current_note)
    return retry_doc


def _clear_frappe_messages():
    try:
        frappe.clear_messages()
    except Exception:
        pass


def _parse_int(value):
    if value is None or value == "":
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _parse_multivalue(value):
    """Form field can arrive as: list (multiple values), comma-separated
    string, or a single string. Normalize to a list of trimmed strings.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        # JSON array (the client may send as JSON.stringify of an array)
        v = value.strip()
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(s).strip() for s in parsed if str(s).strip()]
            except json.JSONDecodeError:
                pass
        # Comma-separated fallback
        return [s.strip() for s in v.split(",") if s.strip()]
    return [str(value).strip()] if str(value).strip() else []


def _occasion_label(value):
    """Map the form's occasion `value` (lowercase key) to its label
    (the Lead Custom Field's option string is the human label)."""
    if not value:
        return None
    mapping = dict(OCCASION_OPTIONS)
    return mapping.get(value, value)


def _indoor_outdoor_label(value):
    if not value:
        return None
    mapping = {"indoor": "Indoor", "outdoor": "Outdoor", "both": "Both"}
    return mapping.get(value.lower(), value)


def _combine_text_values(*values):
    return "; ".join(str(v).strip() for v in values if str(v).strip())


def _payment_rule_for_inquiry(services, num_twisters=None, num_painters=None):
    services = set(services or [])
    artist_services = {"Balloon Twisting", "Face Painting"} & services
    quote_services = {"Balloon Decor", "Delivery", "Pickup", "Events Inquiry", "Something Else"} & services
    if artist_services:
        artist_count = 0
        if "Balloon Twisting" in services:
            artist_count += num_twisters or 1
        if "Face Painting" in services:
            artist_count += num_painters or 1
        rule = commerce_rules.payment_rule_for_lane("artist_service", artist_count=artist_count)
        timing = "Deposit then balance"
        balance_timing = rule.balance_timing
        payment_notes = rule.label
        if quote_services:
            quote_note = "Quoted decor or event work is paid in full before prep starts."
            balance_timing = f"{balance_timing} {quote_note}"
            payment_notes = f"{payment_notes} {quote_note}"
    elif quote_services:
        rule = commerce_rules.payment_rule_for_lane("quote_required")
        timing = "Full payment before prep"
        balance_timing = rule.balance_timing
        payment_notes = "Quoted event work is paid in full before prep starts."
    else:
        rule = commerce_rules.payment_rule_for_lane("retail_checkout")
        timing = "Paid in full at checkout"
        balance_timing = rule.balance_timing
        payment_notes = rule.label
    return {
        "payment_timing": timing,
        "deposit_due": float(rule.deposit_amount),
        "balance_timing": balance_timing,
        "payment_notes": payment_notes,
    }


def _lead_payment_fields(payment_rule):
    meta = frappe.get_meta("Lead")
    fields = {
        "custom_lt_payment_timing": payment_rule.get("payment_timing"),
        "custom_lt_deposit_due": payment_rule.get("deposit_due"),
        "custom_lt_balance_timing": payment_rule.get("balance_timing"),
        "custom_lt_payment_notes": payment_rule.get("payment_notes"),
    }
    return {fieldname: value for fieldname, value in fields.items() if meta.has_field(fieldname)}


def _lead_product_quote_fields(product_quote_payload):
    if not product_quote_payload:
        return {}
    meta = frappe.get_meta("Lead")
    fields = {
        "custom_lt_product_template_item": product_quote_payload.get("website_item_code"),
        "custom_lt_product_page_type": product_quote_payload.get("product_page_type"),
        "custom_lt_product_quote_summary": product_quote_payload.get("summary"),
        "custom_lt_product_quote_payload": json.dumps(product_quote_payload, sort_keys=True, default=str),
    }
    return {fieldname: value for fieldname, value in fields.items() if meta.has_field(fieldname)}


def _lead_product_quote_child_rows(product_quote_payload):
    if not product_quote_payload:
        return []
    meta = frappe.get_meta("Lead")
    if not meta.has_field("custom_lt_product_quote_items"):
        return []
    return [
        {
            "product_page": product_quote_payload.get("website_item_code"),
            "product_page_type": product_quote_payload.get("product_page_type"),
            "commerce_lane": product_quote_payload.get("commerce_lane"),
            "summary": product_quote_payload.get("summary"),
            "payload_json": json.dumps(product_quote_payload, sort_keys=True, default=str),
            "status": "Needs Operator Review",
        }
    ]


def _requested_product_quote_payload(item_code, raw_payload=None):
    incoming = _decode_requested_product_quote_payload(raw_payload)
    if incoming and not item_code:
        item_code = incoming.get("website_item_code")
    if not item_code:
        return None
    item = frappe.db.get_value(
        "Website Item",
        {"item_code": item_code, "published": 1},
        ["item_code", "web_item_name", "item_group", "route"],
        as_dict=True,
    )
    if not item:
        return None

    from locally_twisted.product_page_runtime import product_page_contract_for_website_item
    from locally_twisted.product_quote_request import normalize_public_product_quote_payload

    contract = product_page_contract_for_website_item(item["item_code"])
    if incoming and incoming.get("website_item_code") and incoming.get("website_item_code") != item.get("item_code"):
        frappe.throw(
            _(
                "Tiny snag: this product quote was attached to a different product page. "
                "Please open the product again and send the quote request one more time."
            ),
            frappe.ValidationError,
        )

    return normalize_public_product_quote_payload(
        item=item,
        contract=contract,
        incoming=incoming,
    )


def _decode_requested_product_quote_payload(raw_payload):
    if not raw_payload:
        return {}
    try:
        payload = json.loads(raw_payload)
    except (TypeError, ValueError):
        frappe.throw(
            _(
                "Tiny snag: this product quote did not come through cleanly. "
                "Please open the product again and send the quote request one more time."
            ),
            frappe.ValidationError,
        )
    if not isinstance(payload, dict):
        frappe.throw(
            _(
                "Tiny snag: this product quote did not come through cleanly. "
                "Please open the product again and send the quote request one more time."
            ),
            frappe.ValidationError,
        )

    from locally_twisted.product_page_runtime import CONFIG_VERSION

    if payload.get("schema_version") != CONFIG_VERSION:
        frappe.throw(
            _(
                "Tiny snag: this product quote used an older option format. "
                "Please open the product again and send the quote request one more time."
            ),
            frappe.ValidationError,
        )
    return payload


def _dict_or_empty(value):
    return value if isinstance(value, dict) else {}


def _list_or_empty(value):
    return value if isinstance(value, list) else []


def _requested_item_note(item_code, fallback_name):
    if not item_code and not fallback_name:
        return ""
    item = None
    if item_code:
        item = frappe.db.get_value(
            "Website Item",
            {"item_code": item_code, "published": 1},
            ["item_code", "web_item_name"],
            as_dict=True,
        )
    if item:
        return "Requested product quote: {} ({})".format(
            item.get("web_item_name") or item.get("item_code"),
            item.get("item_code"),
        )
    if fallback_name:
        return "Requested product quote: {}".format(fallback_name)
    return "Requested product quote: {}".format(item_code)


def _service_child_rows(services):
    """Build Lead Table MultiSelect rows from public service labels."""
    return [
        {"service_type": service}
        for service in services
        if service in SERVICE_VALUES
    ]


def _compose_events_inquiry_notes(package_items, package_colors, package_notes):
    parts = []
    if package_items:
        parts.append("Interested pieces: " + ", ".join(package_items))
    if package_colors:
        parts.append("Colors: " + package_colors)
    if package_notes:
        parts.append("Memory: " + package_notes)
    return "\n".join(parts)


def _ensure_lead_source(source_name):
    if frappe.db.exists("Lead Source", source_name):
        return
    try:
        frappe.get_doc({
            "doctype": "Lead Source",
            "source_name": source_name,
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)
    except frappe.DuplicateEntryError:
        pass


def _files_from_request(field_name):
    """Pull all uploaded files for a multi-file field name.

    Werkzeug's MultiDict returns a list via getlist. Returns [] when no
    file matches, when the request isn't multipart, or if files isn't
    available on this request.
    """
    req = frappe.request
    files_obj = getattr(req, "files", None)
    if files_obj is None:
        return []
    try:
        files = files_obj.getlist(field_name) or []
    except Exception:
        single = files_obj.get(field_name)
        files = [single] if single else []
    return [file_obj for file_obj in files if _is_submitted_upload(file_obj)]


def _is_submitted_upload(file_obj):
    filename = (getattr(file_obj, "filename", "") or "").strip()
    if filename:
        return True
    return _file_size(file_obj) > 0


def _is_allowed_photo(f):
    name = (getattr(f, "filename", "") or "").lower()
    mime = (getattr(f, "content_type", "") or "").lower()
    if mime in ALLOWED_PHOTO_MIMES:
        return True
    for ext in ALLOWED_PHOTO_EXTS:
        if name.endswith(ext):
            return True
    return False


def _file_size(f):
    """Get a file's size without exhausting the stream where possible."""
    stream = getattr(f, "stream", None) or f
    try:
        pos = stream.tell()
        stream.seek(0, 2)  # seek to end
        size = stream.tell()
        stream.seek(pos)
        return size
    except Exception:
        return 0


def _photo_upload_summary(submitted):
    return {
        "submitted": submitted,
        "attached": 0,
        "rejected": [],
        "failed": [],
        "customer_message": "",
    }


def _record_photo_upload_issue(
    lead,
    summary,
    file_obj,
    *,
    reason,
    message,
    exception=None,
    severity="warning",
):
    filename = _uploaded_filename(file_obj)
    issue = {
        "filename": filename,
        "reason": reason,
        "message": message,
    }
    bucket = "failed" if reason == "upload_failed" else "rejected"
    summary[bucket].append(issue)
    step = PHOTO_UPLOAD_FAILURE_STEPS.get(reason, f"photo_rejected_{reason}")
    record_backend_failure(
        surface="public_contact_to_lead",
        step=step,
        severity=severity,
        primary_doctype="Lead",
        primary_name=lead.name,
        customer_visible_impact=(
            f"The inquiry was received, but inspiration photo {filename} was not attached: {message}"
        ),
        internal_next_action=(
            "Review the Lead with the customer before relying on inspiration photos."
        ),
        exception=exception or message,
        grouping_key=f"public_contact_to_lead:{step}:{lead.name}:{filename}",
    )


def _uploaded_filename(file_obj):
    filename = (getattr(file_obj, "filename", "") or "").strip()
    return filename or "unnamed upload"


def _photo_upload_customer_message(summary):
    issue_count = len(summary.get("rejected") or []) + len(summary.get("failed") or [])
    if not issue_count:
        return ""
    attached = summary.get("attached") or 0
    if attached:
        return (
            f"We received your request and attached {attached} inspiration photo(s). "
            f"{issue_count} photo file(s) had a little trouble attaching, so we made a note for the team to follow up."
        )
    return (
        "We received your request. The inspiration photo file(s) had a little trouble attaching, "
        "so we made a note for the team to follow up."
    )


def _record_inquiry_communication(
    lead, first_name, email, phone, preferred_contact_method, company, occasion, event_date,
    event_time, event_end_time, event_location, guest_count, services, indoor_outdoor,
    shade_required, colors, decor_types, setup_arrival, decor_notes,
    num_twisters, artist_start, artist_end, twisting_notes,
    num_painters, painter_start, painter_end, painting_notes,
    delivery_notes, package_notes, other_notes, description, photo_count, payment_rule,
    photo_uploads=None,
):
    """Build a readable HTML summary of the form submission and post it
    as a Communication on the Lead's timeline."""
    parts = []

    def line(label, value):
        if value is None or value == "" or value == 0:
            return
        parts.append(f"<strong>{escape_html(label)}:</strong> {escape_html(str(value))}")

    line("Email", email)
    line("Phone", phone)
    line("Preferred contact method", preferred_contact_method)
    line("Company", company)
    line("Occasion", _occasion_label(occasion))
    line("Event date", event_date)
    line("Event start time", event_time)
    line("Event end time", event_end_time)
    line("Location", event_location)
    line("Estimated guests", guest_count)
    if services:
        line("Services requested", ", ".join(services))
    line("Indoor / Outdoor", _indoor_outdoor_label(indoor_outdoor))
    if shade_required:
        line("Shade", "Required")
    line("Colors", colors)
    line("Decor types", decor_types)
    line("Setup arrival", setup_arrival)
    line("Decor notes", decor_notes)
    line("Twisters", num_twisters)
    line("Twister start", artist_start)
    line("Twister end", artist_end)
    line("Twisting notes", twisting_notes)
    line("Face painters", num_painters)
    line("Painter start", painter_start)
    line("Painter end", painter_end)
    line("Painting notes", painting_notes)
    line("Delivery notes", delivery_notes)
    line("Events inquiry notes", package_notes)
    line("Other notes", other_notes)
    line("Payment timing", payment_rule.get("payment_timing"))
    if payment_rule.get("deposit_due"):
        line("Deposit due", "${:.2f}".format(payment_rule["deposit_due"]))
    line("Balance timing", payment_rule.get("balance_timing"))
    if photo_count:
        line("Inspiration photos", f"{photo_count} attached")
    upload_issues = []
    if photo_uploads:
        for item in (photo_uploads.get("rejected") or []) + (photo_uploads.get("failed") or []):
            upload_issues.append(
                f"{item.get('filename') or 'unnamed upload'}: {item.get('message') or item.get('reason')}"
            )
    if upload_issues:
        line("Photo upload issues", "; ".join(upload_issues))

    body_html = "<br>".join(parts) if parts else "(no additional details provided)"
    if description:
        body_html = f"{body_html}<br><br>{escape_html(description).replace(chr(10), '<br>')}"

    frappe.get_doc({
        "doctype": "Communication",
        "communication_type": "Communication",
        "communication_medium": "Email",
        "sender": email,
        "subject": f"New inquiry from {escape_html(first_name)}",
        "content": body_html,
        "sent_or_received": "Received",
        "status": "Open",
        "reference_doctype": "Lead",
        "reference_name": lead.name,
    }).insert(ignore_permissions=True)
