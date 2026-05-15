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
        "communication_copy_policy": _load_source(app_root / "communication_copy_policy.py"),
        "customer_email_theme": _load_source(app_root / "customer_email_theme.py"),
        "lead_cascade": _load_source(app_root / "lead_cascade.py"),
        "payment_success": _load_source(app_root / "www" / "payment_success.py"),
        "product_quote_customer_delivery": _load_source(app_root / "product_quote_customer_delivery.py"),
        "payment_cascade_contract": _load_source(app_root / "verify" / "payment_cascade_contract.py"),
        "patches": _load_source(app_root / "patches.txt"),
    }

    checks = [
        _check_copy_policy(sources["communication_copy_policy"]),
        _check_customer_email_theme(sources["customer_email_theme"]),
        _check_standard_footer_disabled(),
        _check_email_branding_patch(sources["patches"]),
        _check_email_function(
            surface_id="lead_auto_ack",
            source=sources["lead_cascade"],
            function_name="_send_auto_ack_email",
            reference_doctype="Lead",
            required_markers=(
                "form_confirmation_subject",
                "render_customer_email",
                "inline_images=customer_email_inline_images()",
                "reply_to=GENERAL_INBOX",
                "document_copy_kwargs",
                "external_audience=True",
                "primary_recipients=[email]",
                "policy_documents.lanes_for_lead(doc)",
                "_customer_submitted_details_block",
                "_compact_policy_link_block",
                "Here is what we received",
                "If anything you submitted appears incorrect",
                "Generally within less than 24 hours",
            ),
        ),
        _check_business_notification_function(sources["lead_cascade"]),
        _check_email_function(
            surface_id="paid_order_receipt",
            source=sources["payment_success"],
            function_name="_send_receipt_email",
            reference_doctype="Sales Order",
            required_markers=(
                "render_formal_customer_email",
                "inline_images=formal_email_inline_images()",
                "support_email=BILLING_INBOX",
                "reply_to=BILLING_INBOX",
                "document_copy_kwargs",
                "external_audience=True",
                "primary_recipients=[email]",
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
                "render_operator_email",
                "get_operator_email()",
                "Open order in desk",
                "Customer notes",
                "New paid order",
                "document_copy_kwargs",
                "external_audience=False",
                "primary_recipients=[recipient]",
            ),
        ),
        _check_email_function(
            surface_id="first_order_welcome",
            source=sources["payment_success"],
            function_name="_send_welcome_email_if_first_order",
            reference_doctype="Customer",
            required_markers=(
                "render_formal_customer_email",
                "inline_images=formal_email_inline_images()",
                "support_email=GENERAL_INBOX",
                "reply_to=GENERAL_INBOX",
                "document_copy_kwargs",
                "external_audience=True",
                "primary_recipients=[email]",
                "Welcome to Locally Twisted",
                "separate receipt email",
                "If anything changes on your end",
            ),
        ),
        _check_email_function(
            surface_id="product_quote_customer_delivery",
            source=sources["product_quote_customer_delivery"],
            function_name="send_product_quote_customer_review",
            reference_doctype="Quotation",
            required_markers=(
                "message = _customer_message",
                "bcc=[bcc]",
                "reply_to=GENERAL_INBOX",
                "inline_images=formal_email_inline_images()",
                "delayed=True",
            ),
        ),
        _check_function_markers(
            surface_id="product_quote_customer_message",
            source=sources["product_quote_customer_delivery"],
            function_name="_customer_message",
            required_markers=(
                "render_formal_customer_email",
                "support_email=GENERAL_INBOX",
                "Your Locally Twisted quote is ready for review.",
                "It does not charge a card or create an invoice.",
                "Reply to this email",
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


def _check_business_notification_function(source: str) -> dict[str, Any]:
    surface_id = "lead_business_notification"
    failures: list[str] = []
    helper_source, helper_node = _function_source(source, "_business_inquiry_photo_attachments")
    function_source, function_node = _function_source(source, "send_business_inquiry_notification")
    if not helper_source or helper_node is None:
        failures.append("missing function _business_inquiry_photo_attachments")
    if not function_source or function_node is None:
        failures.append("missing function send_business_inquiry_notification")
        return _surface(surface_id, failures)

    for marker in (
        "custom_inspiration_photos",
        '"File"',
        '"attached_to_doctype": "Lead"',
        '"attached_to_name": doc.name',
        '"file_url": ["in", sorted(photo_urls)]',
        'return [{"fid": row["name"]}',
    ):
        if marker not in helper_source:
            failures.append(f"_business_inquiry_photo_attachments missing marker {marker!r}")

    for marker in (
        "render_operator_email",
        "recipients=[BUSINESS_DOCUMENT_COPY]",
        "reply_to=customer_email or GENERAL_INBOX",
        "attachments = _business_inquiry_photo_attachments(doc)",
        "attachments=attachments",
        "document_copy_kwargs",
        "external_audience=False",
        "primary_recipients=[BUSINESS_DOCUMENT_COPY]",
        "BUSINESS_INQUIRY_SUBJECT_PREFIX",
    ):
        if marker not in function_source:
            failures.append(f"send_business_inquiry_notification missing marker {marker!r}")

    sendmail_calls = _sendmail_calls(function_node)
    if len(sendmail_calls) != 1:
        failures.append(f"send_business_inquiry_notification expected exactly one frappe.sendmail call, found {len(sendmail_calls)}")
        return _surface(surface_id, failures)

    call = sendmail_calls[0]
    kwargs = {keyword.arg: keyword.value for keyword in call.keywords if keyword.arg}
    forbidden = sorted((FORBIDDEN_SENDMAIL_KWARGS - {"attachments"}) & set(kwargs))
    if forbidden:
        failures.append(
            "send_business_inquiry_notification sendmail includes forbidden PDF/print kwargs: "
            + ", ".join(forbidden)
        )
    if not _keyword_equals_name(kwargs, "attachments", "attachments"):
        failures.append("send_business_inquiry_notification sendmail must attach only the owner photo refs")
    if not _keyword_equals_string(kwargs, "reference_doctype", "Lead"):
        failures.append("send_business_inquiry_notification sendmail does not reference Lead")
    if not _keyword_equals_false(kwargs, "now"):
        failures.append("send_business_inquiry_notification sendmail is not queued with now=False")
    if "recipients" not in kwargs:
        failures.append("send_business_inquiry_notification sendmail missing recipients")
    if "message" not in kwargs:
        failures.append("send_business_inquiry_notification sendmail missing message")
    return _surface(surface_id, failures)


def _check_function_markers(
    *,
    surface_id: str,
    source: str,
    function_name: str,
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
    return _surface(surface_id, failures)


def _check_customer_email_theme(source: str) -> dict[str, Any]:
    failures: list[str] = []
    for marker in (
        "LOGO_EMBED_NAME",
        "DOG_EMBED_NAME",
        "customer_email_inline_images",
        "lt-logo.png",
        "lt-balloon-dog-red-email-mirrored.png",
        "Locally Twisted 🎈 Thanks",
        "form_confirmation_subject",
        "render_formal_customer_email",
        "render_operator_email",
        "formal_email_inline_images",
        "#0E2240",
        "#B31B34",
        "#B89A5B",
        "max-width:600px",
        "hi@locallytwisted.com",
        "billing@locallytwisted.com",
    ):
        if marker not in source:
            failures.append(f"customer_email_theme.py missing marker {marker!r}")
    for forbidden in ("Sent via ERPNext", "frappe.io/erpnext"):
        if forbidden in source:
            failures.append(f"customer_email_theme.py contains forbidden footer marker {forbidden!r}")
    return _surface("customer_email_theme", failures)


def _check_standard_footer_disabled() -> dict[str, Any]:
    single_value = frappe.db.get_single_value("System Settings", "disable_standard_email_footer")
    default_value = frappe.db.get_default("disable_standard_email_footer")
    failures = []
    if str(single_value) not in {"1", "True", "true"}:
        failures.append("System Settings.disable_standard_email_footer must be enabled")
    if str(default_value) not in {"1", "True", "true"}:
        failures.append("frappe.db.get_default('disable_standard_email_footer') must resolve enabled")
    return _surface("standard_email_footer_disabled", failures)


def _check_email_branding_patch(source: str) -> dict[str, Any]:
    failures = []
    if "locally_twisted.patches.configure_email_branding" not in source:
        failures.append("patches.txt missing configure_email_branding patch")
    return _surface("email_branding_patch_registered", failures)


def _check_copy_policy(source: str) -> dict[str, Any]:
    failures = []
    for marker in (
        'PUBLIC_BUSINESS_ADDRESS = "hi@locallytwisted.com"',
        'BUSINESS_DOCUMENT_COPY = "locallytwisted@gmail.com"',
        '"hi@locallytwisted.com"',
        '"cameron@locallytwisted.com"',
        'return {"bcc": copies}',
        "routed_alias_copy_risks",
    ):
        if marker not in source:
            failures.append(f"communication_copy_policy.py missing marker {marker!r}")
    return _surface("company_copy_policy", failures)


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


def _keyword_equals_name(kwargs: dict[str, ast.AST], name: str, expected: str) -> bool:
    node = kwargs.get(name)
    return isinstance(node, ast.Name) and node.id == expected
