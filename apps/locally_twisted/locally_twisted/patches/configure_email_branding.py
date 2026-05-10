"""Disable Frappe/ERPNext default footer on LT outbound email."""
from __future__ import annotations

import frappe


def execute():
    frappe.db.set_single_value("System Settings", "disable_standard_email_footer", 1)
    frappe.db.set_default("disable_standard_email_footer", "1")
