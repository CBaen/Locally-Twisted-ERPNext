from frappe.model.document import Document


class LTOrganizationPortalMembership(Document):
    def validate(self):
        self.enabled = 1 if self.enabled else 0
        if not self.organization_role:
            self.organization_role = "Event Coordinator"
