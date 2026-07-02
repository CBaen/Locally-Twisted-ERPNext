# Marketing Replacement And Shop Go-Live Plan - 2026-06-08

## Plain-English Decision

Locally Twisted can no longer treat Exploring Not Boring (ENB) as a normal
website administrator. The new site is part of an ERP-backed Frappe/ERPNext
system. Product setup, checkout, payment, customer records, inquiry records,
permissions, public pages, and reporting are connected. Broad page-builder or
website-manager access would not be a harmless marketing login; it would cross
into business-system control.

The plan is not to create a fake WordPress-like access path for ENB. The plan is
to replace the value Jeff cared about - leads - with a controlled Locally
Twisted / Built by Cameron lead-generation and tracking system that fits the ERP
architecture.

This document is a plan and decision packet. It does not approve staging,
live, DNS, Stripe, Search Console, ad-account mutation, customer-data export, or
real-payment testing.

## Current Date And Evidence Boundary

- Current date: 2026-06-08.
- Claims in old docs are evidence only.
- Current source, current repo docs, local verification commands, and official
  platform documentation outrank memory.
- Live payment and ad-platform behavior must be verified at the target account
  and target environment before action.

## What ENB Asked For

From the email thread, ENB asked for the ability/access to:

1. Build/customize landing pages.
2. Track conversions, including ecommerce sales.
3. Add or update site tracking if it is not already set up.

Those are legitimate marketing needs. The mismatch is the access model.

## Why Their Requested Access Does Not Fit This System

The current Locally Twisted site is not a standalone page-builder website. It
has:

- source-controlled Frappe pages and templates;
- ERPNext product, checkout, Sales Order, Payment Request, Sales Invoice, Lead,
  and customer surfaces;
- role-bound access policies;
- a protected marketing-review lane;
- explicit checkout/payment release gates.

Existing local documentation states that external marketing review access is
limited to `/marketing-review`, with no Desk access and no DocPerm rows. That is
the correct boundary for an outside reviewer. It is not enough for ENB to build
pages directly, because direct editing would need a new controlled internal
marketing-authoring architecture, not a broad vendor login.

## Business Position

This should be framed to Jeff as:

> ENB helped with leads in the old website model. The business system has now
> changed. Locally Twisted's website is connected to products, checkout,
> customer records, payments, and operations. Their requested access does not
> fit safely anymore. We are replacing the lead-generation function with a
> controlled system that gives us better tracking, better ownership, and cleaner
> handoff from ad click to inquiry or sale.

Do not frame this as "ENB is bad" unless Jeff asks for a vendor performance
review. The strongest factual argument is architecture and ownership.

## Replacement Promise

The replacement promise is not "AI will do marketing." The replacement promise
is:

- Locally Twisted owns its website, lead paths, conversion tracking, product
  catalog, checkout, and customer data.
- Built by Cameron can operate the technical marketing infrastructure.
- Ads can send traffic to approved Frappe routes and controlled campaign pages.
- Conversion events can be wired to real business actions instead of vague page
  views.
- Jeff gets lead visibility without giving an outside vendor backend power.

## Two Tracks, Not One

### Track A - Lead Replacement And Tracking

Goal: prove quickly that LT/BBC can replace ENB's useful lead function.

This track includes:

- preserve and request ENB's historical ad/export data before removal;
- define approved landing URLs;
- define Google Ads, Meta, GA4, and call/form conversion events;
- create a first-week campaign/reporting plan;
- create a 24-hour lead watch process;
- build a Jeff-facing report packet.

Approval needed before live action:

- ad budget;
- campaign copy/offers;
- ad-platform account access or takeover;
- any customer list upload, audience upload, or lookalike use;
- any actual ad publishing, pausing, budget change, or vendor removal.

### Track B - Shop And Payment Go-Live

Goal: turn on ecommerce only after the live payment and customer-journey gates
pass.

This track includes:

- local ecommerce proof;
- staging/live payment readiness proof;
- live Stripe configuration check without printing secrets;
- webhook readiness;
- policy route readiness;
- first low-risk real payment test with explicit approval;
- rollback/resting-state plan.

Approval needed before live action:

- staging/provider mutation;
- live Stripe keys or webhook configuration;
- unpausing ecommerce on staging/live;
- real payment test;
- DNS/Search Console/provider changes;
- production customer data mutation.

## What We Can Do Immediately

These are safe to do locally or as docs/source work:

- run local launch and ecommerce verification commands;
- document current blockers and pass/fail state;
- prepare Jeff/ENB emails;
- prepare ad and tracking architecture;
- create controlled campaign-page specs;
- list all required IDs/config values;
- create a first-week lead reporting template;
- prepare a transition-export request to ENB.

## Package Impact From ENB's Email

ENB's email does not require another packet and does not require building a
vendor-facing page-builder now.

It does expose one package-level need:

- a controlled, config-driven marketing measurement bridge in the
  `locally_twisted` app.

That bridge should support:

- optional GA4 / Google tag loading when configured;
- optional Google Ads conversion actions when configured;
- optional Meta Pixel / Meta CAPI hooks when configured and approved;
- consent-aware firing for analytics/advertising events;
- browser events for page/product/cart/checkout interaction;
- server-authoritative events for Lead creation and paid purchase
  reconciliation;
- verification that paused checkout does not fire checkout or purchase events;
- clear no-secret behavior in source and logs.

What should not be built now:

- a broad ENB editor account;
- a public/vendor CMS;
- a quick landing-page builder;
- ad-account automation that can spend money;
- customer-list upload or audience creation;
- live tracking tags that fire before GL approves IDs, consent behavior, and
  provider/account ownership.

Existing public routes can serve as launch landing pages. If campaign-specific
landing pages are later needed, they should be source-controlled Frappe routes
or a controlled internal marketing-page workflow with review gates, not a
vendor workaround.

## What We Must Not Do Without Explicit Approval

- Do not remove ENB from ad accounts before exporting current campaigns,
  conversion settings, final URLs, billing, tags, pixels, lead routing, and
  dependencies.
- Do not give ENB broad Desk, Website Manager, System Manager, product, checkout,
  customer, payment, or admin access.
- Do not publish ads or change budgets.
- Do not upload customer lists or create lookalike audiences.
- Do not turn on live payments.
- Do not change live Stripe, DNS, Search Console, Cloudflare, Frappe Cloud, or
  production records.
- Do not treat local Stripe/test-mode proof as live payment readiness.

## Official Platform Reality

Google Ads conversion tracking is built around actions the business defines as
valuable, such as purchases, signups, calls, and other website actions:
https://support.google.com/google-ads/answer/1722054?hl=en

Google's web conversion setup expects website actions to be measured from the
site/data source:
https://support.google.com/google-ads/answer/12216424?hl=en

GA4 ecommerce documentation expects events for shopping behavior such as item
views, add-to-cart, checkout start, purchases, refunds, and item arrays:
https://developers.google.com/analytics/devguides/collection/ga4/ecommerce

Meta Pixel setup expects a pixel/dataset and website events such as purchase:
https://www.facebook.com/help/messenger-app/952192354843755/

Meta Conversions API can supplement Pixel events and improve reliability for
website-event measurement, but it carries more privacy/configuration
responsibility:
https://www.facebook.com/business/help/AboutConversionsAPI

## LT Event Architecture Target

The replacement tracking architecture should map LT business actions to
platform events:

| LT action | Business meaning | GA4 event candidate | Google Ads conversion | Meta event candidate | Notes |
|---|---|---|---|---|---|
| Product page viewed | Shopper interest | `view_item` | Secondary or remarketing signal | `ViewContent` | Requires item id/name/category/value when available. |
| Add to cart | Purchase intent | `add_to_cart` | Secondary unless useful for bidding | `AddToCart` | Must use selected variant and price. |
| Checkout started | High purchase intent | `begin_checkout` | Secondary or primary depending strategy | `InitiateCheckout` | Must not fire when checkout is paused or blocked. |
| Purchase paid | Revenue | `purchase` | Primary purchase conversion | `Purchase` | Must fire only after paid/reconciled order proof. |
| Contact/inquiry submitted | Lead | `generate_lead` or custom lead event | Primary lead conversion | `Lead` | Must fire only after backend Lead/inquiry record exists. |
| Phone click | Call intent | click/call event | Call/click conversion | `Contact` or custom | Needs approved phone-call tracking plan. |
| Quote-first product inquiry | Custom work lead | `generate_lead` plus product context | Lead conversion | `Lead` | Must not look like a paid purchase. |

## Local Source Evidence To Re-check Before Execution

Use these current repo surfaces before changing behavior:

- `locally-twisted-queue.md`
- `workstreams/website-launch.md`
- `workstreams/payment-portal-live-cutover-checklist-2026-05-11.md`
- `workstreams/marketing-review-access-2026-05-15.md`
- `workstreams/user-access-audit-2026-05-15.md`
- `scripts/README.md`
- `scripts/verify/payment_launch_readiness.py`
- `scripts/verify/website_launch_verify.py`
- `scripts/verify/ecommerce_pause_contract.py`
- `scripts/verify/marketing_review_access_boundary.py`

## Verification Commands

Local website and inquiry readiness:

```bash
python scripts/verify/website_launch_verify.py --with-a11y --with-contact-smoke
```

Marketing access boundary:

```bash
npm run test:marketing-review-access
```

Paused ecommerce safety:

```bash
python scripts/verify/ecommerce_pause_contract.py
```

Open ecommerce local proof when intentionally reopened locally:

```bash
npm run test:ecommerce-full
python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
```

Payment local readiness:

```bash
python scripts/verify/payment_launch_readiness.py
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_webhook_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/payment_success_reconciliation_contract.py
python scripts/verify/stripe_amount_parity_contract.py
```

Live readiness, only after target approval:

```bash
python scripts/verify/payment_launch_readiness.py --mode live --base-url <staging-url>
python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
```

## Subagent Lane Split

| Lane | File | Owner output |
|---|---|---|
| Lead replacement | `workstreams/marketing-lead-replacement-lane-2026-06-08.md` | ENB replacement plan, lead watch, campaign readiness. |
| Shop/payment gate | `workstreams/payment-shop-go-live-gate-lane-2026-06-08.md` | Ecommerce and Stripe go-live approval gate. |
| Conversion tracking | `workstreams/conversion-tracking-architecture-lane-2026-06-08.md` | GA4/Google Ads/Meta event architecture and consent/config boundary. |
| Jeff/ENB communication | `workstreams/jeff-enb-transition-communication-lane-2026-06-08.md` | Owner/vendor messaging and transition data request. |
| Controller packet | `workstreams/enb-replacement-shop-go-live-2026-06-08.md` | Parent coordination, status, approval gates, and next sequence. |

## First 24-Hour Watch Plan After Approval

After tracking and shop/payment go-live are explicitly approved:

1. Watch form submissions and backend Lead creation.
2. Watch ad clicks, landing-page sessions, and conversion events.
3. Watch add-to-cart, checkout-start, and purchase events.
4. Watch Stripe webhook events and ERPNext payment reconciliation.
5. Watch Email Queue/receipt/operator notifications.
6. Watch Search Console/GA4 for crawl/indexing and traffic anomalies.
7. Record every issue as either customer-facing, revenue-facing, tracking-only,
   or internal-ops.

## Jeff-Ready Summary

Short version for Jeff:

> ENB's requested access does not fit the new system. The site is now connected
> to the business backend, not a standalone marketing page builder. We can still
> support ad landing pages, conversion tracking, and sales tracking, but those
> have to be owned inside the Locally Twisted system. I recommend we transition
> ENB out of website administration, preserve/export anything currently
> producing leads, and replace their lead-generation function with our own
> controlled Google/Meta/reporting setup tied directly to inquiries and sales.

## Done Definition

This plan is complete when:

- Jeff has a plain-English transition packet.
- ENB has a controlled transition/export request.
- local website/shop/payment readiness has fresh pass/fail evidence.
- conversion tracking architecture is documented.
- live payment blockers are known and approval-gated.
- ad account changes and budgets remain blocked until approval.
- the first 24-hour lead/watch process exists.

This document alone does not make ecommerce live.
