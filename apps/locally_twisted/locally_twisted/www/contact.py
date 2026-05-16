"""/contact route — primary Locally Twisted inquiry form.

/contact is the surviving customer inquiry surface. Old /book traffic is
handled as a route alias, but navigation should point customers here.
"""
import frappe

from locally_twisted.www.book import (
    OCCASION_OPTIONS,
    PACKAGE_ITEM_OPTIONS,
    SERVICE_OPTIONS,
    MAX_PHOTOS,
    MAX_PHOTO_BYTES,
    PREFERRED_CONTACT_OPTIONS,
    build_inquiry_spam_token,
)


no_cache = 1
sitemap = 1


def get_context(context):
    service_param = (frappe.form_dict.get("service") or "").strip().lower()
    intent_param = (frappe.form_dict.get("intent") or "").strip().lower()
    item_param = (frappe.form_dict.get("item") or "").strip()

    preselected_services = []
    if service_param == "btfp":
        preselected_services = ["Balloon Twisting", "Face Painting"]
    elif service_param == "twisting":
        preselected_services = ["Balloon Twisting"]
    elif service_param in {"face-painting", "face_painting", "painting"}:
        preselected_services = ["Face Painting"]

    requested_item = _requested_item(item_param)
    if requested_item and "Balloon Decor" not in preselected_services:
        preselected_services.append("Balloon Decor")

    context.title = "Tell us about your event - Locally Twisted"
    context.metatags = {
        "title": context.title,
        "description": (
            "Send the date, location, services, and setup details for a Utah event "
            "with Locally Twisted."
        ),
        "og:title": context.title,
        "og:description": (
            "Tell Locally Twisted about the Utah event you are planning."
        ),
        "og:type": "website",
        "twitter:card": "summary_large_image",
    }
    context.occasion_options = OCCASION_OPTIONS
    context.selected_occasion = frappe.form_dict.get("occasion") or ""
    context.service_options = SERVICE_OPTIONS
    context.package_item_options = PACKAGE_ITEM_OPTIONS
    context.preferred_contact_options = PREFERRED_CONTACT_OPTIONS
    context.preselected_services = preselected_services
    context.requested_item_code = requested_item.get("item_code") if requested_item else ""
    context.requested_item_name = requested_item.get("web_item_name") if requested_item else ""
    context.contact_intent = intent_param
    context.contact_intro_title = "Tell us about your event"
    context.contact_intro_lede = (
        "Share the date, location, services, and a few setup details. "
        "We'll follow up using your preferred contact method."
    )
    context.max_photos = MAX_PHOTOS
    context.max_photo_mb = MAX_PHOTO_BYTES // (1024 * 1024)
    context.inquiry_spam_token = build_inquiry_spam_token()
    return context


def _requested_item(item_code):
    if not item_code:
        return None
    return frappe.db.get_value(
        "Website Item",
        {"item_code": item_code, "published": 1},
        ["item_code", "web_item_name"],
        as_dict=True,
    )
