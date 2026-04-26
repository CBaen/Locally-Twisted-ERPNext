# HANDOFF — Locally Twisted (First Professional Business Platform)

**Last updated:** 2026-04-26 (Opus 4.7, post-reframe + Phase 1 Slice 1 done — no name chosen)

Overwrite-not-append. ~40 lines. Git is the changelog.

## Live state

**ERPNext v15.105.0 running:** http://localhost:8081 — compose project `locally-twisted-erpnext-v15`. Setup wizard complete. Logins per `CLAUDE.md`.

**Frame:** project is "first professional business platform for LT, built on ERPNext" — not a migration. Jeff Kimber doesn't know about the prior failed Odoo attempt; no artifact on disk should leak that. See `CLAUDE.md` "What this project actually is" + "Reference Disposition" sections.

**Phase 1 Slice 1 (brand foundation) DONE.** LT theme CSS installed via `Website Settings.head_html`. Source-of-truth at `_resources/lt-theme.css`. Verified in served HTML — open `http://localhost:8081/` view-source and look for `<!-- LT Theme: source-of-truth at _resources/lt-theme.css -->`.

**All Phase 1 decision gates resolved:** header nav (Option B — single What-We-Make + occasion landing pages), accessibility (Option B — brief intent-only + actually meet WCAG 2.1 AA, draft text in `.planning/decisions/accessibility-statement.md`), blog (yes — framework + live posts), photography (15 placeholder images in `_resources/images/`), customer-inquiry email (`locallytwisted@gmail.com`), pricing calculator (embedded in BTFP service page, not standalone).

**ERPNext user records:** renamed `locallytwisted@gmail.com` to "Jeff Kimber" (was mis-labeled "Jeff Baen" — Baen is Cameron's middle name that got tangled); disabled (not deleted) `locallytwisted@yahoo.com` placeholder.

## What's already built and carries forward

- **Lead schema** — 45+ Custom Fields, plain-language relabels, hidden "Additional Information" tab, 25 MB upload. Built via `scripts/translate/translate_crm_lead.py` + 4 fix scripts. Feeds Phase 2 (Lead Intake).
- **`Dashboard Reviewed Item` DocType** — built via `scripts/translate/translate_dashboard_review.py`. No current Phase depends on it.
- **nginx Origin pass-through patch** — survives until container recreation; persistence via compose override is P2 backlog.
- **Resources** — `_resources/STYLE-GUIDE.md` (design system), `_resources/policies/` (6 business policy files), `_resources/utah-tax-rates-2026q2.md` (tax research), `_resources/images/` (15 placeholder PNGs).

## Hot direction (load-bearing for next session)

1. **Auto mode.** GL wants forward motion without unnecessary check-ins. Take the lead on technical work; flag dependencies GL didn't think to ask about; apply obvious companion features and report what + why.
2. **Phase 1 is the customer-facing proof.** Phase 1 plan in `.planning/phases/01-customer-site-and-storefront/PLAN.md` — 9 slices (10 was merged into Slice 4). Slice 1 done. Next up: Slice 2 (header + footer).
3. **Verify in UI before claiming done.** Use `python C:/Users/baenb/.claude/scripts/screenshot.py` (primary monitor) — the browser may be on a separate monitor.
4. **Voice & Language:** "Quiet Confidence" on every visible string. Blog uses "Kindergarten Teacher" voice. See `_resources/STYLE-GUIDE.md`.
5. **Reference Disposition:** Odoo dir + Hetzner site + GitHub Odoo repo all retire post-cutover. Don't reach into the Odoo dir for new content; canonical resources are in `_resources/`.

## Known issues to flag

- **Inspiration Photos Table field missing** on Lead — `LT Lead Photo` child DocType exists and `lt_section_photos` Section Break exists, but the Table field connecting them was never created (iter 4 step F failed silently). Empty section heading on the Lead form. Ties to the deferred photo UX decision (a / b / c).
- **GL's "this is one Lead!" realization** — was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction.

## Not in flight

No spawned processes. Docker daemon runs LT compose stack detached. No background agents.

## Reading order on arrival

See `CLAUDE.md` reading order section.
