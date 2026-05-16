"""Employee-authored product blueprint controller."""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime

from locally_twisted.product_blueprint_apply_plan import build_apply_plan_doc
from locally_twisted.product_blueprint_local_apply import (
    LOCAL_APPLY_CONFIRMATION,
    ProductBlueprintApplyError,
    apply_blueprint_locally,
    build_local_apply_preview,
)
from locally_twisted.product_blueprint_validation import validate_blueprint_doc


class LTProductBlueprint(Document):
    def validate(self):
        result = validate_blueprint_doc(self)

        for row, normalized in zip(self.option_rows or [], result["contract"]["option_rows"]):
            row.payload_target = normalized.get("payload_target")
        for row, normalized in zip(self.add_on_rows or [], result["contract"]["add_on_rows"]):
            row.payload_target = normalized.get("payload_target")

        self.validation_status = result["validation_status"]
        self.validation_summary = result["summary"]
        self.validation_json = json.dumps(result, indent=2, sort_keys=True)
        self.apply_plan_json = json.dumps(build_apply_plan_doc(self), indent=2, sort_keys=True)
        self.last_validated_on = now_datetime()
        self.ready_for_live = 0

        if result["save_blockers"]:
            frappe.throw("<br>".join(result["save_blockers"]))


@frappe.whitelist()
def get_local_apply_preview(name: str) -> dict:
    """Return no-write apply preview details for the Desk form."""
    _require_product_setup_user()
    doc = frappe.get_doc("LT Product Blueprint", name)
    doc.check_permission("read")
    return build_local_apply_preview(_doc_to_validation_payload(doc))


@frappe.whitelist()
def apply_locally_from_desk(name: str) -> dict:
    """Apply a blueprint to local ERPNext records from Desk, behind hard guards."""
    _require_local_apply_enabled()
    _require_product_setup_user()
    doc = frappe.get_doc("LT Product Blueprint", name)
    doc.check_permission("write")
    try:
        return apply_blueprint_locally(
            doc,
            allow_writes=True,
            confirmation=LOCAL_APPLY_CONFIRMATION,
        )
    except ProductBlueprintApplyError as exc:
        frappe.throw(_(str(exc)))


def _require_product_setup_user() -> None:
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please sign in before applying product setup records."), frappe.PermissionError)
    roles = set(frappe.get_roles(user))
    if not roles.intersection({"System Manager", "Item Manager"}):
        frappe.throw(
            _("Only System Manager or Item Manager users can apply product setup records."),
            frappe.PermissionError,
        )


def _require_local_apply_enabled() -> None:
    if not _truthy(frappe.conf.get("lt_allow_local_blueprint_apply")):
        frappe.throw(
            _(
                "Local product apply is disabled for this site. "
                "Enable lt_allow_local_blueprint_apply only on a local or test site."
            )
        )


def _doc_to_validation_payload(doc) -> dict:
    # Reuse the controller conversion indirectly without importing private state
    # into the Desk method response.
    return {
        "product_name": doc.product_name,
        "product_slug": doc.product_slug,
        "item_group": doc.item_group,
        "page_template": doc.page_template,
        "buying_path": doc.buying_path,
        "publish_status": doc.publish_status,
        "base_price": doc.base_price,
        "option_rows": [row.as_dict() for row in doc.option_rows or []],
        "color_recipe_rows": [row.as_dict() for row in doc.color_recipe_rows or []],
        "add_on_rows": [row.as_dict() for row in doc.add_on_rows or []],
        "conditional_price_rows": [row.as_dict() for row in doc.conditional_price_rows or []],
        "media_rule_rows": [row.as_dict() for row in doc.media_rule_rows or []],
    }


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
