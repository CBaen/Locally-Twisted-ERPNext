"""Whitelisted owner business access API.

The implementation delegates to provider-neutral DTO functions so ChatGPT,
MCP, phone pages, and future API clients can share the same contract.
"""
from __future__ import annotations

import frappe

from locally_twisted import owner_business_access


@frappe.whitelist()
def action_center(limit=12):
    return owner_business_access.action_center_context(limit=limit)


@frappe.whitelist()
def urgent_contacts(limit=12):
    return {"ok": True, "urgent_contacts": owner_business_access.urgent_contacts(limit=limit)}


@frappe.whitelist()
def upcoming_bookings(limit=6):
    return {"ok": True, "upcoming_bookings": owner_business_access.upcoming_bookings(limit=limit)}


@frappe.whitelist()
def search_contacts(query: str, limit=8):
    return owner_business_access.search_contacts(query=query, limit=limit)


@frappe.whitelist()
def log_contact_attempt(source_doctype: str, source_name: str, channel: str, note: str | None = None):
    return owner_business_access.log_contact_attempt(
        source_doctype=source_doctype,
        source_name=source_name,
        channel=channel,
        note=note,
    )
