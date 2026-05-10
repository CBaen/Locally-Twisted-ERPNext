# Aion/Axion Dirty Worktree Sweep — 2026-05-09

Superseded status note, 2026-05-10: GL later reopened public ecommerce for
full local testing. Keep the paused-commerce notes below as historical sweep
evidence only; current ecommerce proof belongs in `workstreams/shop.md`,
`workstreams/website-launch.md`, and `npm run test:ecommerce-full`.

## Purpose
Classify the large dirty Locally Twisted worktree after Aion/Axion-era edits, protect verified launch-critical work, and separate safe keeps from suspect/parking-lot material.

## Current verified state

- [VERIFIED] `/` and `/home` return 200 with the Locally Twisted homepage.
- [VERIFIED] `/event-balloons`, `/corporate-events`, `/schools-campuses`, `/civic-community`, `/private-celebrations`, `/contact`, `/portfolio`, and `/faq` return 200 with no `Traceback`, `Internal Server Error`, or `Not Found` markers.
- [VERIFIED] `/shop`, `/cart`, and `/checkout` redirect to `/ready-to-order-paused?from=...` for guest traffic and render the branded pause page.
- [LOCAL-PROOF] Focused Playwright launch surface gate passed earlier this sweep: `110 passed (3.5m)` for homepage/compact hero/white-label leakage/paused ecommerce states.
- [LOCAL-PROOF] `python scripts/verify/ecommerce_pause_contract.py` passed.
- [LOCAL-PROOF] `npm run test:search-contract` passed (`2 passed`).
- [LOCAL-PROOF] `python scripts/verify/customer_contact_points_contract.py` passed after aligning the new verifier to the no-purchase launch architecture.
- [LOCAL-PROOF] `python scripts/verify/business_automation_index.py --report output/business-automation-index.json` passed.

## Keep now — launch-critical or verified support

These changes are currently part of the verified no-purchase launch posture and should not be reverted casually:

- `apps/locally_twisted/locally_twisted/ecommerce_pause.py`
- `apps/locally_twisted/locally_twisted/www/ready_to_order_paused.html`
- `apps/locally_twisted/locally_twisted/www/ready_to_order_paused.py`
- `apps/locally_twisted/locally_twisted/hooks.py` additions for:
  - `lt-photo-heroes.css`
  - `/ready-to-order-paused` route rule
  - `before_request = ["locally_twisted.ecommerce_pause.before_request"]`
- `apps/locally_twisted/locally_twisted/www/checkout.py` paused API JSON guard.
- `apps/locally_twisted/locally_twisted/www/checkout.html` handling for `ecommerce_paused` and `quote_required` payloads independent of status code.
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py` no-purchase guard updates.
- `scripts/verify/ecommerce_pause_contract.py`
- `scripts/verify/search_contract.spec.js`
- `apps/locally_twisted/locally_twisted/verify/customer_contact_points_contract.py` / `scripts/verify/customer_contact_points_contract.py` after verifier alignment.
- Homepage hero/contact edits in `www/home.html` and `www/home.py`, plus the generated hero images currently referenced by the launch surface.
- Navbar removal of public ready-to-order/cart surfaces while ecommerce is paused, and search fallback to `/contact`.

## Keep pending final review — likely useful, not launch-blocking

These look aligned with the no-purchase launch direction but should be reviewed before commit grouping:

- `apps/locally_twisted/locally_twisted/api/newsletter.py` idempotent duplicate-signup hardening.
- `scripts/verify/newsletter_concurrency_contract.py`.
- `apps/locally_twisted/locally_twisted/lead_cascade.py` useful lead-title formatting and portfolio link change.
- `apps/locally_twisted/locally_twisted/www/book.py` and form-smoke cleanup changes.
- `apps/locally_twisted/locally_twisted/templates/includes/event_type_page.html` and `www/event_type_pages.py` audience page copy/layout work — verified routes are live, but content should get human/taste review before final publish.
- `apps/locally_twisted/locally_twisted/public/css/lt-photo-heroes.css` and generated hero crops under `public/images/heroes/`.

## Inspect/park — do not commit blindly

These are research/support artifacts or Aion-era broad imports. Keep them out of the launch commit unless explicitly chosen:

- `.codex/skills/**` copied skill packs.
- Top-level raw image folders with spaces, e.g. `assets/hero assets/`, `assets/landing page assets/`, `assets/working pic/`, and logo source PNGs.
- `contests/audience-pages-2026-05-08/**` render gallery/screenshots.
- `audits/**` large research snapshots and Odoo/ERPNext migration material.
- `STAGE-1-LEGAL-OWNER-QUESTIONS.md` until legal/business-owner question flow is intentionally resumed.
- Capability registry/doc edits should be reviewed as their own commit, not bundled into launch code.

## Revert candidates / suspect until proven

No launch-critical regression is currently proven. Avoid destructive revert for now. If we need to shrink the worktree quickly, safest first cut is to leave tracked launch code alone and move/ignore untracked research/assets/skill-pack material rather than touching verified homepage/checkout/pause code.

## Notes

- The old verifier expectation that site search submits to `/shop` was stale for the current no-purchase launch. The implementation and Playwright contract now agree that search submits to `/contact` while ecommerce is paused.
- The old contact-points verifier also looked for inquiry-form JS markers inside the Jinja partial and treated the public alias as the document-copy recipient. It now checks the dedicated inquiry JS file and distinguishes public `hi@locallytwisted.com` from internal document copy `locallytwisted@gmail.com`.
