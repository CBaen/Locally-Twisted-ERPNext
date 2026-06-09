# Conversion Tracking Architecture Lane - 2026-06-08

## Scope

Document the conversion tracking architecture Locally Twisted needs before
replacing ENB and launching ecommerce responsibly.

This is a documentation-only lane. It does not authorize or perform provider,
staging, live, DNS, Stripe, Search Console, ad-account, customer-data, or secret
changes.

## Current Repo Evidence

The new tracking architecture must follow the ERPNext source of truth already
present in this repo:

- `/contact` is the primary public inquiry route. It renders the shared inquiry
  form and posts through `submit_book_inquiry`.
- The inquiry submit path creates an ERPNext `Lead`, attaches customer context,
  handles inspiration photos, records a Lead timeline `Communication`, and lets
  Lead hooks create/link `Contact`, queue acknowledgment email, and create CRM
  follow-up work.
- Guest checkout creates `Customer`, `Contact`, `Address`, `Sales Order`,
  `Payment Request`, and a Stripe Checkout Session. It does not finalize Lead
  conversion before payment.
- Paid-order reconciliation in
  `apps/locally_twisted/locally_twisted/www/payment_success.py` is the purchase
  authority. It marks the `Payment Request`, converts linked inquiry Leads only
  after payment is verified, creates the `Sales Invoice`, sends the customer
  receipt, sends the operator notification, and sends the first-order welcome
  email.
- Public contact points include `tel:+18012850860`. ENB evidence also mentions
  the tracking number `(801) 784-3426`, but ownership and forwarding remain a
  dependency to verify before removing ENB.

Existing cross-links:

- `workstreams/ad-account-takeover-2026-05-19.md`
- `capabilities/recipes/ad-account-takeover-provider-control.md`
- `workstreams/business-automation-index.md`
- `scripts/verify/checkout_lead_conversion_contract.py`
- `scripts/verify/smoke_forms.py`

## Official Platform Source Snapshot

Researched 2026-06-08.

Google official sources:

- GA4 ecommerce events: `https://developers.google.com/analytics/devguides/collection/ga4/ecommerce`
- GA4 purchase setup and DebugView: `https://developers.google.com/analytics/devguides/collection/ga4/set-up-ecommerce`
- GA4 Measurement Protocol: `https://developers.google.com/analytics/devguides/collection/protocol/ga4`
- Send GA4 Measurement Protocol events: `https://developers.google.com/analytics/devguides/collection/protocol/ga4/sending-events`
- Google Ads Google tag conversion tracking: `https://support.google.com/google-ads/answer/7548399`
- Google consent mode overview: `https://developers.google.com/tag-platform/security/concepts/consent-mode`
- Google consent mode website setup: `https://developers.google.com/tag-platform/security/guides/consent`
- Google Ads phone-call conversion tracking: `https://support.google.com/google-ads/answer/6100664`
- Google Ads website phone-call tracking setup: `https://support.google.com/google-ads/answer/6095883`

Meta official sources:

- Meta Pixel reference: `https://developers.facebook.com/docs/meta-pixel/reference`
- Meta Conversions API overview: `https://www.facebook.com/business/help/AboutConversionsAPI`
- Meta Conversions API parameters: `https://developers.facebook.com/docs/marketing-api/conversions-api/parameters`
- Meta Pixel and Conversions API deduplication: `https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events`
- Meta Business Tools: `https://www.facebook.com/help/331509497253087/`

Note: the automated web fetch could open Google docs directly. Meta official
pages are linked here for implementation, but automated fetches hit
Facebook/Meta access blocking or login pages, so exact Meta parameter rules
must be rechecked inside Meta Events Manager / Meta for Developers before any
live Meta implementation.

## Event Architecture

### Browser Events

Browser-side events are useful for page and interaction signals where the
visitor context exists in the browser:

- GA4: `page_view`, `view_item_list`, `view_item`, `add_to_cart`,
  `view_cart`, `begin_checkout`, `add_shipping_info`, `add_payment_info`,
  `generate_lead`, and consent-state updates.
- Google Ads: conversion event snippets for approved conversion actions only,
  with `send_to`, `value`, `currency`, and a dedupe-safe `transaction_id` where
  applicable.
- Meta Pixel: `PageView`, `ViewContent`, `AddToCart`, `InitiateCheckout`,
  `Lead`, `Contact`, and `Purchase` only where the corresponding backend record
  exists or a test event proves the signal is not double-counted.

Browser-side purchase tracking must not fire merely because the customer lands
on a thank-you page. The browser may be used to show a confirmation signal, but
the business purchase event is only valid after ERPNext paid-order
reconciliation succeeds.

### Server Events

Server-side events are needed where ERPNext is the actual source of truth:

- Lead event: after `Lead` creation succeeds on `/contact`.
- Purchase event: after paid reconciliation succeeds for the `Sales Order` and
  linked `Payment Request`.
- Qualified lead or booked event: only after an operator or automation moves
  the ERPNext record to the approved business stage.
- Call outcome event: only after the call tracking source proves a call and LT
  can map it to a Lead, Customer, or offline conversion import.

For GA4, Measurement Protocol can supplement the Google tag for server or
offline events, but Google states it is meant to augment tagging, not replace
browser tagging. A full server-only GA4 path is therefore not the launch
default.

For Meta, Conversions API should be considered for backend Lead and Purchase
events, especially because Meta describes CAPI as a direct connection from
server/CRM/website data to Meta systems and recommends using it alongside the
Pixel for website events. It is not a privacy-policy bypass.

### Dedupe Contract

Every event that can be sent by both browser and server needs a shared event
identity:

- GA4 ecommerce purchase: use ERPNext `Sales Order` as
  `transaction_id`; include `currency`, `value`, `tax`, `shipping`, and `items`
  when available.
- Google Ads purchase conversion: use ERPNext `Sales Order` or
  `Payment Request` as the conversion `transaction_id`; send the exact
  conversion action label supplied by Google Ads.
- Meta Pixel + CAPI: use the same event name and event ID for the browser and
  server copy of a single conversion. Preferred IDs:
  - `lead:<Lead.name>` for Lead.
  - `purchase:<Sales Order.name>` for Purchase.
  - `call:<call-provider-call-id>` for verified call conversions.

If the browser and server cannot share a stable event ID, choose one side for
that event until dedupe is proven. Double-counted purchase or lead events are a
launch blocker because they train ad platforms on false outcomes.

## Consent Boundary

Consent is a business/legal decision, not an engineering guess. Before launch,
humans must choose:

- Whether LT uses Google Tag Manager, direct `gtag.js`, or both.
- Whether LT uses a consent management platform or a small custom consent
  banner.
- Default consent states by region.
- Whether basic consent mode or advanced consent mode is acceptable.
- Which events may include hashed customer identifiers.
- Whether marketing opt-in affects advertising-user-data sharing separately
  from transactional receipt behavior.

Engineering boundary:

- No advertising, analytics, remarketing, or personalized-ad storage before the
  approved consent behavior is implemented.
- Do not send customer email, phone, name, address, IP, or user-agent to Google
  or Meta server APIs unless consent, platform policy, and business approval
  permit it.
- Transactional ERPNext records still exist for order fulfillment and customer
  service. That does not automatically permit marketing/ad-platform upload.
- Consent denial must not break checkout, inquiry submission, receipt email,
  or ERPNext internal records.

Google consent mode v2 fields to plan around:

- `ad_storage`
- `analytics_storage`
- `ad_user_data`
- `ad_personalization`

## Frappe / ERPNext Event Surfaces

Authoritative LT surfaces:

| Surface | Event candidates | Authority |
|---|---|---|
| Public page render | `page_view`, `ViewContent` | Browser only after consent/tag load |
| Product list/category | `view_item_list`, `ViewContent` | Browser with Website Item data |
| Product detail | `view_item`, `ViewContent` | Browser with Website Item / Item data |
| Cart add | `add_to_cart`, `AddToCart` | Browser; server only if persisted cart event is added later |
| Cart view | `view_cart` | Browser; use resolved cart items |
| Checkout start | `begin_checkout`, `InitiateCheckout` | Browser when checkout form starts |
| Shipping/contact details | `add_shipping_info`, `Contact` | Browser only, unless backend submit succeeds |
| Inquiry submit | `generate_lead`, `Lead` | Server after `Lead` insert succeeds |
| Paid purchase | `purchase`, `Purchase`, Google Ads purchase conversion | Server after `reconcile_paid_sales_order` succeeds |
| Phone click | Google Ads click-to-call conversion, Meta `Contact`, GA4 custom event | Browser for click only; not proof of a real call |
| Real call outcome | Google Ads imported call conversion, Meta CAPI offline/system event | Call provider/CRM after call is verified |

Do not treat `Website Item` fields as the authority for final purchase value.
The final purchase value comes from the submitted ERPNext `Sales Order` and
paid reconciliation path.

## Purchase Tracking

Launch purchase tracking should be wired in this order:

1. Create a conversion event envelope in LT code that can be filled from a paid
   `Sales Order` without sending it live.
2. Prove the envelope from fake/rollback-safe paid-order verifier data.
3. Map the envelope to GA4 ecommerce `purchase` parameters:
   `transaction_id`, `currency`, `value`, `tax`, `shipping`, and `items`.
4. Map the same envelope to Google Ads purchase conversion parameters:
   conversion action `send_to`, `value`, `currency`, and `transaction_id`.
5. Map the same envelope to Meta `Purchase` browser/CAPI payloads only after
   dedupe ID and consent handling are proven.
6. Send to test/debug endpoints or dashboard test modes first.
7. Only after GL approval and provider verification should live purchase
   events be enabled.

Purchase event must fail loudly if:

- The Sales Order is missing.
- The Payment Request does not match the Sales Order.
- Paid reconciliation failed or is pending.
- Currency/value cannot be derived.
- Dedupe ID is missing.
- Consent state blocks the intended data transfer.

## Lead Tracking

Lead tracking should fire only after the ERPNext Lead exists.

Preferred event mapping:

- GA4: `generate_lead` for successful inquiry creation.
- Google Ads: lead conversion action only after the Google Ads conversion ID
  and label are confirmed from the LT-owned Google Ads account.
- Meta: `Lead` for the successful web inquiry; `Contact` may be used for
  lower-value contact intent, but must not replace `Lead` for submitted
  inquiry forms.

Lead event fields should be restrained:

- Allowed by default for test/local envelope: Lead name, source surface,
  service category, event type, estimated value bucket if approved, and
  timestamp.
- Not allowed by default: raw name, email, phone, message body, uploaded photo
  metadata, street address, or full event details.
- Hashed email/phone for enhanced conversions or CAPI matching requires human
  approval, consent/legal fit, and dashboard configuration.

Qualified lead tracking is a separate event from raw lead creation. It should
come from an ERPNext CRM stage or owner review action, not the public form
submit.

## Call Tracking

There are three separate call concepts:

1. Phone link click: customer clicked `tel:` on the site. This is useful but is
   not proof that a call connected.
2. Google Ads call conversion: Google can track calls from ads, calls to a
   website number, mobile phone-number clicks, and imported call conversions.
   Google forwarding numbers are required for calls from ads / website call
   tracking / imported call conversion paths named in the official docs.
3. Verified call outcome: a call provider or CRM record proves duration,
   caller, source, and result.

LT should not remove ENB or HighLevel call paths until the following are known:

- Who owns `(801) 784-3426`.
- Whether it forwards to Jeff or another line.
- Whether active ads, landing pages, or Meta lead flows still use it.
- Whether call recordings, missed-call notifications, SMS, or pipeline
  automations live in ENB/HighLevel.
- Whether LT will use Google forwarding numbers, a third-party call-tracking
  provider, or ERPNext-only call logging.

For launch, phone-click events can be tracked locally in browser test mode, but
real call conversions should wait for a provider-owned call-tracking decision.

## Human / Vendor Inputs Needed

Google:

- Active LT Google Ads customer ID and login authority. Known evidence points
  to `437-723-0551`, but dashboard must confirm.
- Google Ads conversion action IDs and labels for purchase, lead, phone click,
  and calls from website if used.
- Google tag ID(s), GA4 measurement ID, GA4 property ID, and web stream ID.
- GTM container ID if GTM is chosen.
- Measurement Protocol API secret only if server-side GA4 is approved.
- Enhanced conversions approval and user-provided-data rules.
- Google call conversion configuration, forwarding-number availability, and
  minimum call-length threshold.

Meta:

- Business Manager ID, ad account ID, Page ID, Instagram account, domain
  ownership state, and billing owner.
- Pixel/dataset ID and whether dataset replaced older pixel terminology.
- CAPI access token or Conversions API Gateway configuration if server-side
  Meta events are approved.
- Test event code for non-live verification.
- Approved event priority/order, custom conversions, lead forms, and partner
  access inventory.
- Confirmation whether `Facebook Painting Leads` is Meta native lead forms,
  HighLevel, or both.

ENB / HighLevel / call vendor:

- Current landing page inventory and final URLs.
- Tracking phone numbers, forwarding rules, SMS/missed-call behavior, and owner.
- Lead pipeline export and historical lead export.
- Existing GA/GTM/Google Ads/Meta pixel/CAPI settings or reports.
- Any scripts currently embedded on old WordPress, HighLevel, or ENB-hosted
  pages.

LT / Built by Cameron:

- Consent policy decision.
- Which purchase, lead, qualified lead, and call outcomes are primary
  conversions versus secondary/observed events.
- Whether to preserve historical ENB reporting continuity or start clean with a
  new measurement baseline.
- Launch approval for live event transmission after local/staging/provider
  tests pass.

## Verification Plan

No live actions are part of this document. Future implementation should use
this verification order.

Static/local proof:

- Add a no-send event envelope and schema verifier.
- Prove no platform secrets or live IDs are hard-coded.
- Prove all event sends are blocked when tracking is disabled.
- Prove consent denial suppresses ad/analytics event dispatch without breaking
  form or checkout behavior.
- Run:
  - `python scripts/verify/smoke_forms.py --form-path /contact --skip-newsletter`
  - `python scripts/verify/checkout_lead_conversion_contract.py`
  - `python scripts/verify/payment_success_reconciliation_contract.py --report output/payment-success-reconciliation-contract.json`
  - `python scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json`

Browser/local proof:

- Intercept browser network calls and confirm no requests leave for Google or
  Meta when disabled.
- With test IDs only, confirm expected event names and payload shape for product
  view, add-to-cart, checkout start, lead submit, and paid purchase.
- Confirm thank-you reload does not duplicate purchase.
- Confirm browser/server purchase paths share the same dedupe ID when both are
  enabled.

Provider test-mode proof:

- Google Tag Assistant / GTM preview proves consent state, tag load order, and
  event snippets without enabling live campaign optimization.
- GA4 DebugView shows test events with correct names, values, currency, items,
  and transaction IDs.
- Google Ads diagnostics show test lead/purchase/call conversion actions
  receiving test traffic only.
- Meta Events Manager Test Events shows Pixel and CAPI test events, with
  matching event name and event ID for deduplication.

Staging/live gate proof:

- GL approves the exact provider accounts, IDs, event list, consent behavior,
  and live-action window.
- Ecommerce pause state and Stripe/live-payment gate are handled by the
  separate ecommerce launch process.
- Provider dashboards are exported before removing ENB access.
- First live events are monitored against ERPNext records one-for-one:
  one paid order equals one platform purchase event, one submitted inquiry
  equals one lead event, and one verified call equals one call conversion.

## No-Live-Actions Boundary

This lane explicitly does not:

- Log in to Google Ads, GA4, GTM, Meta, HighLevel, Frappe Cloud, Cloudflare,
  Stripe, Search Console, or call providers.
- Create, edit, pause, enable, delete, or publish campaigns.
- Create or modify tags, pixels, datasets, conversions, GTM containers,
  consent banners, DNS, domains, webhooks, payment settings, or provider users.
- Read or write secrets, tokens, API keys, OAuth files, customer data exports,
  ad billing data, or production ERPNext records.
- Send test or live customer events to Google, Meta, or any vendor.
- Approve ecommerce launch, live checkout, live Stripe, or ENB access removal.

The next safe step is an implementation plan for a no-send local event envelope
and verifier, followed by human/provider ID inventory in a separate approved
provider-control lane.
