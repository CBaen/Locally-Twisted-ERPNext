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
)


no_cache = 1
sitemap = 1


def get_context(context):
    service_param = (frappe.form_dict.get("service") or "").strip().lower()
    intent_param = (frappe.form_dict.get("intent") or "").strip().lower()

    preselected_services = []
    if service_param == "btfp":
        preselected_services = ["Balloon Twisting", "Face Painting"]
    elif service_param == "twisting":
        preselected_services = ["Balloon Twisting"]
    elif service_param in {"face-painting", "face_painting", "painting"}:
        preselected_services = ["Face Painting"]

    context.title = "Contact Locally Twisted"
    context.metatags = {
        "title": "Contact Locally Twisted",
        "description": (
            "Tell us about your celebration. Balloon decor, twisting, "
            "and face painting along the Wasatch Front."
        ),
        "og:title": "Contact Locally Twisted",
        "og:description": (
            "Tell us about your celebration. Balloon decor, twisting, "
            "and face painting along the Wasatch Front."
        ),
        "og:type": "website",
        "twitter:card": "summary_large_image",
    }
    context.occasion_options = OCCASION_OPTIONS
    context.selected_occasion = frappe.form_dict.get("occasion") or ""
    context.service_options = SERVICE_OPTIONS
    context.package_item_options = PACKAGE_ITEM_OPTIONS
    context.preselected_services = preselected_services
    context.contact_intent = intent_param
    context.contact_intro_title = (
        "Tell us about your celebration"
        if intent_param == "quick"
        else "Let's create something beautiful"
    )
    context.contact_intro_lede = (
        "A few details are enough to get started."
        if intent_param == "quick"
        else "Tell us about your celebration."
    )
    context.max_photos = MAX_PHOTOS
    context.max_photo_mb = MAX_PHOTO_BYTES // (1024 * 1024)
    return context
