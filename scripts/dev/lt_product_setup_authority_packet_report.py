#!/usr/bin/env python3
"""Build offline Product Setup authority packets from saved catalog artifacts.

This report consumes saved JSON files from
``lt_live_readonly_catalog_authority_audit.py``. It is offline only: no env
files, network, Docker, browser profiles, ERPNext, cache clear, deploy, or live
API calls.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


ACTIVE_PRODUCT_SETUP_STATUSES = {
    "Needs Product Review",
    "Needs Price Review",
    "Needs Media Review",
    "Local Preview Ready",
    "Staging Ready",
    "Approved For Live",
    "Live",
    "Hidden",
    "Quote Only",
    "Paused",
}
SOURCE_UNIQUENESS_STATUSES = {
    "Local Preview Ready",
    "Staging Ready",
    "Approved For Live",
}
ALLOWED_OPERATING_BRANDS = {
    "locally_twisted",
    "commercial_balloon_decor",
    "memorial_balloons",
}
SKIP_DIRECTORY_JSON = {
    "index.json",
    "blast-radius.json",
    "authority-packet-report.json",
}
VARIANT_HIGH_THRESHOLD = 500
VARIANT_CRITICAL_THRESHOLD = 2000


class AuthorityPacketBlocked(RuntimeError):
    """Raised when local artifact input is missing or invalid."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        paths = collect_paths(args.input)
        packets = [build_packet(path, load_json(path)) for path in paths]
        report = build_report(packets, paths)
        write_report(report, args.output, pretty=args.pretty)
    except AuthorityPacketBlocked as exc:
        print(f"[LT PRODUCT SETUP AUTHORITY PACKET] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP AUTHORITY PACKET] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[LT PRODUCT SETUP AUTHORITY PACKET] " + ("FAIL" if report["blocked_product_count"] else "PASS"), file=sys.stderr)
    print(f"  products: {report['product_count']}", file=sys.stderr)
    print(f"  blocked_products: {report['blocked_product_count']}", file=sys.stderr)
    print(f"  blocker_count: {report['blocker_count']}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and report["blocker_count"]:
        return 1
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", nargs="+", required=True, help="Saved audit JSON files or directories.")
    parser.add_argument("--output", help="Optional report JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 when any product has blockers.")
    return parser.parse_args(argv)


def collect_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    explicit_files: set[Path] = set()
    for raw in inputs:
        path = Path(raw)
        if not path.exists():
            raise AuthorityPacketBlocked(f"input does not exist: {path}")
        if path.is_dir():
            paths.extend(
                child
                for child in sorted(path.glob("*.json"))
                if child.is_file() and child.name not in SKIP_DIRECTORY_JSON and not child.name.endswith("-projection.json")
            )
        elif path.suffix.lower() == ".json":
            paths.append(path)
            explicit_files.add(path.resolve())
        else:
            raise AuthorityPacketBlocked(f"input is not a JSON file or directory: {path}")
    unique = sorted({path.resolve() for path in paths})
    if not unique:
        raise AuthorityPacketBlocked("no saved audit JSON artifacts found")
    for path in unique:
        if path in explicit_files and path.name in SKIP_DIRECTORY_JSON:
            raise AuthorityPacketBlocked(f"explicit input is a collector/report index, not a product artifact: {path}")
    return unique


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AuthorityPacketBlocked(f"input is not valid JSON: {path}: {exc}") from exc
    except OSError as exc:
        raise AuthorityPacketBlocked(f"could not read input: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise AuthorityPacketBlocked(f"JSON root must be an object: {path}")
    if not is_audit_artifact(payload):
        raise AuthorityPacketBlocked(f"not a recognized catalog authority audit artifact: {path}")
    return payload


def is_audit_artifact(payload: dict[str, Any]) -> bool:
    return any(key in payload for key in ("price_summary", "content_summary", "blueprint_summary", "website_item_summary"))


def build_packet(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, Any]] = []
    product = product_identifier(payload)
    add_existing_failures(blockers, payload.get("failures"))

    product_setup = product_setup_section(payload, product, blockers)
    source_authority = source_authority_section(product_setup)
    price = price_section(payload, blockers)
    copy = copy_section(payload)
    variant = variant_section(payload, blockers)
    option = option_section(payload, blockers)
    release_readiness = release_readiness_section(payload, blockers)

    if copy["differs"]:
        add_blocker(
            blockers,
            "copy_authority_drift",
            "Product Setup story/details differ from Website Item public fields.",
            copy["evidence"],
        )
    if not copy["product_setup_fields_present"]:
        add_blocker(
            blockers,
            "missing_product_setup_copy_evidence",
            "Product Setup story/details copy evidence is missing.",
            copy["evidence"],
        )
    if not copy["website_item_public_fields_present"]:
        add_blocker(
            blockers,
            "missing_website_item_copy_evidence",
            "Website Item public copy evidence is missing.",
            copy["evidence"],
        )

    authority_status = "ready" if not blockers else "blocked"
    return {
        "artifact": str(path),
        "product_identifier": product,
        "authority_status": authority_status,
        "blockers": dedupe_blockers(blockers),
        "price": price,
        "copy": copy,
        "variant": variant,
        "option": option,
        "product_setup": product_setup,
        "source_authority": source_authority,
        "release_readiness": release_readiness,
        "next_action": next_action(blockers, price, copy, variant, product_setup),
    }


def product_identifier(payload: dict[str, Any]) -> dict[str, Any]:
    identifier = payload.get("product_identifier") if isinstance(payload.get("product_identifier"), dict) else {}
    website = payload.get("website_item_summary") if isinstance(payload.get("website_item_summary"), dict) else {}
    blueprint = payload.get("blueprint_summary") if isinstance(payload.get("blueprint_summary"), dict) else {}
    source_brand = first_present(identifier, "brand_lane") or blueprint.get("operating_brand")
    source_brand_state = brand_lane_state(source_brand, identifier.get("brand_lane_status"))
    return {
        "website_item": first_present(identifier, "website_item") or website.get("name"),
        "item_code": first_present(identifier, "item_code") or website.get("item_code") or blueprint.get("target_item_code"),
        "route": first_present(identifier, "route") or website.get("route"),
        "product_setup": first_present(identifier, "product_setup") or blueprint.get("name"),
        "product_name": first_present(identifier, "product_name") or blueprint.get("product_name") or website.get("web_item_name"),
        "brand_lane": source_brand,
        "brand_lane_status": source_brand_state,
    }


def product_setup_section(
    payload: dict[str, Any],
    product: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> dict[str, Any]:
    match = payload.get("match_summary") if isinstance(payload.get("match_summary"), dict) else {}
    blueprint = payload.get("blueprint_summary") if isinstance(payload.get("blueprint_summary"), dict) else {}
    status = str(blueprint.get("publish_status") or "").strip()
    match_status = match.get("blueprint_match_status") or ("matched" if blueprint else "missing")
    brand_lane_status = str(product.get("brand_lane_status") or "").strip()
    operating_brand = str(product.get("brand_lane") or "").strip()
    operating_brand_state = brand_lane_state(operating_brand, brand_lane_status)
    active_status = status in ACTIVE_PRODUCT_SETUP_STATUSES
    brand_lane_proved = bool(product.get("brand_lane")) and brand_lane_status in {"proved", "verified", "resolved"}
    source_uniqueness = source_uniqueness_result(
        status=status,
        match_status=match_status,
        operating_brand=operating_brand,
        operating_brand_state=operating_brand_state,
        candidates=as_list(match.get("candidate_blueprints")),
    )
    active_authority = bool(match_status == "matched" and active_status and brand_lane_proved)

    if not product.get("brand_lane") or not brand_lane_proved:
        add_blocker(
            blockers,
            "brand_lane_unproved",
            "Brand lane is missing or not live-proved, so product authority cannot be approved for mutation.",
            {
                "brand_lane": product.get("brand_lane"),
                "brand_lane_status": brand_lane_status or None,
                "operating_brand_authority_state": operating_brand_state,
            },
        )
    if match_status != "matched":
        add_blocker(
            blockers,
            "product_setup_match_not_resolved",
            "Product Setup match is missing or ambiguous.",
            {"match_status": match_status, "basis": match.get("blueprint_match_basis"), "candidates": match.get("candidate_blueprints")},
        )
    if not status or not active_status:
        add_blocker(
            blockers,
            "product_setup_inactive",
            "Product Setup is draft, inactive, or missing active authority status.",
            {"publish_status": status or None, "product_setup": product.get("product_setup")},
        )
    if source_uniqueness["required"] and not source_uniqueness["proved"]:
        add_blocker(
            blockers,
            "active_uniqueness_unproved",
            "Same-brand source active uniqueness is not proved from the saved artifact.",
            source_uniqueness["evidence"],
        )

    return {
        "publish_status": status or None,
        "active_authority": active_authority,
        "match_status": match_status,
        "match_basis": match.get("blueprint_match_basis"),
        "candidates": as_list(match.get("candidate_blueprints")),
        "active_status": active_status,
        "brand_lane_proved": brand_lane_proved,
        "operating_brand": operating_brand or None,
        "operating_brand_authority_state": operating_brand_state,
        "source_active_uniqueness_required": source_uniqueness["required"],
        "source_active_uniqueness_proved": source_uniqueness["proved"],
        "source_active_uniqueness_status": source_uniqueness["status"],
        "source_active_uniqueness_evidence": source_uniqueness["evidence"],
    }


def source_authority_section(product_setup: dict[str, Any]) -> dict[str, Any]:
    uniqueness_evidence = (
        product_setup.get("source_active_uniqueness_evidence")
        if isinstance(product_setup.get("source_active_uniqueness_evidence"), dict)
        else {}
    )
    status = product_setup.get("source_active_uniqueness_status")
    conflicts = []
    if status == "unproved_duplicate_same_brand":
        conflicts = uniqueness_evidence.get("same_brand_active_source_candidates") or []
    return {
        "operating_brand": {
            "value": product_setup.get("operating_brand"),
            "authority_state": product_setup.get("operating_brand_authority_state"),
            "evidence_source": "LT Product Blueprint.operating_brand",
            "proof_scope": "source_only"
            if product_setup.get("operating_brand_authority_state") == "source_declared"
            else "none",
            "live_brand_lane_proved": bool(product_setup.get("brand_lane_proved")),
        },
        "same_brand_source_uniqueness": {
            "status": status,
            "basis": ["operating_brand", "product_slug", "target_item_code", "target_website_item"],
            "proof_scope": "source_only" if product_setup.get("source_active_uniqueness_proved") else "none",
            "proved": bool(product_setup.get("source_active_uniqueness_proved")),
            "conflicts": conflicts,
            "evidence": uniqueness_evidence,
        },
    }


def price_section(payload: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    price_summary = payload.get("price_summary") if isinstance(payload.get("price_summary"), dict) else {}
    rows = payload.get("rows") if isinstance(payload.get("rows"), dict) else {}
    counts = payload.get("counts") if isinstance(payload.get("counts"), dict) else {}
    setup_rows = rows_from(rows, "blueprint_price_rows")
    item_price_rows = rows_from(rows, "item_prices")
    variants = int_value(counts.get("variants"))

    setup_values = unique_price_labels(
        [
            *prices_from_values(price_summary.get("blueprint_price_row_values")),
            *prices_from_rows(setup_rows, ("price", "base_price", "checkout_price", "price_list_rate", "rate")),
        ]
    )
    base_price = price_label(to_price(price_summary.get("blueprint_base_price")))
    item_price_values = unique_price_labels(
        [
            *prices_from_values(price_summary.get("item_price_values")),
            *prices_from_rows(item_price_rows, ("price_list_rate", "rate", "price", "amount")),
        ]
    )

    setup_by_item = prices_by_item(setup_rows, ("price", "base_price", "checkout_price", "price_list_rate", "rate"))
    runtime_by_item = prices_by_item(item_price_rows, ("price_list_rate", "rate", "price", "amount"))
    missing_runtime = sorted(set(setup_by_item) - set(runtime_by_item))
    compared = sorted(set(setup_by_item) & set(runtime_by_item))
    mismatched = [
        code for code in compared if unique_price_labels(setup_by_item[code]) != unique_price_labels(runtime_by_item[code])
    ]

    drift_status = "not_checked"
    if setup_values and item_price_values:
        drift_status = "match" if setup_values == item_price_values and not mismatched else "mismatch"

    if not setup_values:
        add_blocker(blockers, "missing_setup_price_values", "Missing Product Setup price evidence.", {"base_price": base_price})
    if not item_price_values:
        add_blocker(blockers, "missing_item_price_values", "Missing Item Price authority evidence.", {"item_price_row_count": len(item_price_rows)})
    if missing_runtime:
        add_blocker(
            blockers,
            "missing_item_price_rows",
            "Product Setup price rows do not have matching Item Price rows.",
            {"missing_item_codes": missing_runtime[:25], "missing_count": len(missing_runtime)},
        )
    if drift_status == "mismatch":
        add_blocker(
            blockers,
            "price_mismatch",
            "Product Setup price values differ from Item Price runtime authority.",
            {
                "setup_values": setup_values,
                "item_price_values": item_price_values,
                "mismatched_item_codes": mismatched[:25],
                "mismatched_count": len(mismatched),
            },
        )
    if variants > 1 and len(setup_rows) <= 1 and len(item_price_rows) > 1:
        add_blocker(
            blockers,
            "ambiguous_base_price_to_many_variants",
            "Base price cannot prove the per-variant Item Price mapping for a multi-variant product.",
            {"variants": variants, "setup_price_row_count": len(setup_rows), "item_price_row_count": len(item_price_rows)},
        )

    return {
        "setup_values": setup_values,
        "setup_base_price": base_price,
        "item_price_values": item_price_values,
        "row_counts": {
            "product_setup_price_rows": int_value(counts.get("blueprint_price_rows"), default=len(setup_rows)),
            "item_price_rows": int_value(counts.get("item_prices"), default=len(item_price_rows)),
        },
        "drift_status": drift_status,
        "missing_runtime_item_price_count": len(missing_runtime),
        "mismatched_item_price_count": len(mismatched),
        "proposed_next_action": price_next_action(drift_status, missing_runtime, setup_values, item_price_values),
    }


def copy_section(payload: dict[str, Any]) -> dict[str, Any]:
    content = payload.get("content_summary") if isinstance(payload.get("content_summary"), dict) else {}
    setup = content.get("blueprint_content_fields") if isinstance(content.get("blueprint_content_fields"), dict) else {}
    public = content.get("website_item_content_fields") if isinstance(content.get("website_item_content_fields"), dict) else {}
    pairs = [
        (
            "story",
            first_text(setup, "product_story", "story", "about_this_design", "about", "description"),
            first_text(public, "lt_brand_description", "brand_description", "description", "web_long_description"),
        ),
        (
            "details",
            first_text(setup, "product_details", "details", "whats_included", "included", "copy"),
            first_text(public, "lt_product_details", "product_details", "web_long_description", "short_description"),
        ),
    ]
    differences = [
        {
            "field": label,
            "product_setup_excerpt": excerpt(setup_value),
            "website_item_excerpt": excerpt(public_value),
        }
        for label, setup_value, public_value in pairs
        if setup_value is not None and public_value is not None and normalize_copy(setup_value) != normalize_copy(public_value)
    ]
    return {
        "product_setup_fields_present": bool(setup),
        "website_item_public_fields_present": bool(public),
        "differs": bool(differences),
        "differences": differences,
        "evidence": {
            "difference_count": len(differences),
            "missing_product_setup_copy": not bool(setup),
            "missing_website_item_copy": not bool(public),
        },
    }


def variant_section(payload: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    counts = payload.get("counts") if isinstance(payload.get("counts"), dict) else {}
    rows = payload.get("rows") if isinstance(payload.get("rows"), dict) else {}
    variants = int_value(counts.get("variants"), default=len(rows_from(rows, "variants")))
    item_prices = int_value(counts.get("item_prices"), default=len(rows_from(rows, "item_prices")))
    if variants > VARIANT_CRITICAL_THRESHOLD:
        severity = "critical"
    elif variants > VARIANT_HIGH_THRESHOLD:
        severity = "high"
    elif variants > 0:
        severity = "normal"
    else:
        severity = "none"
    variant_explosion = severity in {"high", "critical"}
    if variant_explosion:
        add_blocker(
            blockers,
            "variant_explosion",
            "Variant count is large enough to require operator review before treating the SKU model as safe.",
            {"variants": variants, "severity": severity, "thresholds": {"high": VARIANT_HIGH_THRESHOLD, "critical": VARIANT_CRITICAL_THRESHOLD}},
        )
    if item_prices == 0:
        add_blocker(blockers, "missing_item_price_rows", "No Item Price rows are present for this product.", {"variants": variants})
    return {
        "variants": variants,
        "item_prices": item_prices,
        "severity_bucket": severity,
        "severity_buckets": {
            "none": variants == 0,
            "normal": 0 < variants <= VARIANT_HIGH_THRESHOLD,
            "high": VARIANT_HIGH_THRESHOLD < variants <= VARIANT_CRITICAL_THRESHOLD,
            "critical": variants > VARIANT_CRITICAL_THRESHOLD,
        },
        "variant_explosion": variant_explosion,
    }


def option_section(payload: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    rows = payload.get("rows") if isinstance(payload.get("rows"), dict) else {}
    option_rows = rows_from(rows, "blueprint_option_rows")
    add_on_rows = rows_from(rows, "blueprint_add_on_rows")
    conditional_price_rows = rows_from(rows, "blueprint_conditional_price_rows")
    media_rule_rows = rows_from(rows, "blueprint_media_rule_rows")
    classification_counts: dict[str, int] = {}
    missing_classification: list[dict[str, Any]] = []
    for row in option_rows:
        classification = str(row.get("selection_behavior") or row.get("role") or "").strip()
        if classification:
            classification_counts[classification] = classification_counts.get(classification, 0) + 1
        else:
            missing_classification.append(
                {
                    "name": row.get("name"),
                    "axis_name": row.get("axis_name"),
                    "idx": row.get("idx"),
                }
            )
    if missing_classification:
        add_blocker(
            blockers,
            "option_classification_missing",
            "One or more Product Setup option axes are missing explicit classification.",
            {"examples": missing_classification[:25], "missing_count": len(missing_classification)},
        )
    if add_on_rows:
        add_blocker(
            blockers,
            "add_on_runtime_proof_missing",
            "Product Setup add-ons require cart/order/document/payment proof before customer-visible use.",
            {"add_on_row_count": len(add_on_rows)},
        )
    if conditional_price_rows:
        add_blocker(
            blockers,
            "conditional_price_runtime_proof_missing",
            "Conditional pricing rows require runtime resolver proof before publish/apply design.",
            {"conditional_price_row_count": len(conditional_price_rows)},
        )
    if media_rule_rows:
        add_blocker(
            blockers,
            "media_role_proof_missing",
            "Option-specific media rules require role-by-role media proof before mutation.",
            {"media_rule_row_count": len(media_rule_rows)},
        )
    return {
        "option_row_count": len(option_rows),
        "add_on_row_count": len(add_on_rows),
        "conditional_price_row_count": len(conditional_price_rows),
        "media_rule_row_count": len(media_rule_rows),
        "classification_counts": dict(sorted(classification_counts.items())),
        "missing_classification_count": len(missing_classification),
    }


def release_readiness_section(payload: dict[str, Any], blockers: list[dict[str, Any]]) -> dict[str, Any]:
    public_summary = payload.get("public_summary") if isinstance(payload.get("public_summary"), dict) else {}
    public_route_proved = bool(public_summary and not public_summary.get("skipped") and public_summary.get("status") == 200)
    if not public_route_proved:
        add_blocker(
            blockers,
            "public_route_proof_missing",
            "Saved artifact does not prove the public route response for this product.",
            {"public_summary": public_summary or None},
        )
    add_blocker(
        blockers,
        "pre_mutation_rollback_packet_missing",
        "Saved audit artifacts are not a pre-mutation rollback packet.",
        {"requires": "row-level planned diff plus rollback snapshots before any write"},
    )
    return {
        "public_route_proved": public_route_proved,
        "rollback_packet_complete": False,
        "mutation_approved": False,
        "deploy_approved": False,
        "cache_clear_approved": False,
    }


def build_report(packets: list[dict[str, Any]], paths: list[Path]) -> dict[str, Any]:
    blocked = [packet for packet in packets if packet["authority_status"] == "blocked"]
    blocker_breakdown: dict[str, int] = {}
    for packet in packets:
        for blocker in packet["blockers"]:
            code = str(blocker.get("code") or "unknown")
            blocker_breakdown[code] = blocker_breakdown.get(code, 0) + 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "proof_mode": "offline saved catalog authority JSON artifacts only; no env, network, Docker, ERPNext, browser, cache, deploy, or mutation",
        "artifact_count": len(paths),
        "product_count": len(packets),
        "blocked_product_count": len(blocked),
        "blocker_count": sum(len(packet["blockers"]) for packet in packets),
        "blocker_breakdown": dict(sorted(blocker_breakdown.items())),
        "catalog_authority_status": "blocked" if blocked else "ready",
        "packets": packets,
        "next_safe_actions": [
            "Resolve brand lane evidence before any active uniqueness or mutation approval.",
            "Resolve Product Setup match/status, Item Price parity, and variant-explosion blockers from saved evidence first.",
            "Use this as planning evidence only; it does not approve repair, cache clear, deploy, or live mutation.",
        ],
    }


def add_existing_failures(blockers: list[dict[str, Any]], failures: Any) -> None:
    for failure in as_list(failures):
        text = str(failure)
        if "brand lane" in text.lower():
            code = "brand_lane_unproved"
        elif "ambiguous" in text.lower() and "product" in text.lower():
            code = "product_setup_match_not_resolved"
        elif "not in an active authority status" in text.lower():
            code = "product_setup_inactive"
        else:
            code = "collector_failure"
        add_blocker(blockers, code, text, {"source": "artifact.failures"})


def brand_lane_state(value: Any, explicit_status: Any = None) -> str:
    status = str(explicit_status or "").strip()
    if status in {"proved", "verified", "resolved"}:
        return status
    brand = str(value or "").strip()
    if not brand:
        return "missing"
    if brand not in ALLOWED_OPERATING_BRANDS:
        return "invalid"
    return "source_declared"


def source_uniqueness_result(
    *,
    status: str,
    match_status: str,
    operating_brand: str,
    operating_brand_state: str,
    candidates: list[Any],
) -> dict[str, Any]:
    required = status in SOURCE_UNIQUENESS_STATUSES
    evidence: dict[str, Any] = {
        "publish_status": status or None,
        "operating_brand": operating_brand or None,
        "operating_brand_authority_state": operating_brand_state,
        "candidate_count": len(candidates),
    }
    if not required:
        return {"required": False, "proved": False, "status": "not_required", "evidence": evidence}
    if match_status != "matched":
        evidence["match_status"] = match_status
        return {"required": True, "proved": False, "status": "unproved_match_not_resolved", "evidence": evidence}
    if operating_brand_state != "source_declared":
        return {"required": True, "proved": False, "status": "unproved_operating_brand_not_source_declared", "evidence": evidence}
    if not candidates:
        return {"required": True, "proved": False, "status": "unproved_missing_candidate_evidence", "evidence": evidence}

    active_candidates = [candidate for candidate in candidates if candidate_active_for_source_uniqueness(candidate)]
    unknown_brand_candidates = [
        candidate for candidate in active_candidates if brand_lane_state(candidate.get("operating_brand")) in {"missing", "invalid"}
    ]
    same_brand_candidates = [
        candidate
        for candidate in active_candidates
        if str(candidate.get("operating_brand") or "").strip() == operating_brand
    ]
    evidence.update(
        {
            "active_source_candidate_count": len(active_candidates),
            "same_brand_active_source_candidate_count": len(same_brand_candidates),
            "unknown_brand_active_source_candidate_count": len(unknown_brand_candidates),
            "same_brand_active_source_candidates": [candidate.get("name") for candidate in same_brand_candidates if candidate.get("name")],
        }
    )
    if unknown_brand_candidates:
        return {"required": True, "proved": False, "status": "unproved_candidate_brand_missing", "evidence": evidence}
    if len(same_brand_candidates) > 1:
        return {"required": True, "proved": False, "status": "unproved_duplicate_same_brand", "evidence": evidence}
    if len(same_brand_candidates) == 1:
        return {"required": True, "proved": True, "status": "source_declared_unique", "evidence": evidence}
    return {"required": True, "proved": False, "status": "unproved_current_candidate_missing_source_brand", "evidence": evidence}


def candidate_active_for_source_uniqueness(candidate: Any) -> bool:
    return isinstance(candidate, dict) and str(candidate.get("publish_status") or "").strip() in SOURCE_UNIQUENESS_STATUSES


def price_next_action(drift_status: str, missing_runtime: list[str], setup_values: list[str], item_price_values: list[str]) -> str:
    if missing_runtime:
        return "Resolve missing Item Price authority rows before preview or repair."
    if not setup_values or not item_price_values:
        return "Collect complete Product Setup and Item Price proof before deciding."
    if drift_status == "mismatch":
        return "Build a no-write projection packet and approval review; do not mutate directly."
    if drift_status == "match":
        return "Price authority matches in saved artifact; keep checking other blockers."
    return "Price authority could not be checked from this artifact."


def next_action(
    blockers: list[dict[str, Any]],
    price: dict[str, Any],
    copy: dict[str, Any],
    variant: dict[str, Any],
    product_setup: dict[str, Any],
) -> str:
    codes = {blocker.get("code") for blocker in blockers}
    if "brand_lane_unproved" in codes:
        return "Resolve brand lane proof before any Product Setup authority or repair decision."
    if "product_setup_match_not_resolved" in codes or "product_setup_inactive" in codes:
        return "Resolve the active Product Setup authority record before projection work."
    if "price_mismatch" in codes or "missing_item_price_rows" in codes or "ambiguous_base_price_to_many_variants" in codes:
        return price["proposed_next_action"]
    if "variant_explosion" in codes:
        return "Review whether this product should stay SKU-expanded or move to configuration choices before publish/apply design."
    if copy["differs"]:
        return "Review Product Setup copy versus public Website Item copy before treating copy as live authority."
    if not product_setup["active_authority"]:
        return "Resolve remaining Product Setup authority blockers before mutation."
    if variant["variant_explosion"]:
        return "Review variant scale before mutation."
    return "No blockers found in saved artifact; still requires separate release packet before any write."


def add_blocker(blockers: list[dict[str, Any]], code: str, message: str, evidence: Any = None) -> None:
    blockers.append({"code": code, "message": message, "evidence": evidence if evidence is not None else {}})


def dedupe_blockers(blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for blocker in reversed(blockers):
        key = str(blocker.get("code") or json.dumps(blocker, sort_keys=True, default=str))
        if key not in seen:
            seen.add(key)
            result.append(blocker)
    return list(reversed(result))


def rows_from(parent: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = parent.get(key)
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def prices_by_item(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[str, list[Decimal]]:
    result: dict[str, list[Decimal]] = {}
    for row in rows:
        item_code = str(row.get("item_code") or row.get("target_item_code") or row.get("name") or "").strip()
        price = to_price(first_present(row, *keys))
        if item_code and price is not None:
            result.setdefault(item_code, []).append(price)
    return result


def prices_from_rows(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[Decimal]:
    return [price for row in rows if (price := to_price(first_present(row, *keys))) is not None]


def prices_from_values(value: Any) -> list[Decimal]:
    return [price for item in as_list(value) if (price := to_price(item)) is not None]


def to_price(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value).strip()).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def price_label(value: Decimal | None) -> str | None:
    return f"{value:.2f}" if value is not None else None


def unique_price_labels(values: list[Decimal]) -> list[str]:
    return [f"{value:.2f}" for value in sorted(set(values))]


def first_present(mapping: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    return None


def first_text(mapping: dict[str, Any], *keys: str) -> str | None:
    value = first_present(mapping, *keys)
    return None if value in (None, "") else str(value)


def normalize_copy(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", str(value))
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def excerpt(value: str | None, limit: int = 160) -> str | None:
    if value is None:
        return None
    text = normalize_copy(value)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=pretty, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise AuthorityPacketBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
