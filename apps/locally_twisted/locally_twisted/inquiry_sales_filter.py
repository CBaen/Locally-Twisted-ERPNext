"""Conservative sales-solicitation classifier for public inquiry forms.

This filter must not block possible customers. It only suppresses the owner
email for high-confidence vendor pitches; the Lead still saves for audit.
"""

from __future__ import annotations

import re
from typing import Any


SALES_PHRASES: tuple[tuple[str, int], ...] = (
    ("virtual assistant", 5),
    ("virtual assistants", 5),
    ("custom built ai tool", 4),
    ("advanced virtual intelligent system", 4),
    ("mavis", 4),
    ("20 man team", 4),
    ("we offer", 3),
    ("we provide", 3),
    ("we overtake", 3),
    ("delegate to a human", 3),
    ("administrative tasks", 3),
    ("graphic design", 3),
    ("video animation", 3),
    ("video animations", 3),
    ("prospecting", 3),
    ("lead generation", 3),
    ("appointment setting", 3),
    ("marketing agency", 3),
    ("our system", 2),
    ("our services", 2),
    ("are you looking for help", 2),
    ("tried emailing you", 1),
    ("reaching out because", 1),
)

CUSTOMER_EVENT_PHRASES: tuple[tuple[str, int], ...] = (
    ("balloon", 4),
    ("face painting", 4),
    ("balloon twisting", 4),
    ("twisting", 3),
    ("decor", 3),
    ("garland", 3),
    ("arch", 3),
    ("bouquet", 3),
    ("backdrop", 3),
    ("birthday", 3),
    ("wedding", 3),
    ("baby shower", 3),
    ("graduation", 3),
    ("school event", 3),
    ("church event", 3),
    ("festival", 3),
    ("grand opening", 3),
    ("company picnic", 3),
    ("corporate event", 3),
    ("event date", 2),
    ("venue", 2),
    ("guests", 2),
    ("party", 2),
    ("entrance", 2),
    ("photo backdrop", 2),
    ("delivery", 2),
    ("pickup", 2),
)

SALES_THRESHOLD = 8
CUSTOMER_OVERRIDE_THRESHOLD = 5


def classify_inquiry_sales_solicitation(payload: dict[str, Any]) -> dict[str, Any]:
    """Return high-confidence sales-solicitation classification.

    `is_solicitation=True` is intentionally hard to reach and can be overridden
    by strong event/customer language.
    """
    text = _normalize(" ".join(_flatten_payload(payload)))
    sales_score, sales_reasons = _score(text, SALES_PHRASES)
    customer_score, customer_reasons = _score(text, CUSTOMER_EVENT_PHRASES)
    is_solicitation = (
        sales_score >= SALES_THRESHOLD
        and customer_score < CUSTOMER_OVERRIDE_THRESHOLD
    )
    return {
        "is_solicitation": is_solicitation,
        "sales_score": sales_score,
        "customer_score": customer_score,
        "sales_reasons": sales_reasons,
        "customer_reasons": customer_reasons,
    }


def _score(text: str, weighted_phrases: tuple[tuple[str, int], ...]) -> tuple[int, list[str]]:
    total = 0
    reasons = []
    for phrase, weight in weighted_phrases:
        pattern = r"(?<![a-z0-9])" + re.escape(phrase) + r"(?![a-z0-9])"
        if re.search(pattern, text):
            total += weight
            reasons.append(phrase)
    return total, reasons


def _flatten_payload(payload: dict[str, Any]) -> list[str]:
    values = []
    for value in payload.values():
        if isinstance(value, (list, tuple, set)):
            values.extend(str(item or "") for item in value)
        else:
            values.append(str(value or ""))
    return values


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()
