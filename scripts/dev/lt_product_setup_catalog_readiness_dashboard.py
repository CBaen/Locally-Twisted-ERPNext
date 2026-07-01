#!/usr/bin/env python3
"""Build an offline catalog readiness dashboard from Product Setup packets.

This report consumes saved JSON from
``lt_product_setup_authority_packet_report.py``. It is source/offline only: no
env files, network, Docker, browser profiles, ERPNext reads, cache clear,
deploy, provider calls, customer messages, or catalog mutation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lt-product-setup-catalog-readiness-dashboard-v1"
PROOF_MODE = (
    "offline saved authority packet report JSON only; no live reads, writes, "
    "cache clear, deploy, provider, payment, DNS, or customer action"
)
APPROVALS_FALSE = {
    "local_apply_approved": False,
    "staging_apply_approved": False,
    "live_apply_approved": False,
    "cache_clear_approved": False,
    "deploy_approved": False,
    "mutation_approved": False,
    "public_success_claim_allowed": False,
}
BLOCKER_GROUP_RULES = {
    "price_runtime": (
        "price",
        "item_price",
        "base_price",
    ),
    "authority_identity": (
        "brand",
        "active_uniqueness",
        "product_setup",
        "match",
        "source",
    ),
    "copy_content": (
        "copy",
        "content",
        "website_item_copy",
    ),
    "variant_model": (
        "variant",
        "sku",
        "option_classification",
    ),
    "media_options_addons": (
        "media",
        "gallery",
        "slideshow",
        "add_on",
        "conditional",
        "option",
    ),
    "public_release_proof": (
        "public",
        "route",
        "rollback",
        "mutation",
        "release",
        "approval",
        "deploy",
        "cache",
    ),
}


class CatalogReadinessBlocked(RuntimeError):
    """Raised when offline input is missing or malformed."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        packet_report = load_packet_report(Path(args.packet_report))
        dashboard = build_dashboard(packet_report, args.packet_report)
        write_report(dashboard, args.output, pretty=args.pretty)
    except CatalogReadinessBlocked as exc:
        print(f"[LT PRODUCT SETUP CATALOG READINESS DASHBOARD] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP CATALOG READINESS DASHBOARD] FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        "[LT PRODUCT SETUP CATALOG READINESS DASHBOARD] "
        + ("FAIL" if dashboard["catalog_counts"]["blocker_count"] else "PASS"),
        file=sys.stderr,
    )
    print(f"  products: {dashboard['catalog_counts']['product_count']}", file=sys.stderr)
    print(f"  blocked_products: {dashboard['catalog_counts']['blocked_product_count']}", file=sys.stderr)
    print(f"  blockers: {dashboard['catalog_counts']['blocker_count']}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and dashboard["catalog_counts"]["blocker_count"]:
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--packet-report", required=True, help="Saved Phase 4 authority packet report JSON.")
    parser.add_argument("--output", help="Optional dashboard JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 while catalog blockers remain.")
    return parser.parse_args(argv)


def load_packet_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise CatalogReadinessBlocked(f"packet report does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogReadinessBlocked(f"packet report is not valid JSON: {path}: {exc}") from exc
    except OSError as exc:
        raise CatalogReadinessBlocked(f"could not read packet report: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CatalogReadinessBlocked(f"packet report JSON root must be an object: {path}")
    packets = payload.get("packets")
    if not isinstance(packets, list):
        raise CatalogReadinessBlocked("packet report must contain a packets list")
    if any(not isinstance(packet, dict) for packet in packets):
        raise CatalogReadinessBlocked("every packet row must be an object")
    return payload


def build_dashboard(packet_report: dict[str, Any], source_path: str) -> dict[str, Any]:
    packets = [packet for packet in packet_report.get("packets", []) if isinstance(packet, dict)]
    product_rows = [product_row(packet) for packet in packets]
    blocker_groups = blocker_group_summary(product_rows)
    variant_summary = variant_explosion_summary(product_rows)
    catalog_counts = catalog_count_summary(packet_report, product_rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": "deterministic-offline-report",
        "deterministic": True,
        "proof_mode": PROOF_MODE,
        "source_report": {
            "path": source_path,
            "catalog_authority_status": packet_report.get("catalog_authority_status"),
            "source_product_count": int_value(packet_report.get("product_count"), default=len(packets)),
            "source_blocker_count": int_value(packet_report.get("blocker_count")),
            "source_blocked_product_count": int_value(packet_report.get("blocked_product_count")),
            "source_generated_at": packet_report.get("generated_at"),
        },
        "catalog_counts": catalog_counts,
        "blocker_group_counts": blocker_groups,
        "variant_explosion_summary": variant_summary,
        "owner_safe_actions": owner_safe_actions(catalog_counts["blocker_count"]),
        "developer_next_actions": developer_next_actions(blocker_groups, variant_summary),
        "publish_apply_approval": dict(APPROVALS_FALSE),
        "product_rows": product_rows,
    }


def product_row(packet: dict[str, Any]) -> dict[str, Any]:
    identifier = section(packet, "product_identifier")
    product_setup = section(packet, "product_setup")
    source_authority = section(packet, "source_authority")
    price = section(packet, "price")
    copy = section(packet, "copy")
    variant = section(packet, "variant")
    option = section(packet, "option")
    release = section(packet, "release_readiness")
    blockers = blockers_from(packet)
    blocker_codes = sorted({str(blocker.get("code") or "unknown") for blocker in blockers})
    grouped_codes = sorted({group_for_code(code) for code in blocker_codes})
    operating_brand = source_operating_brand(source_authority, product_setup, identifier)
    row = {
        "product": {
            "product_setup": identifier.get("product_setup") or product_setup.get("name"),
            "item_code": identifier.get("item_code"),
            "website_item": identifier.get("website_item"),
            "route": identifier.get("route"),
            "product_name": identifier.get("product_name"),
            "operating_brand": operating_brand.get("value"),
            "operating_brand_authority_state": operating_brand.get("authority_state"),
            "brand_lane_status": identifier.get("brand_lane_status"),
        },
        "readiness": {
            "authority_status": packet.get("authority_status") or ("blocked" if blockers else "ready"),
            "owner_state": "Blocked - Proof Needed" if blockers else "Ready For Reviewed Apply",
            "public_success_claim_allowed": False,
            "next_owner_action": owner_next_action(blockers),
            "next_developer_action": packet.get("next_action") or developer_next_action_for_row(blocker_codes),
        },
        "blockers": {
            "count": len(blockers),
            "codes": blocker_codes,
            "groups": grouped_codes,
            "primary_code": blocker_codes[0] if blocker_codes else None,
        },
        "authority": {
            "product_setup_match_status": product_setup.get("match_status"),
            "product_setup_publish_status": product_setup.get("publish_status"),
            "product_setup_active_status": bool(product_setup.get("active_status")),
            "product_setup_active_authority": bool(product_setup.get("active_authority")),
            "live_brand_lane_proved": live_brand_lane_proved(source_authority, product_setup),
            "same_brand_source_uniqueness_status": same_brand_source_uniqueness_status(source_authority, product_setup),
            "same_brand_source_uniqueness_proved": same_brand_source_uniqueness_proved(source_authority, product_setup),
        },
        "price": {
            "drift_status": price.get("drift_status"),
            "setup_values": as_list(price.get("setup_values")),
            "item_price_values": as_list(price.get("item_price_values")),
            "setup_base_price": price.get("setup_base_price"),
            "product_setup_price_rows": int_value(section(price, "row_counts").get("product_setup_price_rows")),
            "item_price_rows": int_value(section(price, "row_counts").get("item_price_rows")),
            "mismatched_item_price_count": int_value(price.get("mismatched_item_price_count")),
            "missing_runtime_item_price_count": int_value(price.get("missing_runtime_item_price_count")),
        },
        "copy": {
            "differs": bool(copy.get("differs")),
            "difference_count": int_value(section(copy, "evidence").get("difference_count")),
            "product_setup_fields_present": bool(copy.get("product_setup_fields_present")),
            "website_item_public_fields_present": bool(copy.get("website_item_public_fields_present")),
        },
        "variant": {
            "variants": int_value(variant.get("variants")),
            "item_prices": int_value(variant.get("item_prices")),
            "severity_bucket": variant.get("severity_bucket") or "unknown",
            "variant_explosion": bool(variant.get("variant_explosion")),
        },
        "option": {
            "option_row_count": int_value(option.get("option_row_count")),
            "add_on_row_count": int_value(option.get("add_on_row_count")),
            "conditional_price_row_count": int_value(option.get("conditional_price_row_count")),
            "media_rule_row_count": int_value(option.get("media_rule_row_count")),
            "missing_classification_count": int_value(option.get("missing_classification_count")),
        },
        "release_readiness": {
            "public_route_proved": bool(release.get("public_route_proved")),
            "rollback_packet_complete": bool(release.get("rollback_packet_complete")),
            "approvals": dict(APPROVALS_FALSE),
        },
    }
    return row


def catalog_count_summary(packet_report: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    blocker_count = sum(int_value(row["blockers"]["count"]) for row in rows)
    blocked_product_count = sum(1 for row in rows if row["blockers"]["count"])
    return {
        "artifact_count": int_value(packet_report.get("artifact_count"), default=len(rows)),
        "product_count": len(rows),
        "blocked_product_count": blocked_product_count,
        "ready_product_count": len(rows) - blocked_product_count,
        "blocker_count": blocker_count,
        "products_with_price_mismatch": count_rows(rows, "price", "drift_status", "mismatch"),
        "products_with_copy_drift": sum(1 for row in rows if row["copy"]["differs"]),
        "products_with_variant_explosion": sum(1 for row in rows if row["variant"]["variant_explosion"]),
        "products_with_public_route_proof": sum(1 for row in rows if row["release_readiness"]["public_route_proved"]),
        "product_setup_matches": count_rows(rows, "authority", "product_setup_match_status", "matched"),
        "active_product_setups": sum(1 for row in rows if row["authority"]["product_setup_active_status"]),
        "inactive_product_setups": sum(1 for row in rows if not row["authority"]["product_setup_active_status"]),
        "source_declared_operating_brands": count_rows(rows, "product", "operating_brand_authority_state", "source_declared"),
        "live_brand_lane_proved": sum(1 for row in rows if row["authority"]["live_brand_lane_proved"]),
        "mutation_approved_products": 0,
        "deploy_approved_products": 0,
        "cache_clear_approved_products": 0,
        "live_apply_approved_products": 0,
    }


def blocker_group_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {
        key: {"blocker_count": 0, "product_count": 0, "codes": {}} for key in sorted((*BLOCKER_GROUP_RULES, "other"))
    }
    for row in rows:
        seen_groups: set[str] = set()
        for code in row["blockers"]["codes"]:
            group = group_for_code(code)
            groups[group]["blocker_count"] += 1
            groups[group]["codes"][code] = groups[group]["codes"].get(code, 0) + 1
            seen_groups.add(group)
        for group in seen_groups:
            groups[group]["product_count"] += 1
    return {
        group: {
            "blocker_count": values["blocker_count"],
            "product_count": values["product_count"],
            "codes": dict(sorted(values["codes"].items())),
        }
        for group, values in groups.items()
        if values["blocker_count"]
    }


def variant_explosion_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    severity_counts: dict[str, int] = {}
    explosion_rows = []
    for row in rows:
        severity = str(row["variant"]["severity_bucket"] or "unknown")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        if row["variant"]["variant_explosion"]:
            explosion_rows.append(
                {
                    "product_setup": row["product"]["product_setup"],
                    "item_code": row["product"]["item_code"],
                    "route": row["product"]["route"],
                    "variants": row["variant"]["variants"],
                    "item_prices": row["variant"]["item_prices"],
                    "severity_bucket": row["variant"]["severity_bucket"],
                    "owner_state": row["readiness"]["owner_state"],
                }
            )
    explosion_rows.sort(key=lambda row: (-int_value(row.get("variants")), str(row.get("item_code") or "")))
    largest = sorted(
        (
            {
                "product_setup": row["product"]["product_setup"],
                "item_code": row["product"]["item_code"],
                "variants": row["variant"]["variants"],
                "item_prices": row["variant"]["item_prices"],
                "severity_bucket": row["variant"]["severity_bucket"],
            }
            for row in rows
        ),
        key=lambda row: (-int_value(row.get("variants")), str(row.get("item_code") or "")),
    )[:10]
    return {
        "variant_explosion_count": len(explosion_rows),
        "severity_counts": dict(sorted(severity_counts.items())),
        "products": explosion_rows,
        "largest_products": largest,
    }


def owner_safe_actions(blocker_count: int) -> list[dict[str, Any]]:
    blocked = blocker_count > 0
    return [
        {"action": "Save draft Product Setup edits", "allowed": True, "reason": "Draft saves do not claim public success."},
        {"action": "Request technical review", "allowed": True, "reason": "Review can continue from offline evidence."},
        {"action": "Review no-write dashboard", "allowed": True, "reason": "Dashboard review does not mutate catalog data."},
        {"action": "Treat saved Product Setup as live proof", "allowed": False, "reason": "Saved authoring data is not public/runtime proof."},
        {
            "action": "Publish/apply/cache/deploy/live mutation",
            "allowed": False,
            "reason": "Blocked until catalog blockers, owner approval, release packet, and post-apply proof are complete."
            if blocked
            else "Still requires a separate reviewed apply packet and explicit approval.",
        },
    ]


def developer_next_actions(groups: dict[str, Any], variant_summary: dict[str, Any]) -> list[str]:
    actions = []
    if "authority_identity" in groups:
        actions.append("Resolve brand lane, Product Setup match, status, and source uniqueness evidence.")
    if "price_runtime" in groups:
        actions.append("Resolve Product Setup price rows against Item Price runtime authority from saved evidence.")
    if "copy_content" in groups:
        actions.append("Review Product Setup copy against Website Item public copy fields.")
    if "variant_model" in groups or variant_summary["variant_explosion_count"]:
        actions.append("Classify high-variant products before any SKU collapse or apply design.")
    if "media_options_addons" in groups:
        actions.append("Capture media, option, add-on, and conditional pricing proof before owner-facing use.")
    if "public_release_proof" in groups:
        actions.append("Prepare public route, rollback, approval, and release proof packets before mutation.")
    return actions or ["No packet blockers found; still prepare a reviewed apply packet before any write."]


def owner_next_action(blockers: list[dict[str, Any]]) -> str:
    codes = {str(blocker.get("code") or "") for blocker in blockers}
    if not blockers:
        return "Request reviewed apply packet; do not assume automatic live change."
    if "brand_lane_unproved" in codes or "active_uniqueness_unproved" in codes:
        return "Keep editing or request technical review; brand and source authority proof is still needed."
    if any("price" in code for code in codes):
        return "Request price/runtime review before treating the product as ready."
    if "variant_explosion" in codes:
        return "Request SKU/choice-shape review before publish design."
    return "Request technical review; this product is not ready for live apply."


def developer_next_action_for_row(codes: list[str]) -> str:
    groups = {group_for_code(code) for code in codes}
    if "authority_identity" in groups:
        return "Resolve product authority identity blockers first."
    if "price_runtime" in groups:
        return "Resolve price/runtime parity blockers first."
    if "variant_model" in groups:
        return "Resolve variant model blockers first."
    if "public_release_proof" in groups:
        return "Build public proof and rollback packet before mutation."
    return "Review remaining blockers from saved packet evidence."


def group_for_code(code: str) -> str:
    normalized = str(code or "unknown").lower()
    for group, needles in BLOCKER_GROUP_RULES.items():
        if any(needle in normalized for needle in needles):
            return group
    return "other"


def blockers_from(packet: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = packet.get("blockers")
    if not isinstance(blockers, list):
        return []
    return [blocker if isinstance(blocker, dict) else {"code": str(blocker), "message": str(blocker)} for blocker in blockers]


def source_operating_brand(
    source_authority: dict[str, Any],
    product_setup: dict[str, Any],
    identifier: dict[str, Any],
) -> dict[str, Any]:
    source_brand = section(source_authority, "operating_brand")
    value = source_brand.get("value") or product_setup.get("operating_brand") or identifier.get("brand_lane")
    state = source_brand.get("authority_state") or product_setup.get("operating_brand_authority_state")
    return {"value": value, "authority_state": state}


def live_brand_lane_proved(source_authority: dict[str, Any], product_setup: dict[str, Any]) -> bool:
    source_brand = section(source_authority, "operating_brand")
    if "live_brand_lane_proved" in source_brand:
        return bool(source_brand.get("live_brand_lane_proved"))
    return bool(product_setup.get("brand_lane_proved"))


def same_brand_source_uniqueness_status(source_authority: dict[str, Any], product_setup: dict[str, Any]) -> Any:
    source_uniqueness = section(source_authority, "same_brand_source_uniqueness")
    return source_uniqueness.get("status") or product_setup.get("source_active_uniqueness_status")


def same_brand_source_uniqueness_proved(source_authority: dict[str, Any], product_setup: dict[str, Any]) -> bool:
    source_uniqueness = section(source_authority, "same_brand_source_uniqueness")
    if "proved" in source_uniqueness:
        return bool(source_uniqueness.get("proved"))
    return bool(product_setup.get("source_active_uniqueness_proved"))


def section(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def count_rows(rows: list[dict[str, Any]], section_name: str, field: str, expected: Any) -> int:
    return sum(1 for row in rows if row[section_name].get(field) == expected)


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=True, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise CatalogReadinessBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
