# Launch V1 Success Contract

Last updated: 2026-05-10 by Codex.

## Purpose

This contract keeps Locally Twisted launch work focused.

The long-term goal is a saleable company infrastructure that can help Jeff transition the business over the next 10 years. The immediate goal is narrower: launch a high-quality public website and ecommerce testing candidate that earns trust from the right buyers, supports SEO/local discovery, captures inquiries, and proves ready-to-order/cart/checkout paths before production cutover.

GL correction, 2026-05-10: public ecommerce is reopened for full local testing. Do not keep using the no-purchase/pause contract as the current proof posture. Also do not treat local open ecommerce tests as production approval: product import completion, full catalog parity, full catalog price parity, product/category media parity, live Stripe, payment webhooks, DNS cutover, and Frappe Cloud/staging promotion remain separate gates. V1 center is public trust/proof/info, /contact inquiry intake with fail-loud Lead evidence, and a tested ready-to-order/cart/checkout path that can be reviewed before live cutover.

Status note, 2026-05-10: Codex opened local ecommerce with `lt_ecommerce_paused=0`; `npm run test:ecommerce-full`, `npm run test:public-verify`, `python scripts/verify/product_page_architecture_readiness.py`, `python scripts/verify/synthetic_business_pipeline.py`, and `python scripts/verify/business_automation_index.py` passed.

Status note, 2026-05-23: the owner-review staging push failed as a release
process. V1 launch success cannot be claimed from the failed session's commits,
app mirror hashes, deploy IDs, interrupted bootstrap attempts, or local proof.
Future release work must satisfy
`workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
before staging/live execution reopens.

Do not use the 10-year ERPNext vision as a reason to delay the website unless the missing backend work directly affects launch trust, inquiry handling, policies, or customer-facing accuracy.

## V1 Launch Promise

V1 succeeds when a real customer can:

- understand Locally Twisted as an experienced Utah event balloon decor company;
- see enough proof to trust the company for corporate, school, city, venue, large private, and family event work;
- browse ready-to-order products without obvious placeholder or incorrect media;
- add verified ready-to-order products to cart and reach checkout in the local testing path;
- submit an inquiry through `/contact`;
- use `/book` only as a quick-intent redirect to `/contact`;
- distinguish tested ecommerce readiness from final live payment/cutover approval;
- see clear privacy, terms, refund/cancellation, accessibility, and service expectation pages;
- experience the site on desktop and mobile without broken layout, clipped text, inaccessible controls, or obvious ERPNext default seams.
- get buyer-ready page shells for the four event audience lanes, with final public copy routed through `brand-copywriter`; do not recreate the removed `/event-balloons` hub without a fresh GL route decision.

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

### 2. Ready-to-Order Decor (Ecommerce Testing Lane)

Open testing lane for launch review. This includes productized bouquets, columns, small decor, seasonal items, delivery-ready items, and other products shown as catalog proof, inquiry context, and tested checkout candidates.

This lane should be substantial because Jeff wants ecommerce long-term. Local testing should prove browse, option selection, cart, checkout, fulfillment, and backend cascades. Live checkout still waits for staging/client approval and live payment/cutover readiness.

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
- ready-to-order ecommerce surfaces imply production live payment/cutover approval when only local/staging testing has passed;
- variant/product media contradicts the selected option where source media exists;
- policy pages are missing, unreachable, or obviously stale;
- homepage or navigation presents the wrong business identity;
- mobile layout overlaps, clips, or hides critical actions;
- exact trust claims are unverified or stale;
- ecommerce full-testing contract is not provable through shop, cart, checkout, fulfillment, and backend cascade verifiers;
- generated or third-party images are used as proof without source/usage clarity.

## Deferred Until After V1

Do not let these delay launch unless they directly break a launch blocker:

- full 10-year operating model;
- live production ecommerce cutover beyond tested local/staging checkout flow;
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
8. Before live cutover, run agency preflight, staging audit, owner review, and staging-to-live gates.
9. After launch, expand backend maturity toward the 10-year saleability system.

## Operating Rule

When a future agent is unsure whether work belongs in V1, ask:

Does this help the website launch with more trust, more accurate customer paths, better visual quality, better findability, or safer business flow?

If yes, consider it for V1.

If no, park it in the appropriate post-launch workstream.
