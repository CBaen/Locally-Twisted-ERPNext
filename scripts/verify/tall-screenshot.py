from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = p.chromium.launch().new_browser().new_context().new_page(viewport={"width": 1366, "height": 2400})
    page.goto("http://localhost:8081/")
    page.screenshot(path="C:/Users/baenb/.claude/lt-desktop-tall.png")
    print("Saved to lt-desktop-tall.png")
