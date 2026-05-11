"""Inventory customer contact points and verify their intake contracts."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
from typing import Any

import frappe

PUBLIC_BUSINESS_ADDRESS = "hi@locallytwisted.com"
LEGAL_ADDRESS = "legal@locallytwisted.com"
BILLING_ADDRESS = "billing@locallytwisted.com"
BUSINESS_DOCUMENT_COPY = "locallytwisted@gmail.com"
FORBIDDEN_STANDING_COPY = "cameron@locallytwisted.com"

MAILTO_ADDRESS_ROLES = {
    PUBLIC_BUSINESS_ADDRESS: "general inquiry",
    LEGAL_ADDRESS: "legal, privacy, terms, accessibility",
    BILLING_ADDRESS: "invoices, refunds, payments, accounts payable",
}

EXPECTED_MAILTO_BY_PATH = {
    "www/accessibility.html": {LEGAL_ADDRESS},
    "www/privacy.html": {LEGAL_ADDRESS},
    "www/terms_of_service.html": {LEGAL_ADDRESS, BILLING_ADDRESS},
    "www/refund_policy.html": {BILLING_ADDRESS},
    "www/faq.html": {PUBLIC_BUSINESS_ADDRESS, BILLING_ADDRESS},
}


def run() -> dict[str, Any]:
    app_root = Path(frappe.get_app_path("locally_twisted"))
    sources = {
        "book_form": _read(app_root / "templates" / "includes" / "book_form.html"),
        "inquiry_js": _read(app_root / "public" / "js" / "lt-inquiry-form-experience.js"),
        "book": _read(app_root / "www" / "book.py"),
        "checkout_html": _read(app_root / "www" / "checkout.html"),
        "checkout": _read(app_root / "www" / "checkout.py"),
        "privacy_html": _read(app_root / "www" / "privacy.html"),
        "newsletter_js": _read(app_root / "public" / "js" / "lt-newsletter.js"),
        "newsletter": _read(app_root / "api" / "newsletter.py"),
        "footer": _read(app_root / "templates" / "includes" / "footer" / "footer.html"),
        "navbar": _read(app_root / "templates" / "includes" / "navbar" / "navbar.html"),
        "event_playground": _read(app_root / "www" / "event_playground.html"),
        "lead_cascade": _read(app_root / "lead_cascade.py"),
        "payment_success": _read(app_root / "www" / "payment_success.py"),
        "copy_policy": _read(app_root / "communication_copy_policy.py"),
        "customer_documents_contract": _read(app_root / "verify" / "customer_documents_contract.py"),
        "payment_cascade_contract": _read(app_root / "verify" / "payment_cascade_contract.py"),
    }

    surfaces = [
        _inquiry_surface(sources),
        _checkout_surface(sources),
        _paid_order_message_surface(sources),
        _newsletter_surface(sources),
        _email_use_notice_surface(sources),
        _shop_search_surface(sources),
        _direct_link_surface(app_root),
        _product_cart_surface(app_root),
    ]
    copy_contract = _business_copy_contract(sources)

    failures = [
        f"{surface['id']}: {failure}"
        for surface in surfaces
        for failure in surface["failures"]
    ]
    failures.extend(f"business_copy: {failure}" for failure in copy_contract["failures"])

    return {
        "ok": not failures,
        "generated_at": datetime.utcnow().isoformat(),
        "read_only": True,
        "surface_count": len(surfaces),
        "surfaces": surfaces,
        "business_copy_contract": copy_contract,
        "failures": failures,
    }


def _inquiry_surface(sources: dict[str, str]) -> dict[str, Any]:
    failures = []
    failures.extend(_missing(
        sources["book_form"],
        (
            "data-form-contract=\"inquiry-v1\"",
            "locally_twisted.www.book.submit_book_inquiry",
            "#received",
        ),
    ))
    failures.extend(_missing(
        sources["inquiry_js"],
        (
            "FALLBACK_ERROR",
            "Tiny snag: your request did not send.",
            "parseServerError",
            "showError",
        ),
    ))
    failures.extend(_missing(
        sources["book"],
        (
            "\"doctype\": \"Lead\"",
            "\"custom_pipeline_stage\": \"New Inquiry\"",
            "\"custom_event_type\": _service_child_rows(services)",
            "\"custom_source_channel\": \"Website Form\"",
            "_record_inquiry_communication",
            "record_backend_failure",
            "frappe.log_error",
            "photo_uploads",
        ),
    ))
    failures.extend(_missing(
        sources["lead_cascade"],
        (
            "_ensure_contact_link",
            "_send_auto_ack_email",
            "stage_cascade.after_insert",
            "document_copy_kwargs",
        ),
    ))
    return _surface(
        "shared_inquiry_form",
        "Lead",
        ["/contact", "/balloon-twisting-and-face-painting", "/book redirect", "product quote links", "checkout quote handoff", "event playground handoff"],
        True,
        True,
        failures,
        "Creates Lead, Contact link, customer acknowledgment Email Queue, CRM Task cascade, and Lead timeline Communication.",
    )


def _checkout_surface(sources: dict[str, str]) -> dict[str, Any]:
    failures = []
    failures.extend(_missing(
        sources["checkout_html"],
        (
            "id=\"lt-checkout-form\"",
            "CHECKOUT_FALLBACK_ERROR",
            "Tiny snag: we could not start checkout just now.",
            "setFeedback('error'",
            "locally_twisted.www.checkout.submit_guest_order",
            "redirectToDeliveryQuote",
        ),
    ))
    failures.extend(_missing(
        sources["checkout"],
        (
            "\"doctype\": \"Customer\"",
            "\"doctype\": \"Contact\"",
            "\"doctype\": \"Address\"",
            "\"doctype\": \"Sales Order\"",
            "\"doctype\": \"Payment Request\"",
            "_record_order_notes",
            "record_backend_failure",
            "create_session_for_sales_order",
        ),
    ))
    return _surface(
        "checkout_order_form",
        "Customer, Contact, Address, Sales Order, Payment Request",
        ["/checkout", "/cart checkout"],
        True,
        True,
        failures,
        "Direct shop checkout does not create a new Lead; it creates order records and converts any prior linked inquiry Lead only after paid-order reconciliation.",
    )


def _paid_order_message_surface(sources: dict[str, str]) -> dict[str, Any]:
    failures = []
    failures.extend(_missing(
        sources["payment_success"],
        (
            "_send_receipt_email",
            "_send_operator_notification",
            "_send_welcome_email_if_first_order",
            "document_copy_kwargs",
            "receipt email cannot be sent",
            "record_backend_failure",
        ),
    ))
    if sources["payment_success"].count("document_copy_kwargs(") < 3:
        failures.append("payment_success.py does not route all three paid-order emails through document_copy_kwargs")
    failures.extend(_missing(
        sources["payment_cascade_contract"],
        (
            "email missing required copy recipient",
            "operator paid-order",
            "email missing required copy recipient",
            "first-order welcome",
            "should not copy routed alias loop",
        ),
    ))
    return _surface(
        "paid_order_messages",
        "Email Queue",
        ["paid receipt", "operator paid-order notification", "first-order welcome"],
        True,
        True,
        failures,
        "Paid-order emails are queued, no PDF attachment is required, and missing recipient cases record backend failure evidence.",
    )


def _newsletter_surface(sources: dict[str, str]) -> dict[str, Any]:
    failures = []
    failures.extend(_missing(
        sources["footer"],
        (
            "data-lt-newsletter",
            "data-lt-newsletter-error",
            "role=\"alert\"",
            "tel:+18012850860",
        ),
    ))
    failures.extend(_missing(
        sources["newsletter_js"],
        (
            "locally_twisted.api.newsletter.signup",
            "Tiny snag: we could not add your email just now.",
            "aria-live",
            "console.error",
        ),
    ))
    failures.extend(_missing(
        sources["newsletter"],
        (
            "\"doctype\": \"LT Newsletter Signup\"",
            "frappe.log_error",
            "UniqueValidationError",
        ),
    ))
    return _surface(
        "newsletter_signup",
        "LT Newsletter Signup",
        ["footer newsletter form"],
        True,
        False,
        failures,
        "Newsletter signup is a marketing opt-in record, not a CRM inquiry Lead and not an outbound customer/order email.",
    )


def _email_use_notice_surface(sources: dict[str, str]) -> dict[str, Any]:
    failures = []
    failures.extend(_missing(
        sources["checkout_html"],
        (
            "Email (for receipt, invoice, and order updates)",
            "separate from order emails",
            "We do not add checkout emails to marketing",
            "If you check the offers box above or join the newsletter",
        ),
    ))
    failures.extend(_missing(
        sources["footer"],
        (
            "Joining signs you up for marketing emails; order and invoice emails are separate.",
        ),
    ))
    failures.extend(_missing(
        sources["privacy_html"],
        (
            "Order emails and marketing emails",
            "We do not add that email to marketing lists",
            "Marketing emails include an unsubscribe option.",
        ),
    ))
    return _surface(
        "email_use_notice",
        "checkout email and newsletter opt-in copy",
        ["/checkout", "footer newsletter form", "/privacy"],
        False,
        False,
        failures,
        "Checkout email use is described as transactional/order-related, while newsletter and marketing emails require separate opt-in copy.",
    )


def _shop_search_surface(sources: dict[str, str]) -> dict[str, Any]:
    failures = _missing(
        sources["navbar"],
        (
            "lt-site-search-panel__form",
            "action=\"{% if ecommerce_paused %}/contact{% else %}/shop{% endif %}\"",
            "method=\"get\"",
        ),
    )
    return _surface(
        "shop_search",
        "querystring only",
        ["desktop/mobile shop search"],
        False,
        False,
        failures,
        "Search is navigation only. It should not create a Lead, customer record, or business email.",
    )


def _direct_link_surface(app_root: Path) -> dict[str, Any]:
    html_files = list((app_root / "www").glob("*.html")) + list((app_root / "templates").rglob("*.html"))
    mailtos: list[dict[str, str]] = []
    tels: list[dict[str, str]] = []
    seen_by_path: dict[str, set[str]] = {}
    failures: list[str] = []
    for path in html_files:
        text = _read(path)
        relative = _relative(app_root, path)
        for address in re.findall(r"mailto:([^\"'>?]+)", text, flags=re.I):
            normalized = address.strip().lower()
            mailtos.append({"path": relative, "address": normalized})
            seen_by_path.setdefault(relative, set()).add(normalized)
            if normalized not in MAILTO_ADDRESS_ROLES:
                failures.append(f"{relative} has unknown customer mailto:{normalized}")
        for phone in re.findall(r"tel:([^\"'>?]+)", text, flags=re.I):
            tels.append({"path": relative, "phone": phone.strip()})
    for relative, expected in EXPECTED_MAILTO_BY_PATH.items():
        actual = seen_by_path.get(relative, set())
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            failures.append(f"{relative} missing expected mailto links: {', '.join(missing)}")
        if unexpected:
            failures.append(f"{relative} has unexpected mailto links: {', '.join(unexpected)}")
    if not mailtos:
        failures.append("no customer mailto links found")
    if not tels:
        failures.append("no customer tel links found")
    return _surface(
        "direct_phone_email_links",
        "external phone/email client",
        ["mailto links", "tel links"],
        True,
        False,
        failures,
        "Direct links leave the site, so they cannot create CRM records or BCC automatically. Mailto links must use the approved role-based customer inbox map.",
        extra={"mailto_links": mailtos, "tel_link_count": len(tels), "approved_addresses": MAILTO_ADDRESS_ROLES},
    )


def _product_cart_surface(app_root: Path) -> dict[str, Any]:
    item_config = _read(app_root / "templates" / "generators" / "item" / "item_configure.html")
    cart = _read(app_root / "www" / "lt_cart.html")
    failures = []
    failures.extend(_missing(item_config, ("get_variant_media", "get_next_attribute_and_values")))
    failures.extend(_missing(cart, ("locally_twisted.api.cart.get_cart_items", "Please refresh the page or call")))
    return _surface(
        "product_and_cart_controls",
        "cart/session state only",
        ["product option controls", "/cart"],
        True,
        False,
        failures,
        "Product and cart controls are not messages. Checkout owns the order record and business-copy path.",
    )


def _business_copy_contract(sources: dict[str, str]) -> dict[str, Any]:
    failures = []
    if f'PUBLIC_BUSINESS_ADDRESS = "{PUBLIC_BUSINESS_ADDRESS}"' not in sources["copy_policy"]:
        failures.append(f"copy policy does not define {PUBLIC_BUSINESS_ADDRESS} as the public business address")
    if f'BUSINESS_DOCUMENT_COPY = "{BUSINESS_DOCUMENT_COPY}"' not in sources["copy_policy"]:
        failures.append(f"copy policy does not define {BUSINESS_DOCUMENT_COPY} as the document copy recipient")
    if "UNSAFE_ROUTED_COPY_ALIASES" not in sources["copy_policy"] or FORBIDDEN_STANDING_COPY not in sources["copy_policy"]:
        failures.append(f"copy policy does not explicitly guard {FORBIDDEN_STANDING_COPY} as an unsafe routed copy alias")
    for key in ("lead_cascade", "payment_success"):
        if "document_copy_kwargs" not in sources[key]:
            failures.append(f"{key} does not use document_copy_kwargs")
    for key in ("customer_documents_contract", "payment_cascade_contract"):
        if "missing required copy recipient" not in sources[key]:
            failures.append(f"{key} does not verify business copy recipients")
        if "should not copy routed alias loop" not in sources[key]:
            failures.append(f"{key} does not guard against routed alias copy loops")
    return {
        "public_business_address": PUBLIC_BUSINESS_ADDRESS,
        "business_copy": BUSINESS_DOCUMENT_COPY,
        "forbidden_standing_copy": FORBIDDEN_STANDING_COPY,
        "passed": not failures,
        "failures": failures,
    }


def _surface(
    surface_id: str,
    record_target: str,
    contact_points: list[str],
    customer_visible_failure: bool,
    business_copy_required: bool,
    failures: list[str],
    notes: str,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "id": surface_id,
        "passed": not failures,
        "record_target": record_target,
        "contact_points": contact_points,
        "customer_visible_failure": customer_visible_failure,
        "business_copy_required": business_copy_required,
        "notes": notes,
        "failures": failures,
    }
    if extra:
        row.update(extra)
    return row


def _missing(source: str, markers: tuple[str, ...]) -> list[str]:
    return [f"missing marker {marker!r}" for marker in markers if marker not in source]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _relative(app_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(app_root)).replace("\\", "/")
    except ValueError:
        return str(path)
