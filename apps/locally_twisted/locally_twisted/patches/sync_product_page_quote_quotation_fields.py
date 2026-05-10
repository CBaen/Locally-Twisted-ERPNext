"""Install/update draft Quotation fields for product-page quote handoff."""
from __future__ import annotations

from locally_twisted.seed.sync_commerce_rules import execute as sync_commerce_rules


def execute():
    sync_commerce_rules(commit=False)
