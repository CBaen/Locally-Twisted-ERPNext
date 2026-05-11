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
]

ORGANIZATION_NAV = [
    ("dashboard", "Organization Home", "/organization"),
    ("events", "Events", "/organization/events"),
    ("billing", "Billing", "/organization/billing"),
    ("files", "Files", "/organization/files"),
    ("people", "People", "/organization/people"),
]

PAGE_CSS = """
.lt-portal {
    background: #FAF7F2;
    color: #0A0A0B;
    padding: 2rem 1rem 3.5rem;
}
.lt-portal__inner {
    max-width: 70rem;
    margin: 0 auto;
}
.lt-portal__hero {
    background: #0E2240;
    border-bottom: 4px solid #B31B34;
    border-radius: 0.375rem;
    color: #FFFDF9;
    padding: 1.5rem;
}
.lt-portal__eyebrow {
    color: #D9C7B3;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    margin: 0 0 0.5rem;
    text-transform: uppercase;
}
.lt-portal h1 {
    color: #FFFDF9;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: clamp(2rem, 5vw, 3.65rem);
    line-height: 1.04;
    margin: 0;
}
.lt-portal__lede {
    color: rgba(255, 253, 249, 0.84);
    line-height: 1.55;
    margin: 0.75rem 0 0;
    max-width: 48rem;
}
.lt-portal__action {
    align-items: center;
    background: #FFFDF9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 0.375rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: space-between;
    margin-top: 1rem;
    padding: 1rem;
}
.lt-portal__action strong,
.lt-portal__panel h2,
.lt-portal__card-title {
    color: #0E2240;
}
.lt-portal__button {
    background: #B31B34;
    border-radius: 0.25rem;
    color: #FFFDF9;
    font-weight: 800;
    padding: 0.7rem 0.95rem;
    text-decoration: none;
}
.lt-portal__button:hover,
.lt-portal__button:focus {
    color: #FFFDF9;
    text-decoration: underline;
}
.lt-portal__nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1rem 0;
}
.lt-portal__nav a {
    background: #FFFDF9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 0.25rem;
    color: #0E2240;
    font-weight: 800;
    padding: 0.55rem 0.75rem;
    text-decoration: none;
}
.lt-portal__nav a[aria-current="page"] {
    background: #0E2240;
    color: #FFFDF9;
}
.lt-portal__grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr;
}
.lt-portal__card,
.lt-portal__panel {
    background: #FFFDF9;
    border: 1px solid rgba(14, 34, 64, 0.16);
    border-radius: 0.375rem;
    box-shadow: 0 12px 28px rgba(10, 10, 11, 0.06);
    padding: 1rem;
}
.lt-portal__card-title {
    display: block;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.08;
}
.lt-portal__meta,
.lt-portal__empty {
    color: rgba(10, 10, 11, 0.72);
    line-height: 1.5;
    margin: 0.35rem 0 0;
}
.lt-portal__list {
    display: grid;
    gap: 0.75rem;
    margin: 0;
    padding: 0;
}
.lt-portal__list li {
    list-style: none;
}
@media (min-width: 760px) {
    .lt-portal {
        padding-top: 3rem;
    }
    .lt-portal__hero,
    .lt-portal__panel,
    .lt-portal__card {
        padding: 1.5rem;
    }
    .lt-portal__grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}
"""


def account_context(context, page_key: str = "dashboard"):
    summary = get_customer_portal_summary()
    context.show_sidebar = True
    context.no_cache = 1
    context.colocated_css = PAGE_CSS
    context.portal_mode = "account"
    context.portal_summary = summary
    context.portal_nav = _nav(ACCOUNT_NAV, page_key)
    context.portal_page = _account_page(page_key, summary)
    context.title = context.portal_page["title"]
    context.metatags = {"robots": "noindex, nofollow", "description": context.portal_page["lede"]}
    return context


def organization_context(context, page_key: str = "dashboard"):
    summary = get_organization_portal_summary()
    context.show_sidebar = True
    context.no_cache = 1
    context.colocated_css = PAGE_CSS
    context.portal_mode = "organization"
    context.portal_summary = summary
    context.portal_nav = _nav(ORGANIZATION_NAV, page_key)
    context.portal_page = _organization_page(page_key, summary)
    context.title = context.portal_page["title"]
    context.metatags = {"robots": "noindex, nofollow", "description": context.portal_page["lede"]}
    return context


def redirect_to(path: str):
    frappe.local.flags.redirect_location = path
    raise frappe.Redirect


def _nav(items, active_key):
    return [
        {"key": key, "label": label, "href": href, "active": key == active_key}
        for key, label, href in items
    ]


def _account_page(page_key: str, summary: dict):
    pages = {
        "dashboard": _page("data-lt-account-dashboard", "My Account | Locally Twisted", "Your Locally Twisted account", "A practical place for quotes, event details, billing, files, and follow-up.", _dashboard_cards(summary)),
        "events": _page("data-lt-account-events", "Event Details | Locally Twisted", "Event Details", "Review the customer-safe details we have for your current or recent events.", _records(summary["events"], "No event details are ready in this account yet.")),
        "quotes": _page("data-lt-account-quotes", "Quotes | Locally Twisted", "Quotes", "Only quotes ready for customer review appear here.", _records(summary["quotes"], "No customer-ready quotes are waiting right now.")),
        "billing": _page("data-lt-account-billing", "Billing | Locally Twisted", "Invoices & Receipts", "Review invoices, receipts, and payment next steps without internal accounting noise.", _records(summary["billing"]["invoices"] + summary["billing"]["payment_requests"], "No billing records are ready in this account yet.")),
        "files": _page("data-lt-account-files", "Files | Locally Twisted", "Files & Inspiration", "Reference files and approved customer-visible event files stay together here.", _records(summary["files"], "No customer-visible files are attached yet.")),
        "checklist": _page("data-lt-account-checklist", "Checklist | Locally Twisted", "Customer Checklist", "Prep notes are tracked here, and important changes go to the team for review.", _records(summary["checklist"]["items"], "No checklist items are available yet.")),
        "repeat": _page("data-lt-account-repeat", "Repeat Client | Locally Twisted", "Repeat Client", summary["repeat"]["message"], _records([summary["repeat"]["source"]] if summary["repeat"]["eligible"] else [], "Once you have an event history, you can request a similar setup here.")),
        "follow_up": _page("data-lt-account-follow-up", "After-Event Follow-Up | Locally Twisted", "After-Event Follow-Up", "Receipts, review prompts, and rebook reminders live here after an event wraps.", _records(summary["follow_up"]["items"], "After-event follow-up will appear once an event has activity.")),
    }
    return pages[page_key]


def _organization_page(page_key: str, summary: dict):
    pages = {
        "dashboard": _page("data-lt-organization-dashboard", "Organization Portal | Locally Twisted", "Organization Portal", "Separate company, school, civic, and AP tools for shared accounts.", _organization_cards(summary)),
        "events": _page("data-lt-organization-events", "Organization Events | Locally Twisted", "Organization Events", "Events connected to this organization account.", _records(summary["events"], "No organization events are visible yet.")),
        "billing": _page("data-lt-organization-billing", "Organization Billing | Locally Twisted", "Organization Billing", "AP-friendly billing records for the organization.", _records(summary["billing"]["invoices"] + summary["billing"]["payment_requests"], "No organization billing records are visible yet.")),
        "files": _page("data-lt-organization-files", "Organization Files | Locally Twisted", "Organization Files", "Customer-visible organization files and references.", _records(summary["files"], "No organization files are visible yet.")),
        "people": _page("data-lt-organization-people", "Organization People | Locally Twisted", "Organization People", "People connected to this organization account.", _records(summary["people"], "No additional organization people are visible yet.")),
    }
    return pages[page_key]


def _page(marker: str, title: str, heading: str, lede: str, records: list[dict]):
    return {"marker": marker, "title": title, "heading": heading, "lede": lede, "records": records}


def _dashboard_cards(summary: dict) -> list[dict]:
    cards = []
    for key, module in summary["modules"].items():
        href = "/organization" if key == "organization" else f"/account/{key.replace('_', '-')}"
        cards.append({"title": module["label"], "status_label": f"{module['count']} ready", "href": href, "description": module["description"]})
    return cards


def _organization_cards(summary: dict) -> list[dict]:
    return [
        {"title": "Memberships", "status_label": str(len(summary["memberships"])), "description": "Organization account links."},
        {"title": "Events", "status_label": str(len(summary["events"])), "description": "Organization events visible to this user."},
        {"title": "Billing", "status_label": str(len(summary["billing"]["invoices"]) + len(summary["billing"]["payment_requests"])), "description": "AP and payment records."},
        {"title": "People", "status_label": str(len(summary["people"])), "description": "Visible organization contacts."},
    ]


def _records(rows: list[dict], empty_message: str) -> list[dict]:
    if not rows:
        return [{"title": "Nothing here yet", "status_label": "Empty", "description": empty_message}]
    normalized = []
    for row in rows:
        normalized.append(
            {
                "title": row.get("title") or row.get("label") or row.get("name") or row.get("contact") or "Portal item",
                "status_label": row.get("status_label") or row.get("organization_role") or row.get("purpose") or "",
                "description": row.get("description") or row.get("location") or row.get("event_date") or row.get("due_date") or "",
                "href": row.get("href") or "",
            }
        )
    return normalized
