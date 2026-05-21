#!/usr/bin/env python3
"""Verify /thank-you does not trust ?order= as paid proof.

This is a source-level guard for the customer-copy regression that triggered
Lane 3: the page must ask ERPNext for payment state before showing confirmed
payment copy, and it must not render order details for an unconfirmed order.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "apps/locally_twisted/locally_twisted/www/thank_you.py"


def main() -> int:
    parse_noop_args(__doc__)

    source = TARGET.read_text(encoding="utf-8")
    tree = ast.parse(source)
    failures: list[str] = []

    get_context = _function(tree, "get_context")
    if get_context is None:
        failures.append("thank_you.py is missing get_context")
    else:
        if "_payment_state_for_sales_order" not in _called_names(get_context):
            failures.append("get_context does not call _payment_state_for_sales_order")
        if "context.thank_you_eyebrow = \"Payment Received\"" in source:
            failures.append("get_context still sets Payment Received before proving paid state")
        if "if so_name and not payment_check_needed:" not in source:
            failures.append("order details are not guarded by payment_check_needed")

    payment_state = _function(tree, "_payment_state_for_sales_order")
    if payment_state is None:
        failures.append("thank_you.py is missing _payment_state_for_sales_order")
    else:
        names = _called_names(payment_state)
        if "_paid_payment_request_for_sales_order" not in names:
            failures.append("paid state does not inspect Payment Request records")
        if "_invoice_state_for_sales_order" not in names:
            failures.append("paid state does not inspect Sales Invoice records")

    for required in (
        "We need to check this payment before we call the order confirmed.",
        "Payment Check",
        "Payment Received",
    ):
        if required not in source:
            failures.append(f"thank-you state copy missing {required!r}")

    if failures:
        print("[THANK YOU PAYMENT STATE CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[THANK YOU PAYMENT STATE CONTRACT] PASS")
    return 0


def _function(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _called_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name):
                names.add(func.id)
            elif isinstance(func, ast.Attribute):
                names.add(func.attr)
    return names


if __name__ == "__main__":
    sys.exit(main())
