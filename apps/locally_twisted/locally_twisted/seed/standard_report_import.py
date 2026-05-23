"""Helpers for syncing code-owned standard reports on hosted sites."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import frappe


@contextmanager
def standard_report_import_context() -> Iterator[None]:
    """Let source-owned Script Report records save outside developer mode.

    Frappe v15 permits standard Report writes during import/migrate/install/patch
    because those records are source artifacts. LT's seed syncs use the same
    contract when repairing a hosted staging site after app install.
    """
    previous = getattr(frappe.flags, "in_import", None)
    frappe.flags.in_import = True
    try:
        yield
    finally:
        frappe.flags.in_import = previous
