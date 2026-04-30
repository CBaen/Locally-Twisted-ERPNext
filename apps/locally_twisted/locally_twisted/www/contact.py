"""/contact route — Hetzner-shaped contact page with the embedded /book form.

Per GL directive 2026-04-30: /contact no longer redirects to /book. It
renders the Hetzner-mirror layout (intro hero + form + info card aside +
Locations + map) but uses the SAME inquiry form as /book via the shared
partial at templates/includes/book_form.html. One form, two URL surfaces.

Same Jinja context as /book so the partial renders identically. Submission
goes to locally_twisted.www.book.submit_book_inquiry.
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
    context.service_options = SERVICE_OPTIONS
    context.max_photos = MAX_PHOTOS
    context.max_photo_mb = MAX_PHOTO_BYTES // (1024 * 1024)
    return context
