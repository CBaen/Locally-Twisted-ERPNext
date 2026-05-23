# Frappe Cloud, Cloudflare, And Stripe Launch Gate

Last updated: 2026-05-16 by Codex.

## Scope

This workstream turns the public launch plan into an executable gate and now
records the post-cutover live state.

Project-root operator runbook: `LT-LAUNCH-RUNBOOK.md`.
Project capability: `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`.

Current launch posture:

- Public pages and inquiry forms are live on `https://locallytwisted.com`.
- The 2026-05-22/23 owner-review staging push failed as a release process and
  is frozen. Do not resume provider/bootstrap mutation from that session. Use
  `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
  and `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
  before future staging/live execution.
- The Frappe Cloud app release and site migration both succeeded.
- `/contact` and `/balloon-twisting-and-face-painting` passed live backend
  smokes after cutover.
- The strict live repeat-email/five-photo verifier passed with customer and
  business Email Queue body/recipient proof and cleanup.
- The 2026-05-14 connection audit proved public Frappe Cloud route health and
  Cloudflare dynamic-route health. It did not prove direct Frappe Cloud
  dashboard/API control from Codex.
- The 2026-05-15 inquiry-photo hotfix and inquiry spam/filter source are live
  as of the 2026-05-16 Frappe Cloud site update. The accepted real smoke proved
  CRM photo rows and owner-only Email Queue attachment refs.
- The 2026-05-19 domain/provider audit confirmed Cloudflare authoritative DNS
  and Frappe Cloud public serving, but found SEO discovery drift: live sitemap
  and canonical metadata still advertise `locallytwisted.v.frappe.cloud`.
  Reindex work is blocked until the source fix is released and the live SEO
  contract passes.
- Staging is separate from live. The 2026-05-16 staging `/#login` failure was
  Website Settings drift on staging, not a live production outage.
- Live Stripe checkout remains closed until the separate product/payment gates
  pass.

This file does not authorize live checkout by itself. The controller still owns
the final go/no-go evidence for payments and ecommerce exposure.

## Current Public Site Release State

| Item | Value |
|---|---|
| Full repo source commit | `631f9a8 Run contact intake schema sync on install` |
| Frappe app mirror commit | `b4b3bf8 Run contact intake schema sync on install` |
| Previous live app hash | `04de8212aa7dbf4895716717865fc6e1029c757b` |
| Current site update/migrate job | `b48j584nua`, `Success`; update job `b48oge6unq`, `Success` |
| Source bench | `bench-39776-000013-f94-virginia` |
| Destination bench | `bench-39776-000015-f94v` |
| Live cache clear | `26es8svcaq`, `Success` |
| Site state after update | Active on `bench-39776-000015-f94v`, no update available |
| Production domain | `https://locallytwisted.com` |
| Frappe Cloud host used for authenticated checks | `https://locallytwisted.v.frappe.cloud` |

## Tracks

| Track | Current state | Gate |
|---|---|---|
| Source/Frappe Cloud | Source and app mirror are live at `631f9a8` / `b4b3bf8`; site update `b48j584nua` and update job `b48oge6unq` succeeded | For future releases: `python scripts/verify/frappe_cloud_preflight.py`; compare previous live app hash to target mirror commit; Frappe Cloud bench deploy and site update/migrate must both be successful |
| Public site/forms | Live smoke on 2026-05-16 proved Lead `CRM-LEAD-2026-00013`, five private Files, five CRM photo rows, owner Email Queue `683s86r04b` with five attachment refs, and customer Email Queue `683suhfaa9` with zero photo attachments | `smoke_forms.py` for each route plus `book_form_repeat_email_photos.py` against live with authenticated backend CDP after future form changes |
| Hidden commerce | Website launch does not approve checkout | `python scripts/verify/ecommerce_pause_contract.py` before relying on a paused/no-purchase posture |
| Cloudflare | Domain now routes to Frappe Cloud for pages/forms; rerun dynamic-route gate after any DNS/cache/security change | `python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com` |
| SEO/reindex | Source guard added for sitemap/canonical public-domain drift, but live still advertises the Frappe Cloud vanity host until a Frappe Cloud release lands | `$env:LT_BASE_URL='https://locallytwisted.com'; npm run test:seo-contract` |
| Stripe | Live checkout remains blocked | `python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com` plus one intentional low-risk real payment test |
| Backend proof before opening checkout | Still required before any checkout scope opens | `business_automation_index.py`, `synthetic_business_pipeline.py`, `payment_backend_config_contract.py`, `payment_webhook_contract.py`, `stripe_amount_parity_contract.py` |

## 2026-05-14 Connection Audit

This audit was read-only for Frappe Cloud and Cloudflare. It proves public
serving and route behavior, not dashboard/API session control.

Results:

- `https://locallytwisted.com` returned HTTP 200 with `Server: Frappe Cloud`.
- `https://locallytwisted.com/api/method/frappe.ping` returned HTTP 200 with
  `{"message":"pong"}`.
- `python scripts/verify/cloudflare_launch_readiness.py --base-url
  https://locallytwisted.com` passed 10 checks with 0 blockers and 0 warnings.
  `/cart` and `/checkout` route to the paused ready-to-order page, and the
  Stripe webhook path reaches Frappe without a Cloudflare challenge or cache
  hit.
- `python scripts/verify/frappe_cloud_preflight.py` passed after
  `dns_current_target` was corrected to recognize `www.locallytwisted.com`
  targeting `locallytwisted.v.frappe.cloud`.
- The local `locally-twisted-erpnext-v15` Docker stack was running; the DB
  container was healthy and frontend was bound to `localhost:8081`.
- Host-level management tooling remains limited: no direct Frappe Cloud CLI,
  host `bench`, or Frappe Cloud environment variables were found. The preflight
  proves GitHub mirror, SSH key, app package, branch, and DNS shape; it is not
  dashboard login proof.

Operational rule for future agents: say which surface you verified. Public
route health, Cloudflare route health, local Docker health, SSH key readiness,
and Frappe Cloud dashboard/API control are different claims.

## 2026-05-16 Inquiry Form Live Release

The inquiry-photo hotfix, inquiry spam/filter hardening, and source-owned
contact intake schema sync are live. Release handoff:
`workstreams/inquiry-form-live-release-2026-05-16.md`.

Live smoke receipt:

- Lead `CRM-LEAD-2026-00013`.
- Contact name `smoke test from cameron`.
- Owner subject `New website inquiry from smoke test from cameron`.
- Owner Email Queue `683s86r04b`, status `Sent`, recipient
  `locallytwisted@gmail.com`, attachment refs `5`.
- Customer Email Queue `683suhfaa9`, status `Sent`, attachment refs `0`.
- Five private Lead Files and five `custom_inspiration_photos` rows.

Scope warning: this release did not mix current dirty working-tree files, but
the app mirror release contained already-committed changes beyond the final
two-file source commit. Future Frappe Cloud release review must compare the
previous live app hash to the target app mirror commit. Do not judge release
scope only from `git show HEAD`.

Staging warning: `https://locallytwisted-staging.frappe.cloud/#login` showing
Sign In was staging Website Settings drift, not live production breakage.
Staging was repaired by setting `home_page=home`, LT branding fields, Standard
theme, and clearing cache with job `fb85o6ncdh`.

## Production Config Contract

Set these explicitly in the Frappe Cloud site config before live checkout:

- `host_name`
- `lt_stripe_settings_name`
- `lt_payment_gateway_account`
- `lt_stripe_payment_method_configuration`
- `lt_operator_email`
- `stripe_webhook_signing_secret`

`payment_launch_readiness.py --mode live` fails if `host_name` is missing,
local-only, or not HTTPS.

Stripe webhook endpoint:

```text
/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

Use the full production URL in Stripe Dashboard after checkout is intentionally
opened:

```text
https://locallytwisted.com/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

## Cloudflare Dynamic Route Contract

Cloudflare must not cache or challenge these dynamic paths:

- `/login`
- `/me`
- `/contact`
- `/cart`
- `/checkout`
- `/payment-success`
- `/thank-you`
- `/api/method/frappe.ping`
- `/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook`

`scripts/verify/cloudflare_launch_readiness.py` checks those paths through
public HTTP and fails on missing `404` routes, Cloudflare challenge markers, or
`cf-cache-status` values that show Cloudflare considered a dynamic route
cacheable. Only absent cache headers, `BYPASS`, and `DYNAMIC` pass. `MISS` is a
blocker because it can become `HIT` on the next request after purge or a
Cache-Everything-style rule.

Fast local contract:

```powershell
python scripts/verify/cloudflare_launch_readiness_contract.py
```

## Frappe Cloud Release Rules

- A bench deploy hash is not live proof. The site update/migrate job must
  succeed too.
- Source-owned schema must exist in the app, not only in the local database.
  The live migration must create the Lead fields and custom DocTypes used by
  public forms.
- Optional legacy fields must be guarded before querying them. The final live
  fix skipped `_rewrite_existing_lead_service_csv()` when `Lead.custom_services`
  is absent.
- Default blank `System Settings.language` and `time_zone` on a fresh Frappe
  Cloud site must be filled before saving `System Settings`.
- After deploy/migrate, run live route/API proofs, not only dashboard checks.
- Compare the previous live app hash to the target app mirror commit before
  promotion. A clean final commit does not prove the full deployed diff is
  narrow.
- Staging `Website Settings.home_page`, app branding, favicon, and theme are
  release-critical config. A staging root that shows login while `/home` works
  is config drift, not proof that live is down.

## Live Verification Receipt

Passed on 2026-05-12 after final deploy and site update:

```powershell
$env:LT_BACKEND_BASE_URL='https://locallytwisted.v.frappe.cloud'
$env:LT_BACKEND_CDP_URL='http://127.0.0.1:9222'
python scripts\verify\book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
python scripts\verify\smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter
python scripts\verify\smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter
```

Strict verifier summary:

```text
BOOK FORM REPEAT EMAIL + 5 PHOTO CHECK PASSED
email_delivery_verified: True
records_kept: False
```

The strict verifier used repeat same-email public submissions with five photos
each, verified customer queues and business queues, verified submitted-detail
email body content, and cleaned verifier-owned ERPNext records. A final cleanup
preview returned zero verifier-owned records across Lead, File, Email Queue,
Communication, Contact, Task, ToDo, Event, and Comment.

Passed on 2026-05-16 after site update `b48j584nua` / update job
`b48oge6unq`:

- `/`, `/#login`, `/contact`, and `/login` returned expected public surfaces.
- Live real smoke `smoke test from cameron` created Lead
  `CRM-LEAD-2026-00013`.
- The Lead had five private Files and five `custom_inspiration_photos` rows.
- Owner Email Queue `683s86r04b` was `Sent` to `locallytwisted@gmail.com`
  with five attachment refs.
- Customer Email Queue `683suhfaa9` was `Sent` with zero photo attachments.

## Current Blockers / Deferrals

- Live Stripe checkout is blocked until live config, policy URLs, webhook, and
  one real low-risk payment test pass.
- Public ecommerce/product checkout remains separate from the pages/forms
  launch and needs its own product/payment/customer-email proof.
- Any future DNS, Cloudflare cache/security, or Frappe Cloud release change
  needs the relevant live route/API/form gates rerun.
- Search Console reindex work is blocked until live sitemap and canonical
  output use `https://locallytwisted.com` instead of the Frappe Cloud vanity
  host.
