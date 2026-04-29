"""Override Frappe's /payment-success page for guest checkouts.

Why this file exists: Frappe's payments app constructs the post-charge
redirect URL in stripe_settings.py:finalize_request — and at line 272 it
unconditionally appends `?redirect_to=None` (literal string "None") even
when the URL already contains `?`. Result: customers land on
    /payment-success?doctype=Payment%20Request&docname=ACC-PRQ-...?redirect_to=None
The malformed second `?` makes `docname` carry the redirect_to suffix,
and even if it didn't, the upstream controller calls
    frappe.get_doc("Payment Request", docname)
under the GUEST session — which 403s because Payment Request is restricted.

We override /payment-success here (via website_route_rules in hooks.py)
to hand guest customers off to /thank-you?order=<so_name>. We don't read
the Payment Request through guest perms; we verify the charge actually
completed (Integration Request status = Completed) and then look up the
Sales Order with elevated read perms.

When the upstream bug is fixed, this override remains useful: it gives
guests a clean post-checkout landing without exposing Payment Request.
"""
import frappe


no_cache = 1
sitemap = 0


def get_context(context):
    docname_raw = (frappe.form_dict.get("docname") or "").strip()
    doctype = (frappe.form_dict.get("doctype") or "").strip()

    docname = docname_raw.split("?", 1)[0] if docname_raw else ""

    if doctype != "Payment Request" or not docname:
        _redirect("/")

    integration_status = frappe.db.get_value(
        "Integration Request",
        {"reference_doctype": "Payment Request", "reference_docname": docname},
        "status",
    )
    if integration_status != "Completed":
        _redirect("/")

    sales_order = frappe.db.get_value("Payment Request", docname, "reference_name")
    if not sales_order:
        _redirect("/")

    _redirect(f"/thank-you?order={sales_order}")


def _redirect(location):
    frappe.local.flags.redirect_location = location
    raise frappe.Redirect
