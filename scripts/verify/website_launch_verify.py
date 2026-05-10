#!/usr/bin/env python3
"""Run the Locally Twisted public website launch verification gate.

This is the single entrypoint behind ``npm run test:website-verify``. It keeps
the launch gate readable, runs Playwright specs with a conservative worker
count, and stops at the first failing step with the exact command named.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "http://localhost:8081"


def parse_worker_count(value: str | None) -> int:
    try:
        return max(1, int(value or "1"))
    except ValueError:
        return 1


DEFAULT_WORKERS = parse_worker_count(os.environ.get("LT_PLAYWRIGHT_WORKERS"))


@dataclass(frozen=True)
class Step:
    name: str
    command: list[str]
    timeout_seconds: int


def command_text(command: Sequence[str]) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline(list(command))
    return " ".join(command)


def local_playwright_command(workers: int, spec: str) -> list[str]:
    bin_name = "playwright.cmd" if os.name == "nt" else "playwright"
    local_bin = ROOT / "node_modules" / ".bin" / bin_name
    executable = str(local_bin) if local_bin.exists() else "npx"
    command = [executable]
    if executable == "npx":
        command.append("playwright")
    return [
        *command,
        "test",
        spec,
        "--reporter=dot",
        "--retries=1",
        f"--workers={workers}",
    ]


def build_steps(args: argparse.Namespace) -> list[Step]:
    python = sys.executable
    workers = max(1, args.workers)
    steps = [
        Step("Verifier CLI safety contract", [python, "scripts/verify/verifier_cli_contract.py"], 120),
        Step("Navigation IA", [python, "scripts/verify/nav_ia.py"], 120),
        Step("Passive layout matrix", local_playwright_command(workers, "scripts/verify/layout_fit.spec.js"), 900),
        Step(
            "Public container contract",
            local_playwright_command(workers, "scripts/verify/container_contract.spec.js"),
            360,
        ),
        Step(
            "Interactive layout states",
            local_playwright_command(workers, "scripts/verify/interactive_layout.spec.js"),
            600,
        ),
        Step(
            "Search contract",
            local_playwright_command(workers, "scripts/verify/search_contract.spec.js"),
            180,
        ),
        Step(
            "Portfolio proof reel",
            local_playwright_command(workers, "scripts/verify/portfolio_reel.spec.js"),
            300,
        ),
        Step("Ecommerce pause contract", [python, "scripts/verify/ecommerce_pause_contract.py"], 180),
    ]

    if args.with_a11y:
        steps.extend(
            [
                Step("Public axe accessibility", ["node", "scripts/verify/a11y_audit.js"], 300),
                Step("Manual accessibility probe", ["node", "scripts/verify/manual_a11y_probe.js"], 300),
            ]
        )

    if args.with_contact_smoke:
        steps.append(
            Step(
                "Contact smoke submission",
                [
                    python,
                    "scripts/verify/smoke_forms.py",
                    "--base-url",
                    args.base_url,
                    "--form-path",
                    "/contact",
                    "--skip-newsletter",
                ],
                360,
            )
        )

    return steps


def run_step(step: Step, env: dict[str, str]) -> int:
    print(f"\n=== {step.name} ===", flush=True)
    print(f"$ {command_text(step.command)}", flush=True)
    started = time.monotonic()
    try:
        proc = subprocess.run(
            step.command,
            cwd=ROOT,
            env=env,
            timeout=step.timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        elapsed = time.monotonic() - started
        print(
            f"[WEBSITE LAUNCH VERIFY] FAIL: {step.name} timed out after {elapsed:.1f}s "
            f"(limit {step.timeout_seconds}s)",
            flush=True,
        )
        return 124

    elapsed = time.monotonic() - started
    if proc.returncode != 0:
        print(
            f"[WEBSITE LAUNCH VERIFY] FAIL: {step.name} exited {proc.returncode} after {elapsed:.1f}s",
            flush=True,
        )
        return proc.returncode

    print(f"[WEBSITE LAUNCH VERIFY] PASS: {step.name} ({elapsed:.1f}s)", flush=True)
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Playwright worker count for browser specs. Defaults to LT_PLAYWRIGHT_WORKERS or 1.",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LT_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL for public route and contact smoke checks.",
    )
    parser.add_argument(
        "--with-a11y",
        action="store_true",
        help="Also run axe and manual accessibility probes.",
    )
    parser.add_argument(
        "--with-contact-smoke",
        action="store_true",
        help="Also submit the /contact smoke form and verify the backend Lead cleanup.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    env = os.environ.copy()
    env["LT_BASE_URL"] = args.base_url
    env["LT_PLAYWRIGHT_WORKERS"] = str(max(1, args.workers))

    steps = build_steps(args)
    started = time.monotonic()
    print(
        f"[WEBSITE LAUNCH VERIFY] starting {len(steps)} steps "
        f"(base_url={args.base_url}, playwright_workers={env['LT_PLAYWRIGHT_WORKERS']})",
        flush=True,
    )

    for step in steps:
        result = run_step(step, env)
        if result != 0:
            return result

    elapsed = time.monotonic() - started
    print(f"\n[WEBSITE LAUNCH VERIFY] PASS: {len(steps)} steps completed in {elapsed:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
