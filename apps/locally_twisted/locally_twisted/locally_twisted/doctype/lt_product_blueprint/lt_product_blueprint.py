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

CATALOG_READINESS_FIELDS = [
    "name",
    "product_name",
    "product_slug",
    "target_item_code",
    "target_website_item",
    "publish_status",
    "validation_status",
    "validation_json",
    "modified",
]

READ_ONLY_FALSE_APPROVALS = {
    "local_apply_approved": False,
    "staging_apply_approved": False,
    "live_apply_approved": False,
    "mutation_approved": False,
    "cache_clear_approved": False,
    "deploy_approved": False,
    "provider_approved": False,
    "payment_approved": False,
    "customer_message_approved": False,
}


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
    _require_product_setup_user("preview product setup records")
    doc = frappe.get_doc("LT Product Blueprint", name)
    doc.check_permission("read")
    return build_local_apply_preview(_doc_to_validation_payload(doc))


@frappe.whitelist()
def get_catalog_readiness_summary() -> dict:
    """Return a read-only catalog readiness summary from saved validation JSON."""
    _require_product_setup_user("view product setup readiness")
    rows = frappe.get_all(
        "LT Product Blueprint",
        fields=CATALOG_READINESS_FIELDS,
        order_by="modified desc, name asc",
        limit_page_length=0,
    )
    product_rows = [_catalog_readiness_row(row) for row in rows]
    counts_by_owner_state = {}
    blocked_count = 0
    public_success_claim_allowed_count = 0
    live_apply_allowed_count = 0

    for row in product_rows:
        state = row["owner_state"]
        counts_by_owner_state[state] = counts_by_owner_state.get(state, 0) + 1
        if row["is_blocked"]:
            blocked_count += 1
        if row["public_success_claim_allowed"]:
            public_success_claim_allowed_count += 1
        if row["live_apply_allowed"]:
            live_apply_allowed_count += 1

    return {
        "proof_mode": "source_saved_validation_only",
        "source": "saved_validation_json",
        "doctype": "LT Product Blueprint",
        "total_products": len(product_rows),
        "counts_by_owner_state": dict(sorted(counts_by_owner_state.items())),
        "blocked_count": blocked_count,
        "public_success_claim_allowed_count": public_success_claim_allowed_count,
        "live_apply_allowed_count": live_apply_allowed_count,
        "approvals": dict(READ_ONLY_FALSE_APPROVALS),
        "rows": product_rows,
    }


@frappe.whitelist()
def apply_locally_from_desk(name: str) -> dict:
    """Apply a blueprint to local ERPNext records from Desk, behind hard guards."""
    _require_local_apply_enabled()
    _require_product_setup_user("apply product setup records")
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


def _require_product_setup_user(action: str) -> None:
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Please sign in before you {0}.").format(action), frappe.PermissionError)
    roles = set(frappe.get_roles(user))
    if not roles.intersection({"System Manager", "Item Manager"}):
        frappe.throw(
            _("Only System Manager or Item Manager users can {0}.").format(action),
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


def _catalog_readiness_row(row) -> dict:
    validation, parse_error = _parse_validation_json(row.get("validation_json"))
    readiness = validation.get("owner_publish_readiness") or {}
    approvals = validation.get("publish_apply_approval") or {}
    blockers = _clipped_blockers(
        [
            *_list_text(validation.get("blockers")),
            *_list_text(validation.get("save_blockers")),
        ]
    )
    if parse_error:
        blockers = ["Saved validation JSON could not be read.", *blockers]

    owner_state = _text(readiness.get("state")) or _text(row.get("validation_status")) or "Not checked"
    next_owner_step = _text(readiness.get("next_owner_step")) or "Review the saved Product Setup readiness before taking action."
    public_success_claim_allowed = readiness.get("public_success_claim_allowed") is True
    live_apply_allowed = readiness.get("publish_apply_allowed") is True or approvals.get("live_apply_approved") is True
    is_blocked = (
        parse_error
        or _text(row.get("validation_status")) == BLOCKED
        or owner_state == "Blocked - Proof Needed"
        or bool(blockers)
    )
    if parse_error:
        next_developer_step = "Re-save this Product Setup so validation JSON can be regenerated."
    elif is_blocked:
        next_developer_step = "Resolve the saved Product Setup blockers before requesting release proof."
    else:
        next_developer_step = "No developer action is approved from this saved source summary."

    return {
        "name": _text(row.get("name")),
        "product_name": _text(row.get("product_name")),
        "product_slug": _text(row.get("product_slug")),
        "target_item_code": _text(row.get("target_item_code")),
        "target_website_item": _text(row.get("target_website_item")),
        "publish_status": _text(row.get("publish_status")),
        "validation_status": _text(row.get("validation_status")),
        "modified": _text(row.get("modified")),
        "evidence_source": "LT Product Blueprint.validation_json",
        "validation_modified_on": _text(row.get("modified")),
        "proof_mode": "source_saved_validation_only",
        "owner_state": owner_state,
        "next_owner_step": next_owner_step,
        "next_developer_step": next_developer_step,
        "developer_help_needed": bool(is_blocked),
        "is_blocked": is_blocked,
        "parse_error": parse_error,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "public_success_claim_allowed": public_success_claim_allowed,
        "live_apply_allowed": live_apply_allowed,
        "approvals": dict(READ_ONLY_FALSE_APPROVALS),
    }


def _parse_validation_json(raw) -> tuple[dict, bool]:
    if not raw:
        return {}, False
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}, True
    if not isinstance(parsed, dict):
        return {}, True
    return parsed, False


def _list_text(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(row) for row in value if _text(row)]


def _clipped_blockers(blockers: list[str], limit: int = 8, max_chars: int = 180) -> list[str]:
    clipped = []
    for blocker in blockers[:limit]:
        clipped.append(blocker if len(blocker) <= max_chars else f"{blocker[: max_chars - 3]}...")
    return clipped


def _truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _text(value) -> str:
    return str(value or "").strip()
