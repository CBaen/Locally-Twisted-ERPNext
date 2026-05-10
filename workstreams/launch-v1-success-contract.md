# Launch V1 Success Contract

Last updated: 2026-05-10 by Codex.

## Purpose

This contract keeps Locally Twisted launch work focused.

The long-term goal is a saleable company infrastructure that can help Jeff transition the business over the next 10 years. The immediate goal is narrower: launch a high-quality no-purchase public website that earns trust from the right buyers, supports SEO/local discovery, captures inquiries, and presents ready-to-order offerings as browse/proof only without looking cheap or unfinished.

GL correction, 2026-05-10: V1 launch is a no-purchase public site. Ecommerce is shut down for launch unless GL explicitly reopens it. Do not treat /shop, product import completion, catalog parity, catalog price parity, product/category media parity, cart, checkout, payment-success, thank-you, live Stripe, payment webhooks, or product-page receiving architecture as V1 launch blockers. V1 launch center is public trust/proof/info plus /contact inquiry intake with fail-loud Lead evidence. Ecommerce/catalog/payment lanes remain post-V1 architecture and cutover work.

Status note, 2026-05-10: backend-automation-guard reports the direct guest checkout API pause contract fixed and `python scripts/verify/ecommerce_pause_contract.py` passing. Keep this as fixed-pending-review until stack-cartographer's independent review lands.

Do not use the 10-year ERPNext vision as a reason to delay the website unless the missing backend work directly affects launch trust, inquiry handling, policies, or customer-facing accuracy.

## V1 Launch Promise

V1 succeeds when a real customer can:

- understand Locally Twisted as an experienced Utah event balloon decor company;
- see enough proof to trust the company for corporate, school, city, venue, large private, and family event work;
- browse ready-to-order products without obvious placeholder or incorrect media;
- submit an inquiry through `/contact`;
- use `/book` only as a quick-intent redirect to `/contact`;
- browse ready-to-order offerings without implied live purchase flow;
- see clear privacy, terms, refund/cancellation, accessibility, and service expectation pages;
- experience the site on desktop and mobile without broken layout, clipped text, inaccessible controls, or obvious ERPNext default seams.
- get buyer-ready page shells for the Event Balloons audience lanes, with final public copy routed through `brand-copywriter`.

## Long-Term Business Direction

The ERPNext build should not make Jeff the whole brand.

The 10-year direction is a company that is easier to sell because it has:

- company-branded copy and proof;
- documented service categories and pricing logic;
- consistent inquiry, quote, order, invoice, payment, and communication records;
- customer/review/proof history;
- staff-usable backend labels and workflows;
- maintainable custom app code;
- agent-readable handoffs, decisions, queues, and verification scripts.

This matters, but it is not all V1 launch work.

## Buyer Priority

Public website priority:

1. Professional event planners, corporate buyers, schools, churches, venues, community organizations, and institutions.
2. Big-scale public or event buyers, including parades, city events, public installations, and large venue activations.
3. Premium private event buyers, including weddings, showers, milestone events, and upscale home or venue events.
4. Family party buyers.

Balloon twisting and face painting are legitimate V1 services with fixed pricing and equal customer-facing availability under the existing agreement. They may speak more directly to family/private event buyers, but they should still feel professionally presented.

## Commercial Lanes

The site should carry three lanes without letting the lowest-value lane define the company.

### 1. Custom Event Decor

Primary brand lane. This includes arches, columns, organic installs, backdrops, photo opportunities, parades, branded installs, large event decor, and custom work.

This lane leads the homepage, gallery/proof system, service pages, and authority copy.

### 2. Ready-to-Order Decor (Browse Lane)

Browse lane for launch. This includes productized bouquets, columns, small decor, seasonal items, delivery-ready items, and other products shown as catalog proof and inquiry context.

This lane should be substantial because Jeff wants ecommerce long-term, but V1 launch keeps it as no-purchase browse/proof, not live checkout.

### 3. Event Entertainment

Balloon twisting and face painting lane. For V1, both are real services with set pricing and the existing customer-facing agreement.

This lane needs clear pricing, deposit/refund language, event-fit copy, and inquiry routing. Do not publicly imply hesitation about face painting or lower confidence in the service.

## Brand Direction For Launch

The current pastel-heavy visual system is not right for the highest-value buyer.

Before major page rendering or redesign, reset the visual direction toward:

- premium event production;
- Utah-local authority;
- clean proof-first photography;
- mature neutrals and high-contrast surfaces;
- restrained accent color;
- balloons and real work as the main color source.

Generated visual companions are allowed for palette boards, concept stills, composition exploration, post-production targets, and representative visuals. They must not be presented as proof of completed Locally Twisted work unless clearly labeled as concept/render.

## Quality Targets

V1 should aim for 80+ where feasible in measurable website quality categories, including performance, accessibility, best practices, and technical SEO.

Do not claim those scores until audited.

Launch-quality also includes things automated scores do not fully judge:

- real mobile screenshots look professional;
- images are not smashed, cropped badly, blurry, or misleading;
- contact and browse paths work as actual business flows;
- policy and refund language is visible where customers need it;
- local proof supports Utah event authority;
- content is structured to answer customer and search-engine questions clearly.

SEO/GEO/AEO work for V1 should focus on:

- clear service/category pages;
- service-area language;
- review and client proof;
- useful question/answer content;
- structured page titles and descriptions;
- image alt text where meaningful;
- Google Business Profile alignment;
- no stale hours, phone, address, or review-count claims.

## Launch Blockers

Treat these as blockers if customer-facing:

- broken route or redirect in a core path;
- `/contact` cannot submit correctly;
- ready-to-order browse surfaces imply live purchase when V1 scope is no-purchase;
- variant/product media contradicts the selected option where source media exists;
- policy pages are missing, unreachable, or obviously stale;
- homepage or navigation presents the wrong business identity;
- mobile layout overlaps, clips, or hides critical actions;
- exact trust claims are unverified or stale;
- no-purchase launch contract is not provable with route pause plus the checkout API pause verifier;
- generated or third-party images are used as proof without source/usage clarity.

## Deferred Until After V1

Do not let these delay launch unless they directly break a launch blocker:

- full 10-year operating model;
- live ecommerce purchase flow (cart, checkout, payment success, thank-you);
- product import completion, catalog parity, catalog price parity, and product/category media parity;
- payment webhooks and live Stripe cutover setup;
- product-page receiving architecture completion;
- deep CRM maturity beyond launch-safe inquiry handling;
- full employee/contractor workflow automation;
- advanced reporting;
- full inventory discipline;
- broad ERPNext training material;
- Design Studio/configurator;
- large-scale backend cleanup unrelated to customer trust, payment, policy, or handoff safety.

## Immediate Sequence

1. Reset color and brand direction before rendering new page concepts.
2. Produce visual companions as generated image boards/concept stills, not browser popups by default.
3. Redesign the proof surface: homepage, gallery/inspiration, and high-value service framing.
4. Clean shop/category/product presentation so ready-to-order browse supports trust instead of cheapening the brand.
5. Reconcile Balloon Twisting & Face Painting with the existing V1 agreement: equal pitch, fixed pricing, clear terms, company language.
6. Build Event Balloon audience-page structure under the active implementation lane; route copy system and fill through `brand-copywriter`.
7. Run real audits after visual/content changes: route checks, layout fit, Lighthouse, accessibility, mobile screenshots, contact, browse surfaces, and policy-source checks.
8. Only after V1 launch, expand backend maturity toward the 10-year saleability system.

## Operating Rule

When a future agent is unsure whether work belongs in V1, ask:

Does this help the website launch with more trust, more accurate customer paths, better visual quality, better findability, or safer business flow?

If yes, consider it for V1.

If no, park it in the appropriate post-launch workstream.
