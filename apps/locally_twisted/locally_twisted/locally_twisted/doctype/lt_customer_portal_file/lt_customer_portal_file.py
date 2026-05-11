from frappe.model.document import Document


class LTCustomerPortalFile(Document):
    def validate(self):
        if not self.purpose:
            self.purpose = "Reference"
        self.visible_to_customer = 1 if self.visible_to_customer else 0
        self.uploaded_by_customer = 1 if self.uploaded_by_customer else 0
