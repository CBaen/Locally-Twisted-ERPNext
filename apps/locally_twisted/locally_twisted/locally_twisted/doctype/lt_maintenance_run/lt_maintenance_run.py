from frappe.model.document import Document


class LTMaintenanceRun(Document):
    def validate(self):
        self.sanitized = 1
        self.customer_data_included = 0
        self.raw_log_access = 0
