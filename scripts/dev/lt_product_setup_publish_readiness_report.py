#!/usr/bin/env python3
"""Build a source-only Product Setup publish readiness report.

This report is meant for owner/workflow design: it turns no-write Product Setup
analysis packets into plain blocked/ready states without mutating catalog data.
It does not read live ERPNext, credentials, providers, cache state, browser
profiles, or customer systems.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "lt-product-setup-publish-readiness-v1"
PROOF_MODE = "offline saved report JSON only; no live reads, writes, cache clear, deploy, provider, payment, DNS, or customer action"
DEFAULT_PRODUCT = "birthday-deliveries"
BLOCKER_GROUPS = {
    "brand_and_public_route": ("brand", "route", "public"),
    "price_and_sku_model": ("price", "sku", "variant", "item_price"),
    "options_addons_payload": ("add_on", "payload", "configuration", "non_sku"),
    "media_files": ("file", "slideshow", "media", "gallery", "image"),
    "history_and_rollback": ("historical", "rollback", "reference"),
    "approval_and_release": ("approval", "release", "mutation", "owner"),
}


class PublishReadinessBlocked(RuntimeError):
    """Raised when input files are missing or malformed."""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        replacement = load_replacement(Path(args.replacement))
        report = build_report(replacement, args.product)
        write_report(report, args.output, pretty=args.pretty)
    except PublishReadinessBlocked as exc:
        print(f"[LT PRODUCT SETUP PUBLISH READINESS] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP PUBLISH READINESS] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[LT PRODUCT SETUP PUBLISH READINESS] " + ("FAIL" if report["blocker_count"] else "PASS"), file=sys.stderr)
    print(f"  product: {report['product']['item_code']}", file=sys.stderr)
    print(f"  owner_status: {report['owner_status']['state']}", file=sys.stderr)
    print(f"  blockers: {report['blocker_count']}", file=sys.stderr)
    if args.output:
        print(f"  output: {Path(args.output).resolve()}", file=sys.stderr)
    if args.fail_on_blocker and report["blocker_count"]:
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--replacement", required=True, help="Phase 11 replacement model report JSON.")
    parser.add_argument("--product", default=DEFAULT_PRODUCT, help=f"Product filter. Defaults to {DEFAULT_PRODUCT}.")
    parser.add_argument("--output", help="Optional report JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Exit 1 while blockers remain.")
    return parser.parse_args(argv)


def load_replacement(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PublishReadinessBlocked(f"replacement report does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PublishReadinessBlocked(f"replacement report is not valid JSON: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise PublishReadinessBlocked(f"replacement JSON root must be an object: {path}")
    if payload.get("schema_version") != "lt-product-setup-replacement-model-v1":
        raise PublishReadinessBlocked(f"unexpected replacement schema_version: {payload.get('schema_version')}")
    return payload


def build_report(replacement: dict[str, Any], product_filter: str) -> dict[str, Any]:
    product = replacement.get("product") if isinstance(replacement.get("product"), dict) else {}
    if normalize(product_filter) not in {
        normalize(product.get("product_setup")),
        normalize(product.get("item_code")),
        normalize(product.get("route_slug")),
        normalize(str(product.get("route") or "").strip("/").split("/")[-1]),
    }:
        raise PublishReadinessBlocked(f"replacement report product does not match {product_filter!r}")
    blockers = replacement.get("blockers") if isinstance(replacement.get("blockers"), list) else []
    grouped = grouped_blockers(blockers)
    owner_status = owner_status_for(blockers)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": "deterministic-offline-report",
        "deterministic": True,
        "proof_mode": PROOF_MODE,
        "product_filter": product_filter,
        "product": product,
        "owner_status": owner_status,
        "state_machine_contract": state_machine_contract(),
        "blocker_count": len(blockers),
        "blocker_groups": grouped,
        "owner_allowed_actions": owner_allowed_actions(blockers),
        "developer_next_actions": developer_next_actions(grouped),
        "publish_apply_approval": {
            "local_apply_approved": False,
            "staging_apply_approved": False,
            "live_apply_approved": False,
            "cache_clear_approved": False,
            "deploy_approved": False,
            "mutation_approved": False,
        },
        "source_report_summary": {
            "replacement_schema_version": replacement.get("schema_version"),
            "replacement_blocker_count": replacement.get("blocker_count"),
            "candidate_sku_variant_count": ((replacement.get("replacement_model") or {}).get("candidate_sku_variant_count") if isinstance(replacement.get("replacement_model"), dict) else None),
        },
    }


def owner_status_for(blockers: list[Any]) -> dict[str, Any]:
    if blockers:
        return {
            "state": "Blocked - Proof Needed",
            "plain_message": "This product is mapped, but it is not ready to publish. The site still needs price, option, public page, history, and rollback proof before a live change is safe.",
            "public_success_claim_allowed": False,
            "next_owner_step": "Keep editing the Product Setup or request technical review; do not treat Save as a live website update.",
        }
    return {
        "state": "Ready For Reviewed Apply",
        "plain_message": "The no-write packet has no blockers. A separate reviewed apply packet is still required before any live change.",
        "public_success_claim_allowed": False,
        "next_owner_step": "Request reviewed apply packet.",
    }


def state_machine_contract() -> list[dict[str, Any]]:
    return [
        {"state": "Draft", "owner_meaning": "Safe to edit. Nothing public is promised.", "requires_public_proof": False},
        {"state": "Needs Review", "owner_meaning": "A human can ask for review, but no public change is promised.", "requires_public_proof": False},
        {"state": "Local Proof Ready", "owner_meaning": "Local proof exists only. Not live.", "requires_public_proof": False},
        {"state": "Staging Ready", "owner_meaning": "Staging proof exists. Not live.", "requires_public_proof": True},
        {"state": "Approved For Live", "owner_meaning": "Approved for a controlled live apply packet, not automatically live.", "requires_public_proof": True},
        {"state": "Live Applied", "owner_meaning": "Live route, cart, documents, rollback, and cache proof passed after apply.", "requires_public_proof": True},
    ]


def grouped_blockers(blockers: list[Any]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {group: [] for group in BLOCKER_GROUPS}
    groups["other"] = []
    for blocker in blockers:
        row = blocker if isinstance(blocker, dict) else {"code": str(blocker), "message": str(blocker)}
        code = normalize(row.get("code"))
        target = "other"
        for group, needles in BLOCKER_GROUPS.items():
            if any(needle in code for needle in needles):
                target = group
                break
        groups[target].append(owner_blocker(row))
    return {key: {"count": len(value), "blockers": value} for key, value in groups.items() if value}


def owner_blocker(row: dict[str, Any]) -> dict[str, Any]:
    code = str(row.get("code") or "unknown")
    return {
        "code": code,
        "developer_message": str(row.get("message") or code),
        "owner_message": owner_message(code),
    }


def owner_message(code: str) -> str:
    lower = code.lower()
    if "brand" in lower:
        return "The system still needs proof that this product belongs to the right brand lane."
    if "route" in lower or "public" in lower:
        return "The public product page has not been proved safe for this change."
    if "price" in lower or "sku" in lower or "variant" in lower:
        return "The price and option shape is not safe to publish yet."
    if "add_on" in lower or "payload" in lower or "configuration" in lower:
        return "Customer choices need cart, order, and receipt proof before they can go live."
    if "file" in lower or "media" in lower or "gallery" in lower or "slideshow" in lower:
        return "Product photos and file references need proof before this change can go live."
    if "historical" in lower or "rollback" in lower or "reference" in lower:
        return "The system still needs history and rollback proof."
    if "approval" in lower or "release" in lower or "mutation" in lower:
        return "A reviewed apply packet and owner approval are required before any live write."
    return "This blocker needs review before the product can move forward."


def owner_allowed_actions(blockers: list[Any]) -> list[dict[str, Any]]:
    return [
        {"action": "Save draft edits", "allowed": True, "reason": "Draft saves do not claim public success."},
        {"action": "Request technical review", "allowed": True, "reason": "Review can continue without live writes."},
        {"action": "Preview no-write packet", "allowed": True, "reason": "Preview is evidence, not a mutation."},
        {"action": "Publish/apply to live", "allowed": False, "reason": "Blocked until no-write blockers, owner approval, release packet, and live proof are complete." if blockers else "Still requires separate reviewed apply approval."},
    ]


def developer_next_actions(groups: dict[str, Any]) -> list[str]:
    actions = []
    if "options_addons_payload" in groups:
        actions.append("Design add-on runtime pricing and payload preservation proof.")
    if "price_and_sku_model" in groups:
        actions.append("Bind candidate SKU rows to exact Item Price proof before any apply path.")
    if "brand_and_public_route" in groups:
        actions.append("Capture live brand-lane and public route proof.")
    if "media_files" in groups:
        actions.append("Capture File attachment and slideshow/gallery reference proof.")
    if "history_and_rollback" in groups:
        actions.append("Run historical-reference checks and produce rollback procedure.")
    if "approval_and_release" in groups:
        actions.append("Prepare pre-mutation release packet and owner-scope approval gate.")
    return actions or ["Prepare reviewed apply packet; no automatic live mutation."]


def normalize(value: Any) -> str:
    return str(value or "").strip().lower().strip("/")


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=True, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise PublishReadinessBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
