# Frappe Cloud, Cloudflare, And Stripe Launch Gate

Last updated: 2026-05-15 by Codex.

## Scope

This workstream turns the public launch plan into an executable gate and now
records the post-cutover live state.

Project-root operator runbook: `LT-LAUNCH-RUNBOOK.md`.
Project capability: `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`.

Current launch posture:

- Public pages and inquiry forms are live on `https://locallytwisted.com`.
- The Frappe Cloud app release and site migration both succeeded.
- `/contact` and `/balloon-twisting-and-face-painting` passed live backend
  smokes after cutover.
- The strict live repeat-email/five-photo verifier passed with customer and
  business Email Queue body/recipient proof and cleanup.
- The 2026-05-14 connection audit proved public Frappe Cloud route health and
  Cloudflare dynamic-route health. It did not prove direct Frappe Cloud
  dashboard/API control from Codex.
- The 2026-05-15 inquiry-photo hotfix is pushed to the full repo and Frappe
  Cloud app mirror, but production is not protected until Frappe Cloud deploy,
  site update/migrate, and live photo-delivery verifier proof pass.
- Live Stripe checkout remains closed until the separate product/payment gates
  pass.

This file does not authorize live checkout by itself. The controller still owns
the final go/no-go evidence for payments and ecommerce exposure.

## Final Public Site Release State

| Item | Value |
|---|---|
| Frappe Cloud custom app release | `72a4se4v64` |
| App hash | `04de8212aa7dbf4895716717865fc6e1029c757b` |
| Bench deploy | `62q1r0otg1`, `Success` |
| Site update/migrate job | `15s16992i2`, `Success` |
| Running deploy pipeline | `false` |
| Production domain | `https://locallytwisted.com` |
| Admin/staging host used for authenticated checks | `https://locallytwisted.v.frappe.cloud` |

## Tracks

| Track | Current state | Gate |
|---|---|---|
| Source/Frappe Cloud | Source and mirror were pushed; final verified live app hash remains `04de8212aa7dbf4895716717865fc6e1029c757b`; new inquiry-photo source is pushed as full repo `4422793` and app mirror `6a06062` but not live-verified | `python scripts/verify/frappe_cloud_preflight.py`; Frappe Cloud bench deploy and site update/migrate must both be successful |
| Public site/forms | Live `/contact` and BTFP smokes passed on the prior release, but the 2026-05-15 photo-storage/owner-attachment hotfix still needs live proof | `smoke_forms.py` for each route plus `book_form_repeat_email_photos.py` against live with authenticated backend CDP, proving CRM photo rows and owner Email Queue attachment refs |
| Hidden commerce | Website launch does not approve checkout | `python scripts/verify/ecommerce_pause_contract.py` before relying on a paused/no-purchase posture |
| Cloudflare | Domain now routes to Frappe Cloud for pages/forms; rerun dynamic-route gate after any DNS/cache/security change | `python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com` |
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

## 2026-05-15 Inquiry Photo Hotfix Deploy Boundary

Source and mirror pushes are complete:

- full ERPNext repo: `4422793 Fix inquiry photo storage and owner attachments`
- Frappe Cloud app mirror: `6a06062 Fix inquiry photo storage and owner
  attachments`

This is not live proof. The next launch pass must deploy the app mirror commit,
confirm bench deploy and site update/migrate success, then run:

```powershell
python scripts\verify\book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222
```

The verifier must prove private Lead Files, `custom_inspiration_photos` rows,
customer queues with no attachments, owner queues with `fid` attachment refs,
and cleanup. Route health and `frappe_cloud_preflight.py` are not enough.

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

## Current Blockers / Deferrals

- Live Stripe checkout is blocked until live config, policy URLs, webhook, and
  one real low-risk payment test pass.
- Public ecommerce/product checkout remains separate from the pages/forms
  launch and needs its own product/payment/customer-email proof.
- Any future DNS, Cloudflare cache/security, or Frappe Cloud release change
  needs the relevant live route/API/form gates rerun.
- Inquiry-photo owner delivery remains pending until app mirror commit
  `6a06062` is deployed, migrated, and live-verified.
