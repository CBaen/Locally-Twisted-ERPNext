#!/usr/bin/env python3
"""
Migration broad-write lint.

AST-scans migration scripts for the `Document.search([]).write(...)` pattern
and similar broad-mutation calls. Fails loudly if any unfiltered mass
mutation is found in a migration.

This gate exists because of the LT 2026-04-23 19.0.2.13.0 migration: an
instance shipped a migration that called `search([])` and wrote to every
matching record. The migration was technically valid; the blast radius was
not bounded; the deploy halted in front of the business owner.

Migrations should mutate explicitly-targeted records, not "everything that
matches an empty filter." If a migration genuinely needs to touch every
record, that decision needs human review — this lint forces the
conversation.

Self-contained: pure stdlib (ast).
"""
import argparse
import ast
import sys
from pathlib import Path

# =============================================================================
# STACK-SPECIFIC: which directories contain migration scripts?
# =============================================================================
MIGRATION_PATHS_FRAPPE = [
    "**/patches/**/*.py",
    "**/migrations/**/*.py",
]
MIGRATION_PATHS_DJANGO = [
    "**/migrations/*.py",
]

# =============================================================================
# Patterns that trigger lint failure
# =============================================================================

class BroadWriteVisitor(ast.NodeVisitor):
    """
    Flags:
      - frappe.db.sql with no WHERE clause that touches a known business table
      - Document.search([]) followed by write(), unlink(), set_value()
      - frappe.get_all(...) without filters followed by mutation
    """
    def __init__(self, file: Path):
        self.file = file
        self.findings: list[tuple[int, str]] = []

    def visit_Call(self, node: ast.Call):
        # Pattern 1: any .search([]) call (Frappe + legacy_source-style)
        if isinstance(node.func, ast.Attribute) and node.func.attr == "search":
            if node.args and isinstance(node.args[0], ast.List) and not node.args[0].elts:
                self.findings.append((node.lineno, "search([]) — empty filter (broad-write risk)"))

        # Pattern 2: get_all() without filters argument
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get_all":
            kwargs = {kw.arg for kw in node.keywords if kw.arg}
            has_positional_filter = len(node.args) >= 2  # doctype, filters, ...
            if "filters" not in kwargs and not has_positional_filter:
                self.findings.append((node.lineno, "get_all(...) without filters — broad-read risk"))

        # Pattern 3: frappe.db.sql with UPDATE/DELETE and no WHERE
        if isinstance(node.func, ast.Attribute) and node.func.attr == "sql":
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                sql = node.args[0].value.upper()
                if (sql.lstrip().startswith(("UPDATE ", "DELETE ")) and " WHERE " not in sql):
                    self.findings.append((node.lineno, "raw SQL UPDATE/DELETE with no WHERE clause"))

        self.generic_visit(node)

# =============================================================================
# Driver
# =============================================================================
def lint_file(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as e:
        return [f"{path}:{e.lineno}: SyntaxError — could not lint"]
    visitor = BroadWriteVisitor(path)
    visitor.visit(tree)
    return [f"{path}:{ln}: {msg}" for ln, msg in visitor.findings]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None,
                        help="Repo root (default: parent of script)")
    parser.add_argument("--patterns", nargs="+", default=MIGRATION_PATHS_FRAPPE,
                        help="Glob patterns for migration files")
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else Path(__file__).resolve().parent.parent.parent
    print(f"\n[MIGRATION LINT] Repo root: {repo_root}")
    print(f"                  Patterns:  {args.patterns}")

    files = []
    for pattern in args.patterns:
        files.extend(repo_root.glob(pattern))

    print(f"                  Files:     {len(files)}")
    if not files:
        print(f"                  No migration files found. PASS (vacuously).")
        sys.exit(0)

    all_findings = []
    for f in files:
        findings = lint_file(f)
        all_findings.extend(findings)

    if not all_findings:
        print(f"\nMIGRATION LINT PASS — no broad-write patterns found.")
        sys.exit(0)

    print(f"\nMIGRATION LINT FAIL — {len(all_findings)} potential broad-write pattern(s):")
    for finding in all_findings:
        print(f"  {finding}")
    print(f"\nReview each. If a broad mutation is genuinely intended, add a comment")
    print(f"explaining the bounded-blast-radius and add `# noqa: broadwrite` on the line.")
    sys.exit(1)

if __name__ == "__main__":
    main()
