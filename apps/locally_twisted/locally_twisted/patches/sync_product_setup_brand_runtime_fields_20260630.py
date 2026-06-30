"""Install/update Product Setup runtime brand fields on Website Item."""
from __future__ import annotations

from locally_twisted.seed.sync_commerce_rules import execute as sync_commerce_rules


def execute():
    sync_commerce_rules(commit=False)
