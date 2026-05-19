"""Dry-run/apply verifier for explicit Website Item ecommerce classifications.

This verifier is intentionally narrow: it only reads/writes Website Item
lt_product_page_type and lt_commerce_lane for the 53 source-backed product-page
records named in the 2026-05-10 ready-to-order ecommerce Phase 2 packet.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

import frappe

from locally_twisted.product_page_runtime import (
    WEBSITE_ITEM_COMMERCE_LANE_FIELD,
    WEBSITE_ITEM_PAGE_TYPE_FIELD,
)

CHECKOUT_READY_AFTER_SMALL_FIX = (
    "unicorn-bouquet",
    "mickey-mouse-bouquet",
    "minion-bouquet",
    "encanto-bouquet",
    "stitch-bouquet",
    "flamingo-bouquet",
    "football-bouquet",
    "soccer-bouquet",
    "space-bouquet",
    "over-the-hill-bouquet",
    "paw-patrol-bouquet",
    "elsa-bouquet",
    "holy-cow-bouquet",
    "easter-balloon-cups",
    "mothers-day-bouquet",
    "graduation-grab-n-go",
    "6-graduation-stands",
)

QUOTE_FIRST = (
    "7-butterfly-column",
    "baby-shower-combination-photo-opt",
    "classic-organic-balloon-garland",
    "basketball-arch",
    "number-balloon-columns",
    "easter-balloon-arch-bunny-ear",
    "halloween-arch",
    "large-head-missionary",
    "premium-organic-garland",
    "premium-organic-arch",
    "pemium-organic-column",
    "pride-progress-rainbow-balloon-arch",
    "classic-arch",
    "classic-column",
    "classic-organic-columns",
    "baby-shower-garland",
    "balloon-drop",
    "classic-organic-arch",
    "7-epic-column",
    "organic-grab-n-go",
    "star-column",
    "sleepy-baby-column",
    "baby-table-decor",
    "logo-3-layered-bouquet",
    "6-color-rainbow-arch",
    "mothers-day-front-yard-7-column",
    "classic-organic-for-easel",
    "easter-arch",
    "large-garland",
    "large-organic-column",
    "pride-arch",
)

HIDE_OR_NEEDS_REVIEW = (
    "birthday-deliveries",
    "marble-table-decor",
    "butterfly-get-well-bouquet-latex-free",
    "bandage-get-well-bouquet-latex-free",
    "shooting-star-get-well-bouquet-latex-free",
)

DESIRED_BY_LANE: dict[str, dict[str, str]] = {
    "checkout_ready_after_small_fix": {
        "product_page_type": "simple_product",
        "commerce_lane": "checkout",
    },
    "quote_first": {
        "product_page_type": "complex_custom_product",
        "commerce_lane": "quote_first",
    },
    "hide_or_needs_review": {
        "product_page_type": "needs_review",
        "commerce_lane": "needs_review",
    },
}

EXPECTED_TOTAL = 53
EXPECTED_COUNTS = {
    "checkout_ready_after_small_fix": 17,
    "quote_first": 31,
    "hide_or_needs_review": 5,
}
ONLY_MUTATED_FIELDS = (WEBSITE_ITEM_PAGE_TYPE_FIELD, WEBSITE_ITEM_COMMERCE_LANE_FIELD)


def run(apply: bool = False) -> dict[str, Any]:
    """Return a JSON-serializable report; apply only after strict dry-run gates."""
    apply = bool(apply)
    failures: list[str] = []
    meta = frappe.get_meta("Website Item")
    for fieldname in ONLY_MUTATED_FIELDS:
        if not meta.has_field(fieldname):
            failures.append(f"Website Item missing field: {fieldname}")

    desired_rows = _desired_rows()
    lane_counts = Counter(row["lane"] for row in desired_rows)
    if len(desired_rows) != EXPECTED_TOTAL:
        failures.append(f"desired row count {len(desired_rows)} != expected {EXPECTED_TOTAL}")
    for lane, expected in EXPECTED_COUNTS.items():
        if lane_counts.get(lane, 0) != expected:
            failures.append(f"desired lane count {lane}={lane_counts.get(lane, 0)} != expected {expected}")
    duplicates = sorted(_duplicates([row["item_code"] for row in desired_rows]))
    if duplicates:
        failures.append(f"duplicate desired item_code values: {', '.join(duplicates)}")

    snapshots: list[dict[str, Any]] = []
    missing: list[str] = []
    ambiguous: list[dict[str, Any]] = []
    planned_changes: list[dict[str, Any]] = []

    if not failures:
        for desired in desired_rows:
            matches = frappe.get_all(
                "Website Item",
                filters={"item_code": desired["item_code"]},
                fields=[
                    "name",
                    "item_code",
                    "web_item_name",
                    "published",
                    WEBSITE_ITEM_PAGE_TYPE_FIELD,
                    WEBSITE_ITEM_COMMERCE_LANE_FIELD,
                    "modified",
                ],
                order_by="name asc",
            )
            if not matches:
                missing.append(desired["item_code"])
                continue
            if len(matches) > 1:
                ambiguous.append(
                    {
                        "item_code": desired["item_code"],
                        "matches": [row.get("name") for row in matches],
                    }
                )
                continue
            current = matches[0]
            before = {
                "product_page_type": current.get(WEBSITE_ITEM_PAGE_TYPE_FIELD),
                "commerce_lane": current.get(WEBSITE_ITEM_COMMERCE_LANE_FIELD),
            }
            after = {
                "product_page_type": desired["product_page_type"],
                "commerce_lane": desired["commerce_lane"],
            }
            needs_change = before != after
            snapshot = {
                "lane": desired["lane"],
                "name": current.get("name"),
                "item_code": current.get("item_code"),
                "web_item_name": current.get("web_item_name"),
                "published": current.get("published"),
                "before": before,
                "desired": after,
                "needs_change": needs_change,
                "reverse_set": before,
                "modified_before": str(current.get("modified")),
            }
            snapshots.append(snapshot)
            if needs_change:
                planned_changes.append(snapshot)

    if missing:
        failures.append(f"missing Website Item identities: {', '.join(missing)}")
    if ambiguous:
        failures.append("ambiguous Website Item identities: " + "; ".join(
            f"{row['item_code']} -> {', '.join(row['matches'])}" for row in ambiguous
        ))
    if len(snapshots) != EXPECTED_TOTAL:
        failures.append(f"matched Website Item count {len(snapshots)} != expected {EXPECTED_TOTAL}")

    action = "dry_run"
    applied_changes: list[dict[str, Any]] = []
    if apply:
        action = "apply_blocked" if failures else "apply"
        if not failures:
            for change in planned_changes:
                frappe.db.set_value(
                    "Website Item",
                    change["name"],
                    {
                        WEBSITE_ITEM_PAGE_TYPE_FIELD: change["desired"]["product_page_type"],
                        WEBSITE_ITEM_COMMERCE_LANE_FIELD: change["desired"]["commerce_lane"],
                    },
                )
                applied_changes.append(change)
            frappe.db.commit()

    after_snapshots: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    if apply and not failures:
        for desired in desired_rows:
            row = frappe.db.get_value(
                "Website Item",
                {"item_code": desired["item_code"]},
                [
                    "name",
                    "item_code",
                    "web_item_name",
                    WEBSITE_ITEM_PAGE_TYPE_FIELD,
                    WEBSITE_ITEM_COMMERCE_LANE_FIELD,
                    "modified",
                ],
                as_dict=True,
            )
            after = {
                "product_page_type": row.get(WEBSITE_ITEM_PAGE_TYPE_FIELD),
                "commerce_lane": row.get(WEBSITE_ITEM_COMMERCE_LANE_FIELD),
            }
            expected = {
                "product_page_type": desired["product_page_type"],
                "commerce_lane": desired["commerce_lane"],
            }
            record = {
                "lane": desired["lane"],
                "name": row.get("name"),
                "item_code": row.get("item_code"),
                "web_item_name": row.get("web_item_name"),
                "after": after,
                "expected": expected,
                "matches_expected": after == expected,
                "modified_after": str(row.get("modified")),
            }
            after_snapshots.append(record)
            if after != expected:
                mismatches.append(record)
        if mismatches:
            failures.append(f"post-apply stored value mismatches: {len(mismatches)}")

    final_counts = _stored_counts(desired_rows) if not failures or snapshots else {}
    return {
        "ok": not failures,
        "action": action,
        "apply_requested": apply,
        "expected_total": EXPECTED_TOTAL,
        "expected_counts": EXPECTED_COUNTS,
        "matched_count": len(snapshots),
        "missing": missing,
        "ambiguous": ambiguous,
        "only_mutated_doctype": "Website Item",
        "only_mutated_fields": list(ONLY_MUTATED_FIELDS),
        "planned_change_count": len(planned_changes),
        "applied_change_count": len(applied_changes),
        "desired_counts": dict(lane_counts),
        "stored_counts_for_targets": final_counts,
        "records": snapshots,
        "after_records": after_snapshots,
        "mismatches": mismatches,
        "failures": failures,
        "reversal_note": (
            "Use each record's name with reverse_set.product_page_type and "
            "reverse_set.commerce_lane to restore prior Website Item field values. "
            "No publish/delete/reimport/media/price fields are touched by this verifier."
        ),
    }


def _desired_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    rows.extend(_lane_rows("checkout_ready_after_small_fix", CHECKOUT_READY_AFTER_SMALL_FIX))
    rows.extend(_lane_rows("quote_first", QUOTE_FIRST))
    rows.extend(_lane_rows("hide_or_needs_review", HIDE_OR_NEEDS_REVIEW))
    return rows


def _lane_rows(lane: str, item_codes: tuple[str, ...]) -> list[dict[str, str]]:
    desired = DESIRED_BY_LANE[lane]
    return [
        {
            "lane": lane,
            "item_code": item_code,
            "product_page_type": desired["product_page_type"],
            "commerce_lane": desired["commerce_lane"],
        }
        for item_code in item_codes
    ]


def _duplicates(values: list[str]) -> set[str]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def _stored_counts(desired_rows: list[dict[str, str]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for desired in desired_rows:
        key = f"{desired['product_page_type']}|{desired['commerce_lane']}"
        value = frappe.db.count(
            "Website Item",
            {
                "item_code": desired["item_code"],
                WEBSITE_ITEM_PAGE_TYPE_FIELD: desired["product_page_type"],
                WEBSITE_ITEM_COMMERCE_LANE_FIELD: desired["commerce_lane"],
            },
        )
        counts[key] = counts.get(key, 0) + int(value or 0)
    return counts
