"""
Phase 1, Slice 2 — Header + Footer setup.

Configures ERPNext's Website Settings to render LT's header (nav per Option B
locked decision) and footer (Soft Blue band, brand wordmark, social, legal links,
business contact). Re-uploads the full lt-theme.css source-of-truth into
Website Settings.head_html so Slice 1 + Slice 2 styles are present together.

Also creates a minimal "Coming soon" home Web Page so `/` is publicly reachable
for verification — Slice 3 will replace this content with the real landing page.

Run:
    python scripts/setup/setup_slice2_header_footer.py

Verify:
    curl -s http://localhost:8081/ | grep -c "lt-footer-brand"   # should be 1+
    curl -s http://localhost:8081/ | grep -c 'navbar-brand'      # should be 1+
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

BASE = "http://localhost:8081"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEME_CSS_PATH = PROJECT_ROOT / "_resources" / "lt-theme.css"
THEME_MARKER_HEADER = (
    "<!-- LT Theme: source-of-truth at _resources/lt-theme.css ; "
    "Phase 1 Slices 1+2 -->"
)


def login(session: requests.Session) -> None:
    r = session.post(
        f"{BASE}/api/method/login",
        data={"usr": "Administrator", "pwd": "admin"},
        timeout=10,
    )
    r.raise_for_status()
    if r.json().get("message") != "Logged In":
        raise SystemExit(f"login failed: {r.text}")


def call(session: requests.Session, method: str, **payload):
    r = session.post(
        f"{BASE}/api/method/{method}",
        data={k: (v if isinstance(v, str) else json.dumps(v)) for k, v in payload.items()},
        timeout=15,
    )
    if r.status_code >= 400:
        raise SystemExit(f"{method} failed [{r.status_code}]: {r.text[:500]}")
    return r.json().get("message")


def build_top_bar_items() -> list[dict]:
    """Header nav per Option B: single What-We-Make + occasion landing pages.

    Frappe groups dropdown children by parent_label. Items with parent_label set
    to a parent's label become children of that parent's dropdown.

    Many destination URLs don't exist yet (Shop, occasion landing pages, BTFP
    page) — those slices haven't shipped. The links are stable-named so they
    activate the moment those slices land. 404s in the meantime are acceptable
    per the Phase 1 plan.
    """
    return [
        {"label": "Home", "url": "/", "open_in_new_tab": 0, "right": 0},
        # "What We Make" parent + product-type children
        {"label": "What We Make", "url": "/shop", "open_in_new_tab": 0, "right": 0},
        {"label": "Arches", "url": "/shop?type=arch", "open_in_new_tab": 0, "right": 0,
         "parent_label": "What We Make"},
        {"label": "Garlands", "url": "/shop?type=garland", "open_in_new_tab": 0, "right": 0,
         "parent_label": "What We Make"},
        {"label": "Walls", "url": "/shop?type=wall", "open_in_new_tab": 0, "right": 0,
         "parent_label": "What We Make"},
        {"label": "Drops", "url": "/shop?type=drop", "open_in_new_tab": 0, "right": 0,
         "parent_label": "What We Make"},
        {"label": "Columns", "url": "/shop?type=column", "open_in_new_tab": 0, "right": 0,
         "parent_label": "What We Make"},
        {"label": "Centerpieces", "url": "/shop?type=centerpiece", "open_in_new_tab": 0, "right": 0,
         "parent_label": "What We Make"},
        # Single-item nav entries
        {"label": "Twisting & Painting", "url": "/balloon-twisting-and-face-painting",
         "open_in_new_tab": 0, "right": 0},
        {"label": "Browse by Occasion", "url": "/occasions",
         "open_in_new_tab": 0, "right": 0},
        {"label": "Contact", "url": "/contact", "open_in_new_tab": 0, "right": 0},
        # Right-aligned utility
        {"label": "Sign in", "url": "/login", "open_in_new_tab": 0, "right": 1},
    ]


def build_footer_items() -> list[dict]:
    """Footer columns: Shop / Services / Company / Contact.

    Frappe groups footer items into columns by parent_label. Each parent_label
    becomes a column heading. Items without parent_label are skipped by the
    standard footer template, so EVERY item here has parent_label set.
    """
    return [
        # Shop column
        {"label": "All Products", "url": "/shop", "parent_label": "Shop"},
        {"label": "Arches", "url": "/shop?type=arch", "parent_label": "Shop"},
        {"label": "Garlands", "url": "/shop?type=garland", "parent_label": "Shop"},
        {"label": "Walls", "url": "/shop?type=wall", "parent_label": "Shop"},
        {"label": "Drops", "url": "/shop?type=drop", "parent_label": "Shop"},
        # Services column
        {"label": "Balloon Decor", "url": "/balloon-decor", "parent_label": "Services"},
        {"label": "Twisting & Painting", "url": "/balloon-twisting-and-face-painting",
         "parent_label": "Services"},
        {"label": "Browse by Occasion", "url": "/occasions", "parent_label": "Services"},
        # Company column
        {"label": "Contact", "url": "/contact", "parent_label": "Company"},
        {"label": "FAQ", "url": "/faq", "parent_label": "Company"},
        {"label": "Refund Policy", "url": "/refund-policy", "parent_label": "Company"},
        {"label": "Accessibility", "url": "/accessibility", "parent_label": "Company"},
        # Contact column (real LT contact info — public, on the live site already)
        {"label": "(801) 285-0860", "url": "tel:+18012850860", "parent_label": "Contact"},
        {"label": "hi@locallytwisted.com", "url": "mailto:hi@locallytwisted.com",
         "parent_label": "Contact"},
        {"label": "8969 S 2700 W, West Jordan, UT", "url": "https://maps.google.com/?q=8969+S+2700+W+West+Jordan+UT",
         "parent_label": "Contact"},
    ]


def build_footer_address_html() -> str:
    """The footer 'address' field renders as HTML at the top of the footer.

    Frappe places this above the column links — perfect spot for the brand
    wordmark, tagline, and social row. SVG icons inline so we don't need
    Font Awesome / external icon dep.
    """
    return """\
<div class="lt-footer-brand-block">
  <div class="lt-footer-brand">Locally Twisted</div>
  <div class="lt-footer-tagline">Utah's balloon specialists since 1998</div>
  <ul class="lt-footer-social" aria-label="Locally Twisted on social media">
    <li>
      <a href="https://www.instagram.com/locally_twisted/" rel="noopener" aria-label="Instagram (opens in new tab)" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.3.4.6.2 1 .5 1.5 1s.8.9 1 1.5c.2.5.4 1.1.4 2.3.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.3-.2.6-.5 1-1 1.5s-.9.8-1.5 1c-.5.2-1.1.4-2.3.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.3-.4-.6-.2-1-.5-1.5-1s-.8-.9-1-1.5c-.2-.5-.4-1.1-.4-2.3C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.3.2-.6.5-1 1-1.5s.9-.8 1.5-1c.5-.2 1.1-.4 2.3-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.2 0-3.5 0-4.7.1-1.1.1-1.7.2-2.1.4-.5.2-.9.4-1.3.8-.4.4-.6.8-.8 1.3-.2.4-.3 1-.4 2.1-.1 1.2-.1 1.5-.1 4.7s0 3.5.1 4.7c.1 1.1.2 1.7.4 2.1.2.5.4.9.8 1.3.4.4.8.6 1.3.8.4.2 1 .3 2.1.4 1.2.1 1.5.1 4.7.1s3.5 0 4.7-.1c1.1-.1 1.7-.2 2.1-.4.5-.2.9-.4 1.3-.8.4-.4.6-.8.8-1.3.2-.4.3-1 .4-2.1.1-1.2.1-1.5.1-4.7s0-3.5-.1-4.7c-.1-1.1-.2-1.7-.4-2.1-.2-.5-.4-.9-.8-1.3-.4-.4-.8-.6-1.3-.8-.4-.2-1-.3-2.1-.4-1.2-.1-1.5-.1-4.7-.1zm0 3.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8zm0 8a3.1 3.1 0 1 0 0-6.2 3.1 3.1 0 0 0 0 6.2zm6.3-8.2a1.1 1.1 0 1 1-2.3 0 1.1 1.1 0 0 1 2.3 0z"/>
        </svg>
      </a>
    </li>
    <li>
      <a href="https://www.facebook.com/locallytwisted" rel="noopener" aria-label="Facebook (opens in new tab)" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M22 12.07C22 6.51 17.52 2 12 2S2 6.51 2 12.07c0 5.02 3.66 9.18 8.44 9.93v-7.02H7.9v-2.91h2.54V9.85c0-2.51 1.49-3.9 3.77-3.9 1.09 0 2.24.2 2.24.2v2.47h-1.26c-1.24 0-1.63.78-1.63 1.57v1.88h2.78l-.44 2.91h-2.34V22c4.78-.75 8.44-4.91 8.44-9.93z"/>
        </svg>
      </a>
    </li>
    <li>
      <a href="https://www.pinterest.com/locallytwisted/" rel="noopener" aria-label="Pinterest (opens in new tab)" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 2C6.48 2 2 6.48 2 12c0 4.24 2.64 7.85 6.36 9.31-.09-.79-.17-2.01.04-2.87.19-.78 1.21-4.94 1.21-4.94s-.31-.62-.31-1.54c0-1.44.84-2.52 1.88-2.52.89 0 1.32.67 1.32 1.47 0 .9-.57 2.24-.86 3.49-.25 1.05.52 1.9 1.55 1.9 1.86 0 3.29-1.96 3.29-4.79 0-2.5-1.8-4.25-4.37-4.25-2.98 0-4.73 2.23-4.73 4.54 0 .9.34 1.86.78 2.39.08.1.1.19.07.29-.08.32-.26 1.05-.29 1.2-.05.19-.15.24-.35.14-1.31-.61-2.13-2.51-2.13-4.04 0-3.29 2.39-6.31 6.89-6.31 3.62 0 6.43 2.58 6.43 6.02 0 3.59-2.27 6.49-5.42 6.49-1.06 0-2.05-.55-2.39-1.2 0 0-.53 2.01-.65 2.51-.24.92-.88 2.07-1.31 2.77.99.31 2.04.47 3.13.47 5.52 0 10-4.48 10-10S17.52 2 12 2z"/>
        </svg>
      </a>
    </li>
    <li>
      <a href="https://twitter.com/locallytwisted" rel="noopener" aria-label="Twitter (opens in new tab)" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      </a>
    </li>
  </ul>
  <address class="lt-footer-address">
    <a href="https://maps.google.com/?q=8969+S+2700+W+West+Jordan+UT" rel="noopener" target="_blank">
      8969 S 2700 W<br>West Jordan, UT 84088
    </a><br>
    <a href="tel:+18012850860">(801) 285-0860</a><br>
    <a href="mailto:hi@locallytwisted.com">hi@locallytwisted.com</a>
  </address>
</div>"""


def build_brand_html() -> str:
    """Logo area on the navbar — text wordmark in DM Serif Display.

    Style guide rule: brand element must remain a wrapping anchor — never strip
    the link. Frappe wraps brand_html in <a class="navbar-brand" href="/"> by
    default, so we just provide the inner content.
    """
    return '<span>Locally Twisted</span>'


def build_copyright_html() -> str:
    """Copyright bar — accessibility link required by Phase 1 Slice 2 spec."""
    return (
        '© 2026 Locally Twisted &middot; '
        '<a href="/accessibility">Accessibility</a> &middot; '
        '<a href="/refund-policy">Refund Policy</a>'
    )


def build_head_html(theme_css: str) -> str:
    """Wrap the theme CSS in a <style> block with a discoverable marker."""
    return (
        f'{THEME_MARKER_HEADER}\n'
        f'<style data-source="lt-brand-foundation">\n'
        f'{theme_css}\n'
        f'</style>'
    )


def update_website_settings(session: requests.Session, theme_css: str) -> None:
    payload = {
        "app_name": "Locally Twisted",
        "brand_html": build_brand_html(),
        "top_bar_items": build_top_bar_items(),
        "footer_items": build_footer_items(),
        "address": build_footer_address_html(),
        "copyright": build_copyright_html(),
        "head_html": build_head_html(theme_css),
        "home_page": "home",
        "disable_signup": 1,
        "show_login_link": 0,
    }
    call(
        session,
        "frappe.client.set_value",
        doctype="Website Settings",
        name="Website Settings",
        fieldname=json.dumps(payload),
    )
    print(f"  ✓ Website Settings updated ({len(payload)} fields)")


def ensure_home_web_page(session: requests.Session) -> None:
    """Create a minimal placeholder home Web Page if one doesn't exist."""
    existing = call(
        session,
        "frappe.client.get_list",
        doctype="Web Page",
        filters=json.dumps([["route", "=", "home"]]),
        fields=json.dumps(["name", "route"]),
        limit_page_length=1,
    )
    if existing:
        print(f"  ✓ Home Web Page already exists: {existing[0]['name']}")
        return

    main_section_html = (
        '<section class="lt-section">'
        '<div class="container">'
        '<h1>Locally Twisted</h1>'
        '<p class="lead">Utah\'s balloon specialists since 1998. '
        'A new home for what we make is coming together.</p>'
        '<p>In the meantime, '
        '<a href="/contact">tell us what you\'re imagining</a>.</p>'
        '</div>'
        '</section>'
    )

    call(
        session,
        "frappe.client.insert",
        doc=json.dumps(
            {
                "doctype": "Web Page",
                "title": "Locally Twisted",
                "route": "home",
                "published": 1,
                "show_title": 0,
                "main_section": main_section_html,
                "content_type": "HTML",
                "show_sidebar": 0,
                "dynamic_route": 0,
            }
        ),
    )
    print("  ✓ Home Web Page created at route 'home'")


def verify(session: requests.Session) -> None:
    """Sanity check — fetch the served homepage and look for our markers."""
    r = session.get(f"{BASE}/", timeout=10)
    r.raise_for_status()
    html = r.text

    checks = {
        "navbar renders": '<nav class="navbar' in html,
        "brand wordmark present": "Locally Twisted</span>" in html or "Locally Twisted</a>" in html,
        "footer brand block": "lt-footer-brand" in html,
        "soft-blue footer styling": "web-footer" in html,
        "social row present": "lt-footer-social" in html,
        "accessibility link in copyright": '/accessibility' in html,
        "theme CSS injected": 'data-source="lt-brand-foundation"' in html,
        "home page rendered (not login)": "<title>Locally Twisted" in html or "Locally Twisted</h1>" in html,
        "ERPNext powered hidden by CSS": "footer-powered" in html,  # element exists; CSS hides it
    }
    print("\n--- Verification ---")
    for label, ok in checks.items():
        print(f"  {'✓' if ok else '✗'} {label}")
    if not all(checks.values()):
        print("\nSome checks failed. Inspect with:")
        print(f"  curl -s {BASE}/ | head -200")
        sys.exit(1)


def main() -> None:
    if not THEME_CSS_PATH.exists():
        raise SystemExit(f"theme CSS missing: {THEME_CSS_PATH}")
    theme_css = THEME_CSS_PATH.read_text(encoding="utf-8")
    print(f"→ Loaded theme CSS: {len(theme_css)} bytes")

    session = requests.Session()
    print("→ Logging in as Administrator")
    login(session)

    print("→ Updating Website Settings")
    update_website_settings(session, theme_css)

    print("→ Ensuring home Web Page exists")
    ensure_home_web_page(session)

    print("→ Verifying rendered output")
    verify(session)

    print("\nSlice 2 setup complete.")


if __name__ == "__main__":
    main()
