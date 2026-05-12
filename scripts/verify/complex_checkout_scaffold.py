#!/usr/bin/env python3
"""Generate the local complex checkout scaffold report.

This verifier is read-only. It refreshes the existing ProductPatternContract
report from local ERPNext, then maps every product into the next complex
checkout UI/server-contract proof lane.

Run:
  python scripts/verify/complex_checkout_scaffold.py
  python scripts/verify/complex_checkout_scaffold.py --input output/product-pattern-contract.json --skip-refresh
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from locally_twisted.catalog_contract.complex_checkout_scaffold import (
    build_complex_checkout_scaffold_report,
)


DEFAULT_PRODUCT_PATTERN_REPORT = ROOT / "output" / "product-pattern-contract.json"
DEFAULT_PRODUCT_PATTERN_MARKDOWN = ROOT / "output" / "product-pattern-contract.md"
DEFAULT_OUTPUT = ROOT / "output" / "complex-checkout-scaffold.json"
DEFAULT_MARKDOWN = ROOT / "output" / "complex-checkout-scaffold.md"


class ScaffoldFail(Exception):
    pass


def main() -> int:
    args = _parse_args()
    input_path = _rooted(args.input)
    output_path = _rooted(args.output)
    markdown_path = _rooted(args.markdown)

    try:
        if not args.skip_refresh:
            _refresh_product_pattern_report(input_path)
        artifact = _load_json(input_path)
        report = build_complex_checkout_scaffold_report(
            artifact,
            metadata={
                "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "source_product_pattern_report": _display_path(input_path),
                "logic_note": (
                    "Source-only local scaffold; does not update Frappe Cloud, Cloudflare, or the live domain."
                ),
            },
        )
    except ScaffoldFail as exc:
        print(f"[COMPLEX CHECKOUT SCAFFOLD] FAIL\n  - {exc}")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report.to_artifact(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    summary = report.summary()
    print("[COMPLEX CHECKOUT SCAFFOLD] " + ("PASS" if summary.get("ok") else "FAIL"))
    print(f"  - report: {_display_path(output_path)}")
    print(f"  - markdown: {_display_path(markdown_path)}")
    print(f"  - products: {summary.get('source_products')}")
    print(f"  - direct checkout guards: {summary.get('direct_checkout_regression_guards')}")
    print(f"  - simple lane-flip candidates: {summary.get('simple_axis_lane_flip_candidates')}")
    print(f"  - complex UI required: {summary.get('complex_ui_required_products')}")
    print(f"  - add-on/conditional blocked: {summary.get('add_on_or_conditional_blocked_products')}")
    for failure in report.contract_failures:
        print(f"  - {failure}")
    return 0 if summary.get("ok") else 2


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--input",
        default=str(DEFAULT_PRODUCT_PATTERN_REPORT),
        help="ProductPatternContract JSON input path. Refreshed unless --skip-refresh is set.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Complex checkout scaffold JSON output path.",
    )
    parser.add_argument(
        "--markdown",
        default=str(DEFAULT_MARKDOWN),
        help="Complex checkout scaffold Markdown output path.",
    )
    parser.add_argument(
        "--skip-refresh",
        action="store_true",
        help="Do not rerun product_pattern_contract.py before building the scaffold.",
    )
    return parser.parse_args()


def _refresh_product_pattern_report(report_path: Path) -> None:
    markdown_path = DEFAULT_PRODUCT_PATTERN_MARKDOWN
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "verify" / "product_pattern_contract.py"),
        "--report",
        str(report_path),
        "--markdown",
        str(markdown_path),
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=240)
    if proc.returncode != 0:
        raise ScaffoldFail(
            "ProductPatternContract refresh failed; scaffold was not built.\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ScaffoldFail(f"missing ProductPatternContract input: {_display_path(path)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ScaffoldFail("ProductPatternContract input must be a JSON object")
    return data


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    sys.exit(main())
