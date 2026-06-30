#!/usr/bin/env python3
"""Build an offline catalog blast-radius report from saved authority artifacts.

This helper reads saved live-audit or projection-preview JSON files. It does
not read credentials, call the network, inspect Docker, clear cache, deploy, or
write ERPNext data.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        paths = collect_paths(args.input)
        products = [summarize_artifact(path) for path in paths]
        report = build_report(products, paths)
        write_report(report, args.output, pretty=args.pretty)
    except BlastRadiusBlocked as exc:
        print(f"[LT PRODUCT SETUP CATALOG BLAST RADIUS] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT PRODUCT SETUP CATALOG BLAST RADIUS] FAIL: {exc}", file=sys.stderr)
        return 1

    print("[LT PRODUCT SETUP CATALOG BLAST RADIUS] " + ("FAIL" if report["risk_count"] else "PASS"))
    print(f"  products: {report['product_count']}")
    print(f"  risk_count: {report['risk_count']}")
    print(f"  blocker_count: {report['blocker_count']}")
    if args.output:
        print(f"  output: {Path(args.output).resolve()}")
    if args.fail_on_risk and (report["risk_count"] or report["blocker_count"]):
        return 1
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        help="Saved JSON artifact files or directories containing .json artifacts.",
    )
    parser.add_argument("--output", help="Optional report JSON path. Defaults to stdout.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--fail-on-risk", action="store_true", help="Exit nonzero when risks or blockers are present.")
    return parser.parse_args(argv)


class BlastRadiusBlocked(RuntimeError):
    """Raised when local artifact input is invalid."""


def collect_paths(inputs: list[str]) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if not path.exists():
            raise BlastRadiusBlocked(f"input does not exist: {path}")
        if path.is_dir():
            paths.extend(sorted(child for child in path.glob("*.json") if child.is_file()))
        elif path.suffix.lower() == ".json":
            paths.append(path)
        else:
            raise BlastRadiusBlocked(f"input is not a JSON file or directory: {path}")
    unique = sorted({path.resolve() for path in paths})
    if not unique:
        raise BlastRadiusBlocked("no JSON artifacts found")
    return unique


def summarize_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BlastRadiusBlocked(f"JSON root must be an object: {path}")
    artifact_type = detect_type(payload)
    if artifact_type == "projection":
        return summarize_projection(path, payload)
    return summarize_audit(path, payload)


def detect_type(payload: dict[str, Any]) -> str:
    if any(key in payload for key in ("drift_summary", "proposed_changes", "approval_state")):
        return "projection"
    if any(key in payload for key in ("price_summary", "content_summary", "blueprint_summary", "website_item_summary")):
        return "audit"
    raise BlastRadiusBlocked("artifact is neither a recognized live audit nor projection preview")


def summarize_projection(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    product = payload.get("product_identifier") if isinstance(payload.get("product_identifier"), dict) else {}
    drift_summary = payload.get("drift_summary") if isinstance(payload.get("drift_summary"), dict) else {}
    proposed = payload.get("proposed_changes") if isinstance(payload.get("proposed_changes"), dict) else {}
    price = drift_summary.get("price") if isinstance(drift_summary.get("price"), dict) else {}
    copy = drift_summary.get("copy") if isinstance(drift_summary.get("copy"), dict) else {}
    blockers = as_list(payload.get("blockers"))
    limitations = as_list(payload.get("limitations"))
    risks = []
    if price.get("drift_detected") or proposed.get("item_prices"):
        risks.append("price_drift")
    if copy.get("drift_detected") or proposed.get("website_item_copy"):
        risks.append("copy_drift")
    if limitations:
        risks.append("preview_limitations")
    return {
        "artifact": str(path),
        "artifact_type": "projection",
        "product": product,
        "route": payload.get("route") or product.get("route"),
        "risks": sorted(set(risks)),
        "blockers": blockers,
        "limitations": limitations,
        "counts": {
            "item_price_changes": len(as_list(proposed.get("item_prices"))),
            "copy_suggestions": len(as_list(proposed.get("website_item_copy"))),
            "blockers": len(blockers),
            "limitations": len(limitations),
        },
        "next_action": next_action(risks, blockers),
    }


def summarize_audit(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    blueprint = payload.get("blueprint_summary") if isinstance(payload.get("blueprint_summary"), dict) else {}
    website = payload.get("website_item_summary") if isinstance(payload.get("website_item_summary"), dict) else {}
    price = payload.get("price_summary") if isinstance(payload.get("price_summary"), dict) else {}
    content = payload.get("content_summary") if isinstance(payload.get("content_summary"), dict) else {}
    blockers = as_list(payload.get("failures"))
    risks = []
    setup_prices = sorted(str(value) for value in as_list(price.get("blueprint_price_row_values")))
    item_prices = sorted(str(value) for value in as_list(price.get("item_price_values")))
    if setup_prices and item_prices and setup_prices != item_prices:
        risks.append("price_drift")
    setup_copy = content.get("blueprint_content_fields") if isinstance(content.get("blueprint_content_fields"), dict) else {}
    public_copy = content.get("website_item_content_fields") if isinstance(content.get("website_item_content_fields"), dict) else {}
    if setup_copy and public_copy and json.dumps(setup_copy, sort_keys=True) != json.dumps(public_copy, sort_keys=True):
        risks.append("copy_drift")
    if not blueprint:
        blockers.append("missing Product Setup summary")
    if not website:
        blockers.append("missing Website Item summary")
    return {
        "artifact": str(path),
        "artifact_type": "audit",
        "product": {
            "product_setup": blueprint.get("name"),
            "item_code": website.get("item_code") or blueprint.get("target_item_code"),
            "website_item": website.get("name") or blueprint.get("target_website_item"),
            "product_name": blueprint.get("product_name") or website.get("web_item_name"),
        },
        "route": website.get("route"),
        "risks": sorted(set(risks)),
        "blockers": blockers,
        "limitations": [
            {
                "code": "audit_not_projection",
                "message": "Audit artifacts show drift but do not include row-level proposed changes or rollback targets.",
            }
        ],
        "counts": {
            "item_price_changes": 0,
            "copy_suggestions": 0,
            "blockers": len(blockers),
            "limitations": 1,
        },
        "next_action": next_action(risks, blockers),
    }


def build_report(products: list[dict[str, Any]], paths: list[Path]) -> dict[str, Any]:
    risky = [product for product in products if product["risks"]]
    blockers = [product for product in products if product["blockers"]]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "proof_mode": "offline saved JSON artifacts only; no live reads or writes",
        "artifact_count": len(paths),
        "product_count": len(products),
        "risk_count": len(risky),
        "blocker_count": sum(len(product["blockers"]) for product in products),
        "risk_breakdown": risk_breakdown(products),
        "products": products,
        "next_safe_actions": [
            "Generate one saved live read-only audit artifact per published Website Item before calling this catalog-wide.",
            "Run projection preview for each risky audit before any repair packet.",
            "Stop before live writes until brand lane, active Product Setup uniqueness, rollback snapshots, and business copy/price approval are resolved.",
        ],
    }


def risk_breakdown(products: list[dict[str, Any]]) -> dict[str, int]:
    breakdown: dict[str, int] = {}
    for product in products:
        for risk in product["risks"]:
            breakdown[risk] = breakdown.get(risk, 0) + 1
    return dict(sorted(breakdown.items()))


def next_action(risks: list[str], blockers: list[Any]) -> str:
    if blockers:
        return "Resolve missing authority evidence before preview or repair."
    if "price_drift" in risks or "copy_drift" in risks:
        return "Create/review projection preview and pre-mutation packet; do not repair directly."
    if risks:
        return "Review limitations before treating this product as clean."
    return "No authority drift detected in this artifact."


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def write_report(report: dict[str, Any], output_path: str | None, *, pretty: bool) -> None:
    payload = json.dumps(report, indent=2 if pretty else None, sort_keys=pretty, default=str) + "\n"
    if output_path:
        output = Path(output_path)
        if output.exists() and output.is_dir():
            raise BlastRadiusBlocked(f"output path is a directory: {output}")
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


if __name__ == "__main__":
    raise SystemExit(main())
