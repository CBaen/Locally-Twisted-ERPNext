"""Install LT branded password-reset template and guard against generic fallback."""
from __future__ import annotations

from locally_twisted.password_reset_email import ensure_password_reset_template


def execute():
    report = ensure_password_reset_template(commit=False)
    if not report.get("ok"):
        failures = "; ".join(report.get("failures") or ["unknown password reset template failure"])
        raise RuntimeError(f"Locally Twisted password reset template setup failed: {failures}")
