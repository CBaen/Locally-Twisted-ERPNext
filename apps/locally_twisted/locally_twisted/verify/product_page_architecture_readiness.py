"""Architecture readiness audit for LT reusable ERPNext product-page templates.

This is a status gate, not a migration runner. It maps GL's ecommerce-template
objective to evidence rows so a pile of passing proof contracts cannot be
confused with public ecommerce/import readiness.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import frappe
from frappe.utils import now_datetime


APP_ROOT = Path(frappe.get_app_path("locally_twisted"))
PASS = "pass"
BLOCKED = "blocked"
PARTIAL = "partial"
DEFERRED = "deferred"
INFO = "info"
CORE_ARCHITECTURE = "core_architecture"
BUSINESS_IMPORT_APPROVAL = "business_import_approval"
PUBLIC_REOPEN = "public_reopen"
OUT_OF_SCOPE_DEFERRED = "out_of_scope_deferred"


def run(source_catalog_path: str | None = None) -> dict[str, object]:
    """Return a JSON-safe architecture readiness report."""
    contract_results = {
        "page_architecture": _run_contract(
            "locally_twisted.verify.product_page_architecture_contract.run",
            kwargs={"source_catalog_path": source_catalog_path} if source_catalog_path else None,
        ),
        "runtime": _run_contract("locally_twisted.verify.product_page_runtime_contract.run"),
        "add_on_dependency": _run_contract("locally_twisted.verify.product_add_on_dependency_contract.run"),
        "quote_customization": _run_contract("locally_twisted.verify.product_quote_customization_contract.run"),
        "quote_operator_review": _run_contract("locally_twisted.verify.product_quote_operator_review_contract.run"),
        "quote_acceptance": _run_contract("locally_twisted.verify.product_quote_acceptance_contract.run"),
        "quote_customer_delivery": _run_contract("locally_twisted.verify.product_quote_customer_delivery_contract.run"),
        "quote_operator_send": _run_contract("locally_twisted.verify.product_quote_operator_send_control_contract.run"),
    }
    paused = _public_ecommerce_paused()
    criteria = _criteria(contract_results, paused)
    summary = Counter(row["status"] for row in criteria)
    summary_by_category = {
        category: dict(Counter(row["status"] for row in criteria if row.get("category") == category))
        for category in (CORE_ARCHITECTURE, BUSINESS_IMPORT_APPROVAL, PUBLIC_REOPEN, OUT_OF_SCOPE_DEFERRED)
    }
    blockers = [
        f"{row['id']}: {row['blocker']}"
        for row in criteria
        if row["status"] == BLOCKED and row.get("blocker")
    ]
    technical_architecture_blockers = [
        f"{row['id']}: {row['blocker']}"
        for row in criteria
        if row.get("category") == CORE_ARCHITECTURE and row["status"] == BLOCKED and row.get("blocker")
    ]
    import_reopen_blockers = [
        f"{row['id']}: {row['blocker']}"
        for row in criteria
        if row.get("category") in {BUSINESS_IMPORT_APPROVAL, PUBLIC_REOPEN}
        and row["status"] == BLOCKED
        and row.get("blocker")
    ]
    unexpected_contract_failures = [
        f"{name}: {'; '.join(result['failures'])}"
        for name, result in contract_results.items()
        if result["status"] != PASS
    ]
    technical_architecture_ok = not technical_architecture_blockers and not unexpected_contract_failures
    import_reopen_ok = technical_architecture_ok and not import_reopen_blockers
    return {
        "ok": import_reopen_ok,
        "technical_architecture_ok": technical_architecture_ok,
        "import_reopen_ok": import_reopen_ok,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "scope": "erpnext_frappe_product_page_template_architecture",
        "ok_meaning": (
            "true only when the core architecture and all business/import/public-reopen gates are clear; "
            "the public-reopen gate is separate from local ecommerce implementation readiness"
        ),
        "fake_products_are_evidence_only": True,
        "public_ecommerce_paused": paused,
        "finance_deferred": True,
        "summary": {
            PASS: summary.get(PASS, 0),
            BLOCKED: summary.get(BLOCKED, 0),
            PARTIAL: summary.get(PARTIAL, 0),
            DEFERRED: summary.get(DEFERRED, 0),
            INFO: summary.get(INFO, 0),
        },
        "summary_by_category": summary_by_category,
        "criteria": criteria,
        "contract_results": contract_results,
        "technical_architecture_blockers": technical_architecture_blockers,
        "import_reopen_blockers": import_reopen_blockers,
        "blockers": blockers,
        "unexpected_contract_failures": unexpected_contract_failures,
    }


def _criteria(contract_results: dict[str, dict[str, object]], public_ecommerce_paused: bool) -> list[dict[str, object]]:
    page_architecture = _contract_ok(contract_results, "page_architecture")
    runtime = _contract_ok(contract_results, "runtime")
    add_on_dependency = _contract_ok(contract_results, "add_on_dependency")
    quote_customization = _contract_ok(contract_results, "quote_customization")
    quote_operator_review = _contract_ok(contract_results, "quote_operator_review")
    quote_acceptance = _contract_ok(contract_results, "quote_acceptance")
    quote_customer_delivery = _contract_ok(contract_results, "quote_customer_delivery")
    quote_operator_send = _contract_ok(contract_results, "quote_operator_send")
    labels_ok = _plain_template_labels_present()
    dependency_helper_ok = _dependency_helper_contract_ok()

    return [
        _row(
            "research_and_plan_grounding",
            PASS,
            "The lane is grounded in the ERPNext/Frappe receiving-architecture synthesis and OpenClaw/Codex handoff framing.",
            evidence=[
                "C:/Users/baenb/.openclaw/workspace/projects/lightdeck-command-center/workstreams/locally-twisted-paid-work-cockpit.md",
                "research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md",
                "workstreams/erpnext-ecommerce-receiving-architecture.md",
                "capabilities/recipes/erpnext-ecommerce-receiving-architecture.md",
            ],
        ),
        _row(
            "two_reusable_template_types",
            PASS if runtime and labels_ok else BLOCKED,
            "The reusable types exist as logic classes, not product families: Ready-to-order page and Configurable product page.",
            blocker=None if runtime and labels_ok else "Product-page runtime or plain labels are not currently proven.",
            evidence=[
                "locally_twisted/product_page_labels.py",
                "locally_twisted/product_page_runtime.py",
                "locally_twisted/verify/product_page_runtime_contract.py",
            ],
            verifiers=["python scripts/verify/product_page_runtime_contract.py"],
        ),
        _row(
            "backend_driven_product_page_contract",
            PASS if page_architecture else BLOCKED,
            "Product pages have one generic receiving contract from source/ERPNext axis semantics to controls, versioned payload, resolver boundary, and document parity.",
            blocker=None if page_architecture else _contract_blocker(contract_results, "page_architecture"),
            evidence=[
                "locally_twisted/catalog_contract/product_page_architecture_contract.py",
                "locally_twisted/product_options.py",
                "locally_twisted/templates/generators/item/item_details.html",
                "locally_twisted/verify/product_page_architecture_contract.py",
            ],
            verifiers=[
                "python scripts/verify/product_page_architecture_contract_contract.py",
                "python scripts/verify/product_page_architecture_contract.py",
            ],
        ),
        _row(
            "line_level_order_invoice_preservation",
            PASS if runtime else BLOCKED,
            "Selected product meaning is stored on Quotation Item, Sales Order Item, and Sales Invoice Item fields.",
            blocker=None if runtime else _contract_blocker(contract_results, "runtime"),
            evidence=[
                "locally_twisted/product_page_runtime.py",
                "locally_twisted/product_quote_runtime.py",
            ],
            verifiers=["python scripts/verify/product_page_runtime_contract.py"],
        ),
        _row(
            "ready_to_order_internal_cart_checkout",
            PASS if runtime and add_on_dependency else BLOCKED,
            "The internal ready-to-order path can preserve configured cart lines, checkout lines, and the confirmed foil-number add-on.",
            blocker=None if runtime and add_on_dependency else _join_blockers(
                _contract_blocker(contract_results, "runtime"),
                _contract_blocker(contract_results, "add_on_dependency"),
            ),
            evidence=[
                "locally_twisted/product_page_runtime.py",
                "locally_twisted/templates/generators/item/item_configure.html",
                "locally_twisted/verify/product_add_on_dependency_contract.py",
            ],
            verifiers=[
                "python scripts/verify/product_page_runtime_contract.py",
                "python scripts/verify/cart_checkout_contract.py",
                "python scripts/verify/product_add_on_dependency_contract.py",
            ],
        ),
        _row(
            "quote_first_lead_to_draft_quotation",
            PASS if runtime and quote_customization else BLOCKED,
            "Configurable product pages preserve selected options, notes, and color recipes from product page to Lead and draft Quotation.",
            blocker=None if runtime and quote_customization else _join_blockers(
                _contract_blocker(contract_results, "runtime"),
                _contract_blocker(contract_results, "quote_customization"),
            ),
            evidence=[
                "locally_twisted/product_quote_runtime.py",
                "locally_twisted/verify/product_quote_customization_contract.py",
            ],
            verifiers=[
                "python scripts/verify/product_page_runtime_contract.py",
                "python scripts/verify/product_quote_customization_contract.py",
            ],
        ),
        _row(
            "accepted_quote_to_draft_sales_order",
            PASS if quote_acceptance else BLOCKED,
            "A human-approved product-page quote can create a draft Sales Order while preserving payloads and avoiding invoice/payment side effects.",
            blocker=None if quote_acceptance else _contract_blocker(contract_results, "quote_acceptance"),
            evidence=[
                "locally_twisted/product_quote_acceptance.py",
                "locally_twisted/www/quote_accept.py",
                "locally_twisted/www/quote_accept.html",
            ],
            verifiers=[
                "python scripts/verify/product_quote_acceptance_contract.py",
                "npm run test:quote-accept-experience",
            ],
        ),
        _row(
            "operator_quote_review_workflow",
            PASS if quote_operator_review else BLOCKED,
            "Internal product-page quote review reports customer-review readiness and blockers without creating orders, invoices, or payment requests.",
            blocker=None if quote_operator_review else _contract_blocker(contract_results, "quote_operator_review"),
            evidence=[
                "locally_twisted/product_quote_operator_review.py",
                "locally_twisted/verify/product_quote_operator_review_contract.py",
            ],
            verifiers=[
                "python scripts/verify/product_quote_operator_review.py --report output/product-quote-operator-review.json",
                "python scripts/verify/product_quote_operator_review_contract.py",
            ],
        ),
        _row(
            "customer_quote_delivery_bcc",
            PASS if quote_customer_delivery and quote_operator_send else BLOCKED,
            "Reviewed product-page quote approval links have a customer sender and operator Desk send control with required business BCC.",
            blocker=None if quote_customer_delivery and quote_operator_send else _join_blockers(
                _contract_blocker(contract_results, "quote_customer_delivery"),
                _contract_blocker(contract_results, "quote_operator_send"),
            ),
            evidence=[
                "locally_twisted/product_quote_customer_delivery.py",
                "locally_twisted/product_quote_operator_send.py",
                "locally_twisted/public/js/lt-product-quote-quotation.js",
            ],
            verifiers=[
                "python scripts/verify/product_quote_customer_delivery_contract.py",
                "python scripts/verify/product_quote_operator_send_control_contract.py",
            ],
        ),
        _row(
            "fail_loud_customer_and_operator_boundaries",
            PASS if runtime and quote_acceptance and quote_operator_send else BLOCKED,
            "Broken or incomplete paths block fake success with customer-safe copy and operator/developer evidence.",
            blocker=None if runtime and quote_acceptance and quote_operator_send else _join_blockers(
                _contract_blocker(contract_results, "runtime"),
                _contract_blocker(contract_results, "quote_acceptance"),
                _contract_blocker(contract_results, "quote_operator_send"),
            ),
            evidence=[
                "locally_twisted/failure_recorder.py",
                "locally_twisted/product_page_runtime.py",
                "locally_twisted/www/quote_accept.html",
            ],
            verifiers=[
                "python scripts/verify/record_level_failure_contract.py",
                "python scripts/verify/product_page_runtime_contract.py",
                "npm run test:quote-accept-experience",
            ],
        ),
        _row(
            "source_dependency_matrices",
            PASS if dependency_helper_ok else BLOCKED,
            "Source-backed dependency matrices can narrow options and fail loudly for impossible or unknown selections.",
            blocker=None if dependency_helper_ok else "Dependency helper proof failed inside Frappe.",
            evidence=[
                "locally_twisted/catalog_contract/dependency_rules.py",
                "locally_twisted/catalog_contract/models.py",
            ],
            verifiers=["python scripts/verify/product_page_dependency_contract.py"],
        ),
        _row(
            "add_on_subsystem_beyond_foil_number",
            PASS,
            "GL cleared the remaining source add-on approval block for commerce-lane testing.",
            category=BUSINESS_IMPORT_APPROVAL,
            evidence=[
                "locally_twisted/catalog_contract/addon_rules.py",
                "locally_twisted/catalog_contract/addon_review.py",
                "locally_twisted/product_page_runtime.py",
                "audits/catalog-import-audit-2026-05-08/22-product-add-on-approval-packet.md",
                "audits/catalog-import-audit-2026-05-08/22-product-add-on-approval-packet.json",
                "GL instruction 2026-05-10: unblock all business blocks",
            ],
            verifiers=[
                "python scripts/verify/product_add_on_dependency_contract.py",
                "python scripts/verify/product_add_on_approval_packet.py",
            ],
        ),
        _row(
            "source_price_import_readiness",
            PASS,
            "GL cleared the source price review block for commerce-lane testing.",
            category=BUSINESS_IMPORT_APPROVAL,
            evidence=[
                "locally_twisted/catalog_contract/price_review.py",
                "audits/catalog-import-audit-2026-05-08/21-product-page-price-enrichment-report.md",
                "audits/catalog-import-audit-2026-05-08/21-product-page-price-enrichment-candidates.json",
                "audits/catalog-import-audit-2026-05-08/24-product-page-price-review-packet.md",
                "audits/catalog-import-audit-2026-05-08/24-product-page-price-review-packet.json",
                "GL instruction 2026-05-10: unblock all business blocks",
            ],
            verifiers=[
                "python scripts/verify/product_page_price_enrichment_contract.py",
                "python scripts/verify/product_page_price_review_packet.py",
            ],
        ),
        _row(
            "source_media_gallery_readiness",
            PASS,
            "GL cleared the source media/gallery review block for commerce-lane testing.",
            category=BUSINESS_IMPORT_APPROVAL,
            evidence=[
                "locally_twisted/catalog_contract/media_classification.py",
                "audits/catalog-import-audit-2026-05-08/20-product-page-media-visibility-report.md",
                "audits/catalog-import-audit-2026-05-08/23-product-page-media-classification-packet.md",
                "audits/catalog-import-audit-2026-05-08/23-product-page-media-classification-packet.json",
                "GL instruction 2026-05-10: unblock all business blocks",
            ],
            verifiers=[
                "python scripts/verify/product_page_media_visibility_contract.py",
                "python scripts/verify/product_page_media_classification_packet.py",
            ],
        ),
        _row(
            "public_ecommerce_reopen",
            BLOCKED if public_ecommerce_paused else PASS,
            "Public shop, product, cart, checkout, and ready-to-order surfaces match the configured public exposure mode.",
            blocker=(
                "Public ecommerce live exposure is locked by site config; "
                "continue local build/test work under this safety lock."
                if public_ecommerce_paused
                else None
            ),
            category=PUBLIC_REOPEN,
            evidence=["locally_twisted/ecommerce_pause.py"],
            verifiers=[
                "python scripts/verify/ecommerce_pause_contract.py",
                "npm run test:checkout-experience",
            ],
        ),
        _row(
            "finance_bank_payment",
            DEFERRED,
            "Bank/finance/payment integration is explicitly backburnered and is not a current ecommerce-template blocker.",
            category=OUT_OF_SCOPE_DEFERRED,
            evidence=["CODING-HANDOFF.md", "locally-twisted-queue.md"],
        ),
    ]


def _row(
    row_id: str,
    status: str,
    summary: str,
    *,
    blocker: str | None = None,
    category: str = CORE_ARCHITECTURE,
    evidence: list[str] | None = None,
    verifiers: list[str] | None = None,
) -> dict[str, object]:
    return {
        "id": row_id,
        "status": status,
        "category": category,
        "summary": summary,
        "blocker": blocker,
        "evidence": evidence or [],
        "verifiers": verifiers or [],
    }


def _run_contract(method: str, *, kwargs: dict[str, object] | None = None) -> dict[str, object]:
    try:
        result = frappe.get_attr(method)(**(kwargs or {}))
    except Exception:
        return {"status": BLOCKED, "method": method, "failures": [frappe.get_traceback()]}
    if result.get("ok") is True:
        return {"status": PASS, "method": method, "failures": []}
    return {"status": BLOCKED, "method": method, "failures": list(result.get("failures") or ["not ok"])}


def _contract_ok(contract_results: dict[str, dict[str, object]], name: str) -> bool:
    return contract_results.get(name, {}).get("status") == PASS


def _contract_blocker(contract_results: dict[str, dict[str, object]], name: str) -> str:
    result = contract_results.get(name) or {}
    failures = result.get("failures") or []
    if not failures:
        return ""
    return f"{name}: {'; '.join(str(failure) for failure in failures[:3])}"


def _join_blockers(*blockers: str) -> str:
    return "; ".join(blocker for blocker in blockers if blocker)


def _public_ecommerce_paused() -> bool:
    from locally_twisted.ecommerce_pause import is_ecommerce_paused

    return bool(is_ecommerce_paused())


def _plain_template_labels_present() -> bool:
    from locally_twisted.product_page_labels import (
        COMMERCE_LANE_LABELS,
        PRODUCT_PAGE_TYPE_LABELS,
    )

    expected_values = {
        PRODUCT_PAGE_TYPE_LABELS.get("simple_product"),
        PRODUCT_PAGE_TYPE_LABELS.get("complex_custom_product"),
        COMMERCE_LANE_LABELS.get("checkout"),
        COMMERCE_LANE_LABELS.get("quote_first"),
    }
    if not {"Ready-to-order page", "Configurable product page"}.issubset(expected_values):
        return False
    internal_markers = ("simple_product", "complex_custom_product", "quote_first", "needs_review", "_")
    return all(
        isinstance(label, str)
        and label.strip()
        and not any(marker in label for marker in internal_markers)
        for label in expected_values
    )


def _dependency_helper_contract_ok() -> bool:
    from locally_twisted.catalog_contract.dependency_rules import available_options_for_selection
    from locally_twisted.catalog_contract.models import OptionDependencyMatrixContract

    matrix = OptionDependencyMatrixContract(
        axes=("Size", "Finish"),
        valid_combinations=(
            {"Size": "Small", "Finish": "Classic"},
            {"Size": "Large", "Finish": "Classic"},
            {"Size": "Large", "Finish": "Deluxe"},
        ),
    )
    narrowed = available_options_for_selection(matrix, {"Size": "Small"})
    if narrowed != {"Size": ("Small",), "Finish": ("Classic",)}:
        return False
    try:
        available_options_for_selection(matrix, {"Finish": "Impossible"})
    except ValueError:
        pass
    else:
        return False
    try:
        available_options_for_selection(matrix, {"Unknown": "Small"})
    except ValueError:
        return True
    return False
