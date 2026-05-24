#!/usr/bin/env python3
"""Guard Odoo/reference material from deployable app runtime paths.

This verifier is intentionally offline. It scans tracked repo files and fails
when deployable LT app code or assets depend on Odoo-named reference paths.
Reference-only resources, audits, and setup/scrape tooling are allowed.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
APP_RUNTIME_PREFIX = "apps/locally_twisted/locally_twisted/"
APP_VERIFY_PREFIX = APP_RUNTIME_PREFIX + "verify/"

FORBIDDEN_RUNTIME_PATTERNS = (
    ("odoo_reference_resource", "_resources/odoo-live"),
    ("odoo_swatch_asset_path", "color-swatches/odoo"),
    ("odoo_swatch_contract_map", "odoo_color_swatch_map.json"),
    ("odoo_temp_catalog_path", "lt-odoo-live-catalog.json"),
    ("odoo_live_host", "http://5.78.136.133"),
    ("odoo_combination_endpoint", "/website_sale/get_combination_info"),
)
MAX_REPORTED_FAILURES = 120


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str | None = None


@dataclass(frozen=True)
class BoundaryFailure:
    path: str
    rule: str
    detail: str
    line: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "rule": self.rule,
            "detail": self.detail,
            "line": self.line,
        }


def scan_files(files: Iterable[SourceFile]) -> list[BoundaryFailure]:
    failures: list[BoundaryFailure] = []
    reported_path_failures: set[tuple[str, str]] = set()
    for source in files:
        path = normalize_path(source.path)
        if not is_app_runtime_path(path):
            continue

        for failure in path_failures(path):
            key = (failure.path, failure.rule)
            if key not in reported_path_failures:
                reported_path_failures.add(key)
                failures.append(failure)
        if source.text is not None and should_scan_text(path):
            failures.extend(text_failures(path, source.text))
    return failures


def normalize_path(path: str) -> str:
    return str(path or "").replace("\\", "/")


def is_app_runtime_path(path: str) -> bool:
    path = normalize_path(path)
    return path.startswith(APP_RUNTIME_PREFIX) and not path.startswith(APP_VERIFY_PREFIX)


def path_failures(path: str) -> list[BoundaryFailure]:
    lowered = path.lower()
    if "/public/images/color-swatches/odoo/" in lowered:
        return [
            BoundaryFailure(
                path=APP_RUNTIME_PREFIX + "public/images/color-swatches/odoo/",
                rule="app_side_odoo_named_deploy_path",
                detail="Deployable LT app paths must not carry Odoo-named files or folders.",
            )
        ]
    parts = lowered.split("/")
    if any("odoo" in part for part in parts[len(APP_RUNTIME_PREFIX.split("/")) - 1 :]):
        return [
            BoundaryFailure(
                path=path,
                rule="app_side_odoo_named_deploy_path",
                detail="Deployable LT app paths must not carry Odoo-named files or folders.",
            )
        ]
    return []


def should_scan_text(path: str) -> bool:
    if path.startswith(APP_RUNTIME_PREFIX + "seed/"):
        return True
    if path in {
        APP_RUNTIME_PREFIX + "staging_owner_review_bootstrap.py",
        APP_RUNTIME_PREFIX + "staging_owner_review_preflight.py",
        APP_RUNTIME_PREFIX + "product_options.py",
        APP_RUNTIME_PREFIX + "catalog_contract/color_rules.py",
        APP_RUNTIME_PREFIX + "catalog_contract/lt_color_swatch_map.json",
        APP_RUNTIME_PREFIX + "catalog_contract/odoo_color_swatch_map.json",
    }:
        return True
    return False


def text_failures(path: str, text: str) -> list[BoundaryFailure]:
    failures: list[BoundaryFailure] = []
    reported_rules: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        normalized = normalize_path(line).lower()
        for rule, needle in FORBIDDEN_RUNTIME_PATTERNS:
            if rule in reported_rules:
                continue
            if forbidden_pattern_present(normalized, needle):
                reported_rules.add(rule)
                failures.append(
                    BoundaryFailure(
                        path=path,
                        line=line_number,
                        rule=rule,
                        detail=f"Deployable app runtime code must not depend on `{needle}`.",
                    )
                )
        if "app_local_seed_data_path" not in reported_rules and references_app_seed_data(line):
            reported_rules.add("app_local_seed_data_path")
            failures.append(
                BoundaryFailure(
                    path=path,
                    line=line_number,
                    rule="app_local_seed_data_path",
                    detail=(
                        "Deployable app runtime/bootstrap code must not depend on "
                        "ignored app-local `seed/_data`; use an LT-owned seed artifact path."
                    ),
                )
            )
    return failures


def forbidden_pattern_present(normalized_line: str, needle: str) -> bool:
    normalized_needle = normalize_path(needle).lower()
    if normalized_needle == "_resources/odoo-live":
        return (
            normalized_needle in normalized_line
            and "_resources/odoo-live-snapshot" not in normalized_line
            and "_resources/odoo-live-mirror" not in normalized_line
        )
    return normalized_needle in normalized_line


def references_app_seed_data(line: str) -> bool:
    normalized = normalize_path(line).lower()
    if "seed/_data" in normalized:
        return True
    compact = " ".join(line.strip().split())
    return (
        '"seed", "_data"' in compact
        or "'seed', '_data'" in compact
        or '"seed", \'_data\'' in compact
        or "'seed', \"_data\"" in compact
    )


def git_working_tree_files(root: Path) -> list[SourceFile]:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    files: list[SourceFile] = []
    for line in proc.stdout.splitlines():
        path = line.strip()
        if path and (root / path).exists():
            files.append(SourceFile(path))
    return files


def load_text(root: Path, path: str) -> str | None:
    try:
        return (root / path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def run_self_test() -> list[str]:
    fixture = [
        SourceFile(
            "apps/locally_twisted/locally_twisted/seed/seed_catalog.py",
            'Path("/workspace/_resources/odoo-live")\n',
        ),
        SourceFile(
            "apps/locally_twisted/locally_twisted/catalog_contract/odoo_color_swatch_map.json",
            '{"asset_base_url": "/assets/locally_twisted/images/color-swatches/odoo/"}\n',
        ),
        SourceFile(
            "apps/locally_twisted/locally_twisted/catalog_contract/lt_color_swatch_map.json",
            '{"source_url_template": "http://5.78.136.133/web/image/product.template.attribute.value/{ptav_id}/image"}\n',
        ),
        SourceFile(
            "apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/example.jpg",
            None,
        ),
        SourceFile(
            "scripts/setup/scrape_odoo_live.py",
            'SOURCE = "_resources/odoo-live"\n',
        ),
        SourceFile("_resources/odoo-live/catalog.json", "{}\n"),
        SourceFile("audits/odoo-erpnext-migration-audit-2026-05-08/report.md", "reference\n"),
    ]
    failures = scan_files(fixture)
    failure_paths = {failure.path for failure in failures}

    errors: list[str] = []
    expected_failures = {
        "apps/locally_twisted/locally_twisted/seed/seed_catalog.py",
        "apps/locally_twisted/locally_twisted/catalog_contract/odoo_color_swatch_map.json",
        "apps/locally_twisted/locally_twisted/catalog_contract/lt_color_swatch_map.json",
        "apps/locally_twisted/locally_twisted/public/images/color-swatches/odoo/",
    }
    for path in expected_failures:
        if path not in failure_paths:
            errors.append(f"self-test did not flag deployable app Odoo coupling: {path}")
    allowed_paths = {
        "scripts/setup/scrape_odoo_live.py",
        "_resources/odoo-live/catalog.json",
        "audits/odoo-erpnext-migration-audit-2026-05-08/report.md",
    }
    for path in allowed_paths:
        if path in failure_paths:
            errors.append(f"self-test incorrectly flagged reference-only path: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run offline scanner self-tests.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test()
        result = {"ok": not errors, "failure_count": len(errors), "failures": errors}
    else:
        source_files = [
            SourceFile(path.path, load_text(REPO_ROOT, path.path))
            for path in git_working_tree_files(REPO_ROOT)
        ]
        failures = scan_files(source_files)
        reported_failures = failures[:MAX_REPORTED_FAILURES]
        result = {
            "ok": not failures,
            "failure_count": len(failures),
            "reported_failure_count": len(reported_failures),
            "omitted_failure_count": max(0, len(failures) - len(reported_failures)),
            "failures": [failure.to_dict() for failure in reported_failures],
        }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[ODOO REFERENCE BOUNDARY] " + ("PASS" if result["ok"] else "FAIL"))
        if result.get("failure_count"):
            print(f"  failure_count: {result['failure_count']}")
        for failure in result["failures"]:
            if isinstance(failure, str):
                print(f"  - {failure}")
            else:
                location = f"{failure['path']}:{failure['line']}" if failure.get("line") else failure["path"]
                print(f"  - {location} [{failure['rule']}] {failure['detail']}")
        if result.get("omitted_failure_count"):
            print(f"  ... omitted {result['omitted_failure_count']} additional failures")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
