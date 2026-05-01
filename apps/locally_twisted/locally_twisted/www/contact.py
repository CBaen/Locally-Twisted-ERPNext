"""/contact route — primary Locally Twisted inquiry form.

/contact is the surviving customer inquiry surface. Old /book traffic is
handled as a route alias, but navigation should point customers here.
"""
import frappe

from locally_twisted.www.book import (
    OCCASION_OPTIONS,
    SERVICE_OPTIONS,
    MAX_PHOTOS,
    MAX_PHOTO_BYTES,
)


no_cache = 1
sitemap = 1


def get_context(context):
    context.title = "Contact - Locally Twisted | Utah's Balloon Specialists"
    context.metatags = {
        "description": (
            "Get in touch with Locally Twisted. Custom balloon decor, "
            "twisting, and face painting across the Wasatch Front. "
            "Two Utah locations: West Jordan and Riverdale."
        ),
        "og:title": "Contact - Locally Twisted",
        "og:description": "Get in touch about your celebration.",
        "og:type": "website",
    }
    context.occasion_options = OCCASION_OPTIONS
    context.selected_occasion = frappe.form_dict.get("occasion") or ""
    context.service_options = SERVICE_OPTIONS
    context.max_photos = MAX_PHOTOS
    context.max_photo_mb = MAX_PHOTO_BYTES // (1024 * 1024)
    return context
