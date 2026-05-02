"""Compatibility route for the retired /shop-by-category page.

The category-card index was too thin for launch and duplicated the better
customer path on /shop. Keep the route alive for old links, but send visitors
to the full shop where category filters and product cards live together.
"""
import frappe

sitemap = 0


def get_context(context):
    frappe.local.flags.redirect_location = "/shop"
    raise frappe.Redirect
