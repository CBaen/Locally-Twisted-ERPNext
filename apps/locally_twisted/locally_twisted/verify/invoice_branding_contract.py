"""Verify Locally Twisted branded invoice print output."""
from __future__ import annotations

import re
from pathlib import Path

import frappe
from frappe.utils import now_datetime


PRINT_FORMAT_NAME = "Locally Twisted Sales Invoice"
LETTER_HEAD_NAME = "Locally Twisted"

REQUIRED_PRINT_FORMAT_MARKERS = [
    "lt-logo.png",
    "Locally Twisted",
    "Sales Invoice",
    "Balloon decor for Utah events",
    "billing@locallytwisted.com",
    "(801) 285-0860",
    "For accounts payable",
    "PO / reference",
    "Customer Service, Continued Event Support, and Repeat Orders:",
    "For new event support or repeat orders, email hi@locallytwisted.com.",
    "lt-support-banner",
    "lt-ap-strip",
    "lt-callout",
    'class="lt-ap-strip lt-callout"',
    'class="lt-policy-block lt-callout"',
    'class="lt-payment-note lt-callout"',
    "border-left: 3px solid #B8B8B8",
    "background: #F5F5F5",
    "@page",
    "Payment receipt",
    "Invoice terms",
    "Corporate invoicing",
    "/terms-of-service#corporate-invoicing",
    "/refund-policy#corporate-invoicing",
    "lt-invoice-number",
    "white-space: nowrap",
    "#111111",
    "lt-document-title .lt-ap-strip",
    ".print-format .lt-invoice .lt-items thead th",
    "padding: 8px 12px !important",
    ".lt-support-banner strong",
]

REQUIRED_RENDER_MARKERS = [
    "lt-logo.png",
    "Locally Twisted",
    "Sales Invoice",
    "Balloon decor for Utah events",
    "billing@locallytwisted.com",
    "(801) 285-0860",
    "For accounts payable",
    "PO / reference",
    "Customer Service, Continued Event Support, and Repeat Orders:",
    "For new event support or repeat orders, email hi@locallytwisted.com.",
    "lt-callout",
]

REQUIRED_RENDER_SECTION_MARKERS = [
    "Payment receipt",
    "Invoice terms",
    "Corporate invoicing",
]

FORBIDDEN_RENDER_MARKERS = [
    "Utah&#39;s balloon specialists",
    "Utah's balloon specialists",
    "#B31B34",
    "#B89A5B",
    "#0E2240",
    "#FAF7F2",
    "lt-invoice-summary",
    "border: 1px solid #CCCCCC",
    "Vendor setup",
    "W-9",
    "annual event support",
    "#2F2A26",
    "#272422",
    "#5A534D",
    "blue dog logo.png",
    "blue-dog",
    "dog logo",
    "dog-logo",
    "lt-dog",
    "balloon dog",
    "balloon-dog",
]

FORBIDDEN_PRINT_STYLE_MARKERS = [
    "#B31B34",
    "#B89A5B",
    "#0E2240",
    "#FAF7F2",
    "#2F2A26",
    "#272422",
    "#5A534D",
    "blue dog logo.png",
    "blue-dog",
    "dog logo",
    "dog-logo",
    "lt-dog",
    "balloon dog",
    "balloon-dog",
    "gold",
    "lt-gold",
    "gold-footer",
    "gold-bar",
    "gold bar",
    "gold rule",
    "brass",
    "berry",
    "navy",
]


def run() -> dict[str, object]:
    failures: list[str] = []
    evidence: dict[str, object] = {
        "generated_at": now_datetime().isoformat(),
        "print_format_name": PRINT_FORMAT_NAME,
        "letter_head_name": LETTER_HEAD_NAME,
    }

    print_format = _print_format()
    if not print_format:
        failures.append(f"Missing Print Format: {PRINT_FORMAT_NAME}")
    else:
        evidence["print_format"] = _compact_print_format(print_format)
        _check_print_format(print_format, failures)

    letter_head = _letter_head()
    if not letter_head:
        failures.append(f"Missing Letter Head: {LETTER_HEAD_NAME}")
    else:
        evidence["letter_head"] = _compact_letter_head(letter_head)
        _check_letter_head(letter_head, failures)

    property_setter = _default_print_property_setter()
    if not property_setter:
        failures.append("Sales Invoice default_print_format Property Setter is missing")
    else:
        evidence["property_setter"] = _compact_property_setter(property_setter)
        if property_setter.value != PRINT_FORMAT_NAME:
            failures.append(
                "Sales Invoice default_print_format Property Setter points to "
                f"{property_setter.value!r}, expected {PRINT_FORMAT_NAME!r}"
            )
        if property_setter.doctype_or_field != "DocType":
            failures.append("Sales Invoice default_print_format Property Setter must apply to the DocType")

    meta_default = getattr(frappe.get_meta("Sales Invoice"), "default_print_format", None)
    evidence["meta_default_print_format"] = meta_default
    if meta_default != PRINT_FORMAT_NAME:
        failures.append(
            f"Sales Invoice meta default_print_format is {meta_default!r}, expected {PRINT_FORMAT_NAME!r}"
        )

    _check_logo_asset(failures, evidence)

    sample_invoice = _sample_invoice()
    evidence["sample_invoice"] = sample_invoice.name if sample_invoice else None
    if not sample_invoice:
        failures.append("No Sales Invoice exists to render-check branded invoice output")
    elif print_format:
        _check_rendered_invoice(sample_invoice.name, failures, evidence)
        _check_default_rendered_invoice(sample_invoice.name, failures, evidence)

    return {
        "ok": not failures,
        "failures": failures,
        "evidence": evidence,
    }


def _print_format():
    if not frappe.db.exists("Print Format", PRINT_FORMAT_NAME):
        return None
    return frappe.get_doc("Print Format", PRINT_FORMAT_NAME)


def _letter_head():
    if not frappe.db.exists("Letter Head", LETTER_HEAD_NAME):
        return None
    return frappe.get_doc("Letter Head", LETTER_HEAD_NAME)


def _default_print_property_setter():
    name = frappe.db.get_value(
        "Property Setter",
        {
            "doc_type": "Sales Invoice",
            "property": "default_print_format",
        },
        "name",
    )
    if not name:
        return None
    return frappe.get_doc("Property Setter", name)


def _sample_invoice():
    rows = frappe.get_all(
        "Sales Invoice",
        fields=["name"],
        order_by="modified desc",
        limit_page_length=1,
    )
    return rows[0] if rows else None


def _check_print_format(doc, failures: list[str]) -> None:
    expected_fields = {
        "doc_type": "Sales Invoice",
        "module": "Locally Twisted",
        "standard": "No",
        "custom_format": 1,
        "disabled": 0,
        "print_format_type": "Jinja",
    }
    for fieldname, expected in expected_fields.items():
        actual = getattr(doc, fieldname, None)
        if actual != expected:
            failures.append(f"Print Format {fieldname} is {actual!r}, expected {expected!r}")

    text = "\n".join([doc.html or "", doc.css or ""])
    for marker in REQUIRED_PRINT_FORMAT_MARKERS:
        if marker not in text:
            failures.append(f"Print Format missing brand marker: {marker}")
    for marker in FORBIDDEN_PRINT_STYLE_MARKERS:
        if _contains_marker(text, marker):
            failures.append(f"Print Format still uses forbidden invoice branding marker: {marker}")
    if '<section class="lt-ap-strip">' in (doc.html or ""):
        failures.append("Invoice AP strip is still a standalone section instead of being attached to the document title")
    if not re.search(r'<div\b[^>]*class="[^"]*\blt-ap-strip\b', doc.html or ""):
        failures.append("Invoice AP strip is not nested in the document title as a summary panel")
    _check_invoice_callout_treatment(doc.html or "", doc.css or "", failures)
    _check_support_banner_treatment(doc.css or "", failures)


def _check_letter_head(doc, failures: list[str]) -> None:
    expected_fields = {
        "source": "HTML",
        "disabled": 0,
        "is_default": 1,
    }
    for fieldname, expected in expected_fields.items():
        actual = getattr(doc, fieldname, None)
        if actual != expected:
            failures.append(f"Letter Head {fieldname} is {actual!r}, expected {expected!r}")

    content = doc.content or ""
    for marker in ["Locally Twisted", "billing@locallytwisted.com", "(801) 285-0860", "lt-logo.png"]:
        if marker not in content:
            failures.append(f"Letter Head missing brand marker: {marker}")
    for marker in FORBIDDEN_PRINT_STYLE_MARKERS:
        if _contains_marker(content, marker):
            failures.append(f"Letter Head still uses forbidden invoice branding marker: {marker}")


def _check_invoice_callout_treatment(html: str, css: str, failures: list[str]) -> None:
    for class_name in ["lt-ap-strip", "lt-policy-block", "lt-payment-note"]:
        if not re.search(rf'class="[^"]*\b{class_name}\b[^"]*\blt-callout\b[^"]*"', html):
            failures.append(f"{class_name} is not using the shared gray invoice callout class")

    callout_rule = _css_rule_body(css, ".lt-callout")
    if not callout_rule:
        failures.append("Missing shared .lt-callout CSS rule for gray invoice callouts")
        return

    required_declarations = {
        "background": "#F5F5F5",
        "border-left": "3px solid #B8B8B8",
        "border-top": "0",
        "border-right": "0",
        "border-bottom": "0",
    }
    for property_name, expected_value in required_declarations.items():
        if not re.search(
            rf"{re.escape(property_name)}\s*:\s*{re.escape(expected_value)}\s*;",
            callout_rule,
            re.IGNORECASE,
        ):
            failures.append(f".lt-callout missing {property_name}: {expected_value}")


def _check_support_banner_treatment(css: str, failures: list[str]) -> None:
    banner_rule = _css_rule_body(css, ".lt-support-banner")
    if not banner_rule:
        failures.append("Missing .lt-support-banner CSS rule")
        return

    required_declarations = {
        "background": "#111111",
        "color": "#FFFFFF",
    }
    for property_name, expected_value in required_declarations.items():
        if not re.search(
            rf"{re.escape(property_name)}\s*:\s*{re.escape(expected_value)}\s*;",
            banner_rule,
            re.IGNORECASE,
        ):
            failures.append(f".lt-support-banner missing {property_name}: {expected_value}")

    strong_rule = _css_rule_body(css, ".lt-support-banner strong")
    if not strong_rule:
        failures.append("Missing .lt-support-banner strong CSS rule to keep bold support text white")
        return

    if not re.search(r"color\s*:\s*#FFFFFF\s*;", strong_rule, re.IGNORECASE):
        failures.append(".lt-support-banner strong missing color: #FFFFFF")


def _css_rule_body(css: str, selector: str) -> str | None:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>.*?)\}}", css, re.DOTALL)
    if not match:
        return None
    return match.group("body")


def _check_rendered_invoice(invoice_name: str, failures: list[str], evidence: dict[str, object]) -> None:
    try:
        html = frappe.get_print(
            "Sales Invoice",
            invoice_name,
            print_format=PRINT_FORMAT_NAME,
            letterhead=LETTER_HEAD_NAME,
        )
    except Exception as exc:  # pragma: no cover - surfaced through bench verifier output
        failures.append(f"Rendered invoice check failed: {type(exc).__name__}: {exc}")
        return

    evidence["rendered_length"] = len(html)
    evidence["rendered_contains_invoice_name"] = invoice_name in html
    if invoice_name not in html:
        failures.append(f"Rendered invoice missing invoice name: {invoice_name}")

    text = _normalize_html_text(html)
    for marker in REQUIRED_RENDER_MARKERS:
        if marker not in text and marker not in html:
            failures.append(f"Rendered invoice missing brand marker: {marker}")
    _check_rendered_invoice_section(text, html, "Rendered invoice", failures)
    _check_forbidden_render_markers(html, text, "Rendered invoice", failures)


def _check_default_rendered_invoice(invoice_name: str, failures: list[str], evidence: dict[str, object]) -> None:
    try:
        html = frappe.get_print(
            "Sales Invoice",
            invoice_name,
        )
    except Exception as exc:  # pragma: no cover - surfaced through bench verifier output
        failures.append(f"Default rendered invoice check failed: {type(exc).__name__}: {exc}")
        return

    evidence["default_rendered_length"] = len(html)
    text = _normalize_html_text(html)
    for marker in REQUIRED_RENDER_MARKERS:
        if marker not in text and marker not in html:
            failures.append(f"Default rendered invoice missing brand marker: {marker}")
    _check_rendered_invoice_section(text, html, "Default rendered invoice", failures)
    _check_forbidden_render_markers(html, text, "Default rendered invoice", failures)


def _check_logo_asset(failures: list[str], evidence: dict[str, object]) -> None:
    path = Path(frappe.get_app_path("locally_twisted", "public", "icons", "lt-logo.png"))
    evidence["logo_asset_path"] = str(path)
    evidence["logo_asset_exists"] = path.exists()
    if not path.exists():
        failures.append(f"Letter Head logo asset is missing: {path}")


def _check_forbidden_render_markers(
    html: str,
    text: str,
    label: str,
    failures: list[str],
) -> None:
    for marker in FORBIDDEN_RENDER_MARKERS:
        if _contains_marker(html, marker) or _contains_marker(text, marker):
            failures.append(f"{label} still contains retired copy: {marker}")


def _check_rendered_invoice_section(
    text: str,
    html: str,
    label: str,
    failures: list[str],
) -> None:
    if not any(marker in text or marker in html for marker in REQUIRED_RENDER_SECTION_MARKERS):
        failures.append(
            f"{label} missing invoice status section marker: "
            + ", ".join(REQUIRED_RENDER_SECTION_MARKERS)
        )


def _compact_print_format(doc) -> dict[str, object]:
    return {
        "name": doc.name,
        "doc_type": doc.doc_type,
        "module": doc.module,
        "standard": doc.standard,
        "custom_format": doc.custom_format,
        "disabled": doc.disabled,
        "print_format_type": doc.print_format_type,
        "html_length": len(doc.html or ""),
        "css_length": len(doc.css or ""),
    }


def _compact_letter_head(doc) -> dict[str, object]:
    return {
        "name": doc.name,
        "source": doc.source,
        "disabled": doc.disabled,
        "is_default": doc.is_default,
        "content_length": len(doc.content or ""),
    }


def _compact_property_setter(doc) -> dict[str, object]:
    return {
        "name": doc.name,
        "doc_type": doc.doc_type,
        "doctype_or_field": doc.doctype_or_field,
        "field_name": doc.field_name,
        "property": doc.property,
        "value": doc.value,
        "property_type": doc.property_type,
    }


def _normalize_html_text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _contains_marker(text: str, marker: str) -> bool:
    return marker.lower() in text.lower()
