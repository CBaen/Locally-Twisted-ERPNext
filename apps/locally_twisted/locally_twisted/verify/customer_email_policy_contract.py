"""Static no-send contract for customer/operator email policy boundaries."""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import frappe
from frappe.utils import now_datetime


FORBIDDEN_SENDMAIL_KWARGS = {
    "attachments",
    "attach_print",
    "print_format",
    "print_letterhead",
    "as_pdf",
}


def run() -> dict[str, object]:
    app_root = Path(frappe.get_app_path("locally_twisted"))
    sources = {
        "lead_cascade": _load_source(app_root / "lead_cascade.py"),
        "payment_success": _load_source(app_root / "www" / "payment_success.py"),
        "payment_cascade_contract": _load_source(app_root / "verify" / "payment_cascade_contract.py"),
    }

    checks = [
        _check_email_function(
            surface_id="lead_auto_ack",
            source=sources["lead_cascade"],
            function_name="_send_auto_ack_email",
            reference_doctype="Lead",
            required_markers=(
                "policy_documents.customer_policy_block",
                "policy_documents.lanes_for_lead(doc)",
                "include_privacy=True",
                "Before you book",
                "We got your message",
            ),
        ),
        _check_email_function(
            surface_id="paid_order_receipt",
            source=sources["payment_success"],
            function_name="_send_receipt_email",
            reference_doctype="Sales Order",
            required_markers=(
                "This email is your receipt.",
                "policy_documents.customer_policy_block",
                "policy_documents.LANE_READY_TO_ORDER",
                "include_privacy=True",
                "receipt email cannot be sent",
            ),
        ),
        _check_email_function(
            surface_id="paid_order_operator_notification",
            source=sources["payment_success"],
            function_name="_send_operator_notification",
            reference_doctype="Sales Order",
            required_markers=(
                "get_operator_email()",
                "Open order in desk",
                "Customer notes",
                "New paid order",
            ),
        ),
        _check_email_function(
            surface_id="first_order_welcome",
            source=sources["payment_success"],
            function_name="_send_welcome_email_if_first_order",
            reference_doctype="Customer",
            required_markers=(
                "Welcome to Locally Twisted",
                "separate receipt email",
                "If anything changes on your end",
            ),
        ),
        _check_dynamic_contract(sources["payment_cascade_contract"]),
    ]

    failures = [
        f"{check['id']}: {failure}"
        for check in checks
        for failure in check["failures"]
    ]
    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "checked_surfaces": checks,
        "forbidden_sendmail_kwargs": sorted(FORBIDDEN_SENDMAIL_KWARGS),
        "boundaries": {
            "no_email_sent": True,
            "no_email_queue_created": True,
            "no_pdf_attachment": True,
            "no_invoice_mutation": True,
            "source_static_contract": True,
        },
        "failures": failures,
    }


def _check_email_function(
    *,
    surface_id: str,
    source: str,
    function_name: str,
    reference_doctype: str,
    required_markers: tuple[str, ...],
) -> dict[str, Any]:
    failures: list[str] = []
    function_source, function_node = _function_source(source, function_name)
    if not function_source or function_node is None:
        failures.append(f"missing function {function_name}")
        return _surface(surface_id, failures)

    for marker in required_markers:
        if marker not in function_source:
            failures.append(f"{function_name} missing marker {marker!r}")

    sendmail_calls = _sendmail_calls(function_node)
    if len(sendmail_calls) != 1:
        failures.append(f"{function_name} expected exactly one frappe.sendmail call, found {len(sendmail_calls)}")
        return _surface(surface_id, failures)

    call = sendmail_calls[0]
    kwargs = {keyword.arg: keyword.value for keyword in call.keywords if keyword.arg}
    forbidden = sorted(FORBIDDEN_SENDMAIL_KWARGS & set(kwargs))
    if forbidden:
        failures.append(f"{function_name} sendmail includes forbidden PDF/attachment kwargs: {', '.join(forbidden)}")

    if not _keyword_equals_string(kwargs, "reference_doctype", reference_doctype):
        failures.append(f"{function_name} sendmail does not reference {reference_doctype}")
    if not _keyword_equals_false(kwargs, "now"):
        failures.append(f"{function_name} sendmail is not queued with now=False")
    if "recipients" not in kwargs:
        failures.append(f"{function_name} sendmail missing recipients")
    if "message" not in kwargs:
        failures.append(f"{function_name} sendmail missing message")
    return _surface(surface_id, failures)


def _check_dynamic_contract(source: str) -> dict[str, Any]:
    failures = []
    for marker in (
        "customer receipt email missing policy text/link",
        "operator paid-order email is missing checkout notes",
        "missing first-order welcome Email Queue row",
        "second reconciliation created a duplicate customer receipt email",
    ):
        if marker not in source:
            failures.append(f"payment_cascade_contract.py missing marker {marker!r}")
    return _surface("paid_order_dynamic_contract", failures)


def _surface(surface_id: str, failures: list[str]) -> dict[str, Any]:
    return {"id": surface_id, "passed": not failures, "failures": failures}


def _load_source(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _function_source(source: str, function_name: str) -> tuple[str, ast.FunctionDef | None]:
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno]), node
    return "", None


def _sendmail_calls(function_node: ast.FunctionDef) -> list[ast.Call]:
    calls = []
    for node in ast.walk(function_node):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "sendmail":
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "frappe":
            calls.append(node)
    return calls


def _keyword_equals_string(kwargs: dict[str, ast.AST], name: str, expected: str) -> bool:
    node = kwargs.get(name)
    return isinstance(node, ast.Constant) and node.value == expected


def _keyword_equals_false(kwargs: dict[str, ast.AST], name: str) -> bool:
    node = kwargs.get(name)
    return isinstance(node, ast.Constant) and node.value is False
