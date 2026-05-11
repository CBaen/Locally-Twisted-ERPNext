"""Locally Twisted branded login page context."""
from __future__ import annotations

from frappe.www.login import get_context as frappe_login_context


no_cache = True


def get_context(context):
    context = frappe_login_context(context)
    context.hide_website_banner = True
    context.hide_website_footer = True
    context.hide_website_navbar = True
    context.no_cache = 1
    context.no_header = True
    context.title = "Sign In | Locally Twisted"
    context.metatags = {
        "robots": "noindex, nofollow",
        "description": "Sign in to your Locally Twisted customer account.",
    }
    return context
