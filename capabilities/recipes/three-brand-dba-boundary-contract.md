---
id: three-brand-dba-boundary-contract
name: Three-Brand DBA Boundary Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted operating-company boundary across the Locally Twisted, Commercial Balloon Decor, and Memorial Balloons brand lanes
currently_true: true
verification_level: 1
last_verified: 2026-06-28
evidence_quality: direct-user-correction-plus-repo-audit
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - current-truth-needs-evidence
  - customer-client-portal-contract
  - customer-email-delivery-branding-contract
  - external-document-audience-contract
tags:
  - Locally Twisted
  - DBA
  - operating brand
  - ERPNext
  - guardrail
---

# Three-Brand DBA Boundary Contract

Use this recipe before changing any source, docs, website, ERPNext, portal,
invoice, checkout, payment, email, tracking, Meta, lead, file, or automation
surface that could cross Locally Twisted, Commercial Balloon Decor, or Memorial
Balloons.

## Current Contract

Guiding Light's current shape is one Locally Twisted accounting operation with
three separate DBA/service brand lanes:

- `locally_twisted`
- `commercial_balloon_decor`
- `memorial_balloons`

The lanes share back-office ownership/accounting only after explicit routing.
They do not share public copy, styling, websites, trust assets, invoice
appearance, customer portal context, advertising posture, customer files, or
automation defaults by assumption.

No fourth brand lane is approved in this scope.

## Required Agent Behavior

For any affected work, name the brand lane before editing:

- If the answer is `locally_twisted`, use Locally Twisted style, public copy,
  products, event policies, Meta assets, and website behavior only.
- If the answer is `commercial_balloon_decor`, use the commercial buyer,
  corporate/event-installation, quote-first, premium lead-gen lane only.
- If the answer is `memorial_balloons`, use the funeral/memorial tribute lane
  only and do not expose Locally Twisted branding in funeral-facing copy unless
  explicitly approved for legal or back-office context.

If the brand lane is unclear, do not infer it from a stale handoff, search hit,
asset name, repo proximity, or ERPNext default company. Stop and ask or create a
static blocker.

## ERPNext Implementation Direction

The durable implementation should introduce an `operating_brand` field/registry
with exactly these values:

- `locally_twisted`
- `commercial_balloon_decor`
- `memorial_balloons`

2026-07-07 same-bench update: Memorial Balloons should use the same Frappe
Cloud bench as Locally Twisted. Same bench is the backend/operations decision,
not public-brand merger approval. Future Memorial implementation should stay on
the shared bench/back-office path while using separate Memorial public routes,
templates, header/footer, products, forms, customer emails, external documents,
portal/file context, and search metadata. Brand resolution must come from
domain/route/source record and fail closed before a customer-facing,
accounting, portal, email, payment, file, or automation record is created.

The value should be required or resolved fail-closed for:

- public routes, forms, and source pages;
- Lead, Quotation, Sales Order, Sales Invoice, Payment Request, and related
  review queues;
- Stripe/payment metadata and return pages;
- outbound document registry/templates, Email Queue contexts, and print
  formats;
- customer portal files, account pages, organization memberships, and visible
  data summaries;
- Meta/ad tracking, pixels, lead forms, and conversion events.

## Hidden Exposure Map

The 2026-06-28 triad audit found these common failure paths:

- older LT launch-cleanup docs saying Memorial Balloons is separate from LT;
- `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md` using old
  "multi-company" rejection language that predates the DBA/brand-lane shape;
- style and email docs saying "Locally Twisted is the brand" without scoping
  that to the LT public brand lane;
- portal, document, checkout, payment, and email code paths that currently
  assume global LT branding;
- Meta operation docs that are broad LT-owned access docs, not CBD or Memorial
  campaign approval;
- stale or quarantined sibling repo worktrees that look more current than they
  are.

## Verification Pattern

Before live or customer-facing brand-lane work, add or run a verifier that
checks the exact lane involved. Useful verifier families:

- static hard-coded brand literal scan;
- Lead -> Quote -> Sales Order -> Invoice -> Payment Request -> Stripe metadata
  inheritance;
- invoice/email/print rendering by operating brand;
- portal account/file isolation by operating brand;
- route/domain/source-record brand resolver;
- Meta tracking/campaign/lead-form separation;
- "single accounting company, three operating brands only" assertion.

Until those verifiers exist and pass, treat runtime multi-brand support as a
planned architecture direction, not proven production behavior.
