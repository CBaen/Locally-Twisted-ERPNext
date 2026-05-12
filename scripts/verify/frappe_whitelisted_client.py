"""Call authenticated Frappe whitelisted methods from an existing CDP browser."""
from __future__ import annotations

import json
from typing import Any


def call_with_cdp(*, base_url: str, method: str, kwargs: dict[str, Any], cdp_url: str) -> dict[str, Any]:
    """Use an already-authenticated browser session without printing cookies."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Python Playwright is required for authenticated live verifier calls") from exc

    target = base_url.rstrip("/")
    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        if not browser.contexts:
            raise RuntimeError(f"No browser contexts available at {cdp_url}")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        if not page.url.startswith(target):
            page.goto(f"{target}/app", wait_until="networkidle", timeout=60000)
        try:
            page.wait_for_function(
                "() => !!(window.csrf_token || (window.frappe && window.frappe.csrf_token))",
                timeout=10000,
            )
        except Exception:
            page.reload(wait_until="networkidle", timeout=60000)
            page.wait_for_function(
                "() => !!(window.csrf_token || (window.frappe && window.frappe.csrf_token))",
                timeout=10000,
            )
        result = page.evaluate(
            """async ({target, method, kwargs}) => {
                const csrf =
                    window.csrf_token ||
                    (window.frappe && window.frappe.csrf_token) ||
                    (document.querySelector('meta[name="csrf-token"]') || {}).content ||
                    "";
                const headers = {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                };
                if (csrf) {
                    headers["X-Frappe-CSRF-Token"] = csrf;
                }
                const response = await fetch(`${target}/api/method/${method}`, {
                    method: "POST",
                    credentials: "include",
                    headers,
                    body: JSON.stringify(kwargs)
                });
                return {
                    ok: response.ok,
                    status: response.status,
                    text: await response.text()
                };
            }""",
            {"target": target, "method": method, "kwargs": kwargs},
        )

    try:
        payload = json.loads(result["text"] or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Authenticated Frappe call returned non-JSON status {result['status']}: "
            f"{result['text'][:500]}"
        ) from exc

    if not result["ok"] or payload.get("exc"):
        raise RuntimeError(
            f"Authenticated Frappe call failed status {result['status']}: "
            f"{result['text'][:1000]}"
        )
    message = payload.get("message")
    return message if isinstance(message, dict) else payload
