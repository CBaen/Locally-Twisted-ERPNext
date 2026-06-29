# Meta Ad Foundation Readiness - 2026-06-29

Purpose: preserve the exact state before Locally Twisted pays for the first
Meta ad test for the Large head Missionary product.

## Scope

- Brand lane: Locally Twisted only.
- Product focus: `large-head-missionary`.
- Public ad route: `/missionary-balloon-gift`.
- Approved spend discussed by GL: `$20/day total`, intended as `$10/day` per ad,
  but Birthday Deliveries is deferred until the missionary test is reviewed.
- No Meta campaign, ad set, ad, budget, billing, Page post, lead form, customer
  message, custom conversion, DNS, Stripe, live customer record, or Frappe Cloud
  mutation was approved in this packet.

## Verified Today

- Capability gate: PASS.
- Triad used three real subagents:
  - Lens A security/customer intake.
  - Lens B deployment/access.
  - Lens C paid ads/tracking.
- Local Kubuntu runtime:
  - `client-stack start lt` started the LT local workshop.
  - `python scripts/verify/kubuntu_doctor.py` passed; only warning was the
    existing uncommitted shared worktree.
- Live read-only route checks passed for `/`, `/contact`,
  `/shop-items/bouquets/large-head-missionary`, `/missionary-balloon-gift`,
  `/cart`, `/checkout`, `/api/method/frappe.ping`, and `/sitemap.xml`.
- Live SEO contract passed 13/13.
- Live `/missionary-balloon-gift` exists and has strong mission calling,
  SLC airport return, homecoming, open house, and farewell party positioning.
- Live product page visible copy already matches that positioning.
- Source product seed copy for `WEB-ITM-0039` is correct on `origin/main`
  after commit `e3aefcd`.
- Consent-gated Meta Pixel PageView loader proof passed for Pixel
  `1079085392230103`; `fbq`/Meta script loaded only after optional consent.
- Meta read-only inventory passed and did not print tokens or read customer
  messages/leads. Page-token lanes remain separate.
- Local backend contracts passed:
  - `python scripts/verify/customer_email_policy_contract.py`
  - `python scripts/verify/inquiry_upload_failure_contract.py`
  - `python scripts/verify/public_access_guard_contract.py`
  - `python scripts/verify/payment_backend_config_contract.py`
  - `python scripts/verify/payment_webhook_contract.py`
  - `python scripts/verify/stripe_amount_parity_contract.py`
  - `python scripts/verify/cart_checkout_contract.py`
  - `python scripts/verify/checkout_lead_conversion_contract.py`
  - `python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081`
- The repeat-email/five-photo local smoke verified customer and business Email
  Queue rows and cleaned 32 verifier-owned local records.

## Source Repairs Completed

Source repo `origin/main`:

- Commit `6165015 Harden inquiry logging before Meta ad test` pushed to
  `https://github.com/CBaen/Locally-Twisted-ERPNext.git`.
- Files:
  - `apps/locally_twisted/locally_twisted/www/book.py`
  - `scripts/verify/inquiry_logging_privacy_contract.py`
  - `scripts/verify/meta_bouquet_ad_landing_pages.py`
- Change:
  - Lead-creation failure logging no longer serializes raw
    `frappe.form_dict`, form URL, or remote IP into Error Log.
  - Replacement helper records safe context only: request path, field names,
    required-field presence, allowlisted selected options, item code, product
    quote presence, and upload count.
  - Added static privacy verifier.
  - Fixed the missionary ad landing-page verifier so `--help` prints usage.
- Verification from clean publish worktree:
  - `python -m py_compile apps/locally_twisted/locally_twisted/www/book.py scripts/verify/inquiry_logging_privacy_contract.py scripts/verify/meta_bouquet_ad_landing_pages.py`
  - `python scripts/verify/inquiry_logging_privacy_contract.py`
  - `python scripts/verify/meta_bouquet_ad_landing_pages.py`
  - `python scripts/verify/marketing_measurement_bridge_contract.py`
  - `python scripts/verify/verifier_cli_contract.py` passed 145 scripts.

Frappe app mirror:

- Current remote tracked branch:
  - repo: `https://github.com/CBaen/Locally-Twisted-Frappe-App.git`
  - branch: `live-shop-discovery-20260529`
  - remote/live hash before repair: `a23fb4083475992935c00faae700d30078c3990b`
  - Frappe Cloud installed app hash also reported `a23fb4083475992935c00faae700d30078c3990b`.
- Local app-mirror release candidate:
  - worktree:
    `/home/guidingl/agent-worktrees/builtbycameron-lt/codex-20260623-lt-stripe-promo-live-tracking-branch`
  - commit: `526e711 Harden inquiry logging before Meta ad test press-deploy-bench-40102`
  - status: local only, ahead 1, not pushed, not deployed.
  - file: `locally_twisted/www/book.py`.
  - verification: `python -m py_compile locally_twisted/www/book.py`.

## Still Blocked Before Spend

- Live Frappe does not have the inquiry logging privacy fix until the app
  mirror commit is pushed and Frappe Cloud updates the site.
- Live `/contact` write smoke has not been run today. It requires explicit GL
  approval because it creates temporary live Lead and Email Queue records, then
  verifies and cleans them.
- Ads Manager billing/UI state and Events Manager PageView proof are not
  approved/proven. API read access and local Pixel proof are not the same as
  final spend readiness.
- Custom conversions remain zero; the first test can only be judged on small
  learning metrics such as landing page views, CTR, CPC, and manual inquiry or
  order notes unless GL approves additional measurement work.
- Page Access Token is still required for Page post, native lead-form,
  comment/message, and Page/IG engagement lanes.
- The main LT checkout is locally proven but live payment/checkout smoke was
  not run today. If the ad CTA emphasizes buying now, run approved live
  checkout/payment proof first. If the first ad CTA is contact/landing-page
  learning only, checkout proof can be an approved deferral.
- Main checkout remains dirty/behind locally. Do not release from the shared
  main checkout. Use the clean publish/app-mirror paths and compare source,
  app mirror, and Frappe Cloud installed hashes.

## Required Approval To Finish Foundation

Ask GL for one explicit release approval with this shape:

> Approve pushing LT app mirror commit `526e711` to
> `live-shop-discovery-20260529`, running the Frappe Cloud site update for
> `locallytwisted-staging.frappe.cloud`, clearing cache if needed, then running
> public route checks and one live `/contact` fake-inquiry smoke with cleanup.

Do not combine that approval with Meta spend approval. Spend approval comes
after the live release and live inquiry smoke pass.

## Next Safe Step

If GL approves the release step, push the app mirror candidate, run the Frappe
Cloud update through the existing API recipe, verify the installed app hash
changes from `a23fb408` to the target app commit, then run the live smoke and
read-only route/Pixel checks. If GL does not approve, keep the campaign/ad work
in draft planning only.
