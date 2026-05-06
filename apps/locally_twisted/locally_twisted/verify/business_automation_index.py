"""Read-only index of LT business automation surfaces and backend connections."""
from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Callable

import frappe
from frappe.utils import now_datetime


ROOT = Path(frappe.get_app_path("locally_twisted")).parent.parent
APP_ROOT = Path(frappe.get_app_path("locally_twisted"))


def run(
    include_digest: bool = True,
    include_synthetic: bool = True,
    include_customer_reminders: bool = True,
    include_customer_reminder_report: bool = True,
) -> dict[str, object]:
    """Return a JSON-safe automation map that fails loudly on broken required links."""
    surfaces = _surfaces(
        include_digest=include_digest,
        include_synthetic=include_synthetic,
        include_customer_reminders=include_customer_reminders,
        include_customer_reminder_report=include_customer_reminder_report,
    )
    rows = [_evaluate(surface) for surface in surfaces]
    failures = _required_failures(rows)

    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
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
    return failures


def _run_check(check: Callable[[], list[str]] | object) -> list[str]:
    if not callable(check):
        return ["internal verifier check is not callable"]
    try:
        return list(check())
    except Exception as exc:  # pragma: no cover - surfaced in bench output
        return [f"{type(exc).__name__}: {exc}"]


def _surfaces(
    include_digest: bool = True,
    include_synthetic: bool = True,
    include_customer_reminders: bool = True,
    include_customer_reminder_report: bool = True,
) -> list[dict[str, object]]:
    surfaces = [
        {
            "id": "public_contact_to_lead",
            "lane": "intake",
            "summary": "/contact exists and maps customer inquiry values into ERPNext Lead fields.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/www/contact.py",
                "locally_twisted/www/contact.html",
            ),
            "connected": _contact_connected,
            "loud_failure": _contact_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/www/contact.py",
                "apps/locally_twisted/locally_twisted/www/contact.html",
            ],
            "verifiers": [
                "python scripts/verify/lead_backend_intake_parity.py",
                "python scripts/verify/contact_service_logic.py --base-url http://localhost:8081",
                "python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter",
            ],
            "creates_fake_data": True,
        },
        {
            "id": "lead_contact_ack_cascade",
            "lane": "intake",
            "summary": "Lead insert cascades into Contact dedup/link, customer acknowledgment email, and first operational Task.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/lead_cascade.py",
                "locally_twisted/stage_cascade.py",
                "locally_twisted/policy_documents.py",
            ),
            "connected": _lead_cascade_connected,
            "loud_failure": _lead_cascade_loud_failure,
            "evidence": [
                "apps/locally_twisted/locally_twisted/hooks.py",
                "apps/locally_twisted/locally_twisted/lead_cascade.py",
                "apps/locally_twisted/locally_twisted/stage_cascade.py",
            ],
            "verifiers": [
                "python scripts/verify/customer_documents_contract.py",
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
            "id": "guest_checkout_to_payment_request",
            "lane": "money",
            "summary": "Guest checkout creates or links Customer, Contact, Address, Sales Order, Payment Request, and Stripe redirect.",
            "required_for_launch": True,
            "exists": lambda: _files_exist(
                "locally_twisted/www/checkout.py",
                "locally_twisted/payments/stripe_session.py",
            ),
            "connected": _checkout_connected,
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
        },
        {
            "id": "payment_success_paid_order_cascade",
            "lane": "money",
            "summary": "Paid checkout reconciles Payment Request, Payment Entry, Sales Invoice, receipt email, operator notification, and welcome email.",
            "required_for_launch": True,
            "exists": lambda: _files_exist("locally_twisted/www/payment_success.py"),
            "connected": _payment_success_connected,
            "loud_failure": _payment_success_loud_failure,
            "evidence": ["apps/locally_twisted/locally_twisted/www/payment_success.py"],
            "verifiers": [
                "python scripts/verify/payment_cascade_contract.py",
                "python scripts/verify/customer_documents_contract.py",
            ],
            "creates_fake_data": True,
        },
        {
            "id": "stripe_amount_parity",
            "lane": "money",
            "summary": "Stripe Checkout Session line items must equal the ERPNext Sales Order and Payment Request amount.",
            "required_for_launch": True,
            "exists": lambda: _files_exist("locally_twisted/payments/stripe_session.py"),
            "connected": _stripe_amount_parity_connected,
            "loud_failure": _stripe_amount_parity_loud_failure,
            "evidence": ["apps/locally_twisted/locally_twisted/payments/stripe_session.py"],
            "verifiers": ["python scripts/verify/stripe_amount_parity_contract.py"],
        },
        {
            "id": "stripe_webhook_reconciliation",
            "lane": "money",
            "summary": "Stripe webhook can reconcile paid Sales Orders through the same paid-order helper.",
            "required_for_launch": True,
            "exists": lambda: _files_exist("locally_twisted/payments/stripe_webhook.py"),
            "connected": _stripe_webhook_connected,
            "loud_failure": _stripe_webhook_loud_failure,
            "evidence": ["apps/locally_twisted/locally_twisted/payments/stripe_webhook.py"],
            "verifiers": [
                "python scripts/verify/payment_webhook_contract.py",
                "python scripts/verify/payment_launch_readiness.py",
            ],
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
            "summary": "No-live customer reminder review report exposes table rows and groups for a future Desk page or internal-only schedule.",
            "required_for_launch": False,
            "exists": lambda: _files_exist("locally_twisted/paperwork/customer_reminder_review_report.py"),
            "connected": _customer_reminder_review_report_connected,
            "loud_failure": lambda: [],
            "evidence": [
                "apps/locally_twisted/locally_twisted/paperwork/customer_reminder_review_report.py",
                "scripts/verify/customer_reminder_review_report.py",
                "scripts/verify/customer_reminder_review_report_contract.py",
            ],
            "verifiers": [
                "python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json",
                "python scripts/verify/customer_reminder_review_report_contract.py",
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
            "summary": "Quote/proposal source templates exist, but no Quotation-to-PDF generation or approval queue is wired yet.",
            "required_for_launch": False,
            "exists": _quote_templates_exist,
            "connected": lambda: ["No Quotation/proposal generator is connected to ERPNext records yet."],
            "loud_failure": lambda: [],
            "future_connection": "Wire Lead/Quotation to quote_estimate and event_proposal_packet review drafts.",
            "verifiers": ["python scripts/verify/outbound_documents_contract.py"],
        },
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


def _contact_connected() -> list[str]:
    failures = []
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
    return failures


def _contact_loud_failure() -> list[str]:
    source = "\n".join([
        _read("locally_twisted/www/contact.py"),
        _read("locally_twisted/www/book.py"),
    ])
    failures = []
    if "frappe.throw" not in source:
        failures.append("contact.py has no frappe.throw loud-failure path visible in source")
    for marker in ("email_id", "custom_event_type"):
        if marker not in source:
            failures.append(f"contact.py source missing required mapping marker {marker}")
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
    return failures


def _lead_cascade_loud_failure() -> list[str]:
    source = _read("locally_twisted/lead_cascade.py")
    failures = []
    if "frappe.log_error" not in source:
        failures.append("lead_cascade does not log cascade exceptions")
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
    for marker in ("frappe.throw", "raise", "frappe.log_error"):
        if marker in source:
            break
    else:
        failures.append("checkout.py has no visible throw/raise/log loud-failure path")
    return failures


def _payment_success_connected() -> list[str]:
    failures = []
    failures.extend(_callables_exist("locally_twisted.www.payment_success.reconcile_paid_sales_order"))
    failures.extend(_doctype_presence(["Payment Request", "Payment Entry", "Sales Invoice", "Email Queue"]))
    source = _read("locally_twisted/www/payment_success.py")
    for marker in ("Payment Entry", "Sales Invoice", "sendmail", "operator"):
        if marker not in source:
            failures.append(f"payment_success.py missing connection marker {marker}")
    return failures


def _payment_success_loud_failure() -> list[str]:
    source = _read("locally_twisted/www/payment_success.py")
    if "raise_on_error" not in source:
        return ["payment_success reconciliation does not expose raise_on_error for contracts"]
    return []


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
        "next_safe_actions",
    ):
        if key not in sections:
            failures.append(f"paperwork_review_digest missing section {key}")
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
    failures.extend(_callables_exist("locally_twisted.paperwork.customer_reminder_review_report.run"))
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
    required = ("business_automation_index",)
    return [f"scheduler_events missing {name}" for name in required if name not in text]


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
    return [
        {
            "id": "contact_intake",
            "commands": [
                "python scripts/verify/lead_backend_intake_parity.py",
                "python scripts/verify/contact_service_logic.py --base-url http://localhost:8081",
                "python scripts/verify/contact_prefill.py --base-url http://localhost:8081",
                "python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter",
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
        {
            "id": "money_path",
            "commands": [
                "python scripts/verify/payment_backend_config_contract.py",
                "python scripts/verify/stripe_amount_parity_contract.py",
                "python scripts/verify/payment_webhook_contract.py",
                "python scripts/verify/checkout_lead_conversion_contract.py",
                "python scripts/verify/checkout_fulfillment_contract.py",
                "python scripts/verify/payment_cascade_contract.py",
            ],
        },
        {
            "id": "synthetic_pipeline",
            "commands": [
                "python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json",
                "python scripts/verify/unpaid_invoice_draft_packet_contract.py",
                "python scripts/verify/customer_reminder_dry_run_contract.py",
                "python scripts/verify/customer_reminder_review_report_contract.py",
                "python scripts/verify/render_outbound_document_previews.py --slug synthetic-pipeline-audit --no-open",
            ],
        },
        {
            "id": "paperwork_documents",
            "commands": [
                "python scripts/verify/customer_documents_contract.py",
                "python scripts/setup/sync_invoice_branding.py",
                "python scripts/verify/invoice_branding_contract.py",
                "python scripts/verify/outbound_documents_contract.py",
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
            "command": "python scripts/verify/customer_documents_contract.py",
            "creates": ["Lead", "Communication", "Email Queue"],
            "cleanup": "rolls back generated records",
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
    }


def _row_summary(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": row.get("id"),
        "summary": row.get("summary"),
        "status": row.get("status"),
        "verifiers": row.get("verifiers"),
    }
