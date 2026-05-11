"""Shared customer portal page context helpers."""
from __future__ import annotations

import frappe

from locally_twisted.customer_portal import get_customer_portal_summary, get_organization_portal_summary


ACCOUNT_NAV = [
    ("events", "Event Details", "/account/events"),
    ("quotes", "Quotes", "/account/quotes"),
    ("billing", "Billing", "/account/billing"),
    ("files", "Files", "/account/files"),
    ("checklist", "Checklist", "/account/checklist"),
    ("repeat", "Repeat", "/account/repeat"),
    ("follow_up", "Follow-Up", "/account/follow-up"),
    ("organization", "Organization Portal", "/organization"),
]

ORGANIZATION_NAV = [
    ("dashboard", "Organization Home", "/organization"),
    ("events", "Events", "/organization/events"),
    ("billing", "Billing", "/organization/billing"),
    ("files", "Files", "/organization/files"),
    ("people", "People", "/organization/people"),
]

PORTAL_ICON_BASE = "/assets/locally_twisted/icons/customer-portal"

NAV_ICONS = {
    "dashboard": "portal-avatar-monogram.svg",
    "events": "portal-calendar.svg",
    "quotes": "portal-file.svg",
    "billing": "portal-credit-card.svg",
    "files": "portal-folder.svg",
    "checklist": "portal-checklist.svg",
    "repeat": "portal-repeat.svg",
    "follow_up": "portal-chat.svg",
    "organization": "portal-building.svg",
    "people": "portal-building.svg",
}


def account_context(context, page_key: str = "dashboard"):
    try:
        summary = get_customer_portal_summary()
    except frappe.PermissionError:
        if frappe.session.user == "Guest":
            raise
        return _access_blocked_context(context)
    context.show_sidebar = False
    context.hide_website_banner = True
    context.hide_website_footer = True
    context.hide_website_navbar = True
    context.no_cache = 1
    context.portal_mode = "account"
    context.portal_summary = summary
    context.portal_nav = _nav(ACCOUNT_NAV, page_key)
    context.portal_page = _account_page(page_key, summary)
    context.portal_metrics = _account_metrics(summary)
    context.portal_icon_base = PORTAL_ICON_BASE
    context.portal_display_name = _short_name(summary["identity"].get("display_name"))
    context.title = context.portal_page["title"]
    context.metatags = {"robots": "noindex, nofollow", "description": context.portal_page["lede"]}
    return context


def organization_context(context, page_key: str = "dashboard"):
    try:
        summary = get_organization_portal_summary()
    except frappe.PermissionError:
        if frappe.session.user == "Guest":
            raise
        return _access_blocked_context(context)
    context.show_sidebar = False
    context.hide_website_banner = True
    context.hide_website_footer = True
    context.hide_website_navbar = True
    context.no_cache = 1
    context.portal_mode = "organization"
    context.portal_summary = summary
    context.portal_nav = _nav(ORGANIZATION_NAV, page_key)
    context.portal_page = _organization_page(page_key, summary)
    context.portal_metrics = _organization_metrics(summary)
    context.portal_icon_base = PORTAL_ICON_BASE
    context.portal_display_name = _short_name(summary["identity"].get("display_name"))
    context.title = context.portal_page["title"]
    context.metatags = {"robots": "noindex, nofollow", "description": context.portal_page["lede"]}
    return context


def redirect_to(path: str):
    frappe.local.flags.redirect_location = path
    raise frappe.Redirect


def _access_blocked_context(context):
    context.show_sidebar = False
    context.hide_website_banner = True
    context.hide_website_footer = True
    context.hide_website_navbar = True
    context.no_cache = 1
    context.portal_mode = "blocked"
    context.portal_access_blocked = True
    context.portal_icon_base = PORTAL_ICON_BASE
    context.portal_display_name = _short_name(frappe.session.user)
    context.title = "Account Access | Locally Twisted"
    context.metatags = {
        "robots": "noindex, nofollow",
        "description": "This sign-in is not connected to a Locally Twisted customer account.",
    }
    return context


def _nav(items, active_key):
    return [
        {"key": key, "label": label, "href": href, "active": key == active_key, "icon": _icon_for(key)}
        for key, label, href in items
    ]


def _account_page(page_key: str, summary: dict):
    pages = {
        "dashboard": _page("data-lt-account-dashboard", "My Account | Locally Twisted", "Your Locally Twisted account", "A practical place for quotes, event details, billing, files, and follow-up.", _dashboard_cards(summary), "portal-avatar-monogram.svg"),
        "events": _page("data-lt-account-events", "Event Details | Locally Twisted", "Event Details", "Review the customer-safe details we have for your current or recent events.", _records(summary["events"], "No event details are ready in this account yet.", "events"), "portal-calendar.svg"),
        "quotes": _page("data-lt-account-quotes", "Quotes | Locally Twisted", "Quotes", "Only quotes ready for customer review appear here.", _records(summary["quotes"], "No customer-ready quotes are waiting right now.", "quotes"), "portal-file.svg"),
        "billing": _page("data-lt-account-billing", "Billing | Locally Twisted", "Invoices & Receipts", "Review invoices, receipts, and payment next steps without internal accounting noise.", _records(summary["billing"]["invoices"] + summary["billing"]["payment_requests"], "No billing records are ready in this account yet.", "billing"), "portal-credit-card.svg"),
        "files": _page("data-lt-account-files", "Files | Locally Twisted", "Files & Inspiration", "Reference files and approved customer-visible event files stay together here.", _records(summary["files"], "No customer-visible files are attached yet.", "files"), "portal-folder.svg"),
        "checklist": _page("data-lt-account-checklist", "Checklist | Locally Twisted", "Customer Checklist", "Prep notes are tracked here, and important changes go to the team for review.", _records(summary["checklist"]["items"], "No checklist items are available yet.", "checklist"), "portal-checklist.svg"),
        "repeat": _page("data-lt-account-repeat", "Repeat Client | Locally Twisted", "Repeat Client", summary["repeat"]["message"], _records([summary["repeat"]["source"]] if summary["repeat"]["eligible"] else [], "Once you have an event history, you can request a similar setup here.", "repeat"), "portal-repeat.svg"),
        "follow_up": _page("data-lt-account-follow-up", "After-Event Follow-Up | Locally Twisted", "After-Event Follow-Up", "Receipts, review prompts, and rebook reminders live here after an event wraps.", _records(summary["follow_up"]["items"], "After-event follow-up will appear once an event has activity.", "follow_up"), "portal-chat.svg"),
    }
    return pages[page_key]


def _organization_page(page_key: str, summary: dict):
    pages = {
        "dashboard": _page("data-lt-organization-dashboard", "Organization Portal | Locally Twisted", "Organization Portal", "Separate company, school, civic, and AP tools for shared accounts.", _organization_cards(summary), "portal-building.svg"),
        "events": _page("data-lt-organization-events", "Organization Events | Locally Twisted", "Organization Events", "Events connected to this organization account.", _records(summary["events"], "No organization events are visible yet.", "events"), "portal-calendar.svg"),
        "billing": _page("data-lt-organization-billing", "Organization Billing | Locally Twisted", "Organization Billing", "AP-friendly billing records for the organization.", _records(summary["billing"]["invoices"] + summary["billing"]["payment_requests"], "No organization billing records are visible yet.", "billing"), "portal-credit-card.svg"),
        "files": _page("data-lt-organization-files", "Organization Files | Locally Twisted", "Organization Files", "Customer-visible organization files and references.", _records(summary["files"], "No organization files are visible yet.", "files"), "portal-folder.svg"),
        "people": _page("data-lt-organization-people", "Organization People | Locally Twisted", "Organization People", "People connected to this organization account.", _records(summary["people"], "No additional organization people are visible yet.", "people"), "portal-building.svg"),
    }
    return pages[page_key]


def _page(marker: str, title: str, heading: str, lede: str, records: list[dict], icon: str):
    return {"marker": marker, "title": title, "heading": heading, "lede": lede, "records": records, "icon": icon}


def _dashboard_cards(summary: dict) -> list[dict]:
    cards = []
    for key, module in summary["modules"].items():
        href = "/organization" if key == "organization" else f"/account/{key.replace('_', '-')}"
        cards.append(
            {
                "title": module["label"],
                "status_label": _ready_label(module["count"]),
                "href": href,
                "cta_label": "Open section",
                "description": module["description"],
                "icon": _icon_for(key),
            }
        )
    return cards


def _organization_cards(summary: dict) -> list[dict]:
    return [
        {
            "title": "Memberships",
            "status_label": _ready_label(len(summary["memberships"])),
            "description": "Organization account links.",
            "icon": "portal-building.svg",
        },
        {
            "title": "Events",
            "status_label": _ready_label(len(summary["events"])),
            "description": "Organization events visible to this user.",
            "icon": "portal-calendar.svg",
        },
        {
            "title": "Billing",
            "status_label": _ready_label(len(summary["billing"]["invoices"]) + len(summary["billing"]["payment_requests"])),
            "description": "AP and payment records.",
            "icon": "portal-credit-card.svg",
        },
        {
            "title": "People",
            "status_label": _ready_label(len(summary["people"])),
            "description": "Visible organization contacts.",
            "icon": "portal-building.svg",
        },
    ]


def _records(rows: list[dict], empty_message: str, icon_key: str) -> list[dict]:
    if not rows:
        return [{"title": "Nothing here yet", "status_label": "Clear", "description": empty_message, "icon": _icon_for(icon_key)}]
    normalized = []
    for row in rows:
        normalized.append(
            {
                "title": row.get("title") or row.get("label") or row.get("name") or row.get("contact") or "Portal item",
                "status_label": _row_status(row),
                "description": row.get("description") or row.get("location") or row.get("event_date") or row.get("due_date") or "",
                "href": row.get("href") or "",
                "cta_label": row.get("cta_label") or "Open",
                "meta": _record_meta(row),
                "icon": _icon_for(icon_key),
            }
        )
    return normalized


def _account_metrics(summary: dict) -> list[dict[str, str]]:
    modules = summary["modules"]
    return [
        {"label": "Events", "value": str(modules["events"]["count"])},
        {"label": "Quotes", "value": str(modules["quotes"]["count"])},
        {"label": "Billing", "value": str(modules["billing"]["count"])},
        {"label": "Files", "value": str(modules["files"]["count"])},
    ]


def _organization_metrics(summary: dict) -> list[dict[str, str]]:
    return [
        {"label": "Events", "value": str(len(summary["events"]))},
        {"label": "Billing", "value": str(len(summary["billing"]["invoices"]) + len(summary["billing"]["payment_requests"]))},
        {"label": "Files", "value": str(len(summary["files"]))},
        {"label": "People", "value": str(len(summary["people"]))},
    ]


def _short_name(display_name: str | None) -> str:
    cleaned = (display_name or "").strip()
    if not cleaned:
        return "there"
    return cleaned.split()[0]


def _ready_label(count: int) -> str:
    return f"{count} ready" if count else "Clear"


def _row_status(row: dict) -> str:
    if "completed" in row:
        return "Done" if row.get("completed") else "To review"
    return row.get("status_label") or row.get("organization_role") or row.get("purpose") or ""


def _record_meta(row: dict) -> list[dict[str, str]]:
    items = [
        ("Date", row.get("event_date") or row.get("posting_date")),
        ("Time", row.get("window")),
        ("Location", row.get("location")),
        ("Guests", row.get("guest_count")),
        ("Amount", _money(row.get("amount"))),
        ("Outstanding", _money(row.get("outstanding_amount"))),
        ("Due", row.get("due_date")),
        ("Valid until", row.get("valid_till")),
        ("Reference", row.get("source_name") or row.get("reference_name")),
    ]
    return [{"label": label, "value": str(value)} for label, value in items if value not in (None, "", 0)]


def _money(value) -> str:
    if value in (None, ""):
        return ""
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _icon_for(key: str) -> str:
    return NAV_ICONS.get(key, "portal-file.svg")
