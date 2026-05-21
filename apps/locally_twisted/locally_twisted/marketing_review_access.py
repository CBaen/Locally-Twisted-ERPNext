"""Website-only marketing review access for external reviewers."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import get_url, now_datetime


MARKETING_REVIEW_ROLE = "LT Marketing Review Access"
MARKETING_REVIEW_COMPANY = "Exploring Not Boring"
MARKETING_REVIEW_ROUTE = "/marketing-review"
MARKETING_REVIEW_PACKET_METHOD = (
    "/api/method/locally_twisted.marketing_review_access.download_marketing_review_packet"
)
MARKETING_REVIEW_PACKET_TITLE = "Locally Twisted Marketing Review Packet"

PUBLIC_REVIEW_LINKS = [
    {
        "label": "Homepage",
        "href": "/",
        "description": "First impression, proof, audiences, and quote path.",
    },
    {
        "label": "Portfolio",
        "href": "/portfolio",
        "description": "Photo proof, work quality, and scan rhythm.",
    },
    {
        "label": "Contact",
        "href": "/contact",
        "description": "Inquiry copy, form clarity, and customer confidence.",
    },
    {
        "label": "Twisting & Face Painting",
        "href": "/balloon-twisting-and-face-painting",
        "description": "Service positioning, packages, and inquiry handoff.",
    },
    {
        "label": "Shop",
        "href": "/shop",
        "description": "Browse path, product clarity, and quote or checkout messaging.",
    },
    {
        "label": "FAQ",
        "href": "/faq",
        "description": "Customer questions, plain-language answers, and trust gaps.",
    },
    {
        "label": "Accessibility",
        "href": "/accessibility",
        "description": "Public accessibility language and support path.",
    },
    {
        "label": "Policies",
        "href": "/terms-of-service",
        "description": "Terms and linked policy surfaces for copy review only.",
    },
]

FORBIDDEN_MARKETING_DOCTYPES = (
    "Lead",
    "Customer",
    "Contact",
    "Address",
    "Quotation",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Communication",
    "Email Queue",
    "File",
    "Web Page",
    "Website Settings",
    "Blog Post",
    "Newsletter",
    "Email Group",
    "Campaign",
    "Item",
    "Item Group",
    "Item Price",
    "Website Item",
    "Project",
    "Task",
    "Error Log",
    "Access Log",
    "Activity Log",
    "Version",
    "LT Maintenance Run",
    "LT Maintenance Health Event",
    "LT Maintenance Action Request",
    "LT Maintenance Action Log",
)

FORBIDDEN_MARKETING_ROLES = {
    "System Manager",
    "Website Manager",
    "Desk User",
    "Customer",
    "Supplier",
    "Item Manager",
    "Accounts User",
    "Accounts Manager",
    "Sales User",
    "Sales Manager",
    "LT Owner Access",
    "LT Accountant Access",
    "LT Maintenance Admin Access",
}


def apply_marketing_review_context(context) -> Any:
    """Populate the protected marketing review page context."""
    require_marketing_review_access()
    context.no_cache = 1
    context.title = "Marketing Review | Locally Twisted"
    context.metatags = {
        "robots": "noindex, nofollow",
        "description": "Website review doorway for Locally Twisted marketing reviewers.",
    }
    context.marketing_review_company = MARKETING_REVIEW_COMPANY
    context.marketing_review_links = PUBLIC_REVIEW_LINKS
    context.marketing_review_role = MARKETING_REVIEW_ROLE
    context.marketing_review_packet = marketing_review_packet_context()
    context.page_css = MARKETING_REVIEW_CSS
    return context


def marketing_review_packet_context() -> dict[str, Any]:
    """Return the current packet metadata for the protected review page."""
    generated_at = now_datetime()
    return {
        "title": MARKETING_REVIEW_PACKET_TITLE,
        "generated_label": generated_at.strftime("%Y-%m-%d %H:%M"),
        "download_href": MARKETING_REVIEW_PACKET_METHOD,
        "sitemap_href": "/sitemap.xml",
        "robots_href": "/robots.txt",
    }


@frappe.whitelist(methods=["GET"])
def download_marketing_review_packet() -> None:
    """Download the current website-only packet for external marketing review."""
    require_marketing_review_access()
    generated_at = now_datetime()
    content = build_marketing_review_packet(generated_at=generated_at)
    filename = f"locally-twisted-marketing-review-packet-{generated_at.strftime('%Y%m%d-%H%M')}.md"

    frappe.response.filename = filename
    frappe.response.filecontent = content.encode("utf-8")
    frappe.response.type = "download"
    frappe.response.display_content_as = "attachment"


def build_marketing_review_packet(generated_at=None) -> str:
    """Build a sanitized, current marketing review packet from approved public inputs."""
    generated_at = generated_at or now_datetime()
    site_url = get_url().rstrip("/")

    lines = [
        f"# {MARKETING_REVIEW_PACKET_TITLE}",
        "",
        f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M')}",
        f"Review company: {MARKETING_REVIEW_COMPANY}",
        f"Access role: {MARKETING_REVIEW_ROLE}",
        "",
        "## Current Status",
        "",
        "- This packet is for public website and ecommerce review only.",
        "- Do not submit indexing, recrawl, Search Console, sitemap submission, or ads launch requests.",
        "- Shop indexing waits until the shop is on staging and owner product approval is recorded.",
        "- This account has no ERPNext Desk, customer record, file, order, invoice, payment, or product-edit authority.",
        "",
        "## Discovery Files",
        "",
        f"- Sitemap: {site_url}/sitemap.xml",
        f"- Robots: {site_url}/robots.txt",
        "",
        "## Review Pages",
        "",
    ]

    for item in PUBLIC_REVIEW_LINKS:
        lines.append(f"- {item['label']}: {site_url}{item['href']} - {item['description']}")

    lines.extend(
        [
            "",
            "## What To Send Back",
            "",
            "- Broken links, missing pages, unclear copy, confusing navigation, mobile layout problems, and product/shop review notes.",
            "- Suggested edits as comments or a separate document. Do not make changes inside ERPNext.",
            "- Any indexing, ads, analytics, or Search Console recommendations as recommendations only, not actions.",
            "",
            "## Access Boundary",
            "",
            "- Approved: view the public review doorway, public website pages, sitemap, robots file, and this packet.",
            "- Not approved: ERPNext Desk, website editing, product editing, customer/client records, files, invoices, payments, email queues, Search Console ownership, sitemap submission, recrawl requests, ad account ownership, or campaign launch authority.",
        ]
    )
    return "\n".join(lines) + "\n"


def require_marketing_review_access(user: str | None = None) -> None:
    """Require the narrow external marketing review role."""
    user = user or frappe.session.user
    if not user or user == "Guest":
        frappe.local.flags.redirect_location = f"/login?redirect-to={MARKETING_REVIEW_ROUTE}"
        raise frappe.Redirect

    if not _has_explicit_marketing_review_role(user):
        frappe.throw(
            _("This review page is only available to approved Locally Twisted marketing reviewers."),
            frappe.PermissionError,
        )


def marketing_role_boundary() -> dict[str, Any]:
    """Return the current least-privilege boundary for the marketing role."""
    role_exists = bool(frappe.db.exists("Role", MARKETING_REVIEW_ROLE))
    role = frappe.get_doc("Role", MARKETING_REVIEW_ROLE) if role_exists else None
    failures: list[str] = []

    if not role_exists:
        failures.append(f"Missing Role {MARKETING_REVIEW_ROLE}")
    elif int(role.get("disabled") or 0):
        failures.append(f"{MARKETING_REVIEW_ROLE} is disabled")
    elif int(role.get("desk_access") or 0):
        failures.append(f"{MARKETING_REVIEW_ROLE} must not grant Desk access")

    for doctype in FORBIDDEN_MARKETING_DOCTYPES:
        if not frappe.db.exists("DocType", doctype):
            continue
        if _role_has_read_permission(doctype, MARKETING_REVIEW_ROLE):
            failures.append(f"{MARKETING_REVIEW_ROLE} can read forbidden DocType {doctype}")

    return {
        "ok": not failures,
        "role": MARKETING_REVIEW_ROLE,
        "company": MARKETING_REVIEW_COMPANY,
        "role_exists": role_exists,
        "desk_access": int(role.get("desk_access") or 0) if role else None,
        "review_route": MARKETING_REVIEW_ROUTE,
        "review_links": PUBLIC_REVIEW_LINKS,
        "forbidden_doctypes": list(FORBIDDEN_MARKETING_DOCTYPES),
        "forbidden_roles": sorted(FORBIDDEN_MARKETING_ROLES),
        "failures": failures,
    }


def _role_has_read_permission(doctype: str, role: str) -> bool:
    return bool(
        frappe.db.exists(
            "DocPerm",
            {
                "parent": doctype,
                "parenttype": "DocType",
                "role": role,
                "permlevel": 0,
                "read": 1,
            },
        )
    )


def marketing_no_records_condition(user: str | None = None) -> str | None:
    """Hide sensitive backend rows from marketing reviewers in list queries."""
    if _is_marketing_review_user(user):
        return "1=0"
    return None


def has_marketing_sensitive_doc_permission(doc=None, ptype: str | None = None, user: str | None = None) -> bool | None:
    """Deny sensitive backend document access for marketing reviewers only."""
    if _is_marketing_review_user(user):
        return False
    return None


def block_marketing_sensitive_doc_mutation(doc, method: str | None = None) -> None:
    """Block owner-scoped framework defaults from creating marketing-visible records."""
    if _is_marketing_review_user():
        frappe.throw(
            _("Marketing review access is public-site review only and cannot change ERPNext records."),
            frappe.PermissionError,
        )


def _is_marketing_review_user(user: str | None = None) -> bool:
    user = user or frappe.session.user
    if not user or user == "Guest":
        return False
    return _has_explicit_marketing_review_role(user)


def is_marketing_review_user(user: str | None = None) -> bool:
    """Return true only for users explicitly assigned marketing review access."""
    return _is_marketing_review_user(user)


def _has_explicit_marketing_review_role(user: str) -> bool:
    return bool(
        frappe.db.exists(
            "Has Role",
            {
                "parenttype": "User",
                "parent": user,
                "role": MARKETING_REVIEW_ROLE,
            },
        )
    )


MARKETING_REVIEW_CSS = """
.lt-marketing-review {
  background: #f7f4ef;
  min-height: 64vh;
  padding: clamp(2.25rem, 6vw, 4.5rem) 1rem;
}
.lt-marketing-review__inner {
  width: min(100%, 1080px);
  margin: 0 auto;
}
.lt-marketing-review__eyebrow {
  margin: 0 0 0.6rem;
  color: var(--lt-crimson);
  font-family: var(--lt-font-body);
  font-size: 0.76rem;
  font-weight: 900;
  text-transform: uppercase;
}
.lt-marketing-review__title {
  max-width: 15ch;
  margin: 0;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(2.2rem, 6vw, 4.1rem);
  line-height: 1;
}
.lt-marketing-review__lede {
  max-width: 64rem;
  margin: 1rem 0 0;
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.6;
}
.lt-marketing-review__notice {
  display: grid;
  gap: 0.35rem;
  margin: 1.4rem 0 0;
  border-left: 4px solid var(--lt-navy);
  background: #fff;
  padding: 1rem 1.15rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-body);
}
.lt-marketing-review__notice strong {
  color: var(--lt-navy);
}
.lt-marketing-review__packet {
  display: grid;
  gap: 0.85rem;
  margin: 1rem 0 0;
  border: 1px solid rgba(14, 34, 64, 0.14);
  border-radius: 6px;
  background: #ffffff;
  padding: 1rem 1.15rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-body);
  box-shadow: 0 12px 28px rgba(10, 10, 11, 0.05);
}
.lt-marketing-review__packet-title {
  margin: 0;
  color: var(--lt-navy);
  font-family: var(--lt-font-heading);
  font-size: 1.18rem;
  line-height: 1.15;
}
.lt-marketing-review__packet-meta {
  margin: 0;
  color: var(--lt-soft-gray);
  font-size: 0.93rem;
  line-height: 1.45;
}
.lt-marketing-review__packet-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}
.lt-marketing-review__packet-action {
  display: inline-flex;
  min-height: 42px;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(14, 34, 64, 0.18);
  border-radius: 999px;
  background: var(--lt-navy);
  color: #ffffff;
  padding: 0.6rem 0.9rem;
  font-size: 0.9rem;
  font-weight: 900;
  text-decoration: none;
}
.lt-marketing-review__packet-action:hover,
.lt-marketing-review__packet-action:focus-visible {
  background: var(--lt-crimson);
  color: #ffffff;
  text-decoration: none;
}
.lt-marketing-review__packet-action--secondary {
  background: #ffffff;
  color: var(--lt-navy);
}
.lt-marketing-review__packet-action--secondary:hover,
.lt-marketing-review__packet-action--secondary:focus-visible {
  background: #f7f4ef;
  color: var(--lt-crimson);
}
.lt-marketing-review__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.85rem;
  margin-top: 1.6rem;
}
.lt-marketing-review__link {
  display: flex;
  min-height: 148px;
  flex-direction: column;
  justify-content: space-between;
  border: 1px solid rgba(14, 34, 64, 0.14);
  border-radius: 6px;
  background: #fff;
  color: var(--lt-ink);
  padding: 1rem;
  text-decoration: none;
  box-shadow: 0 12px 28px rgba(10, 10, 11, 0.05);
}
.lt-marketing-review__link:hover,
.lt-marketing-review__link:focus-visible {
  border-color: var(--lt-crimson);
  color: var(--lt-ink);
  text-decoration: none;
}
.lt-marketing-review__link strong {
  color: var(--lt-navy);
  font-family: var(--lt-font-heading);
  font-size: 1.18rem;
  line-height: 1.1;
}
.lt-marketing-review__link span {
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 0.93rem;
  line-height: 1.45;
}
.lt-marketing-review__footer {
  margin-top: 1.25rem;
  color: var(--lt-navy);
  font-family: var(--lt-font-body);
  font-size: 0.95rem;
  font-weight: 800;
}
.lt-marketing-review__footer a {
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 0.18em;
}
@media (max-width: 860px) {
  .lt-marketing-review__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 560px) {
  .lt-marketing-review__grid {
    grid-template-columns: 1fr;
  }
  .lt-marketing-review__link {
    min-height: 128px;
  }
}
"""
