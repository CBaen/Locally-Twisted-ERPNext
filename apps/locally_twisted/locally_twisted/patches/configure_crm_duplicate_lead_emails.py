"""Allow repeat website inquiries from the same customer email.

Locally Twisted customers may ask about multiple events from the same email
address. ERPNext's default Lead validation blocks that unless CRM Settings
explicitly allows duplicate Lead emails, which breaks the public inquiry form.
"""

import frappe


def execute():
    frappe.db.set_single_value(
        "CRM Settings",
        "allow_lead_duplication_based_on_emails",
        1,
        update_modified=False,
    )
