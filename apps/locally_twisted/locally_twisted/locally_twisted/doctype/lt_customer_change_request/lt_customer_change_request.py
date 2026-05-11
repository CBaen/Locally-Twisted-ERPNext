import json

import frappe
from frappe.model.document import Document


class LTCustomerChangeRequest(Document):
    def validate(self):
        if not self.status:
            self.status = "Submitted"
        if not self.payload_json:
            self.payload_json = "{}"
        try:
            json.loads(self.payload_json)
        except json.JSONDecodeError:
            frappe.throw("Customer change request payload must be valid JSON")
