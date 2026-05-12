"""Re-run intake schema sync for Frappe Cloud sites missing local custom fields."""

from locally_twisted.seed.sync_contact_intake_backend import execute as sync_contact_intake


def execute():
    sync_contact_intake(commit=False)
