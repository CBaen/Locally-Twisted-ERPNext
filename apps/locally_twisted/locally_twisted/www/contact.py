"""/contact route — redirects to /book.

Per GL directive 2026-04-29 (Hetzner /book spec session): the two forms
consolidate into one. /book is the canonical inquiry surface; /contact
preserves the URL for any external links / SEO continuity but routes
everyone to the same form.

The old /contact form's `submit_contact` whitelist endpoint was removed
because the consolidated form lives at
`locally_twisted.www.book.submit_book_inquiry`.

If you arrive here looking for the old form fields (name/email/event
type/message): they're now mapped into the richer Lead Custom Fields
on /book. Old /contact data lived in a Communication HTML blob;
new /book data lives in typed fields. See
`_CLIENTS/locally-twisted/CLAUDE.md` "Hetzner /book and /contact are the
canonical spec for the rebuild" section.
"""
import frappe


no_cache = 1


def get_context(context):
    """Raise frappe.Redirect to send the browser to /book.

    `frappe.local.flags.redirect_location` is the documented mechanism;
    raising `frappe.Redirect` triggers Frappe's website router to issue
    a 302 to the target URL. Same pattern used by /thank-you and
    /payment-success in this app.
    """
    frappe.local.flags.redirect_location = "/book"
    raise frappe.Redirect
