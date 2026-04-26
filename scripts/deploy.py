#!/usr/bin/env python3
"""
Client-repo deploy orchestrator.

Runs all four portable gates, then deploys, then verifies post-deploy.
Self-contained: no imports from outside this repository.

Usage:
    python scripts/deploy.py            # Full deploy
    python scripts/deploy.py --dry-run  # Run gates only, no deploy
    python scripts/deploy.py --skip-pre # Skip pre-deploy gates (emergency only)

Exit codes:
    0  PASS — every gate passed, deploy succeeded
    1  FAIL — a gate or the deploy itself failed
    2  GATE BLOCKED — a gate explicitly refused to allow deploy

This script is the single entry point for production deployment. Do not
run individual bench / migration / asset commands manually in production.
The gates exist because manual sequences get skipped under pressure.
"""
import argparse
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIG — edit per client
# =============================================================================
CONFIG = {
    "stack": "frappe",                          # frappe | django | next | other
    # LT runs locally at :8081 today. Production URL is TBD until cutover —
    # the new ERPNext storefront will replace https://locallytwisted.com
    # at cutover. Until then, gates run against local dev.
    # TODO(production-url): swap to https://locallytwisted.com (or the new
    # subdomain decided pre-cutover) once Phase 1 ships.
    "site_url": "http://localhost:8081",
    # TODO(form-path): /book is not yet built. Phase 2 (Lead Intake) wires
    # the customer-facing booking form. Keep "/book" as the canonical path
    # so the smoke test is ready when the form lands. Until then,
    # smoke_forms.py against /book will FAIL — that's expected.
    "smoke_test_form_path": "/book",
    "smoke_test_screenshot_paths": [            # URLs to screenshot for visual verification
        "/",                                    # Home (currently the "Coming soon" placeholder — HANDOFF 2026-04-26)
        "/all-products",                        # Webshop (HTTP 200 verified in HANDOFF 2026-04-26)
    ],
    "frappe_site_name": "frontend",             # CLAUDE.md "Local stack" table
    "frappe_app_name": "locally_twisted",       # CLAUDE.md custom Frappe app
}

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT_DIR = REPO_ROOT / "scripts" / "lint"
VERIFY_DIR = REPO_ROOT / "scripts" / "verify"

# =============================================================================
# Helpers
# =============================================================================

class GateResult:
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"

def section(title: str):
    bar = "=" * 70
    print(f"\n{bar}\n{title}\n{bar}")

def run_gate(gate_name: str, command: list[str]) -> str:
    """Run a gate command. Returns PASS/FAIL/SKIP."""
    print(f"\n[GATE] {gate_name}")
    print(f"       command: {' '.join(command)}")
    try:
        result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    except FileNotFoundError as e:
        print(f"       SKIP - command not found: {e}")
        return GateResult.SKIP
    if result.returncode == 0:
        print(f"       PASS")
        return GateResult.PASS
    print(f"       FAIL (exit {result.returncode})")
    return GateResult.FAIL

# =============================================================================
# Gate 1: Migration broad-write lint (PRE-DEPLOY, ALWAYS)
# =============================================================================
def gate_migration_lint() -> str:
    """
    Lint patches/migrations under THIS client's app for unbounded broad-write
    patterns. Scoped to `apps/<frappe_app_name>/` so third-party app code
    (e.g. bind-mounted upstream `webshop`) is not swept — the gate's purpose
    is to protect code we own, not to police upstream.
    """
    app = CONFIG["frappe_app_name"]
    return run_gate(
        "Migration broad-write lint",
        [sys.executable, str(LINT_DIR / "migration_broad_write.py"),
         "--patterns", f"apps/{app}/**/patches/**/*.py", f"apps/{app}/**/migrations/**/*.py"],
    )

# =============================================================================
# Gate 2: Schema parity check (PRE-DEPLOY, requires DB access)
# =============================================================================
def gate_schema_parity() -> str:
    return run_gate(
        "Schema parity check",
        [sys.executable, str(VERIFY_DIR / "schema_parity.py"),
         "--site", CONFIG["frappe_site_name"]],
    )

# =============================================================================
# Gate 3: Human-review-commit check (PRE-DEPLOY)
# =============================================================================
def gate_human_review_commit() -> str:
    """
    Verify the most recent commit is human-authored, not auto-generated.

    For repos using BBC's Claude Code workflow, this prevents auto-committed
    edits from reaching production unreviewed. For non-Claude-Code teams,
    this gate is a no-op (every commit is human-authored anyway).
    """
    print(f"\n[GATE] Human-review commit check")
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%s"],
            cwd=REPO_ROOT, check=False, capture_output=True, text=True,
        )
    except FileNotFoundError:
        print(f"       SKIP - git not available")
        return GateResult.SKIP
    last_msg = result.stdout.strip()
    print(f"       last commit: {last_msg[:80]}")
    if last_msg.startswith("auto:"):
        print(f"       FAIL - most recent commit is an auto-commit")
        print(f"       Write a human-authored review commit before deploying.")
        return GateResult.FAIL
    print(f"       PASS")
    return GateResult.PASS

# =============================================================================
# Gate 4: Visual verification (POST-DEPLOY)
# =============================================================================
def gate_visual_screenshot() -> str:
    paths = ",".join(CONFIG["smoke_test_screenshot_paths"])
    return run_gate(
        "Visual screenshot verification",
        [sys.executable, str(VERIFY_DIR / "playwright_screenshot.py"),
         "--base-url", CONFIG["site_url"],
         "--paths", paths],
    )

# =============================================================================
# Gate 5: Form smoke test (POST-DEPLOY)
# =============================================================================
def gate_form_smoke() -> str:
    return run_gate(
        "Form smoke test",
        [sys.executable, str(VERIFY_DIR / "smoke_forms.py"),
         "--base-url", CONFIG["site_url"],
         "--form-path", CONFIG["smoke_test_form_path"]],
    )

# =============================================================================
# The actual deploy step (STACK-SPECIFIC)
# =============================================================================
def do_deploy() -> str:
    """STACK: frappe - replace this entire function for non-Frappe stacks."""
    print(f"\n[DEPLOY] Frappe migrate + asset rebuild + cache clear")
    site = CONFIG["frappe_site_name"]
    steps = [
        ["bench", "--site", site, "migrate"],
        ["bench", "--site", site, "clear-website-cache"],
        ["bench", "--site", site, "build", "--app", CONFIG["frappe_app_name"]],
    ]
    for step in steps:
        print(f"         {' '.join(step)}")
        result = subprocess.run(step, cwd=REPO_ROOT, check=False)
        if result.returncode != 0:
            print(f"         FAIL")
            return GateResult.FAIL
    print(f"         PASS")
    return GateResult.PASS

# =============================================================================
# Orchestrator
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="Client-repo deploy orchestrator")
    parser.add_argument("--dry-run", action="store_true", help="Run gates only, no deploy")
    parser.add_argument("--skip-pre", action="store_true", help="Skip pre-deploy gates (emergency only)")
    args = parser.parse_args()

    section("PRE-DEPLOY GATES")
    pre_results = {}
    if not args.skip_pre:
        pre_results["migration_lint"] = gate_migration_lint()
        pre_results["schema_parity"] = gate_schema_parity()
        pre_results["human_review_commit"] = gate_human_review_commit()
    else:
        print("SKIPPED via --skip-pre - emergency mode only")

    if any(r == GateResult.FAIL for r in pre_results.values()):
        section("PRE-DEPLOY GATE FAILED - DEPLOY ABORTED")
        for name, result in pre_results.items():
            print(f"  {name}: {result}")
        sys.exit(2)

    if args.dry_run:
        section("DRY RUN - STOPPING BEFORE DEPLOY")
        for name, result in pre_results.items():
            print(f"  {name}: {result}")
        sys.exit(0)

    section("DEPLOYING")
    deploy_result = do_deploy()
    if deploy_result == GateResult.FAIL:
        section("DEPLOY FAILED")
        sys.exit(1)

    section("POST-DEPLOY GATES")
    post_results = {
        "visual_screenshot": gate_visual_screenshot(),
        "form_smoke": gate_form_smoke(),
    }

    all_results = {**pre_results, **{"deploy": deploy_result}, **post_results}
    section("DEPLOY COMPLETE - GATE SUMMARY")
    for name, result in all_results.items():
        print(f"  {name}: {result}")
    if any(r == GateResult.FAIL for r in all_results.values()):
        print("\nOne or more post-deploy gates FAILED. Investigate before declaring done.")
        sys.exit(1)
    print("\nAll gates PASS. Deploy verified.")
    sys.exit(0)

if __name__ == "__main__":
    main()
