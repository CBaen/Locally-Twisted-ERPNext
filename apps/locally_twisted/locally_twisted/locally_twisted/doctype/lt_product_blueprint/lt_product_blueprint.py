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
from locally_twisted.product_blueprint_runtime_authority import runtime_authority_save_blockers
from locally_twisted.product_blueprint_validation import BLOCKED, validate_blueprint_doc
from locally_twisted.product_setup_runtime import ACTIVE_SETUP_STATUSES


class LTProductBlueprint(Document):
    def validate(self):
        result = validate_blueprint_doc(self)
        active_uniqueness_blockers = _active_uniqueness_save_blockers(self)
        runtime_authority_blockers = runtime_authority_save_blockers(self)
        authority_blockers = [*active_uniqueness_blockers, *runtime_authority_blockers]
        if authority_blockers:
            result["ok"] = False
            result["validation_status"] = BLOCKED
            result["blockers"].extend(authority_blockers)
            result["save_blockers"].extend(authority_blockers)
            result["summary"] = (
                "Blocked: active Product Setup authority must be safe before preview, "
                "staging, live approval, or local apply."
            )

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


def _active_uniqueness_save_blockers(doc: Document) -> list[str]:
    if _text(getattr(doc, "publish_status", "")) not in ACTIVE_SETUP_STATUSES:
        return []
    operating_brand = _text(getattr(doc, "operating_brand", ""))
    if not operating_brand:
        return []

    or_filters = []
    for fieldname in ("product_slug", "target_item_code", "target_website_item"):
        value = _text(getattr(doc, fieldname, ""))
        if value:
            or_filters.append([fieldname, "=", value])
    if not or_filters:
        return []

    rows = frappe.get_all(
        "LT Product Blueprint",
        filters={
            "operating_brand": operating_brand,
            "publish_status": ["in", sorted(ACTIVE_SETUP_STATUSES)],
        },
        or_filters=or_filters,
        fields=["name", "product_slug", "target_item_code", "target_website_item", "publish_status"],
        order_by="modified desc",
        limit_page_length=10,
    )
    conflicts = [row for row in rows if _text(row.get("name")) != _text(getattr(doc, "name", ""))]
    if not conflicts:
        return []

    labels = ", ".join(
        f"{row.get('name')} ({row.get('publish_status')})"
        for row in conflicts[:5]
        if row.get("name")
    )
    return [
        "Active Product Setup authority conflict for operating brand "
        f"{operating_brand}: {labels or 'another active Product Setup'}. "
        "Only one active Product Setup may target the same slug, Item, or Website Item per operating brand."
    ]


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
        "operating_brand": doc.operating_brand,
        "item_group": doc.item_group,
        "page_template": doc.page_template,
        "buying_path": doc.buying_path,
        "publish_status": doc.publish_status,
        "shop_visibility": doc.shop_visibility,
        "base_price": doc.base_price,
        "target_item_code": doc.target_item_code,
        "target_website_item": doc.target_website_item,
        "price_rows": [row.as_dict() for row in doc.price_rows or []],
        "product_summary": doc.product_summary,
        "product_story": doc.product_story,
        "product_details": doc.product_details,
        "primary_image": doc.primary_image,
        "gallery_image_rows": [row.as_dict() for row in doc.gallery_image_rows or []],
        "option_rows": [row.as_dict() for row in doc.option_rows or []],
        "color_recipe_rows": [row.as_dict() for row in doc.color_recipe_rows or []],
        "add_on_rows": [row.as_dict() for row in doc.add_on_rows or []],
        "conditional_price_rows": [row.as_dict() for row in doc.conditional_price_rows or []],
        "media_rule_rows": [row.as_dict() for row in doc.media_rule_rows or []],
        "content_rule_rows": [row.as_dict() for row in doc.content_rule_rows or []],
    }


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _text(value) -> str:
    return str(value or "").strip()
