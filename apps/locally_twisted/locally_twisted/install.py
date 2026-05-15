"""Install and migration hooks for LT-owned ERPNext schema."""
from __future__ import annotations

from locally_twisted.seed.sync_contact_intake_backend import execute as sync_contact_intake_backend


def after_install() -> None:
    """Ensure fresh Frappe Cloud sites receive the contact intake schema."""
    sync_contact_intake_backend(commit=False)


def after_migrate() -> None:
    """Repair or refresh contact intake schema during bench/site updates."""
    sync_contact_intake_backend(commit=False)
