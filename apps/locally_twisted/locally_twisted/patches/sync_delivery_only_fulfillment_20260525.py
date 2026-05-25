"""Sync line-level fulfillment fields for delivery-only category checkout."""

from locally_twisted.seed.sync_commerce_rules import execute as sync_commerce_rules


def execute():
    sync_commerce_rules(commit=False)
