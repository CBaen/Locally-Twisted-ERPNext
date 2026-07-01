"""Pure Product Setup catalog readiness summary builder."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


BLOCKED = "Blocked"
PROOF_MODE = "source_saved_validation_only"
SUMMARY_SOURCE = "saved_validation_json"
EVIDENCE_SOURCE = "LT Product Blueprint.validation_json"

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
    "public_success_claim_allowed": False,
}


def build_catalog_readiness_summary(rows: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Build a source-only catalog readiness summary from Product Setup rows."""
    product_rows = [build_catalog_readiness_row(row) for row in rows]
    counts_by_owner_state: dict[str, int] = {}
    blocked_count = 0

    for row in product_rows:
        state = row["owner_state"]
        counts_by_owner_state[state] = counts_by_owner_state.get(state, 0) + 1
        if row["is_blocked"]:
            blocked_count += 1

    return {
        "proof_mode": PROOF_MODE,
        "source": SUMMARY_SOURCE,
        "doctype": "LT Product Blueprint",
        "total_products": len(product_rows),
        "counts_by_owner_state": dict(sorted(counts_by_owner_state.items())),
        "blocked_count": blocked_count,
        "public_success_claim_allowed_count": 0,
        "live_apply_allowed_count": 0,
        "approvals": false_approvals(),
        "rows": product_rows,
    }


def build_catalog_readiness_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Build one Desk summary row from a row-like mapping."""
    validation, parse_error, missing_validation_json = _parse_validation_json(row.get("validation_json"))
    readiness = _mapping(validation.get("owner_publish_readiness"))
    approvals = _mapping(validation.get("publish_apply_approval"))
    blockers = _clipped_blockers(
        [
            *_list_text(validation.get("blockers")),
            *_list_text(validation.get("save_blockers")),
        ]
    )
    unsafe_claims = _unsafe_source_approval_claims(readiness, approvals)
    if parse_error:
        blockers = ["Saved validation JSON could not be read.", *blockers]
    elif missing_validation_json:
        blockers = ["Saved validation JSON is missing; re-save this Product Setup before claiming proof.", *blockers]
    elif unsafe_claims:
        blockers = [
            "Saved validation JSON included source-only approval claims; release proof is still required.",
            *blockers,
        ]

    if parse_error or missing_validation_json or unsafe_claims:
        owner_state = "Blocked - Proof Needed"
    else:
        owner_state = _text(readiness.get("state")) or _text(row.get("validation_status")) or "Not checked"
    next_owner_step = (
        _text(readiness.get("next_owner_step"))
        or "Review the saved Product Setup readiness before taking action."
    )
    is_blocked = (
        parse_error
        or missing_validation_json
        or unsafe_claims
        or _text(row.get("validation_status")) == BLOCKED
        or owner_state == "Blocked - Proof Needed"
        or bool(blockers)
    )
    if parse_error or missing_validation_json:
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
        "evidence_source": EVIDENCE_SOURCE,
        "validation_modified_on": _text(row.get("modified")),
        "proof_mode": PROOF_MODE,
        "owner_state": owner_state,
        "next_owner_step": next_owner_step,
        "next_developer_step": next_developer_step,
        "developer_help_needed": bool(is_blocked),
        "is_blocked": is_blocked,
        "parse_error": parse_error,
        "missing_validation_json": missing_validation_json,
        "unsafe_source_approval_claims": unsafe_claims,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "public_success_claim_allowed": False,
        "live_apply_allowed": False,
        "approvals": false_approvals(),
    }


def false_approvals() -> dict[str, bool]:
    """Return a fresh false approval map so callers cannot mutate the constant."""
    return dict(READ_ONLY_FALSE_APPROVALS)


def _parse_validation_json(raw: Any) -> tuple[dict[str, Any], bool, bool]:
    if raw in (None, ""):
        return {}, False, True
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {}, True, False
    if not isinstance(parsed, dict):
        return {}, True, False
    return parsed, False, False


def _mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    return {}


def _unsafe_source_approval_claims(readiness: Mapping[str, Any], approvals: Mapping[str, Any]) -> bool:
    unsafe_readiness_flags = (
        "public_success_claim_allowed",
        "publish_apply_allowed",
    )
    unsafe_approval_flags = (
        "local_apply_approved",
        "staging_apply_approved",
        "live_apply_approved",
        "mutation_approved",
        "cache_clear_approved",
        "deploy_approved",
        "provider_approved",
        "payment_approved",
        "customer_message_approved",
        "public_success_claim_allowed",
    )
    return any(readiness.get(flag) is True for flag in unsafe_readiness_flags) or any(
        approvals.get(flag) is True for flag in unsafe_approval_flags
    )


def _list_text(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(row) for row in value if _text(row)]


def _clipped_blockers(blockers: list[str], limit: int = 8, max_chars: int = 180) -> list[str]:
    clipped = []
    for blocker in blockers[:limit]:
        clipped.append(blocker if len(blocker) <= max_chars else f"{blocker[: max_chars - 3]}...")
    return clipped


def _text(value: Any) -> str:
    return str(value or "").strip()
