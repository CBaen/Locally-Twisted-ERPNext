"""LT Newsletter Signup DocType controller.

Sets signed_up_at automatically on insert. Frappe Datetime fields do not
support a SQL-level now() default, so we set it programmatically here.
"""
import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class LTNewsletterSignup(Document):
    def before_insert(self):
        """Auto-populate signed_up_at on first creation."""
        if not self.signed_up_at:
            self.signed_up_at = now_datetime()
