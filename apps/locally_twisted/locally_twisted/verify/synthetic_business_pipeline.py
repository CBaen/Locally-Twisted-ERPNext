"""Synthetic backend pipeline audit for fake-data launch hardening.

This verifier is deliberately separated from live cutover readiness. It runs
fake-data and rollback-safe contracts that expose broken cascading data and
missing pipe connections without requiring live Stripe keys or real customer
records.
"""
from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime


SYNTHETIC_CONTRACTS = (
    {
        "id": "stripe_amount_parity",
        "lane": "money",
        "runner": "locally_twisted.verify.stripe_amount_parity_contract.run",
        "command": "python scripts/verify/stripe_amount_parity_contract.py",
        "data_mode": "in_memory_fake_order",
        "creates": [],
        "cleanup": "no database records created",
    },
    {
        "id": "checkout_lead_conversion",
        "lane": "money",
        "runner": "locally_twisted.verify.checkout_lead_conversion_contract.run",
        "command": "python scripts/verify/checkout_lead_conversion_contract.py",
        "data_mode": "rollback_fake_guest_checkout",
        "creates": ["Lead", "Contact", "Customer", "Sales Order", "Payment Request", "Task"],
        "cleanup": "intercepts commits and rolls back generated records",
    },
    {
        "id": "checkout_fulfillment",
        "lane": "money",
        "runner": "locally_twisted.verify.checkout_fulfillment_contract.run",
        "command": "python scripts/verify/checkout_fulfillment_contract.py",
        "data_mode": "rollback_fake_fulfillment_checkout",
        "creates": ["Customer", "Contact", "Address", "Sales Order", "Payment Request"],
        "cleanup": "stubs Stripe session creation, intercepts commits, and rolls back generated records",
    },
    {
        "id": "payment_success_paid_order_cascade",
        "lane": "money",
        "runner": "locally_twisted.verify.payment_cascade_contract.run",
        "command": "python scripts/verify/payment_cascade_contract.py",
        "data_mode": "rollback_fake_paid_order",
        "creates": [
            "Customer",
            "Contact",
            "Address",
            "Sales Order",
            "Payment Request",
            "Payment Entry",
            "Sales Invoice",
            "Email Queue",
        ],
        "cleanup": "intercepts commits and rolls back generated records",
    },
    {
        "id": "stripe_webhook_reconciliation",
        "lane": "money",
        "runner": "locally_twisted.verify.payment_webhook_contract.run",
        "command": "python scripts/verify/payment_webhook_contract.py",
        "data_mode": "mocked_stripe_event",
        "creates": [],
        "cleanup": "no Stripe call; request/signature parsing is mocked",
    },
    {
        "id": "customer_document_policy",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.customer_documents_contract.run",
        "command": "python scripts/verify/customer_documents_contract.py",
        "data_mode": "rollback_fake_lead_acknowledgment",
        "creates": ["Lead", "Communication", "Email Queue"],
        "cleanup": "intercepts commits and rolls back generated records",
    },
    {
        "id": "outbound_document_templates",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.outbound_documents_contract.run",
        "command": "python scripts/verify/outbound_documents_contract.py",
        "data_mode": "template_registry_contract",
        "creates": [],
        "cleanup": "no database records created",
    },
    {
        "id": "unpaid_invoice_draft_packet_outliers",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.unpaid_invoice_draft_packet_contract.run",
        "command": "python scripts/verify/unpaid_invoice_draft_packet_contract.py",
        "data_mode": "in_memory_fake_unpaid_invoice_scenarios",
        "creates": [],
        "cleanup": "uses in-memory fake review payloads only",
    },
)

GUARD_DOCTYPES = (
    "Lead",
    "Contact",
    "Customer",
    "Address",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Task",
    "Email Queue",
    "Communication",
    "Error Log",
)


def run() -> dict[str, object]:
    """Run the synthetic audit and return JSON-safe, fail-loud evidence."""
    from locally_twisted.paperwork import paperwork_review_digest
    from locally_twisted.verify import business_automation_index, paperwork_status

    before = _guard_counts()
    failures: list[str] = []

    contract_items = [_run_contract(spec) for spec in SYNTHETIC_CONTRACTS]
    broken_piping = [item for item in contract_items if not item["ok"]]

    status = paperwork_status.run()
    automation = business_automation_index.run(include_digest=False, include_synthetic=False)
    digest = paperwork_review_digest.run()

    after = _guard_counts()
    if before != after:
        failures.append("synthetic audit changed guarded document counts")
    if status.get("ok") is not True:
        failures.extend(f"paperwork_status: {failure}" for failure in status.get("failures") or ["not ok"])
    if automation.get("ok") is not True:
        failures.extend(f"business_automation_index: {failure}" for failure in automation.get("failures") or ["not ok"])
    if digest.get("ok") is not True:
        failures.extend(f"paperwork_review_digest: {failure}" for failure in digest.get("failures") or ["not ok"])

    failures.extend(
        f"{item['id']}: {failure}"
        for item in broken_piping
        for failure in item.get("failures") or ["contract returned not ok"]
    )

    sections = {
        "synthetic_operating_readiness": _section(
            "synthetic_operating_readiness",
            "Synthetic operating readiness",
            contract_items,
        ),
        "broken_piping": _section(
            "broken_piping",
            "Broken piping",
            broken_piping,
        ),
        "inefficiencies": _section(
            "inefficiencies",
            "Inefficiencies and partial connections",
            _inefficiency_items(status, automation),
        ),
        "cutover_deferred_not_blocking": _section(
            "cutover_deferred_not_blocking",
            "Cutover deferred, not blocking synthetic readiness",
            _cutover_items(status),
        ),
    }

    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "synthetic_only": True,
        "live_inputs_required": False,
        "uses_real_customer_data": False,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "persistent_mutation_allowed": False,
        "source_surfaces": [
            "business_automation_index",
            "paperwork_status",
            "paperwork_review_digest",
            *[str(spec["runner"]) for spec in SYNTHETIC_CONTRACTS],
        ],
        "summary": {
            "synthetic_contract_count": len(contract_items),
            "synthetic_contract_pass_count": sum(1 for item in contract_items if item["ok"]),
            "broken_piping_count": len(broken_piping),
            "inefficiency_count": sections["inefficiencies"]["count"],
            "cutover_deferred_count": sections["cutover_deferred_not_blocking"]["count"],
        },
        "sections": sections,
        "mutation_guard": {
            "guarded_doctypes": list(GUARD_DOCTYPES),
            "before": before,
            "after": after,
            "changed": before != after,
        },
        "boundaries": {
            "live_stripe_keys_required": False,
            "live_customer_records_required": False,
            "real_user_information_required": False,
            "no_live_stripe_checkout": True,
            "no_customer_send": True,
            "no_persisted_fake_records": True,
            "live_cutover_is_separate": True,
        },
        "failures": failures,
    }


def _run_contract(spec: dict[str, Any]) -> dict[str, Any]:
    try:
        result = frappe.get_attr(str(spec["runner"]))()
    except Exception:
        result = {"ok": False, "failures": [frappe.get_traceback()]}

    failures = list(result.get("failures") or [])
    return {
        "id": spec["id"],
        "lane": spec["lane"],
        "ok": bool(result.get("ok")),
        "command": spec["command"],
        "data_mode": spec["data_mode"],
        "live_inputs_required": False,
        "uses_real_customer_data": False,
        "creates": spec["creates"],
        "cleanup": spec["cleanup"],
        "failures": failures,
        "evidence": _evidence_summary(result),
    }


def _section(section_id: str, label: str, items: list[Any]) -> dict[str, Any]:
    return {
        "id": section_id,
        "label": label,
        "count": len(items),
        "items": items,
    }


def _inefficiency_items(status: dict[str, Any], automation: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for note in status.get("attention_items") or []:
        items.append(
            {
                "id": "paperwork_setup_gap",
                "lane": "paperwork",
                "label": note,
                "source": "paperwork_status.attention_items",
            }
        )
    for row in automation.get("exists_but_not_connected") or []:
        items.append(
            {
                "id": row.get("id"),
                "lane": row.get("lane"),
                "label": row.get("summary"),
                "future_connection": row.get("future_connection"),
                "verifiers": row.get("verifiers") or [],
                "source": "business_automation_index.exists_but_not_connected",
            }
        )
    return items


def _cutover_items(status: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        dict(item)
        for item in status.get("cutover_deferred_not_blocking") or []
    ]


def _evidence_summary(result: dict[str, Any]) -> dict[str, Any]:
    ignored_keys = {
        "ok",
        "failures",
        "traceback",
        "generated_at",
        "scenarios",
        "packets",
        "review_candidates",
    }
    evidence = {}
    if isinstance(result.get("evidence"), dict):
        evidence.update(result["evidence"])
    for key, value in result.items():
        if key in ignored_keys or key in evidence:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            evidence[key] = value
        elif isinstance(value, list):
            evidence[key] = len(value)
    return evidence


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }
