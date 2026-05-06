"""Inquiry-form submit endpoint and retired /book route.

/contact renders the form partial. /book redirects to /contact?intent=quick.

Spec: Hetzner http://5.78.136.133/book — saved 2026-04-29 to
_resources/odoo-live-snapshot/hetzner-book.html. The local Odoo clone is
stale; do not use it as canonical.

The form mirrors Hetzner's structure with one consolidation rule from
GL (2026-04-29): Name + Email required, Phone optional. Hetzner /book has
all three required; we inherit /contact's "email-required, phone-optional"
shape because /contact is consolidated into /book.

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
  8. Returns JSON {ok: true, lead: <name>} -> client shows the received modal

Loud-failure compliance (per project CLAUDE.md + global loud-failure rule):
  - User: visible error banner with retry; never blank page on failure
  - Developer: frappe.log_error on every uncaught exception with payload
  - Monitor: scripts/verify/smoke_forms.py covers /contact on every deploy
"""
import json

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import escape_html, validate_email_address

from locally_twisted import commerce_rules


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
    ("svc_package", "Events Inquiry", "Events Inquiry"),
    ("svc_other", "Something Else", "Something Else"),
]
SERVICE_VALUES = {value for _cb_id, value, _label in SERVICE_OPTIONS}


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


def get_context(context):
    frappe.local.flags.redirect_location = "/contact?intent=quick"
    raise frappe.Redirect


@frappe.whitelist(allow_guest=True)
@rate_limit(limit=20, seconds=60 * 60)
def submit_book_inquiry():
    """Receive a /book form submission and create a Lead + linked records.

    Reads `frappe.form_dict` for fields and `frappe.request.files` for
    photos. All fields are optional except first_name + email (per GL's
    consolidation rule (b) 2026-04-29). Returns JSON; raises on
    persistence failure so the client-side script can render an error.
    """
    fd = frappe.form_dict

    # Required fields
    first_name = (fd.get("contact_name") or "").strip()
    email = (fd.get("email_from") or "").strip()
    if not first_name:
        frappe.throw(_("Please tell us your name."), frappe.ValidationError)
    if not email:
        frappe.throw(_("Please give us an email so we can reply."), frappe.ValidationError)
    email = validate_email_address(email, throw=True)

    # Optional contact fields
    phone = (fd.get("phone") or "").strip()
    company = (fd.get("partner_name") or "").strip()

    # Event basics
    occasion = (fd.get("x_occasion_type") or "").strip()
    event_date = (fd.get("x_event_date") or "").strip() or None
    event_time = (fd.get("x_event_time") or "").strip()
    event_end_time = (fd.get("x_event_end_time") or "").strip()
    event_location = (fd.get("x_event_location") or "").strip()
    guest_count = _parse_int(fd.get("x_guest_count"))

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
    requested_item = _requested_item_note(
        (fd.get("lt_requested_item_code") or "").strip(),
        (fd.get("lt_requested_item_name") or "").strip(),
    )
    if requested_item:
        description = _combine_text_values(requested_item, description)
    payment_rule = _payment_rule_for_inquiry(services, num_twisters, num_painters)

    # Lead Source: ensure "Website" exists (idempotent)
    _ensure_lead_source("Website")

    # Build the Lead. lead_cascade.before_insert auto-titles it.
    lead_doc = {
        "doctype": "Lead",
        "first_name": first_name,
        "last_name": "",
        "email_id": email,
        "mobile_no": phone or None,
        "company_name": company or None,
        "source": "Website",
        "status": "Open",
        "custom_pipeline_stage": "New Inquiry",
        "custom_occasion_type": _occasion_label(occasion),
        "custom_event_date": event_date,
        "custom_event_time": event_time or None,
        "custom_event_end_time": event_end_time or None,
        "custom_event_location": event_location or None,
        "custom_guest_count": guest_count,
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
    lead = frappe.get_doc(lead_doc)
    try:
        lead.insert(ignore_permissions=True)
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

    # Attach photos as File records linked to the Lead. Each File becomes
    # a row in the Lead's Attachments sidebar. Hard-cap MAX_PHOTOS files
    # and MAX_PHOTO_BYTES per file -- silently drop excess so a malicious
    # form submission can't blow up storage.
    photo_files = _files_from_request("ufile")
    attached = 0
    for f in photo_files[:MAX_PHOTOS]:
        if not _is_allowed_photo(f):
            continue
        size = _file_size(f)
        if size > MAX_PHOTO_BYTES:
            continue
        try:
            frappe.get_doc({
                "doctype": "File",
                "file_name": f.filename,
                "is_private": 0,
                "content": f.stream.read() if hasattr(f, "stream") else f.read(),
                "attached_to_doctype": "Lead",
                "attached_to_name": lead.name,
            }).insert(ignore_permissions=True)
            attached += 1
        except Exception as e:
            frappe.log_error(
                title=f"/book photo upload failed for {lead.name}",
                message=f"{type(e).__name__}: {e}\nfilename: {f.filename}",
            )

    # Inbound Communication on the Lead's timeline. Captures the
    # message body + the structured summary so Jeff has one place to read
    # the customer's submission verbatim.
    _record_inquiry_communication(
        lead, first_name, email, phone, company, occasion, event_date,
        event_time, event_end_time, event_location, guest_count, services, indoor_outdoor,
        shade_required, colors, decor_types, setup_arrival, decor_notes,
        num_twisters, artist_start, artist_end, twisting_notes,
        num_painters, painter_start, painter_end, painting_notes,
        delivery_notes, package_notes, other_notes, description, attached, payment_rule,
    )

    frappe.db.commit()
    return {"ok": True, "lead": lead.name, "photos": attached}


# -------------------------- helpers ---------------------------------- #


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
        return files_obj.getlist(field_name) or []
    except Exception:
        single = files_obj.get(field_name)
        return [single] if single else []


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


def _record_inquiry_communication(
    lead, first_name, email, phone, company, occasion, event_date,
    event_time, event_end_time, event_location, guest_count, services, indoor_outdoor,
    shade_required, colors, decor_types, setup_arrival, decor_notes,
    num_twisters, artist_start, artist_end, twisting_notes,
    num_painters, painter_start, painter_end, painting_notes,
    delivery_notes, package_notes, other_notes, description, photo_count, payment_rule,
):
    """Build a readable HTML summary of the form submission and post it
    as a Communication on the Lead's timeline."""
    parts = []

    def line(label, value):
        if value is None or value == "" or value == 0:
            return
        parts.append(f"<strong>{escape_html(label)}:</strong> {escape_html(str(value))}")

    line("Phone", phone)
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
