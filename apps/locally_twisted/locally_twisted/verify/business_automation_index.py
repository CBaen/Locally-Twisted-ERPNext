"""Read-only index of LT business automation surfaces and backend connections."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Callable

import frappe
from frappe.utils import now_datetime

from locally_twisted.verify.business_automation_product_quote import (
    product_quote_acceptance_surface,
    product_quote_customer_delivery_surface,
    product_quote_operator_send_control_surface,
    product_quote_operator_review_surface,
)


ROOT = Path(frappe.get_app_path("locally_twisted")).parent.parent
APP_ROOT = Path(frappe.get_app_path("locally_twisted"))
NO_PURCHASE_MONEY_DEFERRAL = (
    "Deferred while public ecommerce pause mode is active: checkout/payment/Stripe "
    "is not the current launch gate in that mode."
)


def run(
    include_digest: bool = True,
    include_synthetic: bool = True,
    include_customer_reminders: bool = True,
    include_customer_reminder_report: bool = True,
    run_runtime_contracts: bool = True,
) -> dict[str, object]:
    """Return a JSON-safe automation map that fails loudly on broken required links."""
    surfaces = _surfaces(
        include_digest=include_digest,
        include_synthetic=include_synthetic,
        include_customer_reminders=include_customer_reminders,
        include_customer_reminder_report=include_customer_reminder_report,
        run_runtime_contracts=run_runtime_contracts,
    )
    rows = [_evaluate(surface) for surface in surfaces]
    record_level_failures = _record_level_health_rows()
    failures = _required_failures(rows)
    if record_level_failures:
        failures.append(f"record_level_failures: {len(record_level_failures)} open backend failure blocker(s)")

    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "runtime_contracts_executed": run_runtime_contracts,
        "summary": {
            "surface_count": len(rows),
            "required_count": sum(1 for row in rows if row["required_for_launch"]),
            "connected_count": sum(1 for row in rows if row["status"] == "exists_and_connected"),
            "loud_failure_gap_count": sum(1 for row in rows if row["loud_failure_gap"]),
        },
        "exists_and_connected": [row for row in rows if row["status"] == "exists_and_connected"],
        "exists_but_not_connected": [row for row in rows if row["status"] == "exists_but_not_connected"],
        "missing_needs_connection": [row for row in rows if row["status"] == "missing_needs_connection"],
        "missing_should_connect": [row for row in rows if row["status"] == "missing_should_connect"],
        "loud_failure_gaps": [row for row in rows if row["loud_failure_gap"]],
        "record_level_failures": record_level_failures,
        "checkups": _checkups(),
        "fake_data_contracts": _fake_data_contracts(),
        "failures": failures,
    }


def scheduled_checkup() -> None:
    """Scheduled checkup entrypoint for Frappe Cloud or any scheduler-enabled site."""
    result = run()
    attention = (
        result.get("failures")
        or result.get("missing_needs_connection")
        or result.get("loud_failure_gaps")
        or result.get("record_level_failures")
    )
    if attention:
        frappe.log_error(
            title="LT business automation checkup needs attention",
            message=json.dumps(_scheduled_log_payload(result), indent=2, default=str),
        )


def _evaluate(surface: dict[str, object]) -> dict[str, object]:
    exists_check = surface["exists"]
    connected_check = surface["connected"]
    loud_check = surface.get("loud_failure") or (lambda: [])

    exists_failures = _run_check(exists_check)
    connected_failures = _run_check(connected_check) if not exists_failures else []
    loud_failures = _run_check(loud_check) if not exists_failures else []

    if exists_failures:
        status = "missing_needs_connection" if surface["required_for_launch"] else "missing_should_connect"
    elif connected_failures:
        status = "exists_but_not_connected"
    else:
        status = "exists_and_connected"

    return {
        "id": surface["id"],
        "lane": surface["lane"],
        "summary": surface["summary"],
        "required_for_launch": surface["required_for_launch"],
        "status": status,
        "exists_failures": exists_failures,
        "connection_failures": connected_failures,
        "loud_failure_gap": bool(loud_failures),
        "loud_failure_notes": loud_failures,
        "evidence": surface.get("evidence") or [],
        "verifiers": surface.get("verifiers") or [],
        "creates_fake_data": surface.get("creates_fake_data", False),
        "future_connection": surface.get("future_connection"),
    }


def _required_failures(rows: list[dict[str, object]]) -> list[str]:
    failures = []
    for row in rows:
        if not row["required_for_launch"]:
            continue
        if row["status"] != "exists_and_connected":
            details = row["exists_failures"] or row["connection_failures"]
            failures.append(f"{row['id']}: {row['status']} ({'; '.join(details)})")
        if row["loud_failure_gap"]:
            details = row["loud_failure_notes"] or ["missing loud-failure evidence"]
            failures.append(f"{row['id']}: loud_failure_gap ({'; '.join(details)})")
    return failures


def _run_check(check: Callable[[], list[str]] | object) -> list[str]:
    if not callable(check):
        return ["internal verifier check is not callable"]
    try:
        return list(check())
    except Exception as exc:  # pragma: no cover - surfaced in bench output
        return [f"{type(exc).__name__}: {exc}"]


def _record_level_health_rows() -> list[dict[str, object]]:
    try:
        from locally_twisted.failure_recorder import record_health_failures

        return record_health_failures(limit=100)
    except Exception as exc:
        return [
            {
                "surface": "record_level_failure_recorder",
                "step": "record_health_query",
                "severity": "error",
                "internal_next_action": "Fix record-level failure health reporting.",
                "error": f"{type(exc).__name__}: {exc}",
            }
        ]


def _surfaces(
    include_digest: bool = True,
    include_synthetic: bool = True,
    include_customer_reminders: bool = True,
    include_customer_reminder_report: bool = True,
    run_runtime_contracts: bool = True,
) -> list[dict[str, object]]:
    no_purchase_v1 = _no_purchase_v1_active()
    surfaces = [
        {
            "id": "record_level_failure_recorder",
            "lane": "checkups",
            "summary": "Backend partial failures write Error Log evidence plus record-level blockers with exact affected record IDs.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/failure_recorder.py",
                "locally_twisted/verify/record_level_failure_contract.py",
            ),
            "connected": lambda: _record_level_failure_connected(run_runtime_contracts=run_runtime_contracts),
            "loud_failure": _record_level_failure_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/failure_recorder.py",
                "apps/locally_twisted/locally_twisted/verify/record_level_failure_contract.py",
            ],
            "verifiers": ["python scripts/verify/record_level_failure_contract.py"],
            "creates_fake_data": True,
        },
        {
            "id": "public_contact_to_lead",
            "lane": "intake",
            "summary": "/contact exists, maps customer inquiry values into ERPNext Lead fields, and makes rejected inspiration uploads visible.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/www/contact.py",
                "locally_twisted/www/contact.html",
                "locally_twisted/www/book.py",
                "locally_twisted/templates/includes/book_form.html",
            ),
            "connected": lambda: _contact_connected(run_runtime_contracts=run_runtime_contracts),
            "loud_failure": _contact_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/www/contact.py",
                "apps/locally_twisted/locally_twisted/www/contact.html",
                "apps/locally_twisted/locally_twisted/www/book.py",
                "apps/locally_twisted/locally_twisted/templates/includes/book_form.html",
                "apps/locally_twisted/locally_twisted/verify/inquiry_upload_failure_contract.py",
            ],
            "verifiers": [
                "python scripts/verify/lead_backend_intake_parity.py",
                "python scripts/verify/contact_service_logic.py --base-url http://localhost:8081",
                "python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter",
                "python scripts/verify/inquiry_upload_failure_contract.py",
            ],
            "creates_fake_data": True,
        },
        {
            "id": "lead_contact_ack_cascade",
            "lane": "intake",
            "summary": "Lead insert cascades into Contact dedup/link, customer acknowledgment email with required internal copies, and first operational Task.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/lead_cascade.py",
                "locally_twisted/communication_copy_policy.py",
                "locally_twisted/stage_cascade.py",
                "locally_twisted/policy_documents.py",
                "locally_twisted/verify/customer_email_policy_contract.py",
            ),
            "connected": _lead_cascade_connected,
            "loud_failure": _lead_cascade_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/hooks.py",
                "apps/locally_twisted/locally_twisted/lead_cascade.py",
                "apps/locally_twisted/locally_twisted/communication_copy_policy.py",
                "apps/locally_twisted/locally_twisted/stage_cascade.py",
                "apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py",
            ],
            "verifiers": [
                "python scripts/verify/customer_documents_contract.py",
                "python scripts/verify/customer_email_policy_contract.py",
                "python scripts/verify/crm_stage_cascade.py",
            ],
            "creates_fake_data": True,
        },
        {
            "id": "crm_stage_task_cascade",
            "lane": "operations",
            "summary": "Custom Lead pipeline stage changes create and close operational Tasks only.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/crm_pipeline.py",
                "locally_twisted/stage_cascade.py",
                "locally_twisted/seed/sync_stage_cascade.py",
            ),
            "connected": _stage_task_connected,
            "loud_failure": _stage_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/crm_pipeline.py",
                "apps/locally_twisted/locally_twisted/stage_cascade.py",
            ],
            "verifiers": [
                "python scripts/setup/sync_stage_cascade.py",
                "python scripts/verify/crm_pipeline_parity.py",
                "python scripts/verify/crm_stage_cascade.py",
            ],
            "creates_fake_data": True,
        },
        {
            "id": "ecommerce_no_purchase_api_guard",
            "lane": "checkups",
            "summary": "Pause-mode direct checkout APIs fail loudly and cannot create purchase, order, or payment records.",
            "required_for_launch": no_purchase_v1,
            "exists": lambda: _files_exist(
                "locally_twisted/ecommerce_pause.py",
                "locally_twisted/www/checkout.py",
            ),
            "connected": _no_purchase_checkout_guard_connected,
            "loud_failure": _no_purchase_checkout_guard_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/ecommerce_pause.py",
                "apps/locally_twisted/locally_twisted/www/checkout.py",
                "scripts/verify/ecommerce_pause_contract.py",
            ],
            "verifiers": ["python scripts/verify/ecommerce_pause_contract.py"],
        },
        {
            "id": "guest_checkout_to_payment_request",
            "lane": "money",
            "summary": "Guest checkout creates or links Customer, Contact, Address, Sales Order, Payment Request, and Stripe redirect.",
            "required_for_launch": not no_purchase_v1,
            "exists": lambda: _files_exist(
                "locally_twisted/www/checkout.py",
                "locally_twisted/payments/stripe_session.py",
            ),
            "connected": lambda: _deferred_money_connected() if no_purchase_v1 else _checkout_connected(),
            "loud_failure": _checkout_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/www/checkout.py",
                "apps/locally_twisted/locally_twisted/payments/stripe_session.py",
            ],
            "verifiers": [
                "python scripts/verify/checkout_lead_conversion_contract.py",
                "python scripts/verify/payment_backend_config_contract.py",
                "python scripts/verify/payment_launch_readiness.py",
            ],
            "creates_fake_data": True,
            "future_connection": NO_PURCHASE_MONEY_DEFERRAL if no_purchase_v1 else None,
        },
        {
            "id": "payment_success_paid_order_cascade",
            "lane": "money",
            "summary": "Paid checkout reconciles Payment Request, Payment Entry, Sales Invoice, receipt email, operator notification, welcome email, required internal copies, and pending-reconciliation thank-you copy.",
            "required_for_launch": not no_purchase_v1,
            "exists": lambda: _files_exist(
                "locally_twisted/www/payment_success.py",
                "locally_twisted/communication_copy_policy.py",
                "locally_twisted/www/thank_you.py",
                "locally_twisted/www/thank_you.html",
                "locally_twisted/verify/payment_success_reconciliation_contract.py",
                "locally_twisted/verify/customer_email_policy_contract.py",
            ),
            "connected": lambda: (
                _deferred_money_connected()
                if no_purchase_v1
                else _payment_success_connected(run_runtime_contracts=run_runtime_contracts)
            ),
            "loud_failure": _payment_success_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/www/payment_success.py",
                "apps/locally_twisted/locally_twisted/communication_copy_policy.py",
                "apps/locally_twisted/locally_twisted/www/thank_you.py",
                "apps/locally_twisted/locally_twisted/www/thank_you.html",
                "apps/locally_twisted/locally_twisted/verify/payment_success_reconciliation_contract.py",
                "apps/locally_twisted/locally_twisted/verify/customer_email_policy_contract.py",
            ],
            "verifiers": [
                "python scripts/verify/payment_cascade_contract.py",
                "python scripts/verify/payment_success_reconciliation_contract.py",
                "python scripts/verify/customer_documents_contract.py",
                "python scripts/verify/customer_email_policy_contract.py",
            ],
            "creates_fake_data": True,
            "future_connection": NO_PURCHASE_MONEY_DEFERRAL if no_purchase_v1 else None,
        },
        {
            "id": "stripe_amount_parity",
            "lane": "money",
            "summary": "Stripe Checkout Session line items must equal the ERPNext Sales Order and Payment Request amount.",
            "required_for_launch": not no_purchase_v1,
            "exists": lambda: _files_exist("locally_twisted/payments/stripe_session.py"),
            "connected": lambda: _deferred_money_connected() if no_purchase_v1 else _stripe_amount_parity_connected(),
            "loud_failure": _stripe_amount_parity_loud_failure,
            "evidence": ["apps/locally_twisted/locally_twisted/payments/stripe_session.py"],
            "verifiers": ["python scripts/verify/stripe_amount_parity_contract.py"],
            "future_connection": NO_PURCHASE_MONEY_DEFERRAL if no_purchase_v1 else None,
        },
        {
            "id": "stripe_webhook_reconciliation",
            "lane": "money",
            "summary": "Stripe webhook can reconcile paid Sales Orders through the same paid-order helper.",
            "required_for_launch": not no_purchase_v1,
            "exists": lambda: _files_exist("locally_twisted/payments/stripe_webhook.py"),
            "connected": lambda: _deferred_money_connected() if no_purchase_v1 else _stripe_webhook_connected(),
            "loud_failure": _stripe_webhook_loud_failure,
            "evidence": ["apps/locally_twisted/locally_twisted/payments/stripe_webhook.py"],
            "verifiers": [
                "python scripts/verify/payment_webhook_contract.py",
                "python scripts/verify/payment_launch_readiness.py",
            ],
            "future_connection": NO_PURCHASE_MONEY_DEFERRAL if no_purchase_v1 else None,
        },
        {
            "id": "branded_sales_invoice",
            "lane": "paperwork",
            "summary": "Sales Invoice defaults to the code-owned Locally Twisted print format and branded Letter Head.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/seed/sync_invoice_branding.py",
                "locally_twisted/verify/invoice_branding_contract.py",
            ),
            "connected": _invoice_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/seed/sync_invoice_branding.py",
                "apps/locally_twisted/locally_twisted/verify/invoice_branding_contract.py",
            ],
            "verifiers": [
                "python scripts/setup/sync_invoice_branding.py",
                "python scripts/verify/invoice_branding_contract.py",
            ],
        },
        {
            "id": "outbound_document_registry",
            "lane": "paperwork",
            "summary": "Outbound document templates are registered for invoices, receipts, proposals, packets, statements, reminders, work orders, and follow-ups.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/outbound_documents/registry.py",
                "locally_twisted/verify/outbound_documents_contract.py",
            ),
            "connected": _outbound_documents_connected,
            "loud_failure": lambda: [],
            "evidence": ["apps/locally_twisted/locally_twisted/outbound_documents/registry.py"],
            "verifiers": [
                "python scripts/verify/outbound_documents_contract.py",
                "python scripts/verify/render_outbound_document_previews.py --slug outbound-documents-YYYYMMDD",
            ],
        },
        {
            "id": "outbound_document_send_readiness",
            "lane": "paperwork",
            "summary": "External document families return field, recipient, internal copy routing, approval, and record-level blockers before any customer delivery.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/outbound_documents/send_readiness.py",
                "locally_twisted/communication_copy_policy.py",
                "locally_twisted/verify/outbound_document_send_readiness_contract.py",
            ),
            "connected": lambda: _outbound_document_send_readiness_connected(
                run_runtime_contracts=run_runtime_contracts
            ),
            "loud_failure": _outbound_document_send_readiness_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/outbound_documents/send_readiness.py",
                "apps/locally_twisted/locally_twisted/communication_copy_policy.py",
                "apps/locally_twisted/locally_twisted/verify/outbound_document_send_readiness_contract.py",
            ],
            "verifiers": ["python scripts/verify/outbound_document_send_readiness_contract.py"],
            "creates_fake_data": True,
        },
        {
            "id": "paperwork_status_checkup",
            "lane": "checkups",
            "summary": "Read-only paperwork status reports invoices, payment requests, email queue state, setup gaps, and cutover-deferred live payment items.",
            "required_for_launch": True,
            "exists": lambda: _files_exist("locally_twisted/verify/paperwork_status.py"),
            "connected": _paperwork_status_connected,
            "loud_failure": lambda: [],
            "evidence": ["apps/locally_twisted/locally_twisted/verify/paperwork_status.py"],
            "verifiers": ["python scripts/verify/paperwork_status.py --report output/paperwork-status.json"],
        },
        {
            "id": "scheduled_business_checkups",
            "lane": "checkups",
            "summary": "General backend checkups should run automatically on a schedule, not only by manual scripts.",
            "required_for_launch": False,
            "exists": _manual_checkups_exist,
            "connected": _scheduled_checkups_connected,
            "loud_failure": lambda: [],
            "future_connection": "Wire a scheduled job or external monitor for business_automation_index, paperwork_status, payment readiness, email queue, stale tasks, and zero-new-leads checks.",
            "verifiers": ["python scripts/verify/business_automation_index.py --report output/business-automation-index.json"],
        },
        {
            "id": "client_operations_heartbeat",
            "lane": "checkups",
            "summary": "Sanitized client operations heartbeat combines system health, business digest topics, notification preferences, approval tiers, and Maintenance Admin access boundaries.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/maintenance/heartbeat.py",
                "locally_twisted/seed/sync_maintenance_package.py",
                "locally_twisted/locally_twisted/report/lt_maintenance_heartbeat/lt_maintenance_heartbeat.py",
            ),
            "connected": _maintenance_heartbeat_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/maintenance/heartbeat.py",
                "apps/locally_twisted/locally_twisted/seed/sync_maintenance_package.py",
                "apps/locally_twisted/locally_twisted/locally_twisted/report/lt_maintenance_heartbeat/lt_maintenance_heartbeat.py",
            ],
            "verifiers": [
                "python scripts/setup/sync_maintenance_package.py",
                "python scripts/verify/maintenance_heartbeat.py",
                "python scripts/verify/maintenance_admin_boundary.py",
            ],
        },
        {
            "id": "accountant_workspace",
            "lane": "finance",
            "summary": "Accountant Home workspace exposes receivables, payment requests, banking, vendors, and setup shortcuts.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/seed/sync_finance_workspace.py",
                "locally_twisted/seed/sync_backend_workspaces.py",
            ),
            "connected": _finance_workspace_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py",
                "apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py",
            ],
            "verifiers": [
                "python scripts/setup/sync_finance_workspace.py",
                "python scripts/verify/finance_workspace_parity.py",
                "python scripts/verify/backend_workspace_parity.py",
            ],
        },
        {
            "id": "unpaid_invoice_review_surface",
            "lane": "paperwork",
            "summary": "Unpaid/overdue invoices become draft-only reminder and statement review candidates without sending or accounting mutations.",
            "required_for_launch": False,
            "exists": lambda: _files_exist("locally_twisted/paperwork/unpaid_invoice_review.py"),
            "connected": _unpaid_invoice_review_connected,
            "loud_failure": lambda: [],
            "evidence": ["apps/locally_twisted/locally_twisted/paperwork/unpaid_invoice_review.py"],
            "verifiers": ["python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json"],
        },
        {
            "id": "unpaid_invoice_draft_packet",
            "lane": "paperwork",
            "summary": "Unpaid invoice review candidates render draft-only reminder and statement packets for human review.",
            "required_for_launch": False,
            "exists": lambda: _files_exist("locally_twisted/paperwork/unpaid_invoice_draft_packet.py"),
            "connected": _unpaid_invoice_draft_packet_connected,
            "loud_failure": lambda: [],
            "evidence": ["apps/locally_twisted/locally_twisted/paperwork/unpaid_invoice_draft_packet.py"],
            "verifiers": [
                "python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json"
            ],
        },
        {
            "id": "paperwork_review_digest",
            "lane": "paperwork",
            "summary": "Read-only internal digest combines paperwork status, automation index, unpaid review, and draft packets into one review surface.",
            "required_for_launch": False,
            "exists": lambda: _files_exist("locally_twisted/paperwork/paperwork_review_digest.py"),
            "connected": _paperwork_review_digest_connected,
            "loud_failure": lambda: [],
            "evidence": ["apps/locally_twisted/locally_twisted/paperwork/paperwork_review_digest.py"],
            "verifiers": [
                "python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json"
            ],
        },
        {
            "id": "customer_reminder_dry_run",
            "lane": "paperwork",
            "summary": "No-live customer reminder dry run prepares internal review queue items and cadence suggestions without customer delivery.",
            "required_for_launch": False,
            "exists": lambda: _files_exist("locally_twisted/paperwork/customer_reminder_dry_run.py"),
            "connected": _customer_reminder_dry_run_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/paperwork/customer_reminder_dry_run.py",
                "scripts/verify/customer_reminder_dry_run.py",
                "scripts/verify/customer_reminder_dry_run_contract.py",
            ],
            "verifiers": [
                "python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json",
                "python scripts/verify/customer_reminder_dry_run_contract.py",
            ],
        },
        {
            "id": "customer_reminder_review_report",
            "lane": "paperwork",
            "summary": "No-live customer reminder review rows are exposed through an internal Desk Script Report without customer delivery.",
            "required_for_launch": False,
            "exists": lambda: _files_exist(
                "locally_twisted/paperwork/customer_reminder_review_report.py",
                "locally_twisted/locally_twisted/report/lt_customer_reminder_review/lt_customer_reminder_review.py",
                "locally_twisted/seed/sync_finance_workspace.py",
            ),
            "connected": _customer_reminder_review_report_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/paperwork/customer_reminder_review_report.py",
                "apps/locally_twisted/locally_twisted/locally_twisted/report/lt_customer_reminder_review/lt_customer_reminder_review.py",
                "apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py",
                "scripts/verify/customer_reminder_review_report.py",
                "scripts/verify/customer_reminder_review_report_contract.py",
                "scripts/verify/finance_workspace_parity.py",
            ],
            "verifiers": [
                "python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json",
                "python scripts/verify/customer_reminder_review_report_contract.py",
                "python scripts/verify/finance_workspace_parity.py",
            ],
        },
        {
            "id": "synthetic_business_pipeline",
            "lane": "checkups",
            "summary": "Synthetic no-live audit runs fake-data/rollback-safe contracts and separates current operating readiness from live cutover readiness.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/verify/synthetic_business_pipeline.py",
            ),
            "connected": _synthetic_business_pipeline_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/verify/synthetic_business_pipeline.py",
                "scripts/verify/synthetic_business_pipeline.py",
            ],
            "verifiers": [
                "python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json"
            ],
            "creates_fake_data": True,
        },
        {
            "id": "quote_proposal_generation",
            "lane": "paperwork",
            "summary": "Lead/Quotation-style quote and proposal data can render draft-only internal review packets without sending or finance mutations.",
            "required_for_launch": False,
            "exists": lambda: [
                *_quote_templates_exist(),
                *_files_exist(
                    "locally_twisted/paperwork/quote_proposal_draft_packet.py",
                    "locally_twisted/verify/quote_proposal_draft_packet_contract.py",
                ),
            ],
            "connected": _quote_proposal_connected,
            "loud_failure": _quote_proposal_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/paperwork/quote_proposal_draft_packet.py",
                "apps/locally_twisted/locally_twisted/verify/quote_proposal_draft_packet_contract.py",
            ],
            "verifiers": [
                "python scripts/verify/quote_proposal_draft_packet.py --report output/quote-proposal-draft-packet.json",
                "python scripts/verify/quote_proposal_draft_packet_contract.py",
            ],
        },
        product_quote_operator_review_surface(run_runtime_contracts=run_runtime_contracts),
        product_quote_acceptance_surface(run_runtime_contracts=run_runtime_contracts),
        product_quote_customer_delivery_surface(run_runtime_contracts=run_runtime_contracts),
        product_quote_operator_send_control_surface(run_runtime_contracts=run_runtime_contracts),
        {
            "id": "vendor_setup_packet_generation",
            "lane": "finance",
            "summary": "Vendor setup/W-9 packet template exists, but no approved W-9 file, Supplier/vendor data, or secure-send workflow is connected.",
            "required_for_launch": False,
            "exists": _vendor_template_exists,
            "connected": _vendor_setup_connected,
            "loud_failure": lambda: [],
            "future_connection": "Connect accounting-approved W-9, vendor facts, Suppliers, and secure reviewed delivery.",
            "verifiers": ["python scripts/verify/outbound_documents_contract.py"],
        },
        {
            "id": "bank_reconciliation_cutover",
            "lane": "finance",
            "summary": "Banking/reconciliation DocTypes exist in ERPNext, but LT has no Bank Account/default bank connected.",
            "required_for_launch": False,
            "exists": lambda: _doctype_presence(["Bank Account", "Bank Transaction", "Bank Reconciliation Tool"]),
            "connected": _banking_connected,
            "loud_failure": lambda: [],
            "future_connection": "Create Bank Account, set Company default bank, then test CSV import before live sync.",
            "verifiers": ["python scripts/verify/finance_inventory.py --json"],
        },
        {
            "id": "payroll_hrms",
            "lane": "finance",
            "summary": "Payroll should eventually be part of the all-in-one system, but HRMS/payroll DocTypes are not ready.",
            "required_for_launch": False,
            "exists": lambda: _doctype_presence(["Employee"]),
            "connected": _payroll_connected,
            "loud_failure": lambda: [],
            "future_connection": "Install/evaluate HRMS and connect payroll only after accountant/provider approval.",
            "verifiers": ["python scripts/verify/finance_inventory.py --json"],
        },
    ]
    if not include_digest:
        surfaces = [surface for surface in surfaces if surface["id"] != "paperwork_review_digest"]
    if not include_synthetic:
        surfaces = [surface for surface in surfaces if surface["id"] != "synthetic_business_pipeline"]
    if not include_customer_reminders:
        surfaces = [surface for surface in surfaces if surface["id"] != "customer_reminder_dry_run"]
    if not include_customer_reminder_report:
        surfaces = [surface for surface in surfaces if surface["id"] != "customer_reminder_review_report"]
    return surfaces


def _record_level_failure_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(_callables_exist(
        "locally_twisted.failure_recorder.record_backend_failure",
        "locally_twisted.failure_recorder.record_health_failures",
        "locally_twisted.verify.record_level_failure_contract.run",
    ))
    source = _read("locally_twisted/failure_recorder.py")
    for marker in (
        "FAILURE_COMMENT_PREFIX",
        "Error Log",
        "Comment",
        "record_health_failures",
    ):
        if marker not in source:
            failures.append(f"failure_recorder.py missing marker {marker}")
    if not failures and run_runtime_contracts:
        result = frappe.get_attr("locally_twisted.verify.record_level_failure_contract.run")()
        if not result.get("ok"):
            failures.extend(result.get("failures") or ["record-level failure contract failed"])
    return failures


def _record_level_failure_loud_failure() -> list[str]:
    failures = []
    for path, markers in {
        "locally_twisted/lead_cascade.py": (
            "record_backend_failure",
            "contact_dedup_link",
            "customer_ack_email",
            "initial_task_cascade",
        ),
        "locally_twisted/www/checkout.py": (
            "record_backend_failure",
            "checkout_notes_transfer",
        ),
        "locally_twisted/www/payment_success.py": (
            "record_backend_failure",
            "lead_conversion",
            "receipt_email_missing_recipient",
            "PaidOrderReconciliationError",
        ),
    }.items():
        source = _read(path)
        for marker in markers:
            if marker not in source:
                failures.append(f"{path} missing record-level failure marker {marker}")
    return failures


def _contact_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.verify.inquiry_upload_failure_contract.run"))
    failures.extend(_doctype_presence(["Lead", "LT Service Type", "LT Lead Service Type", "LT Lead Photo"]))
    expected_services = {
        "Balloon Decor",
        "Balloon Twisting",
        "Face Painting",
        "Delivery",
        "Pickup",
        "Events Inquiry",
        "Something Else",
    }
    found = {
        row.name
        for row in frappe.get_all("LT Service Type", fields=["name"], limit_page_length=200)
    }
    missing = sorted(expected_services - found)
    if missing:
        failures.append("LT Service Type missing values: " + ", ".join(missing))
    lead_meta = frappe.get_meta("Lead")
    for fieldname in (
        "custom_event_type",
        "custom_event_date",
        "custom_event_time",
        "custom_event_location",
        "custom_package_notes",
        "custom_lt_payment_timing",
    ):
        if not lead_meta.has_field(fieldname):
            failures.append(f"Lead missing field {fieldname}")
    contact_source = "\n".join([
        _read("locally_twisted/www/contact.py"),
        _read("locally_twisted/www/book.py"),
        _read("locally_twisted/templates/includes/book_form.html"),
    ])
    for marker in ("custom_event_type", "custom_package_notes", "custom_lt_payment_timing"):
        if marker not in contact_source:
            failures.append(f"contact.py does not write/read {marker}")
    if not failures and run_runtime_contracts:
        result = frappe.get_attr("locally_twisted.verify.inquiry_upload_failure_contract.run")()
        if not result.get("ok"):
            failures.extend(result.get("failures") or ["inquiry upload failure contract failed"])
    return failures


def _contact_loud_failure() -> list[str]:
    source = "\n".join([
        _read("locally_twisted/www/contact.py"),
        _read("locally_twisted/www/book.py"),
        _read("locally_twisted/templates/includes/book_form.html"),
    ])
    failures = []
    if "frappe.throw" not in source:
        failures.append("contact.py has no frappe.throw loud-failure path visible in source")
    for marker in ("email_id", "custom_event_type"):
        if marker not in source:
            failures.append(f"contact.py source missing required mapping marker {marker}")
    for marker in ("record_backend_failure", "photo_rejected_unsupported_type", "customer_message", "received_message"):
        if marker not in source:
            failures.append(f"contact upload path missing loud-failure marker {marker}")
    return failures


def _lead_cascade_connected() -> list[str]:
    failures = []
    hooks = _hooks()
    lead_events = (getattr(hooks, "doc_events", {}) or {}).get("Lead") or {}
    expected = {
        "before_insert": "locally_twisted.lead_cascade.before_insert",
        "after_insert": "locally_twisted.lead_cascade.after_insert",
        "on_update": "locally_twisted.stage_cascade.on_update",
    }
    for event, dotted in expected.items():
        if lead_events.get(event) != dotted:
            failures.append(f"Lead {event} hook expected {dotted}, found {lead_events.get(event)!r}")
    failures.extend(_callables_exist(
        "locally_twisted.lead_cascade.before_insert",
        "locally_twisted.lead_cascade.after_insert",
        "locally_twisted.stage_cascade.after_insert",
        "locally_twisted.stage_cascade.on_update",
    ))
    failures.extend(_customer_email_policy_connected())
    return failures


def _lead_cascade_loud_failure() -> list[str]:
    source = _read("locally_twisted/lead_cascade.py")
    failures = []
    for marker in ("record_backend_failure", "contact_dedup_link", "customer_ack_email", "initial_task_cascade"):
        if marker not in source:
            failures.append(f"lead_cascade missing record-level failure marker {marker}")
    return failures


def _stage_task_connected() -> list[str]:
    failures = []
    task_meta = frappe.get_meta("Task")
    for fieldname in ("custom_lt_lead", "custom_pipeline_stage", "custom_lt_cascade_key"):
        if not task_meta.has_field(fieldname):
            failures.append(f"Task missing cascade field {fieldname}")
    failures.extend(_lead_cascade_connected())
    return failures


def _stage_loud_failure() -> list[str]:
    source = _read("locally_twisted/stage_cascade.py")
    if "frappe.log_error" not in source:
        return ["stage_cascade does not log failures"]
    return []


def _no_purchase_v1_active() -> bool:
    try:
        from locally_twisted.ecommerce_pause import is_ecommerce_paused

        return bool(is_ecommerce_paused())
    except Exception:
        return False


def _deferred_money_connected() -> list[str]:
    return []


def _no_purchase_checkout_guard_connected() -> list[str]:
    if not _no_purchase_v1_active():
        return []

    failures = []
    failures.extend(_callables_exist(
        "locally_twisted.ecommerce_pause.is_ecommerce_paused",
        "locally_twisted.www.checkout.preview_checkout_totals",
        "locally_twisted.www.checkout.submit_guest_order",
    ))
    source = _read("locally_twisted/www/checkout.py")
    for marker in (
        "_assert_checkout_api_open(\"preview_checkout_totals\")",
        "_assert_checkout_api_open(\"submit_guest_order\")",
        "NO_PURCHASE_CHECKOUT_STATUS",
        "ecommerce_paused",
    ):
        if marker not in source:
            failures.append(f"checkout.py missing no-purchase guard marker {marker}")
    return failures


def _no_purchase_checkout_guard_loud_failure() -> list[str]:
    if not _no_purchase_v1_active():
        return []

    source = _read("locally_twisted/www/checkout.py")
    failures = []
    for marker in (
        "frappe.log_error",
        "LT paused checkout API blocked",
        "NO_PURCHASE_CHECKOUT_MESSAGE",
        "NO_PURCHASE_CHECKOUT_STATUS",
        "contact_url",
    ):
        if marker not in source:
            failures.append(f"checkout.py missing loud/customer-safe no-purchase guard marker {marker}")
    return failures


def _checkout_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist(
        "locally_twisted.www.checkout.submit_guest_order",
        "locally_twisted.payments.stripe_session.create_session_for_sales_order",
    ))
    failures.extend(_doctype_presence(["Customer", "Contact", "Address", "Sales Order", "Payment Request"]))
    if not frappe.db.count("Payment Gateway Account"):
        failures.append("No Payment Gateway Account records exist")
    checkout_source = _read("locally_twisted/www/checkout.py")
    for marker in ("Customer", "Sales Order", "Payment Request", "create_session_for_sales_order"):
        if marker not in checkout_source:
            failures.append(f"checkout.py missing connection marker {marker}")
    return failures


def _checkout_loud_failure() -> list[str]:
    source = _read("locally_twisted/www/checkout.py")
    failures = []
    for marker in ("frappe.throw", "record_backend_failure", "checkout_notes_transfer"):
        if marker not in source:
            failures.append(f"checkout.py missing loud failure marker {marker}")
    return failures


def _payment_success_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(_callables_exist(
        "locally_twisted.www.payment_success.reconcile_paid_sales_order",
        "locally_twisted.verify.payment_success_reconciliation_contract.run",
    ))
    failures.extend(_doctype_presence(["Payment Request", "Payment Entry", "Sales Invoice", "Email Queue"]))
    source = _read("locally_twisted/www/payment_success.py")
    for marker in ("Payment Entry", "Sales Invoice", "sendmail", "operator"):
        if marker not in source:
            failures.append(f"payment_success.py missing connection marker {marker}")
    if not failures and run_runtime_contracts:
        result = frappe.get_attr("locally_twisted.verify.payment_success_reconciliation_contract.run")()
        if not result.get("ok"):
            failures.extend(result.get("failures") or ["payment success reconciliation contract failed"])
    failures.extend(_customer_email_policy_connected())
    return failures


def _customer_email_policy_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.verify.customer_email_policy_contract.run"))
    if failures:
        return failures

    result = frappe.get_attr("locally_twisted.verify.customer_email_policy_contract.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["customer_email_policy_contract.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("customer_email_policy_contract is not read-only")
    if result.get("send_allowed") is not False:
        failures.append("customer_email_policy_contract allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("customer_email_policy_contract allows mutations")

    expected = {
        "lead_auto_ack",
        "paid_order_receipt",
        "paid_order_operator_notification",
        "first_order_welcome",
        "paid_order_dynamic_contract",
    }
    surface_ids = {surface.get("id") for surface in result.get("checked_surfaces") or []}
    missing = sorted(expected - surface_ids)
    if missing:
        failures.append("customer email policy contract missing surfaces: " + ", ".join(missing))
    for surface in result.get("checked_surfaces") or []:
        if surface.get("passed") is not True:
            failures.append(f"customer email policy surface failed: {surface.get('id')}")
    return failures


def _payment_success_loud_failure() -> list[str]:
    source = "\n".join([
        _read("locally_twisted/www/payment_success.py"),
        _read("locally_twisted/www/thank_you.py"),
        _read("locally_twisted/www/thank_you.html"),
    ])
    failures = []
    for marker in (
        "raise_on_error",
        "record_backend_failure",
        "receipt_email_missing_recipient",
        "PaidOrderReconciliationError",
        "reconciliation=pending",
        "reconciliation_pending",
        "Receipt status",
    ):
        if marker not in source:
            failures.append(f"payment_success.py missing paid-order loud failure marker {marker}")
    return failures


def _stripe_webhook_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.payments.stripe_webhook.stripe_webhook"))
    source = _read("locally_twisted/payments/stripe_webhook.py")
    for marker in ("reconcile_paid_sales_order", "checkout.session.completed", "frappe.log_error"):
        if marker not in source:
            failures.append(f"stripe_webhook.py missing marker {marker}")
    return failures


def _stripe_amount_parity_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist(
        "locally_twisted.payments.stripe_session.stripe_line_items_for_sales_order",
        "locally_twisted.verify.stripe_amount_parity_contract.run",
    ))
    source = _read("locally_twisted/payments/stripe_session.py")
    for marker in ("grand_total", "amount_expected_cents", "stripe_line_items_for_sales_order"):
        if marker not in source:
            failures.append(f"stripe_session.py missing amount-parity marker {marker}")
    if not failures:
        result = frappe.get_attr("locally_twisted.verify.stripe_amount_parity_contract.run")()
        if not result.get("ok"):
            failures.extend(result.get("failures") or ["stripe amount parity contract failed"])
    return failures


def _stripe_amount_parity_loud_failure() -> list[str]:
    source = _read("locally_twisted/payments/stripe_session.py")
    if "frappe.throw" not in source and "raise" not in source:
        return ["stripe_session.py does not loudly fail when Stripe amount cannot match ERPNext total"]
    return []


def _stripe_webhook_loud_failure() -> list[str]:
    source = _read("locally_twisted/payments/stripe_webhook.py")
    if "frappe.log_error" not in source:
        return ["stripe webhook does not log webhook failures"]
    return []


def _invoice_connected() -> list[str]:
    failures = []
    print_format_name = "Locally Twisted Sales Invoice"
    if not frappe.db.exists("Print Format", print_format_name):
        failures.append(f"Missing Print Format {print_format_name}")
    if not frappe.db.exists("Letter Head", "Locally Twisted"):
        failures.append("Missing Letter Head Locally Twisted")
    default_format = getattr(frappe.get_meta("Sales Invoice"), "default_print_format", None)
    if default_format != print_format_name:
        failures.append(f"Sales Invoice default_print_format is {default_format!r}, expected {print_format_name!r}")
    return failures


def _outbound_documents_connected() -> list[str]:
    failures = []
    from locally_twisted.outbound_documents.registry import REQUIRED_DOCUMENT_IDS, OUTBOUND_DOCUMENTS, validate_registry

    result = validate_registry()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["outbound document registry verifier failed"])
    missing = sorted(set(REQUIRED_DOCUMENT_IDS) - set(OUTBOUND_DOCUMENTS))
    if missing:
        failures.append("Outbound registry missing ids: " + ", ".join(missing))
    return failures


def _outbound_document_send_readiness_connected(*, run_runtime_contracts: bool = True) -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.outbound_documents.send_readiness.evaluate_send_readiness",
            "locally_twisted.verify.outbound_document_send_readiness_contract.run",
        )
    )
    if not run_runtime_contracts:
        return failures

    result = frappe.get_attr("locally_twisted.verify.outbound_document_send_readiness_contract.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["outbound document send-readiness contract returned not ok"])
    if result.get("read_only") is not True:
        failures.append("outbound document send-readiness contract is not read-only")
    if result.get("send_allowed") is not False:
        failures.append("outbound document send-readiness contract allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("outbound document send-readiness contract allows mutations")
    expected = {
        "all_documents_block_without_required_fields",
        "all_documents_ready_when_complete",
        "payment_reminder_missing_payment_path_blocks_send",
        "vendor_w9_missing_secure_attachment_blocks_send",
        "record_level_blocker_writes_evidence",
    }
    scenario_ids = {scenario.get("id") for scenario in result.get("scenarios") or []}
    missing = sorted(expected - scenario_ids)
    if missing:
        failures.append("send-readiness contract missing scenarios: " + ", ".join(missing))
    for scenario in result.get("scenarios") or []:
        if scenario.get("passed") is not True:
            failures.append(f"send-readiness scenario failed: {scenario.get('id')}")
    return failures


def _outbound_document_send_readiness_loud_failure() -> list[str]:
    failures = []
    source = _read("locally_twisted/outbound_documents/send_readiness.py")
    for marker in (
        "blocked_send_until",
        "record_backend_failure",
        "correct_recipient_confirmed",
        "company_branding_confirmed",
        "payment_path",
    ):
        if marker not in source:
            failures.append(f"send_readiness.py missing marker {marker}")
    return failures


def _paperwork_status_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.verify.paperwork_status.run"))
    result = frappe.get_attr("locally_twisted.verify.paperwork_status.run")()
    if not result.get("ok"):
        failures.append("paperwork_status.run returned not ok")
    for key in (
        "invoice_review",
        "payment_request_review",
        "email_queue_review",
        "synthetic_readiness",
        "live_payment_readiness",
        "cutover_deferred_not_blocking",
    ):
        if key not in result:
            failures.append(f"paperwork_status missing {key}")
    if result.get("operating_mode") != "synthetic_without_live_credentials":
        failures.append("paperwork_status is not in synthetic_without_live_credentials mode")
    if result.get("synthetic_readiness", {}).get("live_inputs_required") is not False:
        failures.append("paperwork_status synthetic readiness requires live inputs")
    if result.get("live_payment_readiness", {}).get("checked") is not False:
        failures.append("paperwork_status should defer live payment checks during synthetic review")
    for item in result.get("attention_items") or []:
        if "live" in str(item).lower() and "block" in str(item).lower():
            failures.append("paperwork_status attention items still treat live readiness as a current blocker")
    return failures


def _unpaid_invoice_review_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.paperwork.unpaid_invoice_review.run"))
    result = frappe.get_attr("locally_twisted.paperwork.unpaid_invoice_review.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["unpaid_invoice_review.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("unpaid_invoice_review is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("unpaid_invoice_review allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("unpaid_invoice_review allows mutations")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("unpaid_invoice_review mutation guard changed")
    template_ids = set(result.get("template_ids") or [])
    for document_id in ("payment_reminder_draft", "statement_of_account"):
        if document_id not in template_ids:
            failures.append(f"unpaid_invoice_review missing template id {document_id}")
    for candidate in result.get("review_candidates") or []:
        for document in candidate.get("draft_documents") or []:
            if document.get("send_status") != "draft_only_not_sent":
                failures.append(f"{candidate.get('invoice')} has non-draft document {document.get('document_id')}")
    return failures


def _unpaid_invoice_draft_packet_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.paperwork.unpaid_invoice_draft_packet.run"))
    result = frappe.get_attr("locally_twisted.paperwork.unpaid_invoice_draft_packet.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["unpaid_invoice_draft_packet.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("unpaid_invoice_draft_packet is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("unpaid_invoice_draft_packet allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("unpaid_invoice_draft_packet allows mutations")
    if result.get("packet_type") != "unpaid_invoice_draft_packet":
        failures.append("unpaid_invoice_draft_packet returned the wrong packet_type")
    if result.get("source_review_surface") != "unpaid_invoice_review":
        failures.append("unpaid_invoice_draft_packet is not linked to unpaid_invoice_review")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("unpaid_invoice_draft_packet mutation guard changed")
    for packet in result.get("packets") or []:
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{packet.get('invoice')} packet is not draft-only")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{packet.get('invoice')} packet does not require human approval")
        section_ids = {section.get("document_id") for section in packet.get("sections") or []}
        if section_ids != {"payment_reminder_draft", "statement_of_account"}:
            failures.append(f"{packet.get('invoice')} packet sections are wrong: {sorted(section_ids)}")
        for section in packet.get("sections") or []:
            if section.get("send_status") != "draft_only_not_sent":
                failures.append(f"{packet.get('invoice')} {section.get('document_id')} is not draft-only")
            if "human_approval" not in str(section.get("do_not_send_without") or ""):
                failures.append(f"{packet.get('invoice')} {section.get('document_id')} lacks human approval gate")
    return failures


def _paperwork_review_digest_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.paperwork.paperwork_review_digest.run"))
    result = frappe.get_attr("locally_twisted.paperwork.paperwork_review_digest.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["paperwork_review_digest.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("paperwork_review_digest is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("paperwork_review_digest allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("paperwork_review_digest allows mutations")
    if result.get("digest_type") != "paperwork_review_digest":
        failures.append("paperwork_review_digest returned the wrong digest_type")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("paperwork_review_digest mutation guard changed")
    expected_sources = {
        "paperwork_status",
        "business_automation_index",
        "unpaid_invoice_review",
        "unpaid_invoice_draft_packet",
    }
    missing_sources = sorted(expected_sources - set(result.get("source_surfaces") or []))
    if missing_sources:
        failures.append("paperwork_review_digest missing source surfaces: " + ", ".join(missing_sources))
    sections = result.get("sections") or {}
    for key in (
        "unpaid_invoice_packets",
        "cutover_deferred_not_blocking",
        "setup_gaps",
        "partial_connections",
        "operations_readiness",
        "next_safe_actions",
    ):
        if key not in sections:
            failures.append(f"paperwork_review_digest missing section {key}")
    automation_summary = (result.get("source_summaries") or {}).get("business_automation_index") or {}
    if automation_summary.get("runtime_contracts_executed") is not False:
        failures.append("paperwork_review_digest executes runtime contracts through the automation index")
    if "live_payment_blockers" in sections:
        failures.append("paperwork_review_digest still labels live payment readiness as a current blocker")
    for packet in sections.get("unpaid_invoice_packets", {}).get("items", []):
        if packet.get("send_status") != "draft_only_not_sent":
            failures.append(f"{packet.get('invoice')} digest packet is not draft-only")
        if packet.get("human_approval_required") is not True:
            failures.append(f"{packet.get('invoice')} digest packet does not require human approval")
    return failures


def _customer_reminder_dry_run_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.paperwork.customer_reminder_dry_run.run"))
    result = frappe.get_attr("locally_twisted.paperwork.customer_reminder_dry_run.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["customer_reminder_dry_run.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("customer_reminder_dry_run is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("customer_reminder_dry_run allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("customer_reminder_dry_run allows mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("customer_reminder_dry_run enables customer delivery")
    if result.get("automatic_delivery_enabled") is not False:
        failures.append("customer_reminder_dry_run enables automatic delivery")
    if result.get("operating_mode") != "no_live_internal_review":
        failures.append("customer_reminder_dry_run returned the wrong operating_mode")
    if result.get("reminder_surface") != "customer_reminder_dry_run":
        failures.append("customer_reminder_dry_run returned the wrong reminder_surface")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("customer_reminder_dry_run mutation guard changed")
    sections = result.get("sections") or {}
    for key in ("internal_review_queue", "can_setup_without_live", "live_or_approval_required"):
        if key not in sections:
            failures.append(f"customer_reminder_dry_run missing section {key}")
    for item in result.get("queue_items") or []:
        if item.get("delivery_mode") != "internal_review_only":
            failures.append(f"{item.get('invoice')} reminder item is not internal-review-only")
        if item.get("send_status") != "draft_only_not_sent":
            failures.append(f"{item.get('invoice')} reminder item is not draft-only")
        if item.get("customer_delivery_enabled") is not False:
            failures.append(f"{item.get('invoice')} reminder item enables customer delivery")
    return failures


def _customer_reminder_review_report_connected() -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.paperwork.customer_reminder_review_report.run",
            "locally_twisted.locally_twisted.report.lt_customer_reminder_review.lt_customer_reminder_review.execute",
        )
    )
    result = frappe.get_attr("locally_twisted.paperwork.customer_reminder_review_report.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["customer_reminder_review_report.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("customer_reminder_review_report is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("customer_reminder_review_report allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("customer_reminder_review_report allows mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("customer_reminder_review_report enables customer delivery")
    if result.get("automatic_delivery_enabled") is not False:
        failures.append("customer_reminder_review_report enables automatic delivery")
    if result.get("report_type") != "customer_reminder_review_report":
        failures.append("customer_reminder_review_report returned the wrong report_type")
    if result.get("source_surface") != "customer_reminder_dry_run":
        failures.append("customer_reminder_review_report returned the wrong source_surface")
    if result.get("operating_mode") != "no_live_internal_review":
        failures.append("customer_reminder_review_report returned the wrong operating_mode")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("customer_reminder_review_report mutation guard changed")

    columns = {column.get("fieldname") for column in result.get("columns") or []}
    for fieldname in (
        "invoice",
        "customer_name",
        "recommended_cadence",
        "send_status",
        "blocked_customer_send_until",
    ):
        if fieldname not in columns:
            failures.append(f"customer_reminder_review_report missing column {fieldname}")

    groups = result.get("groups") or {}
    for key in ("review_now", "hold", "blocked_send"):
        if key not in groups:
            failures.append(f"customer_reminder_review_report missing group {key}")

    for row in result.get("rows") or []:
        if row.get("delivery_mode") != "internal_review_only":
            failures.append(f"{row.get('invoice')} reminder report row is not internal-review-only")
        if row.get("send_status") != "draft_only_not_sent":
            failures.append(f"{row.get('invoice')} reminder report row is not draft-only")
        if row.get("customer_delivery_enabled") is not False:
            failures.append(f"{row.get('invoice')} reminder report row enables customer delivery")
        if row.get("automatic_delivery_enabled") is not False:
            failures.append(f"{row.get('invoice')} reminder report row enables automatic delivery")

    report_name = "LT Customer Reminder Review"
    report_exists = bool(frappe.db.exists("Report", report_name))
    if not report_exists:
        failures.append(f"Missing Report {report_name}")
    else:
        report = frappe.get_doc("Report", report_name)
        expected_fields = {
            "report_name": report_name,
            "ref_doctype": "Sales Invoice",
            "report_type": "Script Report",
            "module": "Locally Twisted",
        }
        for key, expected in expected_fields.items():
            if getattr(report, key) != expected:
                failures.append(f"{report_name} {key} expected {expected}, found {getattr(report, key)}")
        if report.disabled:
            failures.append(f"{report_name} is disabled")

    if report_exists:
        desk_result = frappe.get_attr("frappe.desk.query_report.run")(report_name, filters={})
        desk_columns = {
            column.get("fieldname")
            for column in desk_result.get("columns") or []
            if isinstance(column, dict)
        }
        for fieldname in (
            "invoice",
            "customer_name",
            "recommended_cadence",
            "send_status",
            "blocked_customer_send_until",
        ):
            if fieldname not in desk_columns:
                failures.append(f"{report_name} Desk runner missing column {fieldname}")
        for row in desk_result.get("result") or []:
            if row.get("delivery_mode") != "internal_review_only":
                failures.append(f"{row.get('invoice')} Desk report row is not internal-review-only")
            if row.get("send_status") != "draft_only_not_sent":
                failures.append(f"{row.get('invoice')} Desk report row is not draft-only")
            if row.get("customer_delivery_enabled") is not False:
                failures.append(f"{row.get('invoice')} Desk report row enables customer delivery")
    return failures


def _quote_proposal_connected() -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.paperwork.quote_proposal_draft_packet.run",
            "locally_twisted.verify.quote_proposal_draft_packet_contract.run",
        )
    )
    result = frappe.get_attr("locally_twisted.paperwork.quote_proposal_draft_packet.run")()
    if not result.get("ok"):
        failures.extend(result.get("failures") or ["quote_proposal_draft_packet.run returned not ok"])
    if result.get("read_only") is not True:
        failures.append("quote_proposal_draft_packet is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("quote_proposal_draft_packet allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("quote_proposal_draft_packet allows mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("quote_proposal_draft_packet enables customer delivery")
    if result.get("packet_type") != "quote_proposal_draft_packet":
        failures.append("quote_proposal_draft_packet returned the wrong packet_type")
    if result.get("mutation_guard", {}).get("changed"):
        failures.append("quote_proposal_draft_packet mutation guard changed")

    contract = frappe.get_attr("locally_twisted.verify.quote_proposal_draft_packet_contract.run")()
    if not contract.get("ok"):
        failures.extend(contract.get("failures") or ["quote_proposal_draft_packet_contract.run returned not ok"])
    expected = {
        "normal_quote_review_packet",
        "corporate_proposal_review_packet",
        "missing_acceptance_path_blocks_readiness",
        "empty_review_ok",
        "malformed_send_ready_source_fails",
    }
    scenario_ids = {scenario.get("id") for scenario in contract.get("scenarios") or []}
    missing = sorted(expected - scenario_ids)
    if missing:
        failures.append("quote/proposal contract missing scenarios: " + ", ".join(missing))
    for scenario in contract.get("scenarios") or []:
        if scenario.get("passed") is not True:
            failures.append(f"quote/proposal scenario failed: {scenario.get('id')}")
    return failures


def _quote_proposal_loud_failure() -> list[str]:
    failures = []
    source = _read("locally_twisted/paperwork/quote_proposal_draft_packet.py")
    for marker in (
        "draft_only_not_sent",
        "evaluate_send_readiness",
        "human_review_required",
        "no_customer_send",
        "no_sales_invoice",
    ):
        if marker not in source:
            failures.append(f"quote_proposal_draft_packet.py missing marker {marker}")
    return failures


def _synthetic_business_pipeline_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.verify.synthetic_business_pipeline.run"))
    source = _read("locally_twisted/verify/synthetic_business_pipeline.py")
    for marker in (
        "synthetic_only",
        "live_inputs_required",
        "uses_real_customer_data",
        "cutover_deferred_not_blocking",
        "broken_piping",
    ):
        if marker not in source:
            failures.append(f"synthetic_business_pipeline.py missing marker {marker}")
    return failures


def _finance_workspace_connected() -> list[str]:
    failures = []
    if not frappe.db.exists("Workspace", "LT Accountant Home"):
        failures.append("Missing Workspace LT Accountant Home")
    for card in ("Unpaid Invoices", "Overdue Invoices", "Expected Payments", "Recent Paid Orders"):
        if not frappe.db.exists("Number Card", card):
            failures.append(f"Missing Number Card {card}")
    for doctype in ("Sales Invoice", "Payment Request", "Payment Entry", "Customer"):
        failures.extend(_doctype_presence([doctype]))
    if not frappe.db.exists("Report", "LT Customer Reminder Review"):
        failures.append("Missing Report LT Customer Reminder Review")
    else:
        workspace = frappe.get_doc("Workspace", "LT Accountant Home")
        shortcuts = {row.label: row for row in workspace.shortcuts}
        shortcut = shortcuts.get("Reminder Review Report")
        if not shortcut:
            failures.append("LT Accountant Home missing Reminder Review Report shortcut")
        elif shortcut.type != "Report" or shortcut.link_to != "LT Customer Reminder Review":
            failures.append("Reminder Review Report shortcut does not open LT Customer Reminder Review")
    return failures


def _quote_templates_exist() -> list[str]:
    failures = []
    for template in ("quote_estimate.md", "event_proposal_packet.md"):
        if not _app_path(f"locally_twisted/outbound_documents/templates/{template}").exists():
            failures.append(f"Missing template {template}")
    return failures


def _vendor_template_exists() -> list[str]:
    if not _app_path("locally_twisted/outbound_documents/templates/vendor_setup_w9_packet.md").exists():
        return ["Missing vendor_setup_w9_packet.md"]
    return []


def _vendor_setup_connected() -> list[str]:
    failures = []
    supplier_count = frappe.db.count("Supplier") if frappe.db.exists("DocType", "Supplier") else 0
    if supplier_count == 0:
        failures.append("No Supplier/vendor records exist")
    failures.append("No accounting-approved W-9 file registry is connected")
    return failures


def _manual_checkups_exist() -> list[str]:
    return _files_exist(
        "locally_twisted/verify/business_automation_index.py",
        "locally_twisted/verify/paperwork_status.py",
        "locally_twisted/verify/synthetic_business_pipeline.py",
    )


def _scheduled_checkups_connected() -> list[str]:
    hooks = _hooks()
    scheduler_events = getattr(hooks, "scheduler_events", None)
    if not scheduler_events:
        return ["No scheduler_events are connected for business checkups"]
    text = str(scheduler_events)
    required = ("business_automation_index", "maintenance.heartbeat")
    return [f"scheduler_events missing {name}" for name in required if name not in text]


def _maintenance_heartbeat_connected() -> list[str]:
    failures = []
    failures.extend(
        _callables_exist(
            "locally_twisted.maintenance.heartbeat.run",
            "locally_twisted.maintenance.heartbeat.boundary_report",
            "locally_twisted.maintenance.heartbeat.scheduled_light_checkup",
            "locally_twisted.maintenance.heartbeat.scheduled_full_checkup",
        )
    )
    if failures:
        return failures

    heartbeat_run = frappe.get_attr("locally_twisted.maintenance.heartbeat.run")
    result = heartbeat_run(include_heavy=False, write=False)
    if result.get("digest_type") != "client_operations_heartbeat":
        failures.append("maintenance heartbeat returned the wrong digest_type")
    for key, expected in {
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "sanitized": True,
        "raw_log_access": False,
        "customer_data_included": False,
    }.items():
        if result.get(key) is not expected:
            failures.append(f"maintenance heartbeat {key} expected {expected}, found {result.get(key)}")
    if result.get("ok") is not True:
        failures.append("maintenance heartbeat returned ok=false")

    required_topics = {
        "System Health",
        "New Leads",
        "Stale Leads",
        "Appointments",
        "Payments Paid",
        "Payments Late",
        "Documents Due",
        "Failed Automations",
        "Website Errors",
        "Security Events",
    }
    missing_topics = sorted(required_topics - set(result.get("notification_topics_available") or []))
    if missing_topics:
        failures.append("maintenance heartbeat missing topics: " + ", ".join(missing_topics))

    required_events = {
        "public_boot_asset_map",
        "maintenance_scheduler",
        "client_notification_preferences",
        "maintenance_role_boundary",
    }
    event_ids = {event.get("component") for event in result.get("events") or []}
    missing_events = sorted(required_events - event_ids)
    if missing_events:
        failures.append("maintenance heartbeat missing events: " + ", ".join(missing_events))
    for event in result.get("events") or []:
        if event.get("sanitized") is not True:
            failures.append(f"{event.get('component')} heartbeat event is not sanitized")
        if event.get("customer_data_included") is not False:
            failures.append(f"{event.get('component')} heartbeat event includes customer data")
        if event.get("raw_log_access") is not False:
            failures.append(f"{event.get('component')} heartbeat event exposes raw log access")

    tier_by_number = {
        tier.get("tier"): tier for tier in result.get("permission_tiers") or []
    }
    for tier in range(5):
        if tier not in tier_by_number:
            failures.append(f"maintenance heartbeat missing permission tier {tier}")
    if tier_by_number.get(4, {}).get("requires_approval") is not True:
        failures.append("tier 4 maintenance actions must require approval")

    boundary = frappe.get_attr("locally_twisted.maintenance.heartbeat.boundary_report")()
    if boundary.get("ok") is not True:
        failures.extend(boundary.get("failures") or ["maintenance boundary returned ok=false"])

    if not frappe.db.exists("Report", "LT Maintenance Heartbeat"):
        failures.append("Missing Report LT Maintenance Heartbeat")
    else:
        report = frappe.get_doc("Report", "LT Maintenance Heartbeat")
        if report.disabled:
            failures.append("LT Maintenance Heartbeat report is disabled")
        roles = {row.role for row in report.roles}
        if "LT Maintenance Admin Access" not in roles:
            failures.append("LT Maintenance Heartbeat report missing Maintenance Admin role")

    if frappe.db.exists("Report", "LT Maintenance Heartbeat"):
        desk_result = frappe.get_attr("frappe.desk.query_report.run")("LT Maintenance Heartbeat", filters={})
        desk_columns = {
            column.get("fieldname")
            for column in desk_result.get("columns") or []
            if isinstance(column, dict)
        }
        for fieldname in ("component", "status", "severity", "safe_summary", "action_needed", "source"):
            if fieldname not in desk_columns:
                failures.append(f"LT Maintenance Heartbeat Desk runner missing column {fieldname}")
        for row in desk_result.get("result") or []:
            for forbidden_field in ("safe_details", "digest_json", "traceback", "message"):
                if forbidden_field in row:
                    failures.append(f"LT Maintenance Heartbeat report exposes {forbidden_field}")

    hooks = _hooks()
    scheduler_text = str(getattr(hooks, "scheduler_events", None) or "")
    for marker in (
        "locally_twisted.maintenance.heartbeat.scheduled_light_checkup",
        "locally_twisted.maintenance.heartbeat.scheduled_full_checkup",
    ):
        if marker not in scheduler_text:
            failures.append(f"scheduler missing {marker.rsplit('.', 1)[-1]}")
    return failures


def _banking_connected() -> list[str]:
    failures = []
    if frappe.db.exists("DocType", "Bank Account") and frappe.db.count("Bank Account") == 0:
        failures.append("No Bank Account records exist")
    company_bank = frappe.db.get_value("Company", "Locally Twisted", "default_bank_account")
    if not company_bank:
        failures.append("Company default_bank_account is not set")
    return failures


def _payroll_connected() -> list[str]:
    failures = []
    installed = set(frappe.get_installed_apps())
    if "hrms" not in installed:
        failures.append("HRMS is not installed")
    for doctype in ("Payroll Entry", "Salary Slip", "Salary Structure"):
        if not frappe.db.exists("DocType", doctype):
            failures.append(f"Missing payroll DocType {doctype}")
    return failures


def _doctype_presence(doctypes: list[str]) -> list[str]:
    return [f"Missing DocType {doctype}" for doctype in doctypes if not frappe.db.exists("DocType", doctype)]


def _files_exist(*relative_paths: str) -> list[str]:
    failures = []
    for relative_path in relative_paths:
        if not _app_path(relative_path).exists():
            failures.append(f"Missing file {relative_path}")
    return failures


def _callables_exist(*dotted_paths: str) -> list[str]:
    failures = []
    for dotted_path in dotted_paths:
        try:
            frappe.get_attr(dotted_path)
        except Exception as exc:
            failures.append(f"Missing callable {dotted_path}: {type(exc).__name__}: {exc}")
    return failures


def _hooks():
    return importlib.import_module("locally_twisted.hooks")


def _read(relative_path: str) -> str:
    path = _app_path(relative_path)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _app_path(relative_path: str) -> Path:
    return APP_ROOT.parent / relative_path


def _checkups() -> list[dict[str, object]]:
    money_checkup = (
        {
            "id": "no_purchase_ecommerce_guard",
            "commands": [
                "python scripts/verify/ecommerce_pause_contract.py",
            ],
        }
        if _no_purchase_v1_active()
        else {
            "id": "money_path",
            "commands": [
                "python scripts/verify/payment_backend_config_contract.py",
                "python scripts/verify/stripe_amount_parity_contract.py",
                "python scripts/verify/payment_webhook_contract.py",
                "python scripts/verify/checkout_lead_conversion_contract.py",
                "python scripts/verify/checkout_fulfillment_contract.py",
                "python scripts/verify/payment_cascade_contract.py",
                "python scripts/verify/payment_success_reconciliation_contract.py",
            ],
        }
    )
    return [
        {
            "id": "contact_intake",
            "commands": [
                "python scripts/verify/lead_backend_intake_parity.py",
                "python scripts/verify/contact_service_logic.py --base-url http://localhost:8081",
                "python scripts/verify/contact_prefill.py --base-url http://localhost:8081",
                "python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter",
                "python scripts/verify/inquiry_upload_failure_contract.py",
            ],
        },
        {
            "id": "crm_operations",
            "commands": [
                "python scripts/verify/crm_pipeline_parity.py",
                "python scripts/verify/crm_stage_cascade.py",
                "python scripts/verify/backend_schema_inventory.py",
            ],
        },
        money_checkup,
        {
            "id": "synthetic_pipeline",
            "commands": [
                "python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json",
                "python scripts/verify/unpaid_invoice_draft_packet_contract.py",
                "python scripts/verify/customer_email_policy_contract.py",
                "python scripts/verify/customer_reminder_dry_run_contract.py",
                "python scripts/verify/customer_reminder_review_report_contract.py",
                "python scripts/verify/outbound_document_send_readiness_contract.py",
                "python scripts/verify/quote_proposal_draft_packet_contract.py",
                "python scripts/verify/render_outbound_document_previews.py --slug synthetic-pipeline-audit --no-open",
            ],
        },
        {
            "id": "paperwork_documents",
            "commands": [
                "python scripts/verify/customer_documents_contract.py",
                "python scripts/verify/customer_email_policy_contract.py",
                "python scripts/setup/sync_invoice_branding.py",
                "python scripts/verify/invoice_branding_contract.py",
                "python scripts/verify/outbound_documents_contract.py",
                "python scripts/verify/outbound_document_send_readiness_contract.py",
                "python scripts/verify/quote_proposal_draft_packet.py --report output/quote-proposal-draft-packet.json",
                "python scripts/verify/quote_proposal_draft_packet_contract.py",
                "python scripts/verify/paperwork_status.py --report output/paperwork-status.json",
                "python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json",
                "python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json",
                "python scripts/verify/unpaid_invoice_draft_packet_contract.py",
                "python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json",
                "python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json",
                "python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json",
            ],
        },
        {
            "id": "finance_admin",
            "commands": [
                "python scripts/verify/finance_inventory.py --json",
                "python scripts/verify/finance_inventory_contract.py",
                "python scripts/verify/finance_workspace_parity.py",
            ],
        },
        {
            "id": "maintenance_heartbeat",
            "commands": [
                "python scripts/setup/sync_maintenance_package.py",
                "python scripts/verify/frappe_public_boot_contract.py",
                "python scripts/verify/maintenance_heartbeat.py",
                "python scripts/verify/maintenance_admin_boundary.py",
            ],
        },
        {
            "id": "cutover_deferred_not_blocking",
            "commands": [
                "python scripts/verify/payment_launch_readiness.py --mode live",
            ],
        },
    ]


def _fake_data_contracts() -> list[dict[str, object]]:
    return [
        {
            "command": "python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json",
            "creates": [
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
            ],
            "cleanup": "runs in-memory or rollback-safe fake-data contracts; live cutover checks are deferred",
        },
        {
            "command": "python scripts/verify/record_level_failure_contract.py",
            "creates": ["Lead", "Comment", "Error Log"],
            "cleanup": "rolls back transaction and intercepts commit calls",
        },
        {
            "command": "python scripts/verify/inquiry_upload_failure_contract.py",
            "creates": ["Lead", "Communication", "Comment", "Error Log"],
            "cleanup": "rolls back transaction and intercepts commit calls",
        },
        {
            "command": "python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter",
            "creates": ["Lead", "Contact", "Task"],
            "cleanup": "deletes generated smoke Lead and linked cascade Task",
        },
        {
            "command": "python scripts/verify/crm_stage_cascade.py",
            "creates": ["Lead", "Task"],
            "cleanup": "deletes generated test records",
        },
        {
            "command": "python scripts/verify/checkout_lead_conversion_contract.py",
            "creates": ["Lead", "Contact", "Customer", "Sales Order", "Payment Request", "Task"],
            "cleanup": "rolls back transaction",
        },
        {
            "command": "python scripts/verify/payment_cascade_contract.py",
            "creates": ["Customer", "Contact", "Address", "Sales Order", "Payment Request", "Payment Entry", "Sales Invoice", "Email Queue"],
            "cleanup": "rolls back transaction and intercepts commit calls",
        },
        {
            "command": "python scripts/verify/payment_success_reconciliation_contract.py",
            "creates": [],
            "cleanup": "uses fake Stripe/reconciliation responses only",
        },
        {
            "command": "python scripts/verify/customer_documents_contract.py",
            "creates": ["Lead", "Communication", "Email Queue"],
            "cleanup": "rolls back generated records",
        },
        {
            "command": "python scripts/verify/customer_email_policy_contract.py",
            "creates": [],
            "cleanup": "static source contract; no database records created",
        },
        {
            "command": "python scripts/verify/unpaid_invoice_draft_packet_contract.py",
            "creates": [],
            "cleanup": "uses in-memory fake review payloads only",
        },
        {
            "command": "python scripts/verify/customer_reminder_dry_run_contract.py",
            "creates": [],
            "cleanup": "uses in-memory fake reminder queue payloads only",
        },
        {
            "command": "python scripts/verify/customer_reminder_review_report_contract.py",
            "creates": [],
            "cleanup": "uses in-memory fake reminder report payloads only",
        },
        {
            "command": "python scripts/verify/outbound_document_send_readiness_contract.py",
            "creates": ["Lead", "Comment", "Error Log"],
            "cleanup": "uses in-memory fake send-readiness payloads and rolls back record-level blocker evidence",
        },
        {
            "command": "python scripts/verify/quote_proposal_draft_packet_contract.py",
            "creates": [],
            "cleanup": "uses in-memory fake quote/proposal payloads only",
        },
    ]


def _scheduled_log_payload(result: dict[str, object]) -> dict[str, object]:
    return {
        "generated_at": result.get("generated_at"),
        "summary": result.get("summary"),
        "failures": result.get("failures"),
        "missing_needs_connection": [
            _row_summary(row)
            for row in result.get("missing_needs_connection", [])  # type: ignore[arg-type]
        ],
        "loud_failure_gaps": [
            _row_summary(row)
            for row in result.get("loud_failure_gaps", [])  # type: ignore[arg-type]
        ],
        "record_level_failures": result.get("record_level_failures"),
    }


def _row_summary(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": row.get("id"),
        "summary": row.get("summary"),
        "status": row.get("status"),
        "verifiers": row.get("verifiers"),
    }
