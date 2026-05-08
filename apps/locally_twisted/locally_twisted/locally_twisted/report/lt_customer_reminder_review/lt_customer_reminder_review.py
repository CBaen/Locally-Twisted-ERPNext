"""Desk report adapter for the no-live customer reminder review rows."""
from __future__ import annotations

import frappe
from frappe import _

from locally_twisted.paperwork import customer_reminder_review_report


def execute(filters=None):
    """Return columns and rows for Frappe's Script Report runner."""
    result = customer_reminder_review_report.run()
    if result.get("ok") is not True:
        failures = "; ".join(result.get("failures") or ["report returned not ok"])
        frappe.throw(
            _("LT Customer Reminder Review failed before rendering: {0}").format(failures),
            title=_("Reminder Review Blocked"),
        )
    return result.get("columns") or [], result.get("rows") or []
