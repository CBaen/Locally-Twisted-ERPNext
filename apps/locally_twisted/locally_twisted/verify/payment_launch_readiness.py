"""Payment launch-readiness verifier.

This checks non-secret configuration and ERPNext structure needed before a
real Stripe checkout test or live cutover. It does not call Stripe, create
orders, or print secrets.
"""
from __future__ import annotations

import frappe


class ContractFail(Exception):
    pass


def run(mode="local"):
    try:
        return _run_contract(mode=(mode or "local").strip().lower())
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}


def _run_contract(mode):
    if mode not in {"local", "live"}:
        raise ContractFail(f"unknown mode {mode!r}; expected 'local' or 'live'")

    from locally_twisted.payments.settings import (
        get_operator_email,
        get_payment_gateway_account,
        get_stripe_payment_method_configuration,
        get_stripe_settings_name,
    )

    failures = []
    warnings = []

    stripe_settings_name = get_stripe_settings_name()
    payment_gateway_account = get_payment_gateway_account()
    payment_method_configuration = get_stripe_payment_method_configuration()
    operator_email = get_operator_email()

    stripe = _stripe_settings(stripe_settings_name)
    gateway = _payment_gateway_account(payment_gateway_account)
    webshop = _webshop_settings()
    outgoing_email = _outgoing_email_account()

    if not stripe:
        failures.append(f"Stripe Settings {stripe_settings_name!r} does not exist")
        stripe_mode = "missing"
    else:
        stripe_mode = _publishable_key_mode(stripe.get("publishable_key"))
        if stripe_mode == "missing":
            failures.append(f"Stripe Settings {stripe_settings_name!r} has no publishable key")
        elif stripe_mode == "unknown":
            failures.append(
                f"Stripe Settings {stripe_settings_name!r} publishable key is not a pk_test_ or pk_live_ key"
            )
        secret_mode = _secret_key_mode(stripe_settings_name)
        if secret_mode == "missing":
            failures.append(f"Stripe Settings {stripe_settings_name!r} has no secret key")
        elif secret_mode == "unknown":
            failures.append(
                f"Stripe Settings {stripe_settings_name!r} secret key is not an sk_test_ or sk_live_ key"
            )
        elif stripe_mode in {"test", "live"} and secret_mode != stripe_mode:
            failures.append(
                f"Stripe Settings {stripe_settings_name!r} publishable key mode is {stripe_mode}, secret key mode is {secret_mode}"
            )

    if not gateway:
        failures.append(f"Payment Gateway Account {payment_gateway_account!r} does not exist")
    else:
        if gateway.get("currency") != "USD":
            failures.append(
                f"Payment Gateway Account {payment_gateway_account!r} currency is {gateway.get('currency')!r}, expected 'USD'"
            )
        if not gateway.get("payment_account"):
            failures.append(
                f"Payment Gateway Account {payment_gateway_account!r} has no payment account"
            )

    if str(webshop.get("enable_checkout")) != "1":
        failures.append("Webshop Settings enable_checkout is not enabled")

    webshop_gateway = webshop.get("payment_gateway_account")
    if webshop_gateway and webshop_gateway != payment_gateway_account:
        failures.append(
            f"Webshop Settings payment_gateway_account is {webshop_gateway!r}, but checkout resolves {payment_gateway_account!r}"
        )

    if not _looks_like_email(operator_email):
        failures.append(f"operator email {operator_email!r} does not look valid")

    if not outgoing_email:
        failures.append("no outgoing Email Account is enabled")

    webhook_secret_configured = bool(frappe.conf.get("stripe_webhook_signing_secret"))
    if not webhook_secret_configured:
        failures.append("stripe_webhook_signing_secret is not set in site_config")

    if not payment_method_configuration:
        failures.append("Stripe payment method configuration is empty")
    elif not str(payment_method_configuration).startswith("pmc_"):
        failures.append(
            f"Stripe payment method configuration {payment_method_configuration!r} does not start with 'pmc_'"
        )

    if mode == "live":
        _check_live_mode_requirements(
            failures,
            warnings,
            stripe_mode=stripe_mode,
            stripe_settings_name=stripe_settings_name,
            payment_gateway_account=payment_gateway_account,
            payment_method_configuration=payment_method_configuration,
            operator_email=operator_email,
        )
    else:
        if stripe_mode == "test":
            warnings.append("local mode is using Stripe test keys; run with --mode live before cutover")

    return {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "mode": mode,
        "stripe_mode": stripe_mode,
        "stripe_settings_name": stripe_settings_name,
        "payment_gateway_account": payment_gateway_account,
        "payment_gateway_currency": gateway.get("currency") if gateway else None,
        "webshop_checkout_enabled": str(webshop.get("enable_checkout")) == "1",
        "operator_email": operator_email,
        "webhook_secret_configured": webhook_secret_configured,
        "outgoing_email_account": outgoing_email.get("name") if outgoing_email else None,
    }


def _stripe_settings(name):
    return frappe.db.get_value(
        "Stripe Settings",
        name,
        ["name", "gateway_name", "publishable_key"],
        as_dict=True,
    )


def _payment_gateway_account(name):
    return frappe.db.get_value(
        "Payment Gateway Account",
        name,
        ["name", "payment_gateway", "payment_account", "currency", "is_default"],
        as_dict=True,
    )


def _webshop_settings():
    doc = frappe.get_single("Webshop Settings")
    return {
        "enable_checkout": doc.get("enable_checkout"),
        "payment_gateway_account": doc.get("payment_gateway_account"),
        "payment_success_url": doc.get("payment_success_url"),
    }


def _outgoing_email_account():
    rows = frappe.get_all(
        "Email Account",
        filters={"enable_outgoing": 1},
        fields=["name", "email_id", "default_outgoing"],
        order_by="default_outgoing desc, name asc",
        limit=1,
    )
    return rows[0] if rows else None


def _publishable_key_mode(key):
    key = (key or "").strip()
    if not key:
        return "missing"
    if key.startswith("pk_test_"):
        return "test"
    if key.startswith("pk_live_"):
        return "live"
    return "unknown"


def _secret_key_mode(stripe_settings_name):
    secret = frappe.get_doc("Stripe Settings", stripe_settings_name).get_password(
        "secret_key", raise_exception=False
    )
    secret = (secret or "").strip()
    if not secret:
        return "missing"
    if secret.startswith("sk_test_"):
        return "test"
    if secret.startswith("sk_live_"):
        return "live"
    return "unknown"


def _looks_like_email(value):
    value = (value or "").strip()
    return "@" in value and "." in value.rsplit("@", 1)[-1]


def _check_live_mode_requirements(
    failures,
    warnings,
    *,
    stripe_mode,
    stripe_settings_name,
    payment_gateway_account,
    payment_method_configuration,
    operator_email,
):
    if stripe_mode != "live":
        failures.append(
            f"live mode requires pk_live_/sk_live_ Stripe Settings; {stripe_settings_name!r} is {stripe_mode}"
        )

    required_site_config = {
        "lt_stripe_settings_name": stripe_settings_name,
        "lt_payment_gateway_account": payment_gateway_account,
        "lt_stripe_payment_method_configuration": payment_method_configuration,
        "lt_operator_email": operator_email,
        "stripe_webhook_signing_secret": "configured",
    }
    for key in required_site_config:
        if not frappe.conf.get(key):
            failures.append(f"live mode requires explicit site_config key {key!r}")

    host_name = (frappe.conf.get("host_name") or "").strip()
    if not host_name:
        warnings.append("host_name is not set in site_config; confirm production URL generation before live checkout")
    elif "localhost" in host_name or "127.0.0.1" in host_name:
        failures.append(f"host_name is local-only in live mode: {host_name!r}")
