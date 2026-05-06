"""Verify outbound document registry and templates."""
from __future__ import annotations

from frappe.utils import now_datetime


def run() -> dict[str, object]:
    from locally_twisted.outbound_documents.registry import validate_registry

    result = validate_registry()
    evidence = result.setdefault("evidence", {})
    if isinstance(evidence, dict):
        evidence["generated_at"] = now_datetime().isoformat()
    return result
