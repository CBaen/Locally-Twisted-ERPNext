# Design Studio V2 Workstream

Last updated: 2026-05-02 by Codex.

## Status

Background V2 planning lane. First read-only/spec wave completed 2026-05-02.

This is not a V1 launch blocker. Keep launch-critical website, shop, payment, policy, and inquiry work moving separately. This lane exists so the future `Plan Custom Decor` experience can be designed in the background without creating last-minute launch risk.

## Outcome

Build a Frappe-native planning experience for larger custom balloon decor installations.

The intended customer can:

- plan a multi-piece event installation instead of shopping one isolated product
- combine pieces such as classic arches, columns, backdrops, organic garlands, and balloon drops
- compare balloon colors to a company, school, city, church, venue, or organization palette
- understand scale through reference items and common event contexts
- save the design to an account or share it with stakeholders
- send a useful design summary into Locally Twisted's inquiry and CRM workflow

The intended business outcome is higher-quality custom inquiries for corporate, school, civic, community, venue, and premium private events.

## Product Split

Use this split consistently:

| Surface | Purpose | Buyer mode |
|---|---|---|
| Ready to Order | Small, simple, already-structured products such as bouquets, themed items, delivery/pickup-friendly decor, and lower-risk ecommerce products | Customer is ready to buy |
| Plan Custom Decor | Larger, consultative, multi-piece event installations where stakeholders, colors, scale, installation context, and quote conversation matter | Customer needs guided planning |

Do not force every customizable SKU into the design studio. The studio should handle the high-value complexity that makes normal ecommerce feel comical or overwhelming.

## Strategic Frame

This is the bridge between Jeff's desire for ecommerce and the business reality that Locally Twisted makes stronger money and brand authority through larger installations.

The studio should feel:

- premium, professional, and Utah-rooted
- consultative, not childish
- playful through the balloon work, not through toy-like UI
- useful for stakeholders who need to approve an event look
- operationally useful for Locally Twisted's sales follow-up

Avoid:

- rainbow banner UI as the main brand language
- generic party-store styling
- sterile retail-only design that makes LT feel like a commodity catalog
- pretending a planning rendering is a final engineering blueprint
- physics-breaking balloon layouts that Jeff would reject

## Current Source Material

Primary research:

- `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md`
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md`
- `research/contest-customizable-event-decor-tool/BRIEF.md`
- `research/contest-customizable-event-decor-tool/_render/contestant-1/`
- `research/contest-customizable-event-decor-tool/_render/contestant-2/`
- `research/contest-customizable-event-decor-tool/_render/contestant-3/`
- `research/contest-customizable-event-decor-tool/_render/contestant-4/`

Brand and launch context:

- `workstreams/brand-audience-style-reset.md`
- `workstreams/launch-v1-success-contract.md`
- `workstreams/website-launch.md`
- `_resources/STYLE-GUIDE.md`
- `_resources/STYLE-GUIDE.md` version 4.2 or newer for the current Civic Celebration + Slate Blue/Berry + Brand Direction visual contract. The old `_resources/design-guide/` synthesis was deleted on 2026-05-05 and must not be used.

Use these files as evidence and source material, not automatic truth. If a claim affects build behavior, verify it against current files, business approval, or the running ERPNext app.

## Contest Synthesis

The prior contest should be synthesized, not copied.

Keep:

- C1: `pieces considered` sales-context payload and per-piece attribution.
- C2: cascading suggested pieces that inherit the customer's palette.
- C3: dual-audience completion summary for both customer and Locally Twisted sales follow-up.
- C4: visual style cards and low-cognitive-load choices.

Replace:

- toy-like visual language
- rainbow-first banner styling
- simplified balloon illustrations that do not respect professional construction
- any UX that makes a complex corporate installation feel like a casual kids' coloring page

## Frappe-Native North Star

The production implementation should stay inside the Locally Twisted Frappe app.

Probable production shape:

- Public route: `/plan-custom-decor`
- Frappe page file: `apps/locally_twisted/locally_twisted/www/plan_custom_decor.html`
- Optional controller: `apps/locally_twisted/locally_twisted/www/plan_custom_decor.py`
- Optional route alias in `website_route_rules` from `/plan-custom-decor` to `plan_custom_decor`
- Public JS: `apps/locally_twisted/locally_twisted/public/js/design_studio/`
- Public CSS: app CSS included through hooks, not ad hoc `head_html` injection
- Backend methods: whitelisted Frappe methods for save, share, and submit
- Data model: a future `LT Decor Design` or similar DocType with child rows for pieces, colors, scale, organization palette, considered pieces, and stakeholder/share state
- CRM handoff: on submission, create or update an ERPNext Lead with a plain-language design summary and structured design payload

Preferred frontend technology for the first prototype:

- vanilla JavaScript
- Frappe/jQuery only where it matches local app patterns
- inline SVG or canvas only where useful for rendering
- no React or separate build pipeline unless explicitly approved later

## First Prototype Boundary

The first interactive prototype started narrow, then was corrected after GL review.

Corrected prototype coverage:

1. Classic arch
2. Classic column
3. Organic garland
4. Backdrop wall
5. Balloon drop

Reason for correction: the studio quality step must represent customizable product families with large variant spaces and their construction rules. Organic garland and balloon drop cannot be faked or deferred if the review question is whether the design surface respects base products and balloon construction math.

Recommended initial capabilities:

- choose event context
- choose one primary piece
- add complementary pieces
- choose an organization color palette
- map organization colors to closest LT balloon colors
- show scale references
- show a summary card
- capture `pieces considered`
- produce a shareable/savable design payload shape

Do not start with every catalog product, every style, every add-on, or final pricing.

## Agent Team Model

One controller owns this workstream and integration. Side agents should be used for bounded research and spec tasks first.

| Lane | Output | Write scope |
|---|---|---|
| Physics | `research/design-studio-v2/design-studio-physics-rules.md` | Research/spec only |
| UX/Product | `research/design-studio-v2/plan-custom-decor-flow.md` | Research/spec only |
| Visual Brand | `research/design-studio-v2/design-studio-visual-direction.md` | Research/spec only |
| Frappe Architecture | `research/design-studio-v2/frappe-native-design-studio-architecture.md` | Research/spec only |
| QA/Audit | `research/design-studio-v2/design-studio-risk-audit.md` | Research/spec only |
| Controller | This file and integration summary | `workstreams/design-studio-v2.md` |

Prototype implementation should wait until the first spec wave is reviewed and reconciled.

## First Spec Wave

First read-only/spec wave dispatched and completed 2026-05-02 by Codex.

| Lane | Agent | Output | Status |
|---|---|---|---|
| Physics | Pasteur / `019deaf6-583e-7923-8b37-3d6bfc04ef46` | `research/design-studio-v2/design-studio-physics-rules.md` | Complete |
| UX/Product | Kant / `019deaf6-a924-71d2-8dd1-c562d077e846` | `research/design-studio-v2/plan-custom-decor-flow.md` | Complete |
| Visual Brand | Singer / `019deaf6-f83c-7930-ac86-bc88355446d8` | `research/design-studio-v2/design-studio-visual-direction.md` | Complete |
| Frappe Architecture | Boole / `019deaf7-3b59-7690-9620-cfdaff65cb0d` | `research/design-studio-v2/frappe-native-design-studio-architecture.md` | Complete |
| QA/Audit | Carver / `019deaf7-86ac-7982-a3f8-085f8b644c6e` | `research/design-studio-v2/design-studio-risk-audit.md` | Complete |

## Controller Reconciliation

The five specs agree on the major direction:

- `Plan Custom Decor` should be the customer-facing path unless GL chooses another name; `Design Studio` can remain the internal feature name.
- V1 should not expose a half-working studio. If V1 references this idea, it should be a polished guided-inquiry path, not a live configurator promise.
- `Ready to Order` and `Plan Custom Decor` must stay separate in navigation, copy, payloads, and customer expectations.
- Corrected prototype scope should cover variant-heavy product families with distinct construction engines: classic arch, classic column, organic garland, backdrop wall, and balloon drop.
- Bouquets, pricing, quote generation, full catalog integration, photo uploads, and save-to-account should wait.
- The renderer must start from construction rules, especially 4-balloon cluster/quads for classic arches, columns, and backdrops.
- Color names are the production truth. Hex values are visual approximations until approved.
- Visual direction should be `Utah Event Authority Studio`: professional, civic, premium, restrained UI, with joy carried by the balloon work and event imagery.
- Production should stay Frappe-native: Frappe website route, vanilla JS/SVG/canvas where useful, whitelisted methods, future `LT Decor Design` storage, no separate frontend app unless later evidence proves it necessary.
- Save/share is strategically important but cannot be treated casually because stakeholder links can expose event context and contact-adjacent details.
- The preview must say, in plain language, that it is a planning visualization and that final design/install details are confirmed by Locally Twisted.

Main contradictions resolved:

- Contest visuals are not the brand direction. Keep the mechanics, replace the toy-like/rainbow-first presentation.
- Contest `Send to Jeff` copy becomes company-centered language such as `Send this plan to Locally Twisted` or `Send this plan to our team`.
- The contest's Frappe-recreatable claims prove only feasibility of simple mockups, not production persistence, permissions, share links, privacy, or CRM integration.
- Frappe file naming should use `plan_custom_decor.html` with a route alias for `/plan-custom-decor`, rather than a hyphenated file name.

Prototype should not start until GL/controller accepts this reconciliation.

## Agent Rules

Every design-studio agent must follow these rules:

- Stay read-only unless specifically assigned a write scope.
- Do not edit V1 launch-critical routes or files.
- Do not modify `C:\Users\baenb\projects\locally-twisted-odoo\`.
- Do not treat contest artifacts as final product direction.
- Keep Jeff as the owner/process source, not the brand center.
- Use "Locally Twisted" and "we/us" framing for customer-facing direction.
- Keep balloon decor construction separate from balloon twisting.
- Say what is verified, inferred, or still needing GL/Jeff approval.
- Prefer Frappe-native implementation assumptions.
- When describing git or project state, use concrete wording such as active work in progress, uncommitted changes, existing edits, needs review before editing, not launch-ready, possible overlap, or reconciliation needed.

## Quality Gates

Before this can move from background concept to implementation:

- Physics rules are explicit enough that bad renderings can be rejected.
- UX flow clearly separates ready-to-order ecommerce from custom decor planning.
- Visual direction aligns with the premium/civic/professional brand reset.
- Frappe architecture does not require a separate SaaS app or fragile external runtime.
- CRM payload shape is useful for Locally Twisted sales follow-up.
- V1 launch risk is unchanged.

Before this can move from prototype to production:

- Desktop and mobile layouts are verified.
- Accessibility basics are verified.
- Rendered examples do not violate known balloon construction rules.
- Save/share behavior works or is deliberately disabled.
- Lead/CRM handoff has loud failure behavior.
- The tool makes clear that it is a planning visualization, not a guaranteed final engineering drawing.

## Open Decisions

- Customer-facing name: `Plan Custom Decor`, `Design Studio`, or another label.
- Whether V1 should mention the future studio or only provide a polished guided-inquiry path.
- Which corrected product families should move beyond prototype quality review.
- Whether share links should be public token links, account-only saved designs, or both.
- Which Locally Twisted balloon color hex approximations are approved for customer-facing matching.
- Which scale references are acceptable for corporate, school, civic, parade, venue, church, and private event contexts.
- What exact disclaimer should appear near generated planning visuals.
- Whether customers should see construction/balloon counts or whether that stays internal.

## Next Action

Prototype status: corrected review-grade dormant static prototype built under `research/design-studio-v2/prototype/`. It is not production-integrated and does not touch V1 launch routes.

Engine spike status: research-only PlayCanvas/Babylon.js event-builder comparison built under `research/design-studio-v2/event-builder-spike/`. See `workstreams/event-builder-spike.md` for the feature handoff and verification receipts. Both engines passed the verifier; under the agreed decision rule, PlayCanvas is the recommended default for a future hidden Frappe-route spike.

Current review package:

- `research/design-studio-v2/prototype/index.html`
- `research/design-studio-v2/prototype/REVIEW-QA.md`
- `research/design-studio-v2/prototype/verify_review_grade.js`

Latest correction: renderer physics were tightened after GL feedback. Classic arch now uses 200-balloon / 50-cluster math for a 25 ft 11 inch structured arch, and the default spiral is a two-color candy-cane band model. Organic garland now uses strip-backbone density with 11 inch body balloons, 16/24 inch anchors, 5 inch filler, and 10-15% planning overage.

Next review should decide whether the product-family model, corrected construction engines, renderer assumptions, disclaimer, color catalog, size limits, and customer-facing `Plan Custom Decor` naming are strong enough for a hidden Frappe-route spike. Production save/share/Lead behavior remains out of scope until approved separately.
