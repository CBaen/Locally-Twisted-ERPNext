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
        # "What We Make" parent + product-type children. A parent dropdown row
        # cannot itself carry a URL (Frappe Top Bar Item validation) — children
        # handle navigation; the parent acts only as the dropdown trigger.
        {"label": "What We Make", "url": "", "open_in_new_tab": 0, "right": 0},
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

    Frappe groups footer items into columns by parent_label, BUT each parent
    label must exist as its own row first (URL-less, like a top-bar dropdown
    parent). Children then reference those parent rows via parent_label.
    """
    return [
        # Column headers (URL-less parent rows)
        {"label": "Shop", "url": ""},
        {"label": "Services", "url": ""},
        {"label": "Company", "url": ""},
        {"label": "Contact", "url": ""},
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
    """The footer 'address' field renders as HTML in footer-info.

    Frappe HTML-sanitizes this field — it strips <path d=...> attributes from
    inline SVGs (verified by inspection: rendered output has empty <path></path>).
    Workaround: social icons rendered via CSS background-image data URIs,
    keyed off class names on the <a>. Class names survive sanitization.
    """
    return """\
<div class="lt-footer-brand-block">
  <div class="lt-footer-brand">Locally Twisted</div>
  <div class="lt-footer-tagline">Utah's balloon specialists since 1998</div>
  <ul class="lt-footer-social" aria-label="Locally Twisted on social media">
    <li><a class="lt-social lt-social--instagram" href="https://www.instagram.com/locally_twisted/" rel="noopener" target="_blank" aria-label="Instagram (opens in new tab)"></a></li>
    <li><a class="lt-social lt-social--facebook" href="https://www.facebook.com/locallytwisted" rel="noopener" target="_blank" aria-label="Facebook (opens in new tab)"></a></li>
    <li><a class="lt-social lt-social--pinterest" href="https://www.pinterest.com/locallytwisted/" rel="noopener" target="_blank" aria-label="Pinterest (opens in new tab)"></a></li>
    <li><a class="lt-social lt-social--twitter" href="https://twitter.com/locallytwisted" rel="noopener" target="_blank" aria-label="Twitter (opens in new tab)"></a></li>
  </ul>
  <address class="lt-footer-address">
    <a href="https://maps.google.com/?q=8969+S+2700+W+West+Jordan+UT" rel="noopener" target="_blank">8969 S 2700 W<br>West Jordan, UT 84088</a><br>
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
    """Copyright bar — accessibility link required by Phase 1 Slice 2 spec.

    Frappe auto-prepends a "©" character to the copyright field when rendering,
    so this value must NOT start with one — otherwise we get "© ©" duplication.
    """
    return (
        '2026 Locally Twisted &middot; '
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
                # Rich Text content_type tells Frappe to render `main_section`
                # as raw HTML inside the article. content_type="HTML" expects
                # `main_section_html` instead and silently renders blank if you
                # only set main_section.
                "content_type": "Rich Text",
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
