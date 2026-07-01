#!/usr/bin/env python3
"""Build an offline Product Setup pre-mutation release packet report.

This report consumes Phase 15 catalog readiness dashboard JSON. It is
source/offline only: no env files, network, Docker, browser profiles, ERPNext
reads, cache clear, deploy, provider calls, customer messages, or catalog
mutation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lt-product-setup-release-packet-v1"
DASHBOARD_SCHEMA_VERSION = "lt-product-setup-catalog-readiness-dashboard-v1"
PROOF_MODE = (
    "offline saved Phase 15 catalog readiness dashboard JSON only; no live reads, "
    "writes, cache clear, deploy, provider, payment, DNS, customer message, or catalog mutation"
)
APPROVALS_FALSE = {
    "local_apply_approved": False,
    "staging_apply_approved": False,
    "live_apply_approved": False,
    "mutation_approved": False,
    "catalog_mutation_approved": False,
    "cache_clear_approved": False,
    "deploy_approved": False,
    "provider_action_approved": False,
    "payment_action_approved": False,
    "customer_message_approved": False,
    "public_success_claim_allowed": False,
}


class ReleasePacketBlocked(RuntimeError):
    """Raised when offline input is missing, malformed, or ambiguous."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        dashboard = load_dashboard(Path(args.dashboard))
        product_row = select_product_row(dashboard, args.product)
        report = build_report(dashboard, product_row, args.product, args.dashboard)
        write_report(report, args.output, pretty=args.pretty)
    except ReleasePacketBlocked as exc:
        print(f"[LT PRODUCT SETUP RELEASE PACKET] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP RELEASE PACKET] FAIL: {exc}", file=sys.stderr)
        return 1

    status = "FAIL" if report["release_packet"]["blocked"] else "PASS"
    print(f"[LT PRODUCT SETUP RELEASE PACKET] {status}", file=sys.stderr)
    print(f"  product: {report['product']['item_code']}", file=sys.stderr)
    print(f"  dashboard_blockers: {report['source_dashboard_summary']['selected_product_blocker_count']}", file=sys.stderr)
    print(f"  missing_gates: {len(report['missing_gates'])}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and report["release_packet"]["blocked"]:
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dashboard", required=True, help="Saved Phase 15 catalog readiness dashboard JSON.")
    parser.add_argument(
        "--product",
        required=True,
        help="Product filter matching product_setup, item_code, route slug, or route.",
    )
    parser.add_argument("--output", help="Optional release packet JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 while release packet blockers remain.")
    return parser.parse_args(argv)


def load_dashboard(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ReleasePacketBlocked(f"dashboard does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReleasePacketBlocked(f"dashboard is not valid JSON: {path}: {exc}") from exc
    except OSError as exc:
        raise ReleasePacketBlocked(f"could not read dashboard: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ReleasePacketBlocked(f"dashboard JSON root must be an object: {path}")
    if payload.get("schema_version") != DASHBOARD_SCHEMA_VERSION:
        raise ReleasePacketBlocked(f"unexpected dashboard schema_version: {payload.get('schema_version')}")
    rows = payload.get("product_rows")
    if not isinstance(rows, list):
        raise ReleasePacketBlocked("dashboard must contain a product_rows list")
    if any(not isinstance(row, dict) for row in rows):
        raise ReleasePacketBlocked("every dashboard product row must be an object")
    return payload


def select_product_row(dashboard: dict[str, Any], product_filter: str) -> dict[str, Any]:
    wanted = normalize(product_filter)
    matches = [
        row
        for row in dashboard.get("product_rows", [])
        if wanted and wanted in product_match_keys(row)
    ]
    if not matches:
        raise ReleasePacketBlocked(f"dashboard has no product row matching {product_filter!r}")
    if len(matches) > 1:
        match_names = ", ".join(str(section(row, "product").get("item_code") or "<unknown>") for row in matches)
        raise ReleasePacketBlocked(f"product filter {product_filter!r} matched multiple rows: {match_names}")
    return matches[0]


def build_report(
    dashboard: dict[str, Any],
    product_row: dict[str, Any],
    product_filter: str,
    source_path: str,
) -> dict[str, Any]:
    product = product_identifiers(product_row)
    dashboard_blockers = blocker_codes(product_row)
    proof_gates = build_proof_gates(product_row, dashboard_blockers)
    missing_gates = [gate for gate in proof_gates if gate["required"] and not gate["passed"]]
    blocked = bool(dashboard_blockers or missing_gates)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": "deterministic-offline-report",
        "deterministic": True,
        "proof_mode": PROOF_MODE,
        "product_filter": product_filter,
        "product": product,
        "source_dashboard_summary": source_dashboard_summary(dashboard, product_row, source_path),
        "release_packet": {
            "status": "blocked" if blocked else "approved",
            "blocked": blocked,
            "approved": False,
            "approval_reason": "No live or mutation approval exists in this source-only packet.",
            "dashboard_blocker_count": len(dashboard_blockers),
            "missing_gate_count": len(missing_gates),
        },
        "proof_gates": proof_gates,
        "missing_gates": missing_gates,
        "rollback_requirements": rollback_requirements(product_row),
        "target_environment_approvals": target_environment_approvals(),
        "no_downtime_customer_impact": no_downtime_customer_impact(),
        "stop_condition": stop_condition(product, dashboard_blockers, missing_gates),
        "owner_allowed_actions": owner_allowed_actions(blocked),
        "developer_allowed_actions": developer_allowed_actions(blocked),
        "approval_contract": dict(APPROVALS_FALSE),
    }


def product_identifiers(row: dict[str, Any]) -> dict[str, Any]:
    product = section(row, "product")
    route = product.get("route")
    return {
        "product_setup": product.get("product_setup"),
        "item_code": product.get("item_code"),
        "website_item": product.get("website_item"),
        "route": route,
        "route_slug": route_slug(route),
        "product_name": product.get("product_name"),
        "operating_brand": product.get("operating_brand"),
        "operating_brand_authority_state": product.get("operating_brand_authority_state"),
        "brand_lane_status": product.get("brand_lane_status"),
    }


def source_dashboard_summary(dashboard: dict[str, Any], row: dict[str, Any], source_path: str) -> dict[str, Any]:
    counts = section(dashboard, "catalog_counts")
    blockers = section(row, "blockers")
    readiness = section(row, "readiness")
    release = section(row, "release_readiness")
    return {
        "path": source_path,
        "dashboard_schema_version": dashboard.get("schema_version"),
        "dashboard_proof_mode": dashboard.get("proof_mode"),
        "catalog_product_count": int_value(counts.get("product_count")),
        "catalog_blocked_product_count": int_value(counts.get("blocked_product_count")),
        "catalog_blocker_count": int_value(counts.get("blocker_count")),
        "selected_product_authority_status": readiness.get("authority_status"),
        "selected_product_owner_state": readiness.get("owner_state"),
        "selected_product_blocker_count": int_value(blockers.get("count")),
        "selected_product_blocker_codes": list_from(blockers.get("codes")),
        "selected_product_blocker_groups": list_from(blockers.get("groups")),
        "saved_source_public_route_proved": bool(release.get("public_route_proved")),
        "saved_source_rollback_packet_complete": bool(release.get("rollback_packet_complete")),
    }


def build_proof_gates(row: dict[str, Any], dashboard_blockers: list[str]) -> list[dict[str, Any]]:
    release = section(row, "release_readiness")
    readiness = section(row, "readiness")
    return [
        gate("phase_15_dashboard_loaded", True, "Saved Phase 15 dashboard JSON was loaded.", required=True),
        gate("product_filter_matched", True, "Exactly one product row matched the requested filter.", required=True),
        gate(
            "dashboard_blockers_clear",
            not dashboard_blockers,
            "Selected product has no Phase 15 dashboard blockers.",
            required=True,
            evidence={"blocker_codes": dashboard_blockers},
        ),
        gate(
            "fresh_target_site_public_route_proof",
            False,
            "Fresh target-site public route proof is not present in the Phase 15 dashboard.",
            required=True,
            evidence={"saved_source_public_route_proved": bool(release.get("public_route_proved"))},
        ),
        gate(
            "fresh_target_site_cart_checkout_document_proof",
            False,
            "Cart, checkout, document, and receipt proof is not present.",
            required=True,
        ),
        gate(
            "rollback_packet_complete_and_reviewed",
            False,
            "Rollback rows, procedure, owner scope, and review approval are not complete.",
            required=True,
            evidence={"saved_source_rollback_packet_complete": bool(release.get("rollback_packet_complete"))},
        ),
        gate(
            "owner_product_scope_approval",
            False,
            "Owner approval for this exact product and target environment is not present.",
            required=True,
        ),
        gate(
            "developer_release_review",
            False,
            "Developer release review has not approved mutation, cache clear, deploy, or live apply.",
            required=True,
        ),
        gate(
            "target_environment_approval",
            False,
            "No local, staging, or live target environment approval is present.",
            required=True,
        ),
        gate(
            "no_downtime_customer_impact_approval",
            False,
            "No downtime and customer-impact approval is not present.",
            required=True,
        ),
        gate(
            "public_success_claim_allowed",
            bool(readiness.get("public_success_claim_allowed")),
            "Public success claims are not allowed from source-only evidence.",
            required=True,
        ),
    ]


def gate(
    name: str,
    passed: bool,
    message: str,
    *,
    required: bool,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "gate": name,
        "required": required,
        "passed": bool(passed),
        "message": message,
        "evidence": evidence or {},
    }


def rollback_requirements(row: dict[str, Any]) -> dict[str, Any]:
    release = section(row, "release_readiness")
    return {
        "required": True,
        "complete": False,
        "saved_source_rollback_packet_complete": bool(release.get("rollback_packet_complete")),
        "requirements": [
            "Exact rows and fields to mutate must be named before any write.",
            "Pre-mutation values must be captured from the target environment.",
            "Rollback command or manual procedure must be reviewed before any write.",
            "Rollback owner and stop point must be named before any write.",
            "Post-rollback public route and cart proof must be planned before any write.",
        ],
    }


def target_environment_approvals() -> dict[str, Any]:
    return {
        "local": {
            "target_site_proof_present": False,
            "apply_approved": False,
            "mutation_approved": False,
            "cache_clear_approved": False,
        },
        "staging": {
            "target_site_proof_present": False,
            "apply_approved": False,
            "mutation_approved": False,
            "cache_clear_approved": False,
            "deploy_approved": False,
            "provider_action_approved": False,
            "payment_action_approved": False,
            "customer_message_approved": False,
        },
        "live": {
            "target_site_proof_present": False,
            "apply_approved": False,
            "mutation_approved": False,
            "cache_clear_approved": False,
            "deploy_approved": False,
            "provider_action_approved": False,
            "payment_action_approved": False,
            "customer_message_approved": False,
        },
    }


def no_downtime_customer_impact() -> dict[str, Any]:
    return {
        "required": True,
        "approved": False,
        "downtime_approved": False,
        "customer_impact_approved": False,
        "customer_message_approved": False,
        "requirements": [
            "No public success message may be shown until post-apply proof passes.",
            "Customer-facing route, cart, checkout, document, and receipt behavior must be checked.",
            "Cache behavior must be named and approved before any cache clear.",
            "Payment/provider behavior must stay blocked unless separately approved.",
            "Customer messages must stay blocked unless separately approved.",
        ],
    }


def stop_condition(product: dict[str, Any], dashboard_blockers: list[str], missing_gates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "stop": True,
        "reason": "Release packet is source-only and blocked; do not mutate, deploy, clear cache, use providers, take payment action, or message customers.",
        "product": product.get("item_code"),
        "dashboard_blockers": dashboard_blockers,
        "missing_gate_names": [gate["gate"] for gate in missing_gates],
    }


def owner_allowed_actions(blocked: bool) -> list[dict[str, Any]]:
    return [
        {"action": "Review release packet", "allowed": True, "reason": "Reviewing this JSON does not change the catalog."},
        {"action": "Save draft Product Setup edits", "allowed": True, "reason": "Draft saves do not claim public success."},
        {"action": "Ask for target-site proof", "allowed": True, "reason": "Proof can be requested before any write."},
        {"action": "Treat this packet as live approval", "allowed": False, "reason": "This packet is explicitly blocked."},
        {
            "action": "Publish/apply/cache/deploy/live mutation",
            "allowed": False,
            "reason": "Blocked until proof gates and approvals exist." if blocked else "Still requires a separate explicit live approval.",
        },
    ]


def developer_allowed_actions(blocked: bool) -> list[dict[str, Any]]:
    return [
        {"action": "Run offline verifiers", "allowed": True, "reason": "Offline verification does not mutate target records."},
        {"action": "Prepare target-site proof plan", "allowed": True, "reason": "A plan can be prepared without writing records."},
        {"action": "Prepare rollback procedure", "allowed": True, "reason": "Rollback design is required before any write."},
        {"action": "Mutate Product Setup, Item, Website Item, Item Price, cache, deploy, provider, payment, or customer message state", "allowed": False, "reason": "No approval exists in this packet."},
    ] if blocked else [
        {"action": "Run offline verifiers", "allowed": True, "reason": "Offline verification does not mutate target records."},
        {"action": "Prepare reviewed apply packet", "allowed": True, "reason": "This report is not itself apply approval."},
        {"action": "Mutate Product Setup, Item, Website Item, Item Price, cache, deploy, provider, payment, or customer message state", "allowed": False, "reason": "A separate approval is still required."},
    ]


def product_match_keys(row: dict[str, Any]) -> set[str]:
    product = section(row, "product")
    route = product.get("route")
    return {
        normalize(product.get("product_setup")),
        normalize(product.get("item_code")),
        normalize(route),
        normalize(route_slug(route)),
    } - {""}


def blocker_codes(row: dict[str, Any]) -> list[str]:
    blockers = section(row, "blockers")
    return sorted(str(code) for code in list_from(blockers.get("codes")) if str(code))


def route_slug(route: Any) -> str | None:
    value = str(route or "").strip().strip("/")
    if not value:
        return None
    return value.split("/")[-1]


def normalize(value: Any) -> str:
    return str(value or "").strip().lower().strip("/")


def section(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    return value if isinstance(value, dict) else {}


def list_from(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=True, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise ReleasePacketBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
