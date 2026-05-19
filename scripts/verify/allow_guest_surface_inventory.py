#!/usr/bin/env python3
"""Inventory LT public Frappe whitelisted endpoints.

The check is source-only and read-only. It reports every
``@frappe.whitelist(allow_guest=True)`` endpoint in the local app, then marks
endpoints that appear to accept public writes by decorator method settings and
body mutation calls.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT / "apps" / "locally_twisted" / "locally_twisted"
WRITE_HTTP_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
MUTATION_CALLS = {
    "cancel",
    "db_set",
    "delete_doc",
    "delete",
    "insert",
    "make_payment_request",
    "save",
    "set_value",
    "submit",
}
GUARD_MARKERS = {
    "csrf",
    "honeypot",
    "rate",
    "recaptcha",
    "signature",
    "stripe-signature",
    "token",
    "validate",
    "verify",
}


@dataclass(frozen=True)
class GuestEndpoint:
    path: str
    line: int
    module_method: str
    function: str
    public_args: list[str]
    declared_http_methods: list[str] | None
    accepts_public_write: bool
    mutation_indicators: list[str]
    guard_markers: list[str]
    notes: list[str]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--report", help="Write the JSON report to this path")
    args = parser.parse_args()

    result = collect_inventory()
    rendered = json.dumps(result, indent=2, sort_keys=True)

    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[ALLOW GUEST INVENTORY] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 1 if result["parse_errors"] else 0


def collect_inventory() -> dict[str, Any]:
    endpoints: list[GuestEndpoint] = []
    parse_errors: list[dict[str, str]] = []

    for path in _production_python_files():
        rel = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8-sig", errors="replace")
        try:
            tree = ast.parse(source, filename=rel)
        except SyntaxError as exc:
            parse_errors.append({"path": rel, "error": str(exc)})
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            decorator = _guest_whitelist_decorator(node)
            if decorator is None:
                continue
            declared_methods = _declared_methods(decorator)
            mutation_indicators = _mutation_indicators(node)
            guard_markers = _guard_markers(source, node)
            accepts_public_write = bool(mutation_indicators) and (
                declared_methods is None or bool(WRITE_HTTP_METHODS.intersection(declared_methods))
            )
            notes: list[str] = []
            if declared_methods is None:
                notes.append("no methods list declared; Frappe method exposure must be treated as write-capable if the body mutates")
            if accepts_public_write and not guard_markers:
                notes.append("write-capable public endpoint has no obvious source-level guard marker")

            endpoints.append(
                GuestEndpoint(
                    path=rel,
                    line=node.lineno,
                    module_method=f"{_module_path(path)}.{node.name}",
                    function=node.name,
                    public_args=_public_arg_names(node),
                    declared_http_methods=sorted(declared_methods) if declared_methods is not None else None,
                    accepts_public_write=accepts_public_write,
                    mutation_indicators=mutation_indicators,
                    guard_markers=guard_markers,
                    notes=notes,
                )
            )

    endpoint_dicts = [asdict(endpoint) for endpoint in sorted(endpoints, key=lambda row: (row.path, row.line))]
    public_writes = [row for row in endpoint_dicts if row["accepts_public_write"]]
    return {
        "ok": not parse_errors,
        "root": str(ROOT),
        "endpoint_count": len(endpoint_dicts),
        "public_write_endpoint_count": len(public_writes),
        "endpoints": endpoint_dicts,
        "public_write_endpoints": public_writes,
        "parse_errors": parse_errors,
    }


def _production_python_files() -> Iterable[Path]:
    for path in sorted(APP_ROOT.rglob("*.py")):
        rel_parts = path.relative_to(APP_ROOT).parts
        if "__pycache__" in rel_parts or rel_parts[0] == "verify":
            continue
        yield path


def _guest_whitelist_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.Call | None:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and _call_name(decorator.func).endswith("frappe.whitelist"):
            for keyword in decorator.keywords:
                if keyword.arg == "allow_guest" and _truthy_literal(keyword.value):
                    return decorator
    return None


def _declared_methods(decorator: ast.Call) -> set[str] | None:
    for keyword in decorator.keywords:
        if keyword.arg != "methods":
            continue
        value = keyword.value
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            methods = {
                str(item.value).upper()
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }
            return methods
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return {value.value.upper()}
    return None


def _mutation_indicators(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    indicators: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            call_name = _call_name(child.func)
            short_name = call_name.rsplit(".", 1)[-1]
            if short_name in MUTATION_CALLS or call_name.endswith("frappe.db.set_value"):
                indicators.add(call_name)
    return sorted(indicators)


def _guard_markers(source: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    segment = ast.get_source_segment(source, node) or ""
    lowered = segment.lower()
    return sorted(marker for marker in GUARD_MARKERS if marker in lowered)


def _public_arg_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    names = [arg.arg for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs]
    return [name for name in names if name not in {"self", "cls"}]


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _truthy_literal(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _module_path(path: Path) -> str:
    rel = path.relative_to(ROOT / "apps" / "locally_twisted").with_suffix("")
    return ".".join(rel.parts)


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _print_summary(result: dict[str, Any]) -> None:
    print("[ALLOW GUEST INVENTORY] " + ("PASS" if result["ok"] else "FAIL"))
    print(f"  endpoints: {result['endpoint_count']}")
    print(f"  public_write_endpoints: {result['public_write_endpoint_count']}")
    for row in result["endpoints"]:
        method_text = ",".join(row["declared_http_methods"]) if row["declared_http_methods"] else "unspecified"
        write_text = "WRITE" if row["accepts_public_write"] else "read/unknown"
        print(f"    - {row['module_method']} ({row['path']}:{row['line']}) methods={method_text} {write_text}")
        if row["mutation_indicators"]:
            print(f"      mutations: {', '.join(row['mutation_indicators'])}")
        if row["guard_markers"]:
            print(f"      guard_markers: {', '.join(row['guard_markers'])}")
        for note in row["notes"]:
            print(f"      note: {note}")
    if result["parse_errors"]:
        print("  parse_errors:")
        for row in result["parse_errors"]:
            print(f"    - {row['path']}: {row['error']}")


if __name__ == "__main__":
    sys.exit(main())
