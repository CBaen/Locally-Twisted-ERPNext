---
name: Frappe Cloud staging Website Settings drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-16
last_updated: 2026-05-16
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud staging and live release review
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
related_failures:
  - frappe-cloud-release-site-migration-drift.md
  - frappe-cloud-app-mirror-release-scope-drift.md
tags:
  - locally-twisted
  - frappe-cloud
  - staging
  - website-settings
  - route-proof
  - fail-loud
---

# Failure Recipe: Frappe Cloud Staging Website Settings Drift

## Symptom

The Frappe Cloud staging root or `/#login` renders the Sign In surface even
though `/home` and `/contact` render the public site.

## Trigger Conditions

- Staging and live are managed as separate Frappe Cloud sites.
- Staging `Website Settings.home_page` is unset or reset.
- Staging app branding fields are blank/default.
- A staging URL is mistaken for live during incident response.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-16 | Locally Twisted | `https://locallytwisted-staging.frappe.cloud/#login` | GL saw Sign In and thought live was broken | Staging `/` and `/#login` rendered Sign In; staging `/home` and `/contact` rendered public pages; `Website Settings.home_page` was `null`; live host was separately healthy | staging Website Settings repair and route parity documented | guarded |

## Root Pattern

Frappe route behavior can be correct in source while site-level Website
Settings route the staging root to login/default behavior. Staging config drift
is not proof of source breakage or live outage.

## Detection Signals

- `/#login` shows Sign In but `/home` works.
- `Website Settings.home_page` is `null` or not `home`.
- `app_name`, `app_logo`, `brand_html`, or `favicon` are blank/default.
- The incident URL contains `-staging.frappe.cloud`.

## Required Guard

For staging release review, check:

1. environment name in the URL;
2. `/`, `/#login`, `/home`, and `/contact` route titles/status;
3. `Website Settings.home_page`;
4. LT app branding/logo/favicon/theme fields;
5. cache clear result after any settings repair.

## Recovery Recipe

1. Name the environment before diagnosing.
2. Verify live separately if the user says "live broken."
3. On staging, set `Website Settings.home_page = home`.
4. Restore LT app name, logo, brand HTML, favicon, and Standard theme.
5. Clear website/cache through Frappe Cloud or Frappe tools.
6. Recheck staging `/`, `/#login`, and `/contact`.

## What Not To Do

- Do not call live broken from a staging URL.
- Do not debug source templates before checking staging Website Settings.
- Do not promote staging settings repairs to live without separate live proof.
- Do not erase staging as an environment because it drifted; repair the config
  and keep staging separate.

## Cross-links

- `../../workstreams/inquiry-form-live-release-2026-05-16.md`
- `../../workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- `../../LT-LAUNCH-RUNBOOK.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`

## Evidence Quality

Verified during the 2026-05-16 staging incident. Staging was repaired by setting
`home_page=home`, LT branding/logo/favicon, Standard theme, and clearing cache
with Frappe Cloud job `fb85o6ncdh`.
