# Ecommerce Operator Hardening Lane Charter

Date: 2026-06-30

Status: active feature lane setup.

## Purpose

Make the LT ecommerce shop owner-operated. A normal authorized backend user should be able to create and maintain products, prices, photos, variants/options, add-ons, visibility, and product-page content without an AI agent or developer touching raw ERPNext tables for routine work.

The lane exists because the current shop has important pieces, but they are not connected into a complete business workflow. Product Setup can author local product intent, raw catalog edits are guarded, cart and checkout can resolve server-side prices, and media/configuration payloads exist. The missing part is the coherent owner operation layer that projects those changes live, proves them, and fails loudly when incomplete.

## What "ERPNext Is Not Enough" Means

It does not mean "throw ERPNext away." It means ERPNext's stock ecommerce/Item model is only the accounting and catalog substrate.

LT needs behavior ERPNext does not supply by default:

- owner-friendly Product Setup for business meaning;
- SKU-defining vs configuration-only option classification;
- high-cardinality customization without variant explosion;
- selected-option and variant-specific media behavior;
- source-correct price projection to Item Prices;
- add-on line expansion and approval;
- public route/shop/card/product-page projection;
- cart, checkout, Sales Order, payment, invoice, and receipt preservation;
- live proof and operator-visible failure states.

ERPNext remains the backend of record for Items, Website Items, Item Prices, Sales Orders, invoices, and accounting. LT must provide the ecommerce operating layer on top.

## Route Record

```markdown
Mode: real multi-agent triad plus expedition synthesis
Decision needed: how to turn LT ecommerce from developer-operated scaffold into owner-operated shop infrastructure
Scope owner: Locally Twisted ecommerce feature lane
System/project/runtime classification: single project + client/production surface + external research
Allowed actions: repo reads, public/official docs research, local evidence mapping, lane documentation
Forbidden actions: live provider mutation, logged-in account changes, product writes, deploys, payment changes, secret reads
Evidence bar: source-separated local code proof, prior-research evidence, official docs, and live public-route proof where available
Stop condition: stop before implementation or live changes until a scoped build packet and approval exist
```

## Operating Principles

- Owner workflow is the product. If the owner cannot use it, the ecommerce system is not done.
- Product Setup is the normal owner surface; raw ERPNext catalog tables are protected projections.
- Save/publish must either reflect publicly after validation/proof or clearly say it did not.
- Only SKU-defining axes become variants. Configuration, colors, measurements, uploads, review-only choices, and most add-ons are structured line payloads or quote context.
- Price truth starts at owner/source intent and must cascade through public page, cart, checkout, Sales Order, payment, invoice, and receipt.
- Media truth includes primary image, gallery, selected variant image, cart image, payment image, and receipt/customer image where applicable.
- Existing docs and handoffs are claims. Current repo, authenticated DB, public render, and official docs outrank stale notes.

## Lane Boundaries

In scope:

- Product creation and product maintenance workflows.
- Price editing and projection.
- Variant/configuration/add-on architecture.
- Product media, main image, gallery, and selected-option/variant images.
- Public projection to shop cards, product pages, cart, checkout, documents, and payment surfaces.
- Research from prior ERP backend and other ecommerce systems, translated into LT-native architecture.
- Significant-change register and implementation milestones.

Out of scope until separately approved:

- Payment provider enablement or live checkout exposure.
- DNS/Frappe Cloud release actions.
- Live product mutation.
- Full platform migration away from ERPNext.
- Copying code, names, paths, or implementation from the prior ERP source.

## Required Research Lanes

- Ground truth lane: current LT code, doctypes, templates, APIs, verifiers, live route evidence.
- Prior-research lane: local prior ERP research and historical LT ecommerce audit docs, sanitized into architecture lessons.
- External lane: official docs or primary repos for ecommerce systems with product variants/options/media/pricing/publishing workflows.

## Current Default Decisions

- Future target: SKU-only variants plus structured configuration.
- Product Setup becomes the owner source of truth.
- Raw ERPNext catalog edits remain guarded.
- "Immediate" live change means validated projection plus cache clear and public proof for approved users; unsupported or failed projection must be loud.
- Existing 10k+ variants are treated as migration debt, not the desired future shape.
