# HANDOFF — Locally Twisted (First Professional Business Platform)

**Last updated:** 2026-04-26 (Opus 4.7, post-reframe session)

Overwrite-not-append. ~40 lines. Git is the changelog.

## Live state

**ERPNext v15.105.0 running:** http://localhost:8081 — compose project `locally-twisted-erpnext-v15`. Setup wizard complete. Logins per `CLAUDE.md`.

**Frame reset 2026-04-26:** project is no longer "Odoo → ERPNext migration." It is "first professional business platform for LT, built on ERPNext." Jeff Kimber doesn't know about the failed Odoo attempt that preceded this build; no artifact on disk should leak that. See `CLAUDE.md` "What this project actually is" + "Reference Disposition" sections.

**Phase 1 is the new active phase: customer site + storefront** (the proof point — if ERPNext can't deliver this, GL pivots). PROJECT.md and ROADMAP.md have been promoted to the v2 frame. Old 10-phase translation-centric ROADMAP lives in git history.

## What's already built (carries forward into the new ROADMAP)

- **Lead schema** — 45+ Custom Fields on `Lead` with sectioned layout, plain-language relabels of standard fields, "Additional Information" tab hidden, file upload to 25 MB. Built across `scripts/translate/translate_crm_lead.py` + 4 fix scripts. Feeds Phase 2 (Lead Intake).
- **Dashboard Reviewed Item DocType** — built via `scripts/translate/translate_dashboard_review.py`. Quiet placeholder; no Phase yet depends on it.
- **nginx Origin pass-through patch** — applied via `scripts/fix/patch_nginx_socketio_origin.py`. Survives until container recreation; persistent via docker-compose override is a P2 backlog item.
- **Setup wizard finalization** — Cameron + Jeff Kimber (currently mis-labeled as "Jeff Baen" in ERPNext, queued to fix), Address, Company contact details all populated.

## Hot direction (load-bearing for next session)

1. **Auto mode is active.** GL wants forward motion without unnecessary check-ins. Take the lead on technical work; flag dependencies GL didn't think to ask about; apply obvious companion features and report what + why.
2. **Phase 1 is the customer-facing proof.** First slice in `.planning/phases/01-customer-site-and-storefront/PLAN.md` is the brand-token install. Each subsequent slice ends in something visible.
3. **Verify in UI before claiming done.** Use `python C:/Users/baenb/.claude/scripts/screenshot.py` (primary monitor only). Browser is on a separate monitor.
4. **Voice & Language:** plain language, no business jargon. See `CLAUDE.md` and `_resources/STYLE-GUIDE.md` voice section ("Quiet Confidence").
5. **Reference Disposition.** Odoo dir + Hetzner deployment + GitHub Odoo repo all retire post-cutover. Canonical resources live in `_resources/`.

## Decision gates that need GL input before Phase 1 deep work

1. **Header navigation:** consolidated "What We Make" + occasion landing pages (Claude's recommendation) vs. three competing super-menus. See `.planning/decisions/header-navigation.md`.
2. **Accessibility statement:** brief intent-only with working contact (Claude's recommendation) vs. detailed AA conformance claim vs. skip. See `.planning/decisions/accessibility-statement.md`.
3. **Blog presence in Phase 1:** ship framework + one seed post / framework only / defer.
4. **Real photography sourcing:** where do good LT event photos live, or do we ship Phase 1 with placeholders?
5. **Customer-inquiry email destination:** where do current contact-form submissions land?
6. **Pricing calculator:** in Phase 1 or deferred?

## ERPNext user cleanup pending

- Rename `locallytwisted@gmail.com` user record's full_name from "Jeff Baen" to "Jeff Kimber" — explicit GL approval given
- Disable (or delete) `locallytwisted@yahoo.com` placeholder user — explicit GL confirmation it shouldn't exist
  *(Auto-mode safer move: disable instead of delete, since deletion is destructive on the running ERPNext.)*

## Not in flight

No spawned processes. Docker daemon runs LT compose stack detached. No background agents.

## Reading order on arrival

See `CLAUDE.md` reading order section.
