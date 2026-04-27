#!/usr/bin/env python3
"""Capture the BTFP page + each carousel image individually for photo review.

GL flagged: some photos too close-up, one rotated 90 degrees (a little girl).
Goal: produce side-by-side per-image thumbs labeled with filename so we can
critique each one specifically.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "btfp-review-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2)
        page = ctx.new_page()
        msgs, errs = [], []
        page.on("console", lambda m: msgs.append((m.type, m.text)))
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(BASE_URL + "/balloon-twisting-and-face-painting", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(800)

        # Full page screenshot
        page.screenshot(path=str(OUT / "00-full-page-desktop.png"), full_page=True)

        # Crop the services band (where the carousels live)
        services = page.locator(".lt-btfp__services")
        sb = services.bounding_box()
        if sb:
            page.screenshot(path=str(OUT / "01-services-band.png"),
                            clip={"x": 0, "y": sb["y"] - 8, "width": 1280, "height": sb["height"] + 16})

        # Capture EACH photo individually at full natural size for review
        photos = page.locator(".lt-btfp__carousel-img").all()
        print(f"\nFound {len(photos)} photos.\n")
        meta = []
        for idx, img in enumerate(photos, 1):
            src = img.get_attribute("src") or ""
            filename = src.rsplit("/", 1)[-1]
            # Each image's natural size + rendered size
            info = img.evaluate(
                """(el) => ({
                    naturalW: el.naturalWidth,
                    naturalH: el.naturalHeight,
                    renderedW: el.clientWidth,
                    renderedH: el.clientHeight,
                    complete: el.complete,
                })"""
            )
            # Force a screenshot of the actual rendered image
            box = img.bounding_box()
            if box and box["width"] > 0:
                # Scroll into view first
                img.scroll_into_view_if_needed()
                page.wait_for_timeout(150)
                box = img.bounding_box()
                if box and box["width"] > 0:
                    page.screenshot(
                        path=str(OUT / f"photo-{idx:02d}-{filename}.png"),
                        clip={"x": box["x"], "y": box["y"], "width": box["width"], "height": box["height"]},
                    )
            meta.append({
                "idx": idx,
                "filename": filename,
                "src": src,
                **info,
            })
            ratio = info["naturalW"] / info["naturalH"] if info["naturalH"] else 0
            orientation = "portrait" if ratio < 0.95 else ("landscape" if ratio > 1.05 else "square")
            print(f"{idx:2d}. {filename:40s}  natural {info['naturalW']:>4}x{info['naturalH']:>4}  ({orientation}, ratio {ratio:.2f})  rendered {info['renderedW']}x{info['renderedH']}")

        # Print a summary
        print(f"\nConsole msgs: {len(msgs)}  pageerrors: {len(errs)}")
        for kind, text in msgs[:5]:
            print(f"  [{kind}] {text}")
        for e in errs[:5]:
            print(f"  ERR {e}")

        browser.close()
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
