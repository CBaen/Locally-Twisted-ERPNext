# Locally Twisted Three-Brand Boundary

Last updated: 2026-06-28.

## Current Contract

Locally Twisted is the accounting and ERPNext operating company for three
customer-facing DBA/service brands:

- `locally_twisted` - the public Locally Twisted event, balloon decor, balloon
  twisting, face painting, ecommerce, and family/private-event brand.
- `commercial_balloon_decor` - the commercial/corporate decor brand for
  premium installed event work and commercial lead generation.
- `memorial_balloons` - the memorial/funeral tribute brand for celebration of
  life and funeral-facing work.

These are separate brand lanes under the same real-world accounting operation.
Do not treat one brand's facts, style, assets, copy, emails, websites, portals,
forms, Meta/ad state, invoices, or automation decisions as global truth for the
others.

No fourth brand lane is approved in current scope. If a fourth lane appears in
old notes, brainstorms, copied docs, or repo names, treat it as unapproved until
Guiding Light explicitly reopens it.

## ERPNext Boundary

Current planning assumes one ERPNext accounting company/back office, not a new
ERPNext system per DBA/service brand. The implementation still needs source and
runtime work before that is safe:

- add a first-class `operating_brand` concept with the exact allowed values
  above;
- carry that value through Lead, Quotation, Sales Order, Sales Invoice, Payment
  Request, Stripe/payment metadata, outbound emails, print formats, portal
  files, tracking, and review queues;
- resolve brand from route/domain/source record instead of inferring from
  whichever doc an agent read first;
- fail closed when a customer-facing, accounting, portal, ad, or automation
  surface cannot identify its brand lane.

Do not create a separate ERPNext company, site, payment account, Meta asset,
domain routing rule, invoice template, or portal model for a brand lane without
fresh approval and proof that it will not cross-contaminate the other lanes.

## Source Priority

Use this priority when brand-scope documents conflict:

1. Guiding Light's newest explicit correction in the current conversation.
2. This file and `capabilities/recipes/three-brand-dba-boundary-contract.md`.
3. The active brand repo's `AGENTS.md`, decision log, queue, and index.
4. Runtime/source proof from the current repo or verified ERPNext state.
5. Older workstreams, handoffs, research notes, copied docs, and stale
   worktrees as evidence only.

If a doc says Memorial Balloons is separate from Locally Twisted, read it as an
older launch-cleanup boundary: Memorial work was not part of that LT launch
slice. It is not current authority that Memorial Balloons is outside the
Locally Twisted accounting operation.

If a doc says Commercial Balloon Decor should use Locally Twisted resources, do
not collapse the brand lane. It means CBD can use the shared back office after
brand-safe routing, not that its website, copy, trust assets, invoices, or
customer portal can inherit LT defaults blindly.

## Guardrail For Future Agents

Before changing any website, invoice, customer email, portal, payment,
checkout, ad, tracking, lead, file, or automation surface, state which operating
brand the work belongs to and which source proved it.

When in doubt, stop at documentation or static verification. Do not make live
ERPNext, Meta, payment, DNS, customer-data, provider, or account-access changes
to "clean up" brand confusion.
