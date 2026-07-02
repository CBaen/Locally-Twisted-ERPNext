# BTFP Contact Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refresh `/balloon-twisting-and-face-painting` as an editorial service page and make `/contact` the single public inquiry form with service-prefilled links.

**Architecture:** Keep the existing ERPNext Lead architecture in `locally_twisted.www.book.submit_book_inquiry`. Move customer-facing inquiry traffic to `/contact` with query-param prefill. Turn the BTFP page into an education/CTA page and make `/book` redirect to `/contact?intent=quick`.

**Tech Stack:** Frappe/ERPNext v15, Jinja website templates, page controllers in `apps/locally_twisted/locally_twisted/www`, Playwright-based verification scripts, Dockerized bench at `http://localhost:8081`.

---

## File Structure

- Modify `apps/locally_twisted/locally_twisted/www/contact.py`: parse `service` and `intent` query params, set preselected services and metadata for text-message previews.
- Modify `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`: mark preselected service checkboxes and run existing conditional visibility after initial state is rendered.
- Modify `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html`: remove page-local form, replace placeholder spec tables, add canonical contact CTAs.
- Modify `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`: remove the page-local submit endpoint from the customer path and keep only context/CSS used by the editorial page.
- Modify `apps/locally_twisted/locally_twisted/www/book.py`: redirect `/book` to `/contact?intent=quick`.
- Modify `scripts/verify/smoke_forms.py`: default form smoke path becomes `/contact`.
- Create `scripts/verify/contact_prefill.py`: focused Playwright verifier for `/contact?service=...` preselection behavior.
- Run `python scripts/dev/clear_website_cache.py` after Jinja/controller edits.

## Task 1: Add Contact Prefill Verification

**Files:**
- Create: `scripts/verify/contact_prefill.py`

- [ ] **Step 1: Write the failing verifier**

Create `scripts/verify/contact_prefill.py` with this content:

```python
#!/usr/bin/env python3
"""Verify /contact service query parameters preselect the shared inquiry form."""
import argparse
import sys

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("FAIL - playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


CASES = [
    ("/contact?service=btfp", ["Balloon Twisting", "Face Painting"]),
    ("/contact?service=twisting", ["Balloon Twisting"]),
    ("/contact?service=face-painting", ["Face Painting"]),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="Example: http://localhost:8081")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 900})
        for path, expected_services in CASES:
            url = base_url + path
            print(f"[PREFILL] {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except PlaywrightTimeout:
                print("  FAIL - page did not load")
                failures += 1
                continue

            for service in expected_services:
                locator = page.locator(f'input[name="x_services"][value="{service}"]')
                if locator.count() != 1:
                    print(f"  FAIL - checkbox for {service!r} not found")
                    failures += 1
                    continue
                if not locator.first.is_checked():
                    print(f"  FAIL - checkbox for {service!r} is not checked")
                    failures += 1
                else:
                    print(f"  OK - {service} checked")

            if "Balloon Twisting" in expected_services:
                twisting_panel = page.locator('[data-visibility-condition="Balloon Twisting"]')
                if twisting_panel.count() != 1 or not twisting_panel.first.is_visible():
                    print("  FAIL - Balloon Twisting details panel is not visible")
                    failures += 1
            if "Face Painting" in expected_services:
                painting_panel = page.locator('[data-visibility-condition="Face Painting"]')
                if painting_panel.count() != 1 or not painting_panel.first.is_visible():
                    print("  FAIL - Face Painting details panel is not visible")
                    failures += 1

        browser.close()

    if failures:
        print(f"[PREFILL] {failures} failure(s)")
        return 1
    print("[PREFILL] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run verifier to confirm it fails before implementation**

Run:

```bash
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
```

Expected result: at least one `FAIL - checkbox ... is not checked` because the form does not yet read `service` query params.

- [ ] **Step 3: Commit verifier**

Run:

```bash
git add scripts/verify/contact_prefill.py
git commit -m "test: add contact service prefill verifier"
```

## Task 2: Implement Contact Query Param Prefill

**Files:**
- Modify: `apps/locally_twisted/locally_twisted/www/contact.py`
- Modify: `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`

- [ ] **Step 1: Update `contact.py` context**

In `apps/locally_twisted/locally_twisted/www/contact.py`, replace `get_context` with:

```python
def get_context(context):
    service_param = (frappe.form_dict.get("service") or "").strip().lower()
    intent_param = (frappe.form_dict.get("intent") or "").strip().lower()

    preselected_services = []
    if service_param == "btfp":
        preselected_services = ["Balloon Twisting", "Face Painting"]
    elif service_param == "twisting":
        preselected_services = ["Balloon Twisting"]
    elif service_param in {"face-painting", "face_painting", "painting"}:
        preselected_services = ["Face Painting"]

    context.title = "Contact Locally Twisted"
    context.metatags = {
        "title": "Contact Locally Twisted",
        "description": (
            "Tell us about your celebration. Balloon decor, twisting, "
            "and face painting along the Wasatch Front."
        ),
        "og:title": "Contact Locally Twisted",
        "og:description": (
            "Tell us about your celebration. Balloon decor, twisting, "
            "and face painting along the Wasatch Front."
        ),
        "og:type": "website",
        "twitter:card": "summary_large_image",
    }
    context.occasion_options = OCCASION_OPTIONS
    context.selected_occasion = frappe.form_dict.get("occasion") or ""
    context.service_options = SERVICE_OPTIONS
    context.preselected_services = preselected_services
    context.contact_intent = intent_param
    context.contact_intro_title = (
        "Tell us about your celebration"
        if intent_param == "quick"
        else "Let's create something beautiful"
    )
    context.contact_intro_lede = (
        "A few details are enough to get started."
        if intent_param == "quick"
        else "Tell us about your celebration."
    )
    context.max_photos = MAX_PHOTOS
    context.max_photo_mb = MAX_PHOTO_BYTES // (1024 * 1024)
    return context
```

- [ ] **Step 2: Update contact template intro copy**

In `apps/locally_twisted/locally_twisted/www/contact.html`, replace:

```html
<h1>Let's Create Something Amazing</h1>
<p class="lt-contact__intro-lede">Tell us about your celebration</p>
```

with:

```html
<h1>{{ contact_intro_title }}</h1>
<p class="lt-contact__intro-lede">{{ contact_intro_lede }}</p>
```

- [ ] **Step 3: Mark service checkboxes as preselected**

In `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`, replace the service checkbox input:

```html
<input type="checkbox" id="{{ cb_id }}"
       name="x_services"
       value="{{ value }}"
       class="lt-book__service-checkbox"/>
```

with:

```html
<input type="checkbox" id="{{ cb_id }}"
       name="x_services"
       value="{{ value }}"
       class="lt-book__service-checkbox"
       {% if value in (preselected_services or []) %}checked{% endif %}/>
```

- [ ] **Step 4: Run focused verifier**

Run:

```bash
python scripts/dev/clear_website_cache.py
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
```

Expected result: `[PREFILL] PASS`.

- [ ] **Step 5: Commit contact prefill**

Run:

```bash
git add apps/locally_twisted/locally_twisted/www/contact.py apps/locally_twisted/locally_twisted/www/contact.html apps/locally_twisted/locally_twisted/templates/includes/book_form.html
git commit -m "feat: prefill contact form from service links"
```

## Task 3: Convert BTFP Page To Editorial CTA Page

**Files:**
- Modify: `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html`
- Modify: `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`

- [ ] **Step 1: Remove the embedded BTFP form section**

In `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html`, delete the full section beginning:

```html
<section id="lt-booking" class="lt-btfp__booking">
```

and ending at its matching:

```html
</section>
```

Then delete the `<script>` block at the bottom that begins:

```html
<script>
(function () {
    var form = document.getElementById('lt-btfp-form');
```

and ends with:

```html
</script>
```

- [ ] **Step 2: Add a canonical CTA section**

Insert this section where the removed form section was:

```html
<section class="lt-btfp__contact-cta">
    <div class="lt-btfp__contact-cta-inner">
        <p class="lt-btfp__kicker">START HERE</p>
        <h2>Tell us about your event.</h2>
        <p>
            A rough picture is enough to start. Share the date, location,
            guest count, and whether you want balloon twisting, face painting,
            or both. We will follow up with availability and the right team size.
        </p>
        <div class="lt-btfp__contact-actions">
            <a class="lt-btfp__contact-primary" href="/contact?service=btfp">Start the inquiry</a>
            <a class="lt-btfp__contact-secondary" href="tel:+18012850860">(801) 285-0860</a>
        </div>
    </div>
</section>
```

- [ ] **Step 3: Replace placeholder spec values**

In the Balloon Twisting card, replace the four spec rows with:

```html
<div class="lt-btfp__service-spec-row">
    <dt>BEST AT</dt>
    <dd>Birthday parties, school events, festivals, corporate family days</dd>
</div>
<div class="lt-btfp__service-spec-row">
    <dt>PACE</dt>
    <dd>Typically 15&ndash;20 children per hour, depending on design complexity</dd>
</div>
<div class="lt-btfp__service-spec-row">
    <dt>TEAM SIZE</dt>
    <dd>One balloon artist for smaller events; larger events may need more</dd>
</div>
<div class="lt-btfp__service-spec-row">
    <dt>PRICING</dt>
    <dd>$130 first hour, $115 each additional hour &mdash; per artist</dd>
</div>
```

In the Face Painting card, replace the four spec rows with:

```html
<div class="lt-btfp__service-spec-row">
    <dt>BEST AT</dt>
    <dd>Birthday parties, school events, festivals, corporate family days</dd>
</div>
<div class="lt-btfp__service-spec-row">
    <dt>STAFFING</dt>
    <dd>Face painting is staffed separately from balloon twisting</dd>
</div>
<div class="lt-btfp__service-spec-row">
    <dt>ARTISTS</dt>
    <dd>Book one of each when you want twisting and painting at the same time</dd>
</div>
<div class="lt-btfp__service-spec-row">
    <dt>PRICING</dt>
    <dd>$130 first hour, $115 each additional hour &mdash; per artist</dd>
</div>
```

- [ ] **Step 4: Update process CTA language**

In the process section, keep the four-step structure but ensure the deposit text does not imply immediate checkout. Replace the Step 3 paragraph with:

```html
<p>A $50 deposit per artist secures the date after availability and scope are confirmed. We send the next step once the booking details are clear.</p>
```

- [ ] **Step 5: Replace FAQ section with current import capture-backed FAQ**

In the FAQ section, keep the `<details>` pattern and use these four questions and answers:

```html
<details class="lt-btfp__faq-item" open>
    <summary>How many kids can one artist serve per hour?</summary>
    <div class="lt-btfp__faq-answer">
        <p>A balloon artist typically serves 15&ndash;20 children per hour. Face painting is a separate skill, and we book dedicated face painters &mdash; not the same people who twist balloons. For larger events or events that want both at once, we staff one of each so nobody waits in line.</p>
    </div>
</details>

<details class="lt-btfp__faq-item">
    <summary>Do you do outdoor events?</summary>
    <div class="lt-btfp__faq-answer">
        <p>Yes. We handle outdoor events regularly including festivals, school carnivals, and backyard parties. For outdoor balloon decor, we ask about shade availability since direct sun and wind affect balloon longevity.</p>
    </div>
</details>

<details class="lt-btfp__faq-item">
    <summary>How far in advance should I book?</summary>
    <div class="lt-btfp__faq-answer">
        <p>We recommend booking at least 2&ndash;3 weeks in advance for standard events. For weddings and large corporate events, 4&ndash;6 weeks is ideal. Last-minute bookings are sometimes possible.</p>
    </div>
</details>

<details class="lt-btfp__faq-item">
    <summary>What is your service area?</summary>
    <div class="lt-btfp__faq-answer">
        <p>We serve the Wasatch Front including Salt Lake City, Provo, Ogden, Park City, and surrounding areas. We regularly travel to Logan and other Utah locations.</p>
    </div>
</details>
```

- [ ] **Step 6: Remove page-local submit endpoint from the controller**

In `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`, remove:

- `import frappe`
- `from frappe import _`
- `from frappe.rate_limiter import rate_limit`
- `from frappe.utils import escape_html, validate_email_address`
- `SERVICE_CHOICES`
- `HOURS_OPTIONS`
- `EVENT_TYPES`
- `context.service_choices`
- `context.hours_options`
- `context.event_types`
- the full `submit_btfp_booking(...)` function

After this cleanup, the controller should only define `no_cache`, `sitemap`, `PAGE_CSS`, and `get_context`.

- [ ] **Step 7: Add CTA styles to `PAGE_CSS`**

Append this CSS inside `PAGE_CSS`:

```css
.lt-btfp__contact-cta {
    background-color: var(--lt-near-white);
    padding: 4rem 1.5rem;
}
.lt-btfp__contact-cta-inner {
    max-width: 760px;
    margin: 0 auto;
}
.lt-btfp__contact-cta h2 {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2rem;
    color: var(--lt-near-black);
    margin: 0 0 1rem;
    line-height: 1.15;
}
.lt-btfp__contact-cta p {
    color: var(--lt-soft-gray);
    line-height: 1.6;
    margin: 0 0 1.25rem;
}
.lt-btfp__contact-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
}
.lt-btfp__contact-primary,
.lt-btfp__contact-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    border-radius: 0.375rem;
    padding: 0.75rem 1.25rem;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    text-decoration: none;
}
.lt-btfp__contact-primary {
    background-color: var(--lt-teal);
    color: var(--lt-white);
    border: 1px solid var(--lt-teal);
}
.lt-btfp__contact-primary:hover,
.lt-btfp__contact-primary:focus-visible {
    background-color: #006666;
    border-color: #006666;
    color: var(--lt-white);
    text-decoration: none;
}
.lt-btfp__contact-secondary {
    background-color: var(--lt-white);
    color: var(--lt-near-black);
    border: 1px solid rgba(26, 26, 26, 0.18);
}
.lt-btfp__contact-secondary:hover,
.lt-btfp__contact-secondary:focus-visible {
    background-color: var(--lt-blush-tint);
    border-color: var(--lt-near-black);
    color: var(--lt-near-black);
    text-decoration: none;
}
```

- [ ] **Step 8: Verify no BTFP form remains**

Run:

```bash
python scripts/dev/clear_website_cache.py
$html = (Invoke-WebRequest -Uri 'http://localhost:8081/balloon-twisting-and-face-painting' -UseBasicParsing).Content
$html.Contains('id="lt-btfp-form"')
$html.Contains('/contact?service=btfp')
```

Expected output:

```text
False
True
```

- [ ] **Step 9: Commit BTFP editorial page**

Run:

```bash
git add apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py
git commit -m "feat: refresh btfp page as contact-led service page"
```

## Task 4: Redirect `/book` To The Guided Contact Page

**Files:**
- Modify: `apps/locally_twisted/locally_twisted/hooks.py`
- Modify: `apps/locally_twisted/locally_twisted/www/book.py`
- Modify: `scripts/verify/smoke_forms.py`

- [ ] **Step 1: Remove the route-rule alias from `hooks.py`**

In `website_route_rules`, remove:

```python
{"from_route": "/book",
 "to_route": "contact"},
```

This allows `www/book.py` to own the `/book` route and issue the redirect.

- [ ] **Step 2: Replace `book.py` page behavior with a redirect plus retained submit endpoint**

In `apps/locally_twisted/locally_twisted/www/book.py`, keep the constants, helpers, and `submit_book_inquiry` endpoint. Replace only `get_context` with:

```python
def get_context(context):
    frappe.local.flags.redirect_location = "/contact?intent=quick"
    raise frappe.Redirect
```

This preserves `locally_twisted.www.book.submit_book_inquiry` for the shared form while removing `/book` as a rendered public page.

- [ ] **Step 3: Update smoke form defaults**

In `scripts/verify/smoke_forms.py`, replace:

```python
parser.add_argument("--form-path", action="append", default=None,
                    help="path to a form to smoke (repeatable). Default: /book + /contact")
```

with:

```python
parser.add_argument("--form-path", action="append", default=None,
                    help="path to a form to smoke (repeatable). Default: /contact")
```

Replace:

```python
# Both /book and /contact render the same shared inquiry form (per GL
# directive 2026-04-30 — one form, two URL surfaces). Smoke both by
# default so a partial-include regression on either page fails the
# deploy. Override with one or more --form-path flags.
form_paths = args.form_path or ["/book", "/contact"]
```

with:

```python
# /contact is the canonical inquiry form. /book redirects to
# /contact?intent=quick and is not a separate form surface.
form_paths = args.form_path or ["/contact"]
```

- [ ] **Step 4: Verify `/book` redirects**

Run:

```bash
python scripts/dev/clear_website_cache.py --restart
$response = Invoke-WebRequest -Uri 'http://localhost:8081/book' -UseBasicParsing -MaximumRedirection 0 -ErrorAction SilentlyContinue
$response.StatusCode
$response.Headers.Location
```

Expected result: a redirect status such as `301` or `302`, with `Location` containing `/contact?intent=quick`.

- [ ] **Step 5: Commit redirect and smoke update**

Run:

```bash
git add apps/locally_twisted/locally_twisted/hooks.py apps/locally_twisted/locally_twisted/www/book.py scripts/verify/smoke_forms.py
git commit -m "feat: route book traffic to guided contact"
```

## Task 5: Final Verification

**Files:**
- No new code files required.

- [ ] **Step 1: Run route checks**

Run:

```bash
$routes = @('/contact','/contact?service=btfp','/contact?service=twisting','/contact?service=face-painting','/balloon-twisting-and-face-painting')
foreach ($r in $routes) {
  $res = Invoke-WebRequest -Uri "http://localhost:8081$r" -UseBasicParsing
  "$r $($res.StatusCode)"
}
```

Expected result: every listed route prints `200`.

- [ ] **Step 2: Run prefill verifier**

Run:

```bash
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
```

Expected result: `[PREFILL] PASS`.

- [ ] **Step 3: Run form smoke test**

Run:

```bash
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
```

Expected result: form smoke passes. If `LT_ADMIN_PASSWORD` is not set, backend verification may be skipped by the script, but the visible success UI must pass.

- [ ] **Step 4: Capture screenshots**

Run:

```bash
python scripts/verify/playwright_route_screenshot.py --base-url http://localhost:8081 --paths "/balloon-twisting-and-face-painting,/contact?service=btfp" --out-dir scripts/verify/_screenshots/btfp-contact-consolidation
```

Expected result: desktop and mobile screenshots saved under `scripts/verify/_screenshots/btfp-contact-consolidation`.

- [ ] **Step 5: Inspect screenshots**

Open the generated screenshots and verify:

- BTFP page has no embedded form.
- BTFP page has a clear CTA to start inquiry.
- BTFP service card text is not placeholder text.
- Contact page shows the shared form.
- On `/contact?service=btfp`, Balloon Twisting and Face Painting are checked and their detail sections are visible.
- No obvious mobile overlap or horizontal overflow is visible.

- [ ] **Step 6: Commit final verification notes if docs are updated**

Only if a project status or handoff doc is intentionally updated, run:

```bash
git add CODING-HANDOFF.md locally-twisted-decisions.md PROJECT-STATUS.md
git commit -m "docs: record btfp contact consolidation"
```

Do not commit unrelated existing doc changes unless they are verified and intentionally part of this slice.
