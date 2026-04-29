"""Identify the actual computed background-color of the top utility bar."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_context(viewport={"width": 1366, "height": 900}).new_page()
    page.goto("http://localhost:8081/", wait_until="networkidle", timeout=15000)
    page.wait_for_timeout(800)

    selectors = [
        ".lt-header",
        ".lt-header__utility",
        ".lt-header__utility-row",
        ".lt-header__nav",
        "header",
        "body",
    ]
    for sel in selectors:
        if page.locator(sel).count():
            bg = page.locator(sel).first.evaluate(
                "el => getComputedStyle(el).backgroundColor"
            )
            print(f"  {sel:40s} → {bg}")

    b.close()
