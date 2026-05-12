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
        "id": "record_level_failure_recorder",
        "lane": "checkups",
        "runner": "locally_twisted.verify.record_level_failure_contract.run",
        "command": "python scripts/verify/record_level_failure_contract.py",
        "data_mode": "rollback_fake_record_failure",
        "creates": ["Lead", "Comment", "Error Log"],
        "cleanup": "intercepts commits and rolls back generated failure evidence",
    },
    {
        "id": "inquiry_upload_failure_evidence",
        "lane": "intake",
        "runner": "locally_twisted.verify.inquiry_upload_failure_contract.run",
        "command": "python scripts/verify/inquiry_upload_failure_contract.py",
        "data_mode": "rollback_fake_invalid_upload",
        "creates": ["Lead", "Communication", "Comment", "Error Log"],
        "cleanup": "intercepts commits and rolls back generated upload-failure evidence",
    },
    {
        "id": "stripe_amount_parity",
        "lane": "money",
        "runner": "locally_twisted.verify.stripe_amount_parity_contract.run",
        "command": "python scripts/verify/stripe_amount_parity_contract.py",
        "data_mode": "in_memory_fake_order",
        "creates": [],
        "cleanup": "no database records created",
        "deferred_when_ecommerce_paused": True,
    },
    {
        "id": "product_add_on_dependency_boundaries",
        "lane": "ecommerce",
        "runner": "locally_twisted.verify.product_add_on_dependency_contract.run",
        "command": "python scripts/verify/product_add_on_dependency_contract.py",
        "data_mode": "live_contract_no_mutation",
        "creates": [],
        "cleanup": "checks source/runtime add-on contracts without creating business records",
    },
    {
        "id": "checkout_lead_conversion",
        "lane": "money",
        "runner": "locally_twisted.verify.checkout_lead_conversion_contract.run",
        "command": "python scripts/verify/checkout_lead_conversion_contract.py",
        "data_mode": "rollback_fake_guest_checkout",
        "creates": ["Lead", "Contact", "Customer", "Sales Order", "Payment Request", "Task"],
        "cleanup": "intercepts commits and rolls back generated records",
        "deferred_when_ecommerce_paused": True,
    },
    {
        "id": "checkout_fulfillment",
        "lane": "money",
        "runner": "locally_twisted.verify.checkout_fulfillment_contract.run",
        "command": "python scripts/verify/checkout_fulfillment_contract.py",
        "data_mode": "rollback_fake_fulfillment_checkout",
        "creates": ["Customer", "Contact", "Address", "Sales Order", "Payment Request"],
        "cleanup": "stubs Stripe session creation, intercepts commits, and rolls back generated records",
        "deferred_when_ecommerce_paused": True,
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
        "deferred_when_ecommerce_paused": True,
    },
    {
        "id": "payment_success_reconciliation_pending",
        "lane": "money",
        "runner": "locally_twisted.verify.payment_success_reconciliation_contract.run",
        "command": "python scripts/verify/payment_success_reconciliation_contract.py",
        "data_mode": "monkeypatched_browser_return",
        "creates": [],
        "cleanup": "uses fake Stripe/reconciliation responses only",
        "deferred_when_ecommerce_paused": True,
    },
    {
        "id": "stripe_webhook_reconciliation",
        "lane": "money",
        "runner": "locally_twisted.verify.payment_webhook_contract.run",
        "command": "python scripts/verify/payment_webhook_contract.py",
        "data_mode": "mocked_stripe_event",
        "creates": [],
        "cleanup": "no Stripe call; request/signature parsing is mocked",
        "deferred_when_ecommerce_paused": True,
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
        "id": "customer_email_policy_boundaries",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.customer_email_policy_contract.run",
        "command": "python scripts/verify/customer_email_policy_contract.py",
        "data_mode": "static_source_contract",
        "creates": [],
        "cleanup": "no database records created",
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
        "id": "outbound_document_send_readiness",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.outbound_document_send_readiness_contract.run",
        "command": "python scripts/verify/outbound_document_send_readiness_contract.py",
        "data_mode": "in_memory_and_rollback_fake_send_readiness",
        "creates": ["Lead", "Comment", "Error Log"],
        "cleanup": "uses in-memory fake payloads and rolls back record-level blocker evidence",
    },
    {
        "id": "quote_proposal_draft_packets",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.quote_proposal_draft_packet_contract.run",
        "command": "python scripts/verify/quote_proposal_draft_packet_contract.py",
        "data_mode": "in_memory_fake_quote_proposal_scenarios",
        "creates": [],
        "cleanup": "uses in-memory fake quote/proposal payloads only",
    },
    {
        "id": "product_quote_operator_review",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.product_quote_operator_review_contract.run",
        "command": "python scripts/verify/product_quote_operator_review_contract.py",
        "data_mode": "in_memory_fake_product_quote_review_scenarios",
        "creates": [],
        "cleanup": "uses in-memory fake product quote review payloads only",
    },
    {
        "id": "product_quote_acceptance_to_draft_order",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.product_quote_acceptance_contract.run",
        "command": "python scripts/verify/product_quote_acceptance_contract.py",
        "data_mode": "rollback_fake_accepted_product_quote",
        "creates": ["Lead", "Quotation", "Customer", "Sales Order"],
        "cleanup": "intercepts commits and rolls back accepted quote to draft order records",
    },
    {
        "id": "product_quote_customer_delivery",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.product_quote_customer_delivery_contract.run",
        "command": "python scripts/verify/product_quote_customer_delivery_contract.py",
        "data_mode": "rollback_fake_product_quote_customer_delivery",
        "creates": ["Lead", "Quotation"],
        "cleanup": "stubs sendmail, intercepts commits, and rolls back quote link records",
    },
    {
        "id": "product_quote_operator_send_control",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.product_quote_operator_send_control_contract.run",
        "command": "python scripts/verify/product_quote_operator_send_control_contract.py",
        "data_mode": "rollback_fake_product_quote_operator_send",
        "creates": ["Lead", "Quotation"],
        "cleanup": "stubs sendmail, intercepts commits, and rolls back operator quote send records",
    },
    {
        "id": "product_quote_customization_color_recipes",
        "lane": "ecommerce",
        "runner": "locally_twisted.verify.product_quote_customization_contract.run",
        "command": "python scripts/verify/product_quote_customization_contract.py",
        "data_mode": "rollback_fake_color_recipe_quote",
        "creates": ["Lead", "Quotation"],
        "cleanup": "intercepts commits and rolls back color-recipe quote records",
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
    {
        "id": "customer_reminder_dry_run_outliers",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.customer_reminder_dry_run_contract.run",
        "command": "python scripts/verify/customer_reminder_dry_run_contract.py",
        "data_mode": "in_memory_fake_reminder_queue_scenarios",
        "creates": [],
        "cleanup": "uses in-memory fake reminder queue payloads only",
    },
    {
        "id": "customer_reminder_review_report_outliers",
        "lane": "paperwork",
        "runner": "locally_twisted.verify.customer_reminder_review_report_contract.run",
        "command": "python scripts/verify/customer_reminder_review_report_contract.py",
        "data_mode": "in_memory_fake_reminder_report_scenarios",
        "creates": [],
        "cleanup": "uses in-memory fake reminder report payloads only",
    },
)

GUARD_DOCTYPES = (
    "Lead",
    "Contact",
    "Customer",
    "Address",
    "Quotation",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Task",
    "Email Queue",
    "Communication",
    "Error Log",
    "Comment",
)
DEFERRED_MONEY_REASON = (
    "Ecommerce is paused for no-purchase V1; checkout, payment, Stripe, "
    "and paid-order contracts are deferred until GL reopens ecommerce."
)


def run() -> dict[str, object]:
    """Run the synthetic audit and return JSON-safe, fail-loud evidence."""
    from locally_twisted.paperwork import paperwork_review_digest
    from locally_twisted.verify import business_automation_index, paperwork_status

    before = _guard_counts()
    failures: list[str] = []

    active_contracts = _active_contracts()
    deferred_contracts = _deferred_contracts()
    stage_mutations: list[dict[str, Any]] = []
    contract_items = []
    for spec in active_contracts:
        contract_before = _guard_counts()
        item = _run_contract(spec)
        contract_after = _guard_counts()
        contract_delta = _count_delta(contract_before, contract_after)
        if contract_delta:
            item["mutation_delta"] = contract_delta
            stage_mutations.append({"stage": f"contract:{spec['id']}", "delta": contract_delta})
        contract_items.append(item)
    deferred_items = [_deferred_contract_item(spec) for spec in deferred_contracts]
    broken_piping = [item for item in contract_items if not item["ok"]]

    status = _run_guarded_stage("paperwork_status", paperwork_status.run, stage_mutations)
    automation = _run_guarded_stage(
        "business_automation_index",
        lambda: business_automation_index.run(
            include_digest=False,
            include_synthetic=False,
            include_customer_reminders=False,
            include_customer_reminder_report=False,
            run_runtime_contracts=False,
        ),
        stage_mutations,
    )
    digest = _run_guarded_stage("paperwork_review_digest", paperwork_review_digest.run, stage_mutations)

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
            [*_cutover_items(status), *deferred_items],
        ),
        "deferred_money_surfaces": _section(
            "deferred_money_surfaces",
            "Deferred money surfaces",
            deferred_items,
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
            "deferred_contract_count": len(deferred_items),
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
            "stage_mutations": stage_mutations,
        },
        "boundaries": {
            "live_stripe_keys_required": False,
            "live_customer_records_required": False,
            "real_user_information_required": False,
            "no_live_stripe_checkout": True,
            "no_customer_send": True,
            "no_persisted_fake_records": True,
            "live_cutover_is_separate": True,
            "no_purchase_v1": _ecommerce_paused(),
            "deferred_money_reason": DEFERRED_MONEY_REASON if _ecommerce_paused() else None,
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


def _active_contracts() -> list[dict[str, Any]]:
    return [spec for spec in SYNTHETIC_CONTRACTS if not _contract_deferred(spec)]


def _deferred_contracts() -> list[dict[str, Any]]:
    return [spec for spec in SYNTHETIC_CONTRACTS if _contract_deferred(spec)]


def _contract_deferred(spec: dict[str, Any]) -> bool:
    return bool(spec.get("deferred_when_ecommerce_paused") and _ecommerce_paused())


def _ecommerce_paused() -> bool:
    try:
        from locally_twisted.ecommerce_pause import is_ecommerce_paused

        return bool(is_ecommerce_paused())
    except Exception:
        return False


def _deferred_contract_item(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": spec["id"],
        "lane": spec["lane"],
        "ok": True,
        "deferred": True,
        "command": spec["command"],
        "data_mode": spec["data_mode"],
        "live_inputs_required": False,
        "uses_real_customer_data": False,
        "creates": spec["creates"],
        "cleanup": "not run during no-purchase V1 launch proof",
        "reason": DEFERRED_MONEY_REASON,
        "failures": [],
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


def _run_guarded_stage(stage: str, runner, stage_mutations: list[dict[str, Any]]) -> dict[str, Any]:
    before = _guard_counts()
    result = runner()
    after = _guard_counts()
    delta = _count_delta(before, after)
    if delta:
        stage_mutations.append({"stage": stage, "delta": delta})
    return result


def _count_delta(before: dict[str, int], after: dict[str, int]) -> dict[str, dict[str, int]]:
    delta = {}
    for doctype in sorted(set(before) | set(after)):
        old = before.get(doctype, 0)
        new = after.get(doctype, 0)
        if old != new:
            delta[doctype] = {"before": old, "after": new, "delta": new - old}
    return delta
