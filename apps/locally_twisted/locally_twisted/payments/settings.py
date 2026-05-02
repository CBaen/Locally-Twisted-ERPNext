"""Payment configuration helpers for Locally Twisted.

Local dev still defaults to the current Stripe test setup. Production can
override these values in site_config.json without changing checkout code.
"""
from __future__ import annotations

import frappe


DEFAULT_STRIPE_SETTINGS_NAME = "Test"
DEFAULT_PAYMENT_GATEWAY_ACCOUNT = "Stripe-Test - USD - LT"
DEFAULT_STRIPE_PAYMENT_METHOD_CONFIGURATION = "pmc_1TRZH2DfnlZQv66ncb001soG"
DEFAULT_OPERATOR_EMAIL = "locallytwisted@gmail.com"


def get_stripe_settings_name() -> str:
    return _conf_string("lt_stripe_settings_name") or DEFAULT_STRIPE_SETTINGS_NAME


def get_stripe_settings():
    return frappe.get_doc("Stripe Settings", get_stripe_settings_name())


def get_payment_gateway_account() -> str:
    return (
        _conf_string("lt_payment_gateway_account")
        or frappe.db.get_single_value("Webshop Settings", "payment_gateway_account")
        or DEFAULT_PAYMENT_GATEWAY_ACCOUNT
    )


def get_stripe_payment_method_configuration() -> str:
    return (
        _conf_string("lt_stripe_payment_method_configuration")
        or DEFAULT_STRIPE_PAYMENT_METHOD_CONFIGURATION
    )


def get_operator_email() -> str:
    return _conf_string("lt_operator_email") or DEFAULT_OPERATOR_EMAIL


def _conf_string(key: str) -> str:
    value = frappe.conf.get(key)
    if value is None:
        return ""
    return str(value).strip()
