# Three-Brand DBA Boundary Guardrail - 2026-06-28

## Decision

Guiding Light clarified the operating shape: Locally Twisted is the existing
accounting/ERPNext company for three DBA/service brands:

- Locally Twisted
- Commercial Balloon Decor
- Memorial Balloons

These brands need separate public lanes, branding, styling, websites,
automations, portals, customer documents, ads, and source-of-truth paths. They
should not be merged by accident just because they share ownership and
accounting.

The fourth possible brand is not in current scope.

## Triad Review Result

Three real review lanes were used:

- documentation/instruction exposure lens;
- ERPNext/Frappe implementation exposure lens;
- sibling repo and stale-worktree exposure lens.

Shared conclusion: the main risk is accidental authority. Old docs, launch
cleanup notes, global style rules, stale worktrees, and single-brand ERPNext
code can look like the most relevant source and cause an agent to collapse the
brands or over-separate the accounting.

## Exposures Found

- LT launch-cleanup and handoff docs said Memorial Balloons was separate from
  the LT launch repo. That remains true for that old launch-cleanup slice, but
  it is not current authority that Memorial Balloons is outside the Locally
  Twisted accounting operation.
- `.planning/PROJECT.md` and `.planning/REQUIREMENTS.md` rejected
  "multi-company in one ERPNext site" before the current DBA/service-brand
  distinction existed.
- `_resources/STYLE-GUIDE.md` correctly says Locally Twisted is the brand for
  LT public surfaces, but that sentence is unsafe if applied globally to CBD or
  Memorial.
- Customer portal, email, outbound document, checkout, payment, and Meta docs
  are currently written for the LT brand lane and need an operating-brand
  resolver before they can safely serve all three brands.
- Active sibling repos exist at `/home/guidingl/projects/commercial-balloon-decor`
  and `/home/guidingl/projects/memorial-balloons`.
- A stale nested CBD repo exists at
  `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/commercial-balloon-decor`.
  It is not the current active CBD root.
- A Memorial draft worktree at
  `/home/guidingl/agent-worktrees/memorial-balloons/codex-20260625-memorial-balloons-redesign__new-site`
  remains quarantined/unapproved.

Search recovery note: broad repo searches were too large for terminal output,
so the full result sets were recovered into `/tmp/lt-three-brand-doc-exposure.rg`
and `/tmp/lt-three-brand-code-exposure.rg` during this session. The recovered
line counts were 2,886 doc/instruction hits and 1,102 code/setup/verifier hits.

## Guardrails Installed

- Root contract: `BRAND-BOUNDARY.md`.
- Capability recipe:
  `capabilities/recipes/three-brand-dba-boundary-contract.md`.
- Arrival and index docs point future agents to the contract.
- Portal, email, external-document, outbound-document, Meta, planning, queue,
  decisions, lessons, and launch-cleanup docs received dated scope notes.
- Sibling active roots received their own `BRAND-BOUNDARY.md` guard files.
- The nested stale CBD copy received a stale-copy warning.

## Next Safe Implementation Step

Build a static operating-brand exposure verifier before runtime changes. The
first verifier should scan hard-coded brand literals and source surfaces that
create customer-facing pages, emails, documents, checkout/payment state, portal
files, Meta/tracking events, and ERPNext records. It should fail when a surface
could cross brand lanes without an explicit operating-brand source.

No live ERPNext, Meta, DNS, provider, payment, customer-data, access, campaign,
or publishing changes were part of this guardrail work.

## Deep Investigation Update

Date: 2026-06-28.

Triad/expedition result: the docs-level guardrail is real, but source-owned
runtime enforcement is not implemented yet. Current code does not define an
`operating_brand` registry, schema field, resolver, propagation rule, or
brand-scoped verifier across the customer, money, document, portal, tracking,
or Meta paths.

The only approved runtime enum values remain:

- `locally_twisted`
- `commercial_balloon_decor`
- `memorial_balloons`

Verified high-risk runtime surfaces still default to the Locally Twisted lane:

- public route rules and site context;
- Lead/contact intake and custom-field sync;
- Quote, Sales Order, Sales Invoice, Payment Request, checkout, Stripe session,
  Stripe webhook, and payment-success handling;
- customer email theme, invoice branding, outbound documents, print formats,
  and receipt/welcome subjects;
- customer portal summaries, portal files, and customer/contact-scoped
  visibility;
- marketing tracking settings and conversion/event attribution.

Important distinction: `commerce_lane`, event type, service type, client type,
source page, and corporate/private/memorial wording are not DBA brand identity.
They cannot be used as substitutes for `operating_brand`.

Resolved in this pass:

- added `scripts/verify/operating_brand_exposure_contract.py`;
- registered `test:operating-brand-exposure` in `package.json`;
- registered `lt-operating-brand-exposure-contract` in
  `verifier-manifest.json`;
- added active sibling boundary/capability guards in the CBD and Memorial
  repos;
- marked the nested CBD checkout as stale/reference in its exposed docs and
  verifier manifest;
- corrected the Memorial research brief so the historical source-system backend line
  cannot be treated as current ERP truth.

Still gated, not solved:

- live ERPNext custom fields, dimensions, filters, and record migrations;
- source/runtime `operating_brand` implementation;
- brand-safe invoice, email, print, portal, checkout, Stripe, tracking, and
  Meta behavior;
- exact public legal/operator/footer/invoice wording for CBD and Memorial;
- production domains, deployed contact-form behavior, Meta lead forms, pixels,
  ad accounts, and campaign creation.

Next implementation brief should start with a fail-closed operating-brand
registry and static schema verifier, then carry the value through Lead -> Quote
-> Sales Order -> Sales Invoice -> Payment Request -> Stripe metadata ->
webhook/payment success before any CBD or Memorial customer-facing money flow is
enabled.
