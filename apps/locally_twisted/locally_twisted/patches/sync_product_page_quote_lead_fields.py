"""Install/update Lead fields for product-page quote handoff."""
from __future__ import annotations

from locally_twisted.seed.sync_contact_intake_backend import execute as sync_contact_intake


def execute():
    sync_contact_intake(commit=False)
