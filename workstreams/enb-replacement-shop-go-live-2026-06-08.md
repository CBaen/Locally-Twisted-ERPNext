# ENB Replacement And Shop Go-Live Workstream - 2026-06-08

## Purpose

Coordinate the immediate transition from ENB-managed marketing dependence to a
Locally Twisted / Built by Cameron-owned lead, tracking, and ecommerce launch
system.

This workstream exists because ENB asked for website access that does not fit
the current ERP-backed architecture. The work has to protect Jeff's confidence:
if we reduce or remove a vendor he believes produced leads, we need fast proof
that the replacement lead path is operational.

## Scope

In scope:

- documentation;
- source-level planning;
- local verification commands;
- conversion tracking architecture;
- controlled campaign/landing URL planning;
- Jeff/ENB communication drafts;
- explicit approval gates for shop/payment live release.

Out of scope until explicitly approved:

- staging/live/provider mutation;
- DNS or Search Console changes;
- Stripe live configuration or real charges;
- ad account budget/campaign changes;
- ENB access removal;
- customer data export/upload;
- production ERPNext data mutation;
- email sending.

## Current Stage

Stage: `access/reset closeout complete` as of 2026-06-13; marketing/ad/provider lanes remain approval-gated.

Repo: `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`

Branch: `main`

Coordination claim:
`codex-20260608-lt-enb-replacement-shop-go-live-plan`

## Controller Decision

Do not build ENB a broad editing surface. If the business later wants editable
marketing pages, that needs a controlled internal marketing-page architecture
with permissions, workflow, review, and verifiers. It should not be created as a
quick vendor access workaround.

Immediate replacement proof should focus on:

1. lead capture paths;
2. conversion tracking;
3. campaign destinations;
4. reporting;
5. shop/payment go-live readiness.

ENB's email creates one package-level build need: a narrow, config-driven
tracking/conversion bridge. It does not create a need for another packet or a
vendor-facing CMS. Existing routes can serve as the first approved landing
pages; campaign-specific pages can be added later as source-controlled Frappe
routes if the ad plan actually needs them.

## Lane Files

| Lane | File | Status |
|---|---|---|
| Lead replacement | `workstreams/marketing-lead-replacement-lane-2026-06-08.md` | complete with caveat: provider/dashboard state not verified |
| Shop/payment gate | `workstreams/payment-shop-go-live-gate-lane-2026-06-08.md` | complete with caveat: live checkout remains NO-GO |
| Conversion tracking | `workstreams/conversion-tracking-architecture-lane-2026-06-08.md` | complete with caveat: Meta parameters need provider-side recheck |
| Jeff/ENB communication | `workstreams/jeff-enb-transition-communication-lane-2026-06-08.md` | complete |
| Plan-deepen adjustment | `workstreams/enb-replacement-plan-deepen-2026-06-09.md` | complete: separates 72-hour lead rescue from package tracking bridge and long-term SEO/AEO/GEO |
| Root decision packet | `MARKETING-REPLACEMENT-AND-SHOP-GO-LIVE-PLAN-2026-06-08.md` | created by controller |
| External builder access + reset closeout | `workstreams/external-marketing-builder-access-reset-2026-06-13.md` | complete: controlled builder lane deployed; branded reset Email Queue `e4aqh31606` Sent |

## Local Implementation Notes - 2026-06-09

Implemented a disabled-by-default marketing measurement bridge:

- `marketing_measurement.py` normalizes public UTM/referrer attribution and
  builds no-send event envelopes.
- `lt-marketing-bridge.js` captures allowed campaign parameters in browser
  session storage and attaches them to public forms.
- `/contact` inquiry submission records a safe attribution Comment on the new
  Lead after the Lead is created.
- No Google tag, GA4 send, Google Ads send, Meta Pixel, Meta CAPI, customer-list
  upload, ad automation, or live provider mutation was added.

Also fixed local shop smoke blockers without changing product classifications:

- quote-first delivery-only products show quote/install fulfillment language;
- category grids avoid desktop orphan rows by feature-sizing the first real
  product card for odd 7/10-style category counts.

Current verified catalog split remains mixed, not quote-only:

- 29 published checkout Website Items;
- 21 published quote-first Website Items.

## Approval Gates


## Live Access And Reset Closeout - 2026-06-13

Completed the current ENB account-access ask without granting broad admin/site
control:

- added/deployed controlled `LT External Marketing Builder` access;
- kept business records, checkout, pricing, customers, orders, files, logs, and
  Email Queue out of the vendor lane;
- deployed branded Locally Twisted password-reset template and generic-copy
  Email Queue guard;
- patched the guard to decode MIME/quoted-printable queued content instead of
  loosening the generic-blocker;
- sent exactly one actual reset email to `marketing@exploringnotboring.com`;
- verified Email Queue `e4aqh31606` as `Sent` and safely checked the reset page
  without consuming the key.

Deployment receipt: source `456c9a3`, app mirror
`8b10a92274f1699eeb89713dff347f66a0db75f3`, Frappe Cloud patch pipeline
`eutojcn0ei`, active bench `bench-40102-000037-f4v`.

This does not authorize ENB removal, ad account mutations, budget changes,
customer-data export, live tracking changes, or another reset send.


### Gate A - Local Proof Packet

Allowed now:

- run local verification;
- record pass/fail;
- document blockers;
- draft communication;
- define ad/tracking architecture.

Not allowed:

- live payment;
- ad account mutation;
- provider mutation.

### Gate B - Staging/Hosted Shop Proof

Requires explicit approval before any hosted mutation.

Proof needed:

- approved source commit;
- known target URL;
- rollback/resting state;
- shop/product/cart/checkout proof;
- payment readiness proof in target environment;
- no exposed secrets.

### Gate C - Live Payment

Requires explicit approval before any real payment action.

Proof needed:

- `payment_launch_readiness.py --mode live` passes for the target host;
- Stripe webhook endpoint configured;
- operator email configured;
- public policies load;
- first low-risk payment test plan approved;
- rollback/refund path approved.

### Gate D - Marketing Account Takeover Or Vendor Removal

Requires explicit approval before changing access, budgets, campaigns, or
ownership.

Proof needed:

- campaign/export packet from ENB or current ad accounts;
- billing and spend visibility;
- conversion action inventory;
- final URL/UTM inventory;
- lead routing inventory;
- pixel/tag/container inventory;
- replacement launch plan ready.

## First Execution Sequence

1. Complete lane docs.
2. Run local proof commands and record current pass/fail.
3. Add a no-send marketing measurement bridge implementation plan and verifier
   before any live tags.
4. Prepare a 72-hour lead rescue destination map to verified inquiry routes,
   not checkout.
5. Prepare Jeff packet.
6. Prepare ENB transition/export request.
7. Identify missing account IDs and approvals.
8. Ask for approval for the next stage only.

## Local Proof Commands

```bash
python scripts/verify/website_launch_verify.py --with-a11y --with-contact-smoke
npm run test:marketing-review-access
python scripts/verify/ecommerce_pause_contract.py
npm run test:ecommerce-full
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/payment_launch_readiness.py
```

Run the open-ecommerce gates only when the local ecommerce mode is intentionally
opened for proof and restored afterward if required by the current safe posture.

## Stop Conditions

Stop and ask for approval if the next action would:

- change a live account;
- charge a card;
- publish an ad;
- remove ENB access;
- expose customer or payment data;
- change DNS/Search Console/Stripe/Frappe Cloud/Cloudflare;
- alter production ERPNext records;
- change public business policy.

## Current Open Questions

1. Which ad accounts does Jeff want LT/BBC to own immediately: Google only,
   Meta too, or both?
2. Does Jeff want ENB fully removed, or moved to a temporary export-only role
   until replacement proof is visible?
3. What budget is approved for the first replacement test?
4. Which product/service offer should be the first campaign: ready-to-order,
   event decor quote, twisting/face painting, or a seasonal event offer?

## Next Safe Step

Complete this workstream's lane docs, then run local verification and produce a
Jeff-ready packet. Do not proceed to staging/live/payment/ad changes without a
separate approval.

## Lane Completion Notes - 2026-06-08

Four scoped subagent lanes completed:

- `marketing-lead-replacement-lane-2026-06-08.md` records ENB replacement
  objective, source preservation, Google/Meta readiness, first 24-hour lead
  watch, and no-touch boundaries.
- `payment-shop-go-live-gate-lane-2026-06-08.md` records why live shop/payment
  remains NO-GO and what proof is required before a real payment path opens.
- `conversion-tracking-architecture-lane-2026-06-08.md` maps tracking events to
  ERPNext authority and blocks purchase events until paid-order reconciliation.
- `jeff-enb-transition-communication-lane-2026-06-08.md` provides Jeff and ENB
  communication drafts plus a transition-export request.

Known caveats:

- Conversation recall returned incomplete coverage in the lane work; current
  repo/provider evidence must win.
- ENB/Meta/current ad-account dashboard state remains unverified until approved
  provider/account access is used.
- This packet still does not authorize live payment, ad account mutation, ENB
  access removal, customer-data export, or provider changes.
