#!/usr/bin/env python3
"""Lint production ``ignore_permissions=True`` use for local guard evidence.

The check is source-only and read-only. It scans LT app production code,
ignores app verifier modules by default, and fails when a permission bypass has
neither a nearby guard/justification comment nor a controlled wrapper context.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = ROOT / "apps" / "locally_twisted" / "locally_twisted"
JUSTIFICATION_WORDS = re.compile(
    r"\b("
    r"admin|because|bootstrap|controlled|fail|guard|intentional|migration|operator|"
    r"permission|public|safe|setup|signature|system|webhook|why"
    r")\b",
    re.IGNORECASE,
)
GUARD_MARKERS = {
    "frappe.only_for",
    "frappe.has_permission",
    "frappe.get_roles",
    "frappe.session.user",
    "frappe.throw",
    "frappe.local.request.method",
    "get_request_header",
    "stripe-signature",
    "verify",
    "validate",
}
SAFE_WRAPPER_DIRS = {
    "seed": "seed/setup sync context",
    "setup_pages": "setup page sync context",
}


@dataclass(frozen=True)
class PermissionBypass:
    path: str
    line: int
    expression: str
    function: str | None
    context: str
    public_guest_endpoint: bool
    has_justification_comment: bool
    justification_comments: list[str]
    guard_markers: list[str]
    safe_wrapper_context: str | None
    requires_attention: bool


class ParentMap(ast.NodeVisitor):
    def __init__(self) -> None:
        self.parents: dict[ast.AST, ast.AST] = {}

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self.parents[child] = node
        super().generic_visit(node)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--report", help="Write the JSON report to this path")
    parser.add_argument(
        "--include-verifiers",
        action="store_true",
        help="Also scan apps/locally_twisted/locally_twisted/verify",
    )
    args = parser.parse_args()

    result = lint_ignore_permissions(include_verifiers=args.include_verifiers)
    rendered = json.dumps(result, indent=2, sort_keys=True)

    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[IGNORE PERMISSIONS LINT] wrote {report_path.relative_to(ROOT)}")

    if args.json:
        print(rendered)
    else:
        _print_summary(result)

    return 0 if result["ok"] else 1


def lint_ignore_permissions(*, include_verifiers: bool = False) -> dict[str, Any]:
    findings: list[PermissionBypass] = []
    parse_errors: list[dict[str, str]] = []

    for path in _production_python_files(include_verifiers=include_verifiers):
        rel = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8-sig", errors="replace")
        lines = source.splitlines()
        try:
            tree = ast.parse(source, filename=rel)
        except SyntaxError as exc:
            parse_errors.append({"path": rel, "error": str(exc)})
            continue

        parent_map = ParentMap()
        parent_map.visit(tree)
        parents = parent_map.parents
        safe_wrapper = _safe_wrapper_context(path)

        for node in ast.walk(tree):
            expression = _ignore_permissions_expression(node)
            if expression is None:
                continue
            function = _containing_function(node, parents)
            comments = _nearby_comments(lines, getattr(node, "lineno", 0))
            guard_markers = _guard_markers(source, function, node)
            has_comment = any(JUSTIFICATION_WORDS.search(comment) for comment in comments)
            public_guest = bool(function and _is_allow_guest_function(function))
            requires_attention = not (has_comment or guard_markers or safe_wrapper)

            findings.append(
                PermissionBypass(
                    path=rel,
                    line=getattr(node, "lineno", 0),
                    expression=expression,
                    function=function.name if function else None,
                    context=_context_name(path, function),
                    public_guest_endpoint=public_guest,
                    has_justification_comment=has_comment,
                    justification_comments=comments,
                    guard_markers=guard_markers,
                    safe_wrapper_context=safe_wrapper,
                    requires_attention=requires_attention,
                )
            )

    finding_dicts = [asdict(row) for row in sorted(findings, key=lambda row: (row.path, row.line, row.expression))]
    attention = [row for row in finding_dicts if row["requires_attention"]]
    public_guest = [row for row in finding_dicts if row["public_guest_endpoint"]]
    return {
        "ok": not parse_errors and not attention,
        "root": str(ROOT),
        "scanned_verifiers": include_verifiers,
        "bypass_count": len(finding_dicts),
        "requires_attention_count": len(attention),
        "public_guest_bypass_count": len(public_guest),
        "bypasses": finding_dicts,
        "requires_attention": attention,
        "public_guest_bypasses": public_guest,
        "parse_errors": parse_errors,
    }


def _production_python_files(*, include_verifiers: bool) -> Iterable[Path]:
    for path in sorted(APP_ROOT.rglob("*.py")):
        rel_parts = path.relative_to(APP_ROOT).parts
        if "__pycache__" in rel_parts:
            continue
        if not include_verifiers and rel_parts[0] == "verify":
            continue
        yield path


def _ignore_permissions_expression(node: ast.AST) -> str | None:
    if isinstance(node, ast.Call):
        for keyword in node.keywords:
            if keyword.arg == "ignore_permissions" and _truthy_literal(keyword.value):
                return f"{_call_name(node.func)}(..., ignore_permissions=True)"
    if isinstance(node, ast.Assign) and _truthy_literal(node.value):
        for target in node.targets:
            if _call_name(target).endswith("ignore_permissions"):
                return f"{_call_name(target)} = True"
    if isinstance(node, ast.AnnAssign) and _truthy_literal(node.value):
        if _call_name(node.target).endswith("ignore_permissions"):
            return f"{_call_name(node.target)} = True"
    return None


def _containing_function(
    node: ast.AST,
    parents: dict[ast.AST, ast.AST],
) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current
    return None


def _nearby_comments(lines: list[str], lineno: int) -> list[str]:
    if lineno <= 0:
        return []
    start = max(0, lineno - 5)
    end = min(len(lines), lineno)
    comments: list[str] = []
    for line in lines[start:end]:
        stripped = line.strip()
        if stripped.startswith("#"):
            comments.append(stripped.lstrip("#").strip())
        elif " #" in line:
            comments.append(line.split(" #", 1)[1].strip())
    return comments


def _guard_markers(
    source: str,
    function: ast.FunctionDef | ast.AsyncFunctionDef | None,
    node: ast.AST,
) -> list[str]:
    if function is None:
        return []
    segment = ast.get_source_segment(source, function) or ""
    occurrence_line = getattr(node, "lineno", function.lineno)
    prefix_lines = segment.splitlines()[: max(0, occurrence_line - function.lineno + 1)]
    prefix = "\n".join(prefix_lines).lower()
    return sorted(marker for marker in GUARD_MARKERS if marker.lower() in prefix)


def _safe_wrapper_context(path: Path) -> str | None:
    rel_parts = path.relative_to(APP_ROOT).parts
    if rel_parts:
        return SAFE_WRAPPER_DIRS.get(rel_parts[0])
    return None


def _context_name(path: Path, function: ast.FunctionDef | ast.AsyncFunctionDef | None) -> str:
    safe_wrapper = _safe_wrapper_context(path)
    if safe_wrapper:
        return safe_wrapper
    if function and _is_allow_guest_function(function):
        return "public guest endpoint"
    if function and _is_whitelisted_function(function):
        return "authenticated whitelisted endpoint"
    return "runtime production code"


def _is_allow_guest_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and _call_name(decorator.func).endswith("frappe.whitelist"):
            for keyword in decorator.keywords:
                if keyword.arg == "allow_guest" and _truthy_literal(keyword.value):
                    return True
    return False


def _is_whitelisted_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in node.decorator_list:
        if _call_name(decorator).endswith("frappe.whitelist"):
            return True
        if isinstance(decorator, ast.Call) and _call_name(decorator.func).endswith("frappe.whitelist"):
            return True
    return False


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Name):
        return node.id
    return ""


def _truthy_literal(node: ast.AST | None) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _print_summary(result: dict[str, Any]) -> None:
    print("[IGNORE PERMISSIONS LINT] " + ("PASS" if result["ok"] else "FAIL"))
    print(f"  bypasses: {result['bypass_count']}")
    print(f"  requires_attention: {result['requires_attention_count']}")
    print(f"  public_guest_bypasses: {result['public_guest_bypass_count']}")
    for row in result["requires_attention"][:40]:
        function = f"::{row['function']}" if row["function"] else ""
        print(f"    - {row['path']}:{row['line']}{function} {row['expression']}")
        print(f"      context: {row['context']}")
    if len(result["requires_attention"]) > 40:
        print(f"    - ... {len(result['requires_attention']) - 40} more")
    if result["parse_errors"]:
        print("  parse_errors:")
        for row in result["parse_errors"]:
            print(f"    - {row['path']}: {row['error']}")


if __name__ == "__main__":
    sys.exit(main())
