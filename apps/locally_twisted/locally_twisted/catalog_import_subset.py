"""Import subset rules for Odoo-to-ERPNext catalog migration.

These rules are deliberately about backend/schema fit, not product taste or
launch merchandising. A product with variants is allowed when the current
ERPNext/Frappe contract can preserve its meaning.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


OWNER_EXPLICIT_EXCLUDED_SLUGS = {
    "classic-column": "Classic Column",
    "classic-arch": "Classic Arch",
    "classic-organic-arch": "Classic Organic Arch",
    "classic-organic-columns": "Classic Organic Columns",
    "classic-organic-balloon-garland": "Classic Garland",
}

OWNER_MUST_WORK_SLUGS = {
    "graduation-grab-n-go": "Graduation Deliveries",
    "easter-balloon-cups": "Balloon Cups",
    "7-butterfly-column": "7\" Butterfly Column",
}

OWNER_DIRECT_CHECKOUT_SLUGS = {
    "graduation-grab-n-go": "Graduation Grab n Go",
    "7-butterfly-column": "7\" Butterfly Column",
    "6-graduation-stands": "6' Graduation stands",
}

EXCLUSION_REASON_PRIORITY = (
    "owner_explicit_exclusion",
    "schema_backend_blocker",
)


def import_exclusion_reasons(product: dict[str, Any], contract: Any) -> list[dict[str, str]]:
    """Return fail-loud import exclusions for the current ERPNext backend schema."""
    slug = str(product.get("slug") or "").strip()
    reasons: list[dict[str, str]] = []

    if slug in OWNER_EXPLICIT_EXCLUDED_SLUGS:
        reasons.append(
            {
                "code": "owner_explicit_exclusion",
                "detail": f"Owner excluded this structure from the current import subset: {OWNER_EXPLICIT_EXCLUDED_SLUGS[slug]}.",
            }
        )

    if contract.product_page_type == "needs_review" or contract.commerce_lane == "needs_review":
        reasons.append(
            {
                "code": "schema_backend_blocker",
                "detail": "Product contract resolved to needs_review, so current backend schema cannot safely route it.",
            }
        )

    return sorted(reasons, key=lambda reason: _reason_priority(reason["code"]))


def selected_for_import(product: dict[str, Any], contract: Any) -> bool:
    return not import_exclusion_reasons(product, contract)


def primary_exclusion_reason(reasons: list[dict[str, str]]) -> str | None:
    codes = {reason["code"] for reason in reasons}
    for code in EXCLUSION_REASON_PRIORITY:
        if code in codes:
            return code
    return next(iter(codes), None)


def reason_counts(rows: list[dict[str, Any]], *, primary: bool) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for row in rows:
        if primary:
            code = row.get("primary_exclusion_reason")
            if code:
                counter[code] += 1
            continue
        for code in row.get("excluded_reason_codes") or []:
            counter[code] += 1
    return dict(sorted(counter.items()))


def _reason_priority(code: str) -> int:
    try:
        return EXCLUSION_REASON_PRIORITY.index(code)
    except ValueError:
        return len(EXCLUSION_REASON_PRIORITY)


def assert_must_work_products_included(rows: list[dict[str, Any]]) -> list[str]:
    by_slug = {row.get("slug"): row for row in rows}
    errors: list[str] = []
    for slug, label in OWNER_MUST_WORK_SLUGS.items():
        row = by_slug.get(slug)
        if row is None:
            errors.append(f"Owner must-work product missing from source artifacts: {label} ({slug}).")
        elif not row.get("selected_for_v1_import"):
            errors.append(
                f"Owner must-work product excluded without a proven backend blocker: {label} ({slug})."
            )
    return errors
