#!/usr/bin/env python3
"""Offline contract for the staging owner-review bootstrap guard.

This verifier is intentionally source-only. It does not import Frappe, call
Frappe Cloud, enqueue jobs, seed catalogs, or touch provider state.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "staging_owner_review_bootstrap.py"
PREFLIGHT = ROOT / "apps" / "locally_twisted" / "locally_twisted" / "staging_owner_review_preflight.py"

REQUIRED_PREFLIGHT_CHECKS = {
    "standard_report",
    "roles",
    "settings",
    "app_hooks",
    "app_order",
    "target_hash",
    "baseline_counts",
    "destructive_seed_evidence",
}

MUTATING_PREFLIGHT_CALLS = {
    "_set_status",
    "frappe.enqueue",
    "_run_seed_syncs",
    "_ensure_owner_user",
    "_seed_catalog",
    "commit",
}

OLD_DESCRIPTIVE_BACKUP = "Frappe Cloud staging empty-site owner-review bootstrap; no customer data existed."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {
        "ok": not failures,
        "failures": failures,
        "targets": [str(BOOTSTRAP.relative_to(ROOT)), str(PREFLIGHT.relative_to(ROOT))],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[STAGING OWNER REVIEW BOOTSTRAP CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []
    try:
        bootstrap_source = BOOTSTRAP.read_text(encoding="utf-8")
        bootstrap_tree = ast.parse(bootstrap_source, filename=str(BOOTSTRAP))
        preflight_source = PREFLIGHT.read_text(encoding="utf-8")
        preflight_tree = ast.parse(preflight_source, filename=str(PREFLIGHT))
    except Exception as exc:
        return [f"could not parse bootstrap/preflight source: {type(exc).__name__}: {exc}"]

    bootstrap_functions = {node.name: node for node in bootstrap_tree.body if isinstance(node, ast.FunctionDef)}
    preflight_functions = {node.name: node for node in preflight_tree.body if isinstance(node, ast.FunctionDef)}
    required_preflight_functions = {
        "build_bootstrap_preflight",
        "assert_preflight_allows_catalog_mutation",
        "seed_catalog_backup_path",
        "_validate_destructive_seed_evidence",
        "_validate_backup_artifact_evidence",
        "_validate_zero_data_proof",
    }
    required_bootstrap_functions = {
        "preflight_staging_owner_review_bootstrap",
        "_seed_catalog",
    }
    for name in sorted(required_bootstrap_functions - set(bootstrap_functions)):
        failures.append(f"missing required bootstrap guard function: {name}")
    for name in sorted(required_preflight_functions - set(preflight_functions)):
        failures.append(f"missing required preflight guard function: {name}")

    failures.extend(check_preflight_api(bootstrap_functions.get("preflight_staging_owner_review_bootstrap")))
    failures.extend(check_required_preflight_checks(preflight_tree))
    failures.extend(check_run_orders_preflight_before_seed(bootstrap_functions.get("run_staging_owner_review_bootstrap"), bootstrap_source))
    failures.extend(check_seed_catalog_backup_path(bootstrap_functions.get("_seed_catalog")))
    failures.extend(check_evidence_paths(preflight_functions, bootstrap_source + "\n" + preflight_source))
    return failures


def check_preflight_api(function: ast.FunctionDef | None) -> list[str]:
    if function is None:
        return []
    failures: list[str] = []
    decorators = {call_name(decorator) for decorator in function.decorator_list}
    if "frappe.whitelist" not in decorators:
        failures.append("preflight_staging_owner_review_bootstrap must be whitelisted for hosted use")

    mutating_calls = []
    for call in iter_calls(function):
        name = call_name(call.func)
        if name in MUTATING_PREFLIGHT_CALLS:
            mutating_calls.append(f"{name} at line {call.lineno}")
    if mutating_calls:
        failures.append("preflight API contains mutating calls: " + ", ".join(mutating_calls))
    return failures


def check_required_preflight_checks(tree: ast.Module) -> list[str]:
    failures: list[str] = []
    checks = assigned_string_tuple(tree, "PREFLIGHT_REQUIRED_CHECKS")
    missing = sorted(REQUIRED_PREFLIGHT_CHECKS - checks)
    if missing:
        failures.append(f"PREFLIGHT_REQUIRED_CHECKS is missing required checks: {missing}")
    return failures


def check_run_orders_preflight_before_seed(function: ast.FunctionDef | None, source: str) -> list[str]:
    if function is None:
        return []
    failures: list[str] = []
    preflight_lines = call_lines(function, "build_bootstrap_preflight")
    seed_lines = call_lines(function, "_seed_catalog")
    assert_lines = call_lines(function, "assert_preflight_allows_catalog_mutation")
    if not preflight_lines:
        failures.append("run_staging_owner_review_bootstrap does not build a preflight")
    if not assert_lines:
        failures.append("run_staging_owner_review_bootstrap does not assert preflight before catalog mutation")
    if not seed_lines:
        failures.append("run_staging_owner_review_bootstrap does not call _seed_catalog")
    if preflight_lines and seed_lines and min(preflight_lines) > min(seed_lines):
        failures.append("run_staging_owner_review_bootstrap calls _seed_catalog before building preflight")
    if assert_lines and seed_lines and min(assert_lines) > min(seed_lines):
        failures.append("run_staging_owner_review_bootstrap calls _seed_catalog before asserting preflight")
    if 'summary["preflight"]' not in ast.get_source_segment(source, function):
        failures.append("run_staging_owner_review_bootstrap does not record preflight in the bootstrap summary")
    return failures


def check_seed_catalog_backup_path(function: ast.FunctionDef | None) -> list[str]:
    if function is None:
        return []
    failures: list[str] = []
    args = {arg.arg for arg in function.args.args}
    if "preflight" not in args:
        failures.append("_seed_catalog must receive the validated preflight contract")

    execute_calls = [
        call for call in iter_calls(function)
        if call_name(call.func) == "execute"
    ]
    backup_keywords = [
        keyword
        for call in execute_calls
        for keyword in call.keywords
        if keyword.arg == "backup_path"
    ]
    if not backup_keywords:
        failures.append("_seed_catalog execute call is missing backup_path")
    for keyword in backup_keywords:
        if isinstance(keyword.value, ast.Constant):
            failures.append("_seed_catalog passes a literal backup_path into destructive seed")
        if call_name(keyword.value) != "seed_catalog_backup_path":
            failures.append("_seed_catalog backup_path must come from seed_catalog_backup_path(preflight)")
    return failures


def check_evidence_paths(functions: dict[str, ast.FunctionDef], source: str) -> list[str]:
    failures: list[str] = []
    if OLD_DESCRIPTIVE_BACKUP in source:
        failures.append("old descriptive backup string is still present")
    for call in iter_calls(functions.get("_validate_destructive_seed_evidence")):
        pass
    destructive = functions.get("_validate_destructive_seed_evidence")
    if destructive is not None:
        calls = {call_name(call.func) for call in iter_calls(destructive)}
        if "_validate_backup_artifact_evidence" not in calls:
            failures.append("destructive seed evidence does not accept backup artifact evidence")
        if "_validate_zero_data_proof" not in calls:
            failures.append("destructive seed evidence does not accept explicit zero-data proof")
    if '"destructive_seed_evidence"' not in source:
        failures.append("bootstrap summary/preflight does not expose destructive_seed_evidence")
    if "_looks_like_descriptive_backup_string" not in source:
        failures.append("bootstrap does not reject descriptive backup strings")
    return failures


def assigned_string_tuple(tree: ast.Module, name: str) -> set[str]:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if isinstance(node.value, (ast.Tuple, ast.List, ast.Set)):
            return {elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)}
    return set()


def iter_calls(node: ast.AST | None):
    if node is None:
        return
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            yield child


def call_lines(function: ast.FunctionDef, name: str) -> list[int]:
    return [call.lineno for call in iter_calls(function) if call_name(call.func) == name]


def call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    if isinstance(node, ast.Call):
        return call_name(node.func)
    return ""


if __name__ == "__main__":
    sys.exit(main())
