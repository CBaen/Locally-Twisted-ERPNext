"""Resync contact intake schema for required phone/preferred-contact form."""

from locally_twisted.seed.sync_contact_intake_backend import execute as sync_contact_intake


def execute():
    sync_contact_intake()
