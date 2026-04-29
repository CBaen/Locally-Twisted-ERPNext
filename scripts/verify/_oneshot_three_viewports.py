#!/usr/bin/env python3
"""Capture viewport-only screenshots at iPhone SE (320), iPhone (375), iPhone Plus (414).
Goal: confirm hamburger button is visible and within viewport on all three.
"""
import os
import sys
from playwright.sync_api import sync_playwright

VIEWPORTS = [("se_320", 320, 568), ("phone_375", 375, 812), ("plus_414", 414, 896)]
PAGES = ["/", "/contact", "/shop"]

def main():
    out = "scripts/verify/_screenshots/_three_viewports"
    os.makedirs(out, exist_ok=True)
    fails = 0
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for label, w, h in VIEWPORTS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            for path in PAGES:
                slug = path.strip("/").replace("/", "_") or "home"
                fname = f"{slug}__{label}.png"
                try:
                    pg.goto(f"http://localhost:8081{path}", wait_until="networkidle", timeout=30000)
                    # Probe hamburger position
                    info = pg.evaluate("""() => {
                        const t = document.querySelector('.lt-header__toggle');
                        const r = t ? t.getBoundingClientRect() : null;
                        return r ? {L: Math.round(r.left), R: Math.round(r.right), w: Math.round(r.width)} : null;
                    }""")
                    pg.screenshot(path=f"{out}/{fname}", full_page=False)
                    fits = "FITS" if info and info["R"] <= w else "OVERFLOW"
                    print(f"  {label:10} {path:10} hamburger L={info['L']:>3} R={info['R']:>3} (vp={w})  {fits}")
                except Exception as e:
                    print(f"  {label} {path} ERR {e}")
                    fails += 1
            ctx.close()
        b.close()
    print(f"\nSaved to {out}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
