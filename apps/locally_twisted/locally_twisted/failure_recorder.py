"""Reusable record-level evidence for LT backend partial failures."""
from __future__ import annotations

import json
from html import unescape
from typing import Any

import frappe
from frappe.utils import escape_html, now_datetime


FAILURE_COMMENT_PREFIX = "LT_BACKEND_FAILURE"
RESOLUTION_COMMENT_PREFIX = "LT_BACKEND_RESOLVED"
SCHEMA_VERSION = 1


def record_backend_failure(
    *,
    surface: str,
    step: str,
    severity: str,
    primary_doctype: str,
    primary_name: str,
    customer_visible_impact: str,
    internal_next_action: str,
    exception: Exception | str | None = None,
    linked_doctype: str | None = None,
    linked_name: str | None = None,
    grouping_key: str | None = None,
) -> dict[str, Any]:
    """Write durable evidence for a backend partial failure.

    The primary business operation may still continue, but the affected record
    and the Error Log must show what needs operator attention.
    """
    payload = _payload(
        surface=surface,
        step=step,
        severity=severity,
        primary_doctype=primary_doctype,
        primary_name=primary_name,
        customer_visible_impact=customer_visible_impact,
        internal_next_action=internal_next_action,
        exception=exception,
        linked_doctype=linked_doctype,
        linked_name=linked_name,
        grouping_key=grouping_key,
    )

    errors: list[str] = []
    error_log_name = None
    comment_name = None

    try:
        error_log_name = _write_error_log(payload)
    except Exception as exc:  # pragma: no cover - reported in return payload
        errors.append(f"Error Log write failed: {type(exc).__name__}: {exc}")

    try:
        if primary_doctype and primary_name and frappe.db.exists(primary_doctype, primary_name):
            comment_name = _write_record_comment(payload)
        else:
            errors.append(f"Primary record not found: {primary_doctype}:{primary_name}")
    except Exception as exc:  # pragma: no cover - reported in return payload
        errors.append(f"record Comment write failed: {type(exc).__name__}: {exc}")

    if errors:
        try:
            frappe.log_error(
                title="LT backend failure recorder failed",
                message=json.dumps({"payload": payload, "errors": errors}, indent=2, default=str),
            )
        except Exception:
            pass

    return {
        "ok": not errors,
        "schema_version": SCHEMA_VERSION,
        "primary": f"{primary_doctype}:{primary_name}",
        "error_log": error_log_name,
        "comment": comment_name,
        "errors": errors,
        "payload": payload,
    }


def record_health_failures(
    *,
    primary_doctype: str | None = None,
    primary_name: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return recent record-level failure comments with exact record IDs."""
    requested_limit = int(limit or 100)
    if requested_limit <= 0:
        return []
    page_length = max(requested_limit * 4, 100)
    filters: dict[str, Any] = {
        "content": ("like", f"%{FAILURE_COMMENT_PREFIX}%"),
    }
    if primary_doctype:
        filters["reference_doctype"] = primary_doctype
    if primary_name:
        filters["reference_name"] = primary_name

    resolved_at_by_key = _resolved_grouping_keys(
        primary_doctype=primary_doctype,
        primary_name=primary_name,
        limit=max(page_length * 4, requested_limit * 8),
    )

    failures = []
    start = 0
    while len(failures) < requested_limit:
        rows = frappe.get_all(
            "Comment",
            filters=filters,
            fields=["name", "reference_doctype", "reference_name", "content", "creation"],
            order_by="creation desc",
            start=start,
            page_length=page_length,
        )
        if not rows:
            break
        for row in rows:
            payload = _payload_from_comment(row.get("content") or "")
            if not payload:
                continue
            grouping_key = payload.get("grouping_key")
            if grouping_key and _is_resolved(row.get("creation"), resolved_at_by_key.get(grouping_key)):
                continue
            failures.append(
                {
                    "comment": row.get("name"),
                    "primary_doctype": payload.get("primary_doctype") or row.get("reference_doctype"),
                    "primary_name": payload.get("primary_name") or row.get("reference_name"),
                    "linked_doctype": payload.get("linked_doctype"),
                    "linked_name": payload.get("linked_name"),
                    "surface": payload.get("surface"),
                    "step": payload.get("step"),
                    "severity": payload.get("severity"),
                    "customer_visible_impact": payload.get("customer_visible_impact"),
                    "internal_next_action": payload.get("internal_next_action"),
                    "grouping_key": payload.get("grouping_key"),
                    "created": str(row.get("creation")),
                }
            )
            if len(failures) >= requested_limit:
                break
        start += len(rows)
        if len(rows) < page_length:
            break
    return failures


def record_backend_failure_resolution(
    *,
    primary_doctype: str,
    primary_name: str,
    grouping_key: str | None = None,
    surface: str | None = None,
    step: str | None = None,
    resolved_by: str = "Codex",
    resolution_note: str = "Reviewed and resolved.",
    commit: bool = False,
) -> dict[str, Any]:
    """Record that a specific backend failure grouping key has been resolved."""
    if not frappe.db.exists(primary_doctype, primary_name):
        raise ValueError(f"Primary record not found: {primary_doctype}:{primary_name}")

    resolved_key = grouping_key or f"{surface}:{step}:{primary_doctype}:{primary_name}"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": now_datetime().isoformat(),
        "primary_doctype": primary_doctype,
        "primary_name": primary_name,
        "surface": surface,
        "step": step,
        "grouping_key": resolved_key,
        "resolved_by": resolved_by,
        "resolution_note": resolution_note,
    }
    comment = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": primary_doctype,
            "reference_name": primary_name,
            "content": _resolution_comment_content(payload),
        }
    )
    # Permission bypass is guarded to write system resolution evidence onto the affected record.
    comment.insert(ignore_permissions=True)
    if commit:
        frappe.db.commit()
    return {
        "ok": True,
        "comment": comment.name,
        "grouping_key": resolved_key,
        "primary": f"{primary_doctype}:{primary_name}",
    }


def _payload(
    *,
    surface: str,
    step: str,
    severity: str,
    primary_doctype: str,
    primary_name: str,
    customer_visible_impact: str,
    internal_next_action: str,
    exception: Exception | str | None,
    linked_doctype: str | None,
    linked_name: str | None,
    grouping_key: str | None,
) -> dict[str, Any]:
    error_summary = None
    if exception is not None:
        if isinstance(exception, Exception):
            error_summary = f"{type(exception).__name__}: {exception}"
        else:
            error_summary = str(exception)

    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": now_datetime().isoformat(),
        "surface": surface,
        "step": step,
        "severity": severity,
        "primary_doctype": primary_doctype,
        "primary_name": primary_name,
        "linked_doctype": linked_doctype,
        "linked_name": linked_name,
        "customer_visible_impact": customer_visible_impact,
        "internal_next_action": internal_next_action,
        "error_summary": error_summary,
        "grouping_key": grouping_key or f"{surface}:{step}:{primary_doctype}:{primary_name}",
    }


def _write_error_log(payload: dict[str, Any]) -> str | None:
    title = (
        f"LT backend failure: {payload['surface']} / {payload['step']} "
        f"on {payload['primary_doctype']} {payload['primary_name']}"
    )
    return frappe.log_error(
        title=title[:140],
        message=json.dumps(payload, indent=2, default=str),
    )


def _write_record_comment(payload: dict[str, Any]) -> str:
    content = _comment_content(payload)
    comment = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": payload["primary_doctype"],
            "reference_name": payload["primary_name"],
            "content": content,
        }
    )
    # Permission bypass is guarded to write system failure evidence onto the affected record.
    comment.insert(ignore_permissions=True)
    return comment.name


def _comment_content(payload: dict[str, Any]) -> str:
    json_payload = json.dumps(payload, sort_keys=True, default=str)
    return f"{FAILURE_COMMENT_PREFIX}\n<pre>{escape_html(json_payload)}</pre>"


def _resolution_comment_content(payload: dict[str, Any]) -> str:
    json_payload = json.dumps(payload, sort_keys=True, default=str)
    return f"{RESOLUTION_COMMENT_PREFIX}\n<pre>{escape_html(json_payload)}</pre>"


def _payload_from_comment(content: str) -> dict[str, Any] | None:
    if FAILURE_COMMENT_PREFIX not in content:
        return None
    start = content.find("<pre>")
    end = content.find("</pre>", start)
    if start == -1 or end == -1:
        return None
    raw = unescape(content[start + len("<pre>") : end])
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        return None
    return payload


def _payload_from_resolution_comment(content: str) -> dict[str, Any] | None:
    if RESOLUTION_COMMENT_PREFIX not in content:
        return None
    start = content.find("<pre>")
    end = content.find("</pre>", start)
    if start == -1 or end == -1:
        return None
    raw = unescape(content[start + len("<pre>") : end])
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        return None
    return payload


def _resolved_grouping_keys(
    *,
    primary_doctype: str | None,
    primary_name: str | None,
    limit: int,
) -> dict[str, Any]:
    filters: dict[str, Any] = {
        "content": ("like", f"%{RESOLUTION_COMMENT_PREFIX}%"),
    }
    if primary_doctype:
        filters["reference_doctype"] = primary_doctype
    if primary_name:
        filters["reference_name"] = primary_name

    rows = frappe.get_all(
        "Comment",
        filters=filters,
        fields=["name", "reference_doctype", "reference_name", "content", "creation"],
        order_by="creation desc",
        limit=limit,
    )

    resolved_at_by_key: dict[str, Any] = {}
    for row in rows:
        payload = _payload_from_resolution_comment(row.get("content") or "")
        grouping_key = payload.get("grouping_key") if payload else None
        if not grouping_key:
            continue
        current = resolved_at_by_key.get(grouping_key)
        created = row.get("creation")
        if current is None or created > current:
            resolved_at_by_key[grouping_key] = created
    return resolved_at_by_key


def _is_resolved(failure_created: Any, resolved_created: Any) -> bool:
    return resolved_created is not None and failure_created is not None and resolved_created >= failure_created
