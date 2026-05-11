# Locally Twisted Capabilities

This is the shared project capability index for Locally Twisted. It is not
owned by Codex, OpenClaw, Claude, or any one agent. Read it on arrival when the
task depends on reusable LT operating knowledge, then open only the capability
files needed for the current task.

## Root Label

- Purpose: reusable Locally Twisted project operating knowledge, route/layout
  contracts, ERPNext/Frappe implementation patterns, project-specific Failure
  Recipes, and verification guidance.
- Belongs here: LT-specific public-site, ecommerce, ERPNext, paperwork,
  automation, catalog, design, and verification knowledge.
- Does not belong here: systemwide user/process rules, agency-wide standards
  that apply to all clients, secrets, private customer records, raw runtime
  logs, or agent auth/session material.
- Related roots: system/user root
  `C:\Users\baenb\capabilities\INDEX.md`, agency root
  `C:\Users\baenb\projects\Built_by_Cameron\capabilities\INDEX.md`, and source
  package `C:\Users\baenb\projects\capabilities-framework\capabilities\INDEX.md`.

## How To Use This

- Skim the layers below. Know the territory.
- When you reach for help, scan the layer that fits. Do not read every file.
- For known-risk surfaces or familiar failure patterns, check `failures/`
  before recipes.
- When you discover or verify a new capability, add the file in the matching
  layer folder and add the one-liner here.
- Half-formed ideas go in `kitchen/`.
- Dead ends and recurring Failure Recipes go in `failures/`.
- Evidence-backed use, upvotes, downvotes, failures, fixes, and promotions go
  in `evidence/`.

## Capability Lifecycle

This root follows the shared capability schema v2.2. Older files remain
usable as legacy cards, but `currently_true`, `verified`, and `staple` require
new evidence in the stated scope. Do not promote old LT cards from memory alone.

## Principles

- System rule: `C:\Users\baenb\capabilities\principles\no-monolith-files.md` - do not create or expand hand-authored production monoliths; split by clear responsibility unless the file is research/reference material.

## Ingredients

The smallest reusable units. One tool, one command, one MCP server, or a thin
combination.

- [screenshot](ingredients/screenshot.md) - capture the live screen to a file you can read.

## Recipes

Workflows. Multi-step. Clear start and finish.

- [erpnext-ecommerce-receiving-architecture](recipes/erpnext-ecommerce-receiving-architecture.md) - design the ERPNext-side ecommerce receiving ecosystem before importing Odoo-derived products: fields, logic, variants, add-ons, pricing, media, cart, checkout, invoice, mobile/desktop journeys, fail-loud gates, and the current paused-public-commerce boundary (`lt_ecommerce_paused=1`).

- Agency reference: `C:\Users\baenb\projects\Built_by_Cameron\capabilities\recipes\frappe-default-surface-map.md` maps Frappe/Webshop native spacing, wrappers, headings, chrome, and CMS defaults to the usual BBC override moves.
- [claude-reference-library](recipes/claude-reference-library.md) - safely consult older Claude skills/rules as reference material without treating them as truth or copying them wholesale.
- [codex-browser-verification-surface](recipes/codex-browser-verification-surface.md) - choose between public web lookup, silent Playwright render proof, LT route-contract verifiers, and headed browser checks without mixing evidence types.
- [btfp-live-service-page-contract](recipes/btfp-live-service-page-contract.md) - keep the Twisting & Face Painting route, shared inquiry form, and per-artist pricing calculator aligned with the approved business lane.
- [customer-email-delivery-branding-contract](recipes/customer-email-delivery-branding-contract.md) - keep public inquiry email branding, company-copy routing, role inboxes, and Email Queue proof aligned without confusing sent status for delivery.
- [erpnext-business-automation-index](recipes/erpnext-business-automation-index.md) - index ERPNext/Frappe business automations by connected, partially connected, required-missing, useful-missing, fake-data, and loud-failure status.
- [erpnext-catalog-variant-price-parity](recipes/erpnext-catalog-variant-price-parity.md) - audit and repair ERPNext Item variant prices from Odoo's dynamic resolver instead of page base price.
- [erpnext-finance-controlled-automation](recipes/erpnext-finance-controlled-automation.md) - build ERPNext finance/payroll migration surfaces with review queues and accountant approval gates before automation.
- [erpnext-maintenance-heartbeat-boundary](recipes/erpnext-maintenance-heartbeat-boundary.md) - expose scheduled ERPNext maintenance status through sanitized heartbeat records and a narrow role instead of raw logs or broad admin access.
- [erpnext-no-live-customer-reminders](recipes/erpnext-no-live-customer-reminders.md) - prepare customer reminder review queues, cadence suggestions, and blockers without live sending or accounting mutation.
- [external-document-audience-contract](recipes/external-document-audience-contract.md) - build invoices, receipts, proposals, and external packets around the recipient's workflow before brand flourish.
- [erpnext-category-media-approval](recipes/erpnext-category-media-approval.md) - prepare, approve, dry-run, and apply ERPNext Item Group category images without assigning browse media by guess.
- [erpnext-checkout-commerce-rules](recipes/erpnext-checkout-commerce-rules.md) - keep mixed goods/service checkout, delivery fees, deposits, and taxable-line rules aligned in ERPNext/Frappe when checkout is explicitly in scope.
- [erpnext-crm-pipeline-safety](recipes/erpnext-crm-pipeline-safety.md) - translate client-friendly CRM/Kanban stages without corrupting ERPNext native status, finance, or reporting behavior.
- [erpnext-intake-form-parity](recipes/erpnext-intake-form-parity.md) - keep public inquiry forms, ERPNext Lead fields, submit mapping, and Desk operator UX aligned.
- [shared-inquiry-form-experience](recipes/shared-inquiry-form-experience.md) - keep the shared `inquiry-v1` public form honest: backend-proven success only, accessible on-page modal, safe failure copy, and no overlaying cookie notice.
- [erpnext-simplified-role-verification](recipes/erpnext-simplified-role-verification.md) - verify a simplified ERPNext backend role from login through workspace, shortcuts, permissions, and real records.
- [external-design-reference-translation](recipes/external-design-reference-translation.md) - translate Claude/designer/prototype reference code into Frappe-owned production files without silently changing the approved visual contract.
- [fail-loud-operating-law](recipes/fail-loud-operating-law.md) - make forms, automations, documents, containers, and agent claims block false success with actionable failures and verifier evidence.
- [lt-frappe-erpnext-quirks-library](recipes/lt-frappe-erpnext-quirks-library.md) - candidate triage card for LT stack quirks (status, symptom, cause, guardrail, verifier) to check before repeating old framework mistakes.
- [large-source-document-intake](recipes/large-source-document-intake.md) - chunk and source-map large LT reference documents before using them for catalog, policy, checkout, or migration claims.
- [launch-repo-cleanup-and-evidence-retention](recipes/launch-repo-cleanup-and-evidence-retention.md) - clean launch repo debris, raw drops, generated evidence, stale mirrors, and historical experiment output without deleting active source or other-agent work.
- [erpnext-record-level-failure-recorder](recipes/erpnext-record-level-failure-recorder.md) - give partial backend failures one durable blocker/report contract on affected ERPNext records.
- [frappe-public-container-contract](recipes/frappe-public-container-contract.md) - keep Frappe/Webshop page lifecycle while making every LT public section choose contained workflow/reading mode or deliberate full-bleed band mode.
- [homepage-launch-proof-contract](recipes/homepage-launch-proof-contract.md) - keep the launch homepage stable, real-photo-led, compact on mobile, full-stage proof-crawl driven, and free of overlay/cycling regressions.
- [frappe-shop-showroom-symmetry](recipes/frappe-shop-showroom-symmetry.md) - keep shop/category/product showcase layouts photo-led, with rail/dropdown category navigation and no avoidable single-card orphan rows.
- [frappe-product-page-company-first](recipes/frappe-product-page-company-first.md) - keep Webshop product detail pages focused on product clarity and company proof, without generic ecommerce recommendation panels or empty visible boxes.
- [frappe-product-clear-control-contract](recipes/frappe-product-clear-control-contract.md) - keep product options, variant chips, selects, and price/add-to-cart groups clear instead of boxed; pickup/delivery is the approved framed exception.
- [frappe-portfolio-proof-reel](recipes/frappe-portfolio-proof-reel.md) - keep LT's portfolio as a compact native-shell proof collage with large whole photos, center balance, and no wholesale prototype styling.
- [frappe-public-storefront-security](recipes/frappe-public-storefront-security.md) - review and harden public Frappe/Webshop inputs, uploads, receipt pages, preview bridges, and checkout trust boundaries.
- [frappe-public-nav-business-route-contract](recipes/frappe-public-nav-business-route-contract.md) - keep public nav/header/footer route links, mobile drawer search, and approved business lanes aligned while blocking unapproved route replacements.
- [frappe-sitewide-visual-overhaul](recipes/frappe-sitewide-visual-overhaul.md) - ship a Frappe/Webshop visual redesign with cache-busts, route checks, screenshots, and launch-safe receipts.
- [public-site-microinteraction-contract](recipes/public-site-microinteraction-contract.md) - keep small public-site interactions such as card-wide navigation launch-safe, accessible, and free of prototype/demo source drift.
- [lt-brand-copy-audience-pages](recipes/lt-brand-copy-audience-pages.md) - keep Event Balloons audience-page copy company-first, buyer-aware, proof-led, and quote-led without founder-only or product-purchase drift.
- [lt-seo-geo-aeo-contract](recipes/lt-seo-geo-aeo-contract.md) - keep canonical routes, sitemap, metadata, JSON-LD, FAQ visible questions, and technical discovery verifiers in parity.
- [lt-brand-style-guide-consolidation](recipes/lt-brand-style-guide-consolidation.md) - consolidate LT visual authority, delete conflicting style references, and verify old font/pastel/icon drift is gone.
- [cross-browser-motion-visual-verification](recipes/cross-browser-motion-visual-verification.md) - verify animated, marquee, carousel, reduced-motion, and browser-session visual behavior across Chrome/Brave and media-query branches.
- [compact-hero-contract](recipes/compact-hero-contract.md) - keep public page heroes compact, same-height per viewport family, and protected by Playwright checks instead of route-local oversized padding.
- [responsive-container-audit](recipes/responsive-container-audit.md) - audit public routes and stateful UI across breakpoint edges so text, controls, menus, forms, cards, and product selectors stay inside their containers.
- [take-live-coordinated-workflows](recipes/take-live-coordinated-workflows.md) - coordinate multi-agent launch lanes with controller ownership, review gates, and release verification.
- [visual-debugging](recipes/visual-debugging.md) - see what the user sees without asking them to describe it.
- [deploy-static-site-to-cloudflare](recipes/deploy-static-site-to-cloudflare.md) - get a Hugo/Astro/Next-static site live on a custom domain.

## External Design-Studio Capabilities

Moved on 2026-05-11: reusable Event Playground / Plan Custom Decor design capabilities now live in `C:\Users\baenb\projects\design-studio\capabilities\recipes\`. Do not recreate local LT copies unless GL explicitly wants a Frappe implementation contract fork.

- `balloon-material-visual-physics.md`
- `event-playground-construction-truth.md`
- `event-playground-planning-contract.md`
- `playcanvas-event-builder-stage-physics.md`
- `prototype-engine-spike-verification.md`

## Meals

End-to-end compositions of recipes. The shape of a complete piece of work.

- [ship-internal-tool](meals/ship-internal-tool.md) - go from "I need a thing" to "the thing is in production and I can hand it to a colleague."

## Kitchen

[kitchen/](kitchen/) - capabilities being figured out. Promote to a layer when
ready, or move to `failures/` if it did not pan out.

## Failures / Failure Recipes

Dead ends, recurring failure patterns, regressions, and process failures. Read
this layer before recipes when a task touches LT public chrome, route contracts,
approval gates, verifier expectations, payments, customer communication, or any
pattern that feels familiar.

- [failures/](failures/) - Failure Recipes overview, dead-end convention, and template.
- [public-nav-seo-verifier-drift](failures/public-nav-seo-verifier-drift.md) - prevents SEO/GEO/AEO or verifier work from changing header/footer/menu/search public chrome without explicit approval.
- [public-header-contrast-safe-area-regression](failures/public-header-contrast-safe-area-regression.md) - prevents gold header banner hover/focus contrast and mobile safe-area side-order regressions.

## Evidence And Registry

- [evidence/](evidence/) - compact append-only events for use, upvotes, downvotes, failures, fixes, and promotions.
- [registry/](registry/) - generated compact retrieval indexes.

## Reading Order On Arrival

1. Skim this index.
2. Open the layer folder that matches today's task.
3. When in doubt, check `kitchen/` for in-progress notes that might help.
4. Before pursuing an approach that feels familiar, changing a guard/verifier,
   or touching a known-risk surface, check `failures/`.
5. Before trusting a capability as proven, check maturity and evidence.
