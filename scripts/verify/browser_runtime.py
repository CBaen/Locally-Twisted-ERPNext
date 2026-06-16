"""Shared Playwright browser launcher for host-side verifier scripts."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


class MissingPlaywright(RuntimeError):
    pass


LINUX_BROWSER_CANDIDATES = [
    "/usr/bin/brave-browser",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/microsoft-edge",
]


def browser_executable() -> str | None:
    configured = os.environ.get("PLAYWRIGHT_CHROME_PATH")
    if configured:
        return configured
    return next(
        (candidate for candidate in LINUX_BROWSER_CANDIDATES if Path(candidate).exists()),
        None,
    )


def require_playwright():
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise MissingPlaywright(
            "FAIL - playwright not installed. Run with a Python environment that has "
            "playwright, or use the Node Playwright npm scripts for browser checks."
        ) from exc
    return sync_playwright, PlaywrightTimeout


def launch_chromium(playwright, **kwargs):
    launch_kwargs = {"headless": True, **kwargs}
    executable = browser_executable()
    if executable and "executable_path" not in launch_kwargs:
        launch_kwargs["executable_path"] = executable
    return playwright.chromium.launch(**launch_kwargs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--print-browser",
        action="store_true",
        help="Print the browser executable that host-side Python verifiers will prefer.",
    )
    args = parser.parse_args()
    if args.print_browser:
        print(browser_executable() or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
