"""Live/source-backed product-page architecture contract verifier."""

from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis
from locally_twisted.catalog_contract.product_page_architecture_contract import (
    build_product_page_architecture_report,
)
from locally_twisted.product_options import get_product_page_architecture_context
from locally_twisted.verify.product_pattern_contract_report import run as product_pattern_report


def run(source_catalog_path: str | None = None) -> dict[str, Any]:
    """Return a read-only backend-driven product-page architecture report."""

    try:
        pattern = product_pattern_report(source_catalog_path=source_catalog_path)
        architecture = build_product_page_architecture_report(
            pattern.get("products") or (),
            metadata={
                "source": "locally_twisted.verify.product_pattern_contract_report",
                "pattern_report_ok": pattern.get("ok"),
                "generated_from": pattern.get("schema_version"),
                "published_website_item_count": pattern.get("published_website_item_count"),
            },
        )
        dependency_failures = []
        live_projection_failures = _live_projection_failures(pattern.get("products") or ())
        if pattern.get("ok") is not True:
            dependency_failures.extend(str(value) for value in pattern.get("failures") or ["pattern report not ok"])
        failures = [
            *dependency_failures,
            *(architecture.get("failures") or []),
            *live_projection_failures,
        ]
        architecture["ok"] = not failures
        architecture["dependency_failures"] = dependency_failures
        architecture["live_projection_failures"] = live_projection_failures
        architecture["failures"] = failures
        architecture["product_pattern_summary"] = pattern.get("summary") or {}
        architecture["line_field_status"] = pattern.get("line_field_status") or {}
        return architecture
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}


def _live_projection_failures(products: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> list[str]:
    failures: list[str] = []
    for row in products:
        item_code = str(row.get("item_code") or row.get("slug") or "").strip()
        if not item_code:
            continue
        expected_axes = {
            str(axis.get("name") or "").strip(): axis
            for axis in row.get("axis_contracts") or []
            if axis.get("name")
        }
        try:
            live = get_product_page_architecture_context(item_code)
        except Exception as exc:
            failures.append(f"{item_code}: live projection failed: {exc}")
            continue
        for control in live.get("controls") or []:
            axis_name = str(control.get("axis_name") or "").strip()
            source = str(control.get("source") or "").strip()
            if not axis_name or source not in {"combined", "erpnext_variant"}:
                continue
            if not is_balloon_color_axis(axis_name):
                continue
            expected_axis = expected_axes.get(axis_name)
            expected_role = str((expected_axis or {}).get("role") or "sale_unit").strip()
            expected_payload = _expected_payload_target(axis_name, expected_role)
            if str(control.get("role") or "").strip() != expected_role:
                failures.append(
                    f"{item_code}: live {axis_name} role {control.get('role')} != source/backend {expected_role}"
                )
            if expected_payload and str(control.get("payload_target") or "").strip() != expected_payload:
                failures.append(
                    f"{item_code}: live {axis_name} payload {control.get('payload_target')} != {expected_payload}"
                )
    return failures


def _expected_payload_target(axis_name: str, role: str) -> str:
    if role == "sale_unit":
        return "selected_options"
    if role == "customization" and is_balloon_color_axis(axis_name):
        return "color_recipes"
    if role == "customization":
        return "customizations"
    if role in {"add_on", "review_only"}:
        return ""
    return "quote_context"
