from frappe.model.document import Document


class LTMaintenanceActionRequest(Document):
    def validate(self):
        self.sanitized = 1
        self.customer_data_included = 0
        self.raw_log_access = 0
        if str(self.permission_tier or "").startswith(("2", "3", "4")):
            self.approval_required = 1
