"""Portfolio oneshot — verifies the architecture renders end-to-end.

Captures four views to prove the dual-axis filter, the empty state, and
the responsive grid all work:

  1. Desktop tall (1280 x 3500), default state — all 15 cards visible
  2. Mobile tall (375 x 3500), default state — 2-col grid
  3. Filtered: ?event=corporate — Corporate pill auto-pressed, 3 cards
  4. Empty state: ?category=balloon-drops — empty-state component visible
     (proves the "no work matches that filter" UX renders correctly)

Console errors are captured per view. Output goes to
scripts/verify/_screenshots/portfolio-<timestamp>/.
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent / "_screenshots" / f"portfolio-{int(time.time())}"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "http://localhost:8081"


def shoot(page, url, filename, viewport):
    errors = []
    page.set_viewport_size(viewport)
    page.on("pageerror", lambda exc: errors.append(f"PAGEERROR: {exc}"))
    page.on(
        "console",
        lambda msg: errors.append(f"CONSOLE [{msg.type}]: {msg.text}")
        if msg.type in ("error", "warning")
        else None,
    )
    page.goto(url, wait_until="networkidle", timeout=30000)
    # Brief settle for JS init filter
    page.wait_for_timeout(500)
    path = OUT / filename
    page.screenshot(path=str(path), full_page=True)
    visible = page.evaluate(
        """
        () => {
            const cards = document.querySelectorAll('[data-portfolio-card]');
            let v = 0;
            cards.forEach(c => { if (!c.hidden) v += 1; });
            const empty = document.querySelector('[data-portfolio-grid]')?.getAttribute('data-empty');
            const count = document.querySelector('[data-portfolio-count]')?.textContent.trim();
            const title = document.title;
            return { total: cards.length, visible: v, empty, count, title };
        }
        """
    )
    print(f"[{filename}]")
    print(f"  url:       {url}")
    print(f"  viewport:  {viewport}")
    print(f"  title:     {visible['title']}")
    print(f"  cards:     {visible['visible']}/{visible['total']} visible")
    print(f"  count lbl: {visible['count']}")
    print(f"  empty:     {visible['empty']}")
    if errors:
        print(f"  ERRORS:")
        for e in errors[:10]:
            print(f"    - {e}")
    else:
        print(f"  errors:    none")
    print()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context()
    page = ctx.new_page()

    shoot(page, f"{BASE}/portfolio", "01-desktop-default.png", {"width": 1280, "height": 3500})
    shoot(page, f"{BASE}/portfolio", "02-mobile-default.png", {"width": 375, "height": 3500})
    shoot(page, f"{BASE}/portfolio?event=corporate", "03-desktop-corporate.png", {"width": 1280, "height": 2200})
    shoot(page, f"{BASE}/portfolio?category=balloon-drops", "04-desktop-empty-state.png", {"width": 1280, "height": 1600})

    # Modal: click first card and capture open state
    page.set_viewport_size({"width": 1280, "height": 900})
    page.goto(f"{BASE}/portfolio", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(300)
    page.locator('[data-portfolio-card]').first.click()
    page.wait_for_timeout(400)
    modal_state = page.evaluate(
        """
        () => {
            const m = document.querySelector('[data-portfolio-modal]');
            const img = m?.querySelector('[data-modal-image]');
            const title = m?.querySelector('[data-modal-title]');
            const cat = m?.querySelector('[data-modal-category]');
            return {
                hidden: m?.hasAttribute('hidden'),
                bodyLocked: document.body.classList.contains('lt-modal-open'),
                imageSrc: img?.getAttribute('src') || '',
                imageAlt: img?.getAttribute('alt') || '',
                title: title?.textContent || '',
                category: cat?.textContent || '',
                focusedTag: document.activeElement?.tagName,
                focusedClass: document.activeElement?.className,
            };
        }
        """
    )
    page.screenshot(path=str(OUT / "05-desktop-modal-open.png"), full_page=False)
    print("[05-desktop-modal-open.png]")
    print(f"  modal hidden:  {modal_state['hidden']}")
    print(f"  body locked:   {modal_state['bodyLocked']}")
    print(f"  image src:     {modal_state['imageSrc']}")
    print(f"  image alt:     {modal_state['imageAlt'][:60]}...")
    print(f"  title:         {modal_state['title']}")
    print(f"  category:      {modal_state['category']}")
    print(f"  focus moved:   {modal_state['focusedTag']} ({modal_state['focusedClass']})")
    print()

    # ESC closes modal + restores focus
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)
    closed_state = page.evaluate(
        """
        () => ({
            hidden: document.querySelector('[data-portfolio-modal]')?.hasAttribute('hidden'),
            bodyLocked: document.body.classList.contains('lt-modal-open'),
            focusBack: document.activeElement?.classList?.contains('lt-portfolio-card'),
        })
        """
    )
    print("[ESC-close-test]")
    print(f"  modal hidden after ESC: {closed_state['hidden']}")
    print(f"  body lock cleared:      {not closed_state['bodyLocked']}")
    print(f"  focus restored to card: {closed_state['focusBack']}")
    print()

    browser.close()

print(f"Saved to: {OUT}")
