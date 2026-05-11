from frappe.model.document import Document


class LTCustomerChecklistResponse(Document):
    def validate(self):
        self.completed = 1 if self.completed else 0
