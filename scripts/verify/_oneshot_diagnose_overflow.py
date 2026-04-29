#!/usr/bin/env python3
"""Diagnose mobile overflow — find which elements exceed the viewport width."""
import json
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/contact"
VIEWPORT_W = 375

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": VIEWPORT_W, "height": 800})
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle", timeout=30000)

    # Document widths
    sizes = page.evaluate("""() => ({
        innerWidth: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        bodyScrollWidth: document.body.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
    })""")
    print("Page widths:", json.dumps(sizes, indent=2))

    # Find elements wider than viewport
    overflow_elems = page.evaluate(f"""() => {{
        const all = document.querySelectorAll('*');
        const out = [];
        for (const el of all) {{
            const r = el.getBoundingClientRect();
            if (r.right > {VIEWPORT_W} + 1 || r.width > {VIEWPORT_W} + 1) {{
                out.push({{
                    tag: el.tagName.toLowerCase(),
                    cls: (el.className && el.className.toString) ? el.className.toString().slice(0, 80) : '',
                    id: el.id || '',
                    width: Math.round(r.width),
                    right: Math.round(r.right),
                    left: Math.round(r.left),
                }});
                if (out.length > 30) break;
            }}
        }}
        return out;
    }}""")
    print("\nElements wider than viewport (or extending past right edge):")
    for e in overflow_elems[:25]:
        print(f"  {e['tag']:6} w={e['width']:4} L={e['left']:4} R={e['right']:4}  .{e['cls'][:60]}#{e['id']}")

    # Computed grid template on key elements
    grid = page.evaluate("""() => {
        const grid = document.querySelector('.lt-contact__grid');
        const intro = document.querySelector('.lt-contact__intro');
        const heroContainer = document.querySelector('.lt-contact__intro .container');
        return {
            grid_cols: grid ? getComputedStyle(grid).gridTemplateColumns : null,
            grid_width: grid ? grid.getBoundingClientRect().width : null,
            intro_width: intro ? intro.getBoundingClientRect().width : null,
            hero_container_width: heroContainer ? heroContainer.getBoundingClientRect().width : null,
            hero_container_max: heroContainer ? getComputedStyle(heroContainer).maxWidth : null,
        };
    }""")
    print("\nKey element computed values:")
    print(json.dumps(grid, indent=2))

    browser.close()
