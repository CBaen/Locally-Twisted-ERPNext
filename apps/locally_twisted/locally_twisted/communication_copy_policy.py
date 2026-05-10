"""Copy routing for LT paperwork and documentation emails."""
from __future__ import annotations

from collections.abc import Iterable


PUBLIC_BUSINESS_ADDRESS = "hi@locallytwisted.com"
BUSINESS_DOCUMENT_COPY = "locallytwisted@gmail.com"
UNSAFE_ROUTED_COPY_ALIASES = frozenset(
    {
        "hi@locallytwisted.com",
        "cameron@locallytwisted.com",
    }
)


def document_copy_recipients(
    *,
    external_audience: bool,
    primary_recipients: Iterable[str] | None = None,
) -> list[str]:
    """Return internal copy recipients that are not already primary recipients."""
    primary = {_normalize(value) for value in primary_recipients or []}
    copies = [BUSINESS_DOCUMENT_COPY]
    return [
        recipient
        for recipient in _dedupe(copies)
        if _normalize(recipient) not in primary
    ]


def document_copy_kwargs(
    *,
    external_audience: bool,
    primary_recipients: Iterable[str] | None = None,
) -> dict[str, list[str]]:
    """Return Frappe sendmail kwargs for internal document copies."""
    copies = document_copy_recipients(
        external_audience=external_audience,
        primary_recipients=primary_recipients,
    )
    return {"bcc": copies} if copies else {}


def document_copy_field_values(*, external_audience: bool = True) -> dict[str, str]:
    """Return send-readiness field values for approved copy routing."""
    return {"business_copy_recipient": BUSINESS_DOCUMENT_COPY}


def routed_alias_copy_risks(recipients: Iterable[str] | None) -> list[str]:
    """Return routed aliases that can loop back into the Gmail SMTP sender."""
    normalized = {_normalize(value) for value in recipients or []}
    return sorted(normalized.intersection(UNSAFE_ROUTED_COPY_ALIASES))


def _normalize(value: str) -> str:
    return str(value or "").strip().lower()


def _dedupe(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
