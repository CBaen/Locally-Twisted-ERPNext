"""Sync approved shop primary and secondary categories."""
from __future__ import annotations

import frappe

from locally_twisted.seed.sync_shop_taxonomy import apply_approved


def execute():
    report = apply_approved(commit=False)
    if not report.get("ok"):
        failures = report.get("failures") or ["unknown taxonomy sync failure"]
        frappe.throw("Shop taxonomy sync failed: " + "; ".join(str(failure) for failure in failures))
