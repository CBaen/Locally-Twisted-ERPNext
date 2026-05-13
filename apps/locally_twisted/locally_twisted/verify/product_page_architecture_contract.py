"""Live/source-backed product-page architecture contract verifier."""

from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.catalog_contract.product_page_architecture_contract import (
    build_product_page_architecture_report,
)
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
        if pattern.get("ok") is not True:
            dependency_failures.extend(str(value) for value in pattern.get("failures") or ["pattern report not ok"])
        failures = [*dependency_failures, *(architecture.get("failures") or [])]
        architecture["ok"] = not failures
        architecture["dependency_failures"] = dependency_failures
        architecture["failures"] = failures
        architecture["product_pattern_summary"] = pattern.get("summary") or {}
        architecture["line_field_status"] = pattern.get("line_field_status") or {}
        return architecture
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
