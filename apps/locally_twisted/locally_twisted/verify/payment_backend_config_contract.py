"""Payment backend configuration verifier.

This verifies the payment settings layer that checkout depends on. It does
not print Stripe secret keys or webhook secrets.
"""
from __future__ import annotations

import frappe


class ContractFail(Exception):
    pass


def run():
    try:
        return _run_contract()
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}


def _run_contract():
    from locally_twisted.payments.settings import (
        DEFAULT_OPERATOR_EMAIL,
        DEFAULT_PAYMENT_GATEWAY_ACCOUNT,
        DEFAULT_STRIPE_PAYMENT_METHOD_CONFIGURATION,
        DEFAULT_STRIPE_SETTINGS_NAME,
        get_operator_email,
        get_payment_gateway_account,
        get_stripe_payment_method_configuration,
        get_stripe_settings_name,
    )

    failures = []
    warnings = []

    defaults = {
        "stripe_settings_name": get_stripe_settings_name(),
        "payment_gateway_account": get_payment_gateway_account(),
        "stripe_payment_method_configuration": get_stripe_payment_method_configuration(),
        "operator_email": get_operator_email(),
    }

    expected_defaults = {
        "stripe_settings_name": DEFAULT_STRIPE_SETTINGS_NAME,
        "payment_gateway_account": _webshop_payment_gateway_account()
        or DEFAULT_PAYMENT_GATEWAY_ACCOUNT,
        "stripe_payment_method_configuration": DEFAULT_STRIPE_PAYMENT_METHOD_CONFIGURATION,
        "operator_email": DEFAULT_OPERATOR_EMAIL,
    }
    for key, expected in expected_defaults.items():
        if defaults.get(key) != expected:
            failures.append(f"{key} default resolved to {defaults.get(key)!r}, expected {expected!r}")

    override_values = {
        "lt_stripe_settings_name": "LT Config Probe Stripe",
        "lt_payment_gateway_account": "LT Config Probe Gateway",
        "lt_stripe_payment_method_configuration": "pmc_probe_config",
        "lt_operator_email": "operator-probe@example.invalid",
    }
    originals = {key: frappe.conf.get(key) for key in override_values}
    try:
        for key, value in override_values.items():
            setattr(frappe.conf, key, value)

        override_results = {
            "stripe_settings_name": get_stripe_settings_name(),
            "payment_gateway_account": get_payment_gateway_account(),
            "stripe_payment_method_configuration": get_stripe_payment_method_configuration(),
            "operator_email": get_operator_email(),
        }
    finally:
        for key, original in originals.items():
            if original is None:
                frappe.conf.pop(key, None)
            else:
                setattr(frappe.conf, key, original)

    expected_overrides = {
        "stripe_settings_name": override_values["lt_stripe_settings_name"],
        "payment_gateway_account": override_values["lt_payment_gateway_account"],
        "stripe_payment_method_configuration": override_values[
            "lt_stripe_payment_method_configuration"
        ],
        "operator_email": override_values["lt_operator_email"],
    }
    for key, expected in expected_overrides.items():
        if override_results.get(key) != expected:
            failures.append(f"{key} override resolved to {override_results.get(key)!r}, expected {expected!r}")

    stripe_settings = frappe.db.get_value(
        "Stripe Settings",
        defaults["stripe_settings_name"],
        ["name", "gateway_name", "publishable_key"],
        as_dict=True,
    )
    if not stripe_settings:
        failures.append(f"Stripe Settings {defaults['stripe_settings_name']!r} does not exist")
    else:
        stripe_doc = frappe.get_doc("Stripe Settings", stripe_settings.name)
        if not stripe_doc.get_password("secret_key", raise_exception=False):
            failures.append(f"Stripe Settings {stripe_settings.name!r} has no secret key configured")

    gateway_account = frappe.db.get_value(
        "Payment Gateway Account",
        defaults["payment_gateway_account"],
        ["name", "payment_gateway", "payment_account", "currency", "is_default"],
        as_dict=True,
    )
    if not gateway_account:
        failures.append(f"Payment Gateway Account {defaults['payment_gateway_account']!r} does not exist")
    elif gateway_account.currency != "USD":
        failures.append(
            f"Payment Gateway Account {gateway_account.name!r} currency is {gateway_account.currency!r}, expected 'USD'"
        )

    webshop = frappe.db.get_single_value("Webshop Settings", "enable_checkout")
    if str(webshop) != "1":
        failures.append("Webshop Settings enable_checkout is not enabled")

    outgoing_email = frappe.get_all(
        "Email Account",
        filters={"enable_outgoing": 1},
        fields=["name"],
        limit=1,
    )
    if not outgoing_email:
        failures.append("No outgoing Email Account is enabled")

    if not frappe.conf.get("stripe_webhook_signing_secret"):
        warnings.append(
            "stripe_webhook_signing_secret is not set in site_config; webhooks will reject events until it is configured"
        )

    if failures:
        return {"ok": False, "failures": failures, "warnings": warnings}

    return {
        "ok": True,
        "stripe_settings_name": defaults["stripe_settings_name"],
        "payment_gateway_account": defaults["payment_gateway_account"],
        "stripe_payment_method_configuration": defaults[
            "stripe_payment_method_configuration"
        ],
        "operator_email": defaults["operator_email"],
        "webhook_secret_configured": bool(frappe.conf.get("stripe_webhook_signing_secret")),
        "warnings": warnings,
    }


def _webshop_payment_gateway_account():
    return frappe.db.get_single_value("Webshop Settings", "payment_gateway_account")
