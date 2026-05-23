# Frappe Cloud Release Learning Ledger - 2026-05-23

Status: **required-read learning ledger, not release approval**.

This file records the good, bad, and important lessons from the May 23 Frappe
Cloud staging failure review. It exists so future agents do not have to infer
the lesson from scattered packet notes.

Current local source at creation: `d7b00453b327669607f9ae7944e9ede27ddaac42`.
Current mode: forensic-freeze, local/offline only. Provider mutation is not
allowed without a fresh approval artifact.

## Good

- The repo now has a release lock, release controller, identity proof helper,
  status reporter, approval helper, failure ledger helper, app mirror sync plan
  helper, packet prep helper, and release-prevention test suite.
- `npm run test:release-prevention` passes as local prevention proof. This is
  useful infrastructure, but it is not staging proof.
- `python scripts\release\release_status_report.py` gives a plain result. At
  this source it correctly reports `NO-GO` because no fresh mutation-capable
  packet exists.
- Guiding Light's two-account model is now documented as expected:
  `cameronbpaul@gmail.com` and `locallytwisted@gmail.com`. This is not a
  personal failure and must not be treated as suspicious by default.
- Official Frappe Cloud docs refreshed on 2026-05-23 support the guard shape:
  private benches control custom apps/updates, bench deploys are separate from
  source commits, app/site updates have their own deploy/update flow, custom
  app GitHub permissions can block fetching updates, and arbitrary SSH bench
  commands are risky outside debugging.

## Bad

- Staging is still **NO-GO** for owner review.
- The latest staging-reality packet remains
  `workstreams/release-artifacts/2026-05-23-staging-reopen-a5ed680-readonly/`.
  It is source-bound archive evidence, not current-source mutation authority.
- Docs-only commits moved repo `HEAD` after that packet. That is fine, but it
  makes "current-source packet" wording dangerous unless the text clearly says
  the packet is historical staging evidence.
- The app-root mirror/deployed staging app was still at stale hash
  `181076c239b2d1d3d508a41ac471c71f9d2b5158` in the latest read-only packet.
- Hosted preflight still returned HTTP `417` in the latest read-only packet.
- Owner-review proof was missing: zero catalog/Product Setup/gallery rows,
  required owner/marketing users missing, and representative product/category
  routes returned `404`.
- Repeated read-only no-go packets can become noise if they only chase docs-only
  commits. Fresh packets are for changed release input state, explicit reopen
  approval, or a real mutation-capable attempt.

## Important Rules

- Do not use any archived packet as release authority after `HEAD` moves.
- Do not turn GL's dual-account workflow into an account-mismatch blocker by
  itself. The identity proof documents account context; it does not require
  Codex, GitHub, Frappe Cloud, and owner/reviewer email to all match.
- Do not treat local tests, GitHub commits, app mirror hashes, deploy IDs,
  HTTP 200 shells, or `/shop` visibility as owner-review readiness.
- Do not call Frappe Cloud, sync the app mirror, deploy/update, bootstrap,
  migrate, clear cache, touch live/DNS/Stripe/Search Console, unpause checkout,
  or create users while forensic-freeze is active.
- Do not use SSH or bench commands on Frappe Cloud as a shortcut for normal
  release flow. Official docs describe SSH as debugging-only and warn arbitrary
  bench commands can break the managed bench flow.
- Always refresh official Frappe Cloud docs before release execution. The
  current doc set checked on 2026-05-23:
  - `https://docs.frappe.io/cloud/benches`
  - `https://docs.frappe.io/cloud/what-are-benches-and-bench-groups`
  - `https://docs.frappe.io/cloud/benches/updating_a_bench`
  - `https://docs.frappe.io/cloud/sites/how-to-update-an-app-site-on-a-private-bench`
  - `https://docs.frappe.io/cloud/faq/custom_apps`
  - `https://docs.frappe.io/cloud/benches/debugging`

## What GL Needs To Provide

Nothing is needed from GL for local documentation/guard work.

Later, only when GL wants to reopen staging execution, the process needs:

- fresh explicit approval for the exact staging-only action;
- Frappe Cloud/GitHub account session availability or MFA if required;
- confirmation of the intended account/team/site context if the safe surfaces
  are ambiguous.

Until then, the next safe action remains local guard/documentation work or
read-only forensics.
