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
  `/home/guidingl/capabilities/INDEX.md` when present, agency root
  `/home/guidingl/projects/Built_by_Cameron/capabilities/INDEX.md`, and source
  package `/home/guidingl/projects/capabilities-framework/capabilities/INDEX.md`
  when present.
- Latest framework handoff:
  [capabilities-framework-v2-4-seed-update-2026-05-21](../workstreams/capabilities-framework-v2-4-seed-update-2026-05-21.md).
- Latest graduation handoff:
  [capability-graduation-ladder-2026-05-21](../workstreams/capability-graduation-ladder-2026-05-21.md).

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
- Use source/provenance metadata when a capability is borrowed, researched, inspired, agent-generated, or adapted from official docs/user practice; local proof still needs evidence.
- Use graduation metadata when a capability becomes backed by a skill,
  verifier, gate, automation, architecture, or release/live approval boundary.
- Use the project root `verifier-manifest.json` for LT verifier tiers. It is a
  manual-only map, not proof that checks passed and not permission to run live,
  staging, email, payment, or customer-data checks.

## Capability Lifecycle

This root follows the shared capability schema v2.5. Older files remain
usable as legacy cards, but `currently_true`, `verified`, and `staple` require
new evidence in the stated scope. Do not promote old LT cards from memory alone.
Graduation metadata is not trust proof; it points agents to the support system
that carries or should carry the capability.

## Atomic Ingredients

- [Evidence Ledger Event](atomic_ingredients/evidence-ledger-event.md) - compact evidence event for use, upvotes, downvotes, failures, fixes, and promotions.

## Principles

- System rule: `/home/guidingl/capabilities/principles/no-monolith-files.md` when present - do not create or expand hand-authored production monoliths; split by clear responsibility unless the file is research/reference material.
- [multi-agent-coordination-safety](principles/multi-agent-coordination-safety.md) - keep LT parallel-agent work inside the neutral claim/worktree workflow without leaking parent/company repo scope into LT tasks.
- [Current Truth Needs Evidence](principles/current-truth-needs-evidence.md) - prevents capability claims from becoming false certainty.
- [No Monolith Files](principles/no-monolith-files.md) - prevents hand-authored production files from becoming giant catch-all modules except research/reference artifacts.
- [Capability Evolution Gates](principles/capability-evolution-gates.md) - requires evidence, date, result, confidence, and rollback/revalidation for trust-bearing changes.
- [Agent-Centered Infrastructure](principles/agent-centered-infrastructure.md) - keeps framework decisions focused on what helps agents work efficiently and earn trust.
- [Capabilities Should Enhance, Not Become Chores](principles/capabilities-should-enhance-not-become-chores.md) - keeps the framework useful without turning it into paperwork.
- [Capability Graduation Ladder](principles/capability-graduation-ladder.md) - marks when LT capabilities should become skills, verifiers, gates, automations, architecture, or release/live approval boundaries.

## Ingredients

The smallest reusable units. One tool, one command, one MCP server, or a thin
combination.

- [screenshot](ingredients/screenshot.md) - capture the live screen to a file you can read.
- [gh-cli](ingredients/gh-cli.md) - use GitHub CLI for repo, PR, release, and workflow operations after identity is confirmed.
- [wrangler](ingredients/wrangler.md) - use Cloudflare Wrangler for Pages and Workers deployment tasks after account identity is confirmed.

## Recipes

Workflows. Multi-step. Clear start and finish.

- [erpnext-ecommerce-receiving-architecture](recipes/erpnext-ecommerce-receiving-architecture.md) - design the ERPNext-side ecommerce receiving ecosystem before importing or exposing legacy_source-derived products: fields, logic, variants, add-ons, pricing, media, cart, checkout, invoice, mobile/desktop journeys, fail-loud gates, live-exposure safety lock separation, and current product-scope proof.
- [erpnext-webshop-guest-party-contract](recipes/erpnext-webshop-guest-party-contract.md) - preserve and verify the `Guest` User/Customer/Portal User/Contact infrastructure that anonymous Webshop product pricing, variants, cart, and cleanup safety depend on.
- [erpnext-product-blueprint-authoring](recipes/erpnext-product-blueprint-authoring.md) - add staff-authored, local-only ERPNext product blueprints for highly customizable products, with validation, dry-run preview, guarded unpublished local apply, and fixed-price add-on runtime cascade proof.
- [erpnext-live-product-visibility-retirement](recipes/erpnext-live-product-visibility-retirement.md) - retire exact approved products from live visibility by disabling target Items/variants, keeping Website Items unpublished as `needs_review`, and proving route and `/shop` absence without weakening owner catalog guards.

- Agency reference: `C:\Users\baenb\projects\Built_by_Cameron\capabilities\recipes\frappe-default-surface-map.md` maps Frappe/Webshop native spacing, wrappers, headings, chrome, and CMS defaults to the usual BBC override moves.
- [ad-account-takeover-provider-control](recipes/ad-account-takeover-provider-control.md) - take control of Google Ads and Meta/Facebook/Instagram accounts from authenticated provider dashboards, keeping Gmail/Drive/report evidence as support only.
- [claude-reference-library](recipes/claude-reference-library.md) - safely consult older Claude skills/rules as reference material without treating them as truth or copying them wholesale.
- [codex-browser-verification-surface](recipes/codex-browser-verification-surface.md) - choose between public web lookup, silent Playwright render proof, LT route-contract verifiers, and headed browser checks without mixing evidence types.
- [btfp-live-service-page-contract](recipes/btfp-live-service-page-contract.md) - keep the Twisting & Face Painting route, shared inquiry form, and per-artist pricing calculator aligned with the approved business lane.
- [customer-email-delivery-branding-contract](recipes/customer-email-delivery-branding-contract.md) - keep public inquiry email branding, company-copy routing, role inboxes, and Email Queue proof aligned without confusing sent status for delivery.
- [customer-client-portal-contract](recipes/customer-client-portal-contract.md) - keep invite-only customer/client account routes, safe summaries, portal actions, file registration, organization access, visible logout exits, and branded account shell aligned.
- [erpnext-external-review-access](recipes/erpnext-external-review-access.md) - give outside website reviewers a no-Desk `Website User` lane with explicit narrow role membership, protected public review route, and backend record denial.
- [erpnext-external-marketing-access-reset](recipes/erpnext-external-marketing-access-reset.md) - create/audit controlled external marketing builder access and fail-loud branded reset emails without broad admin roles or token leakage.
- [erpnext-owner-business-access-api](recipes/erpnext-owner-business-access-api.md) - expose owner/support business actions through provider-neutral DTOs, phone-first local UI, fake local data, and assistant-ready read/write boundaries without raw ERPNext record access.
- [erpnext-inquiry-photo-delivery-contract](recipes/erpnext-inquiry-photo-delivery-contract.md) - keep public inquiry photo uploads aligned across Lead Files, CRM photo rows, customer count-only confirmations, and owner-only Email Queue attachment refs.
- [erpnext-business-automation-index](recipes/erpnext-business-automation-index.md) - index ERPNext/Frappe business automations by connected, partially connected, required-missing, useful-missing, fake-data, and loud-failure status.
- [erpnext-catalog-variant-price-parity](recipes/erpnext-catalog-variant-price-parity.md) - audit and repair ERPNext Item variant prices from legacy_source/source price enrichment instead of page base price.
- [erpnext-finance-controlled-automation](recipes/erpnext-finance-controlled-automation.md) - build ERPNext finance/payroll migration surfaces with review queues and accountant approval gates before automation.
- [erpnext-maintenance-heartbeat-boundary](recipes/erpnext-maintenance-heartbeat-boundary.md) - expose scheduled ERPNext maintenance status through sanitized heartbeat records and a narrow role instead of raw logs or broad admin access.
- [erpnext-no-live-customer-reminders](recipes/erpnext-no-live-customer-reminders.md) - prepare customer reminder review queues, cadence suggestions, and blockers without live sending or accounting mutation.
- [external-document-audience-contract](recipes/external-document-audience-contract.md) - build invoices, receipts, proposals, and external packets around the recipient's workflow before brand flourish.
- [erpnext-category-media-approval](recipes/erpnext-category-media-approval.md) - prepare, approve, dry-run, and apply ERPNext Item Group category images without assigning browse media by guess.
- [erpnext-checkout-commerce-rules](recipes/erpnext-checkout-commerce-rules.md) - keep mixed goods/service checkout, delivery fees, deposits, and taxable-line rules aligned in ERPNext/Frappe when checkout is explicitly in scope.
- [erpnext-crm-pipeline-safety](recipes/erpnext-crm-pipeline-safety.md) - translate client-friendly CRM/Kanban stages without corrupting ERPNext native status, finance, or reporting behavior.
- [erpnext-intake-form-parity](recipes/erpnext-intake-form-parity.md) - keep public inquiry forms, ERPNext Lead fields, submit mapping, and Desk operator UX aligned.
- [shared-inquiry-form-experience](recipes/shared-inquiry-form-experience.md) - keep the shared `inquiry-v1` public form honest: backend-proven success only, accessible on-page modal, safe failure copy, anti-bot token/honeypot, conservative sales-solicitation suppression, and no overlaying cookie notice.
- [erpnext-simplified-role-verification](recipes/erpnext-simplified-role-verification.md) - verify a simplified ERPNext backend role from login through workspace, shortcuts, permissions, and real records.
- [external-design-reference-translation](recipes/external-design-reference-translation.md) - translate Claude/designer/prototype reference code into Frappe-owned production files without silently changing the approved visual contract.
- [fail-loud-operating-law](recipes/fail-loud-operating-law.md) - make forms, automations, documents, containers, and agent claims block false success with actionable failures and verifier evidence.
- [mandatory-capability-context-gate](recipes/mandatory-capability-context-gate.md) - force LT agents to load the nearest capability index and a task-relevant recipe/failure/skill before edits, high-risk work, release action, or readiness claims.
- [lt-balloon-color-generated-hero-contract](recipes/lt-balloon-color-generated-hero-contract.md) - generate or revise LT balloon/category hero images from owner-approved color names and swatches, with hex values treated only as matching approximations.
- [lt-frappe-erpnext-quirks-library](recipes/lt-frappe-erpnext-quirks-library.md) - candidate triage card for LT stack quirks (status, symptom, cause, guardrail, verifier) to check before repeating old framework mistakes.
- [large-source-document-intake](recipes/large-source-document-intake.md) - chunk and source-map large LT reference documents before using them for catalog, policy, checkout, or migration claims.
- [launch-repo-cleanup-and-evidence-retention](recipes/launch-repo-cleanup-and-evidence-retention.md) - clean launch repo debris, raw drops, generated evidence, stale mirrors, and historical experiment output without deleting active source or other-agent work.
- [kubuntu-repo-recovery-cleanup](recipes/kubuntu-repo-recovery-cleanup.md) - reconcile LT source after Windows-to-Kubuntu or similar host moves by preserving real diffs, removing CRLF/LF-only churn, pruning stale worktree metadata, and proving fast local contracts before source archive.
- Agency reference: `/home/guidingl/projects/Built_by_Cameron/capabilities/recipes/kubuntu-client-runtime-doctor.md` explains the cross-client doctor pattern. LT's concrete doctor is `scripts/verify/kubuntu_doctor.py` and its manifest bundle is `lt-kubuntu-doctor`.
- [provider-release-surface-cleanup](recipes/provider-release-surface-cleanup.md) - inventory, label, retire, or delete Frappe Cloud sites/benches, app mirrors, temp clones, and release surfaces only after public-domain, provider, live-record, and source/app identity proof.
- [frappe-cloud-cloudflare-stripe-launch-gate](recipes/frappe-cloud-cloudflare-stripe-launch-gate.md) - coordinate Frappe Cloud staging, Cloudflare DNS/security, Stripe live readiness, human account access, and ecommerce fallback without treating preflight as cutover approval.
- [erpnext-record-level-failure-recorder](recipes/erpnext-record-level-failure-recorder.md) - give partial backend failures one durable blocker/report contract on affected ERPNext records.
- [frappe-public-container-contract](recipes/frappe-public-container-contract.md) - keep Frappe/Webshop page lifecycle while making every LT public section choose contained workflow/reading mode or deliberate full-bleed band mode.
- [homepage-launch-proof-contract](recipes/homepage-launch-proof-contract.md) - keep the launch homepage stable, real-photo-led, compact on mobile, full-stage proof-crawl driven, recoverable when blocks are hidden, and free of overlay/cycling/crop-container regressions.
- [frappe-shop-showroom-symmetry](recipes/frappe-shop-showroom-symmetry.md) - keep shop/category/product showcase layouts photo-led, with rail/dropdown category navigation and no avoidable single-card orphan rows.
- [frappe-product-page-company-first](recipes/frappe-product-page-company-first.md) - keep Webshop product detail pages focused on product clarity and company proof, without generic ecommerce recommendation panels or empty visible boxes.
- [frappe-product-clear-control-contract](recipes/frappe-product-clear-control-contract.md) - keep product options, variant chips, selects, and price/add-to-cart groups clear instead of boxed; pickup/delivery is the approved framed exception.
- [frappe-portfolio-proof-reel](recipes/frappe-portfolio-proof-reel.md) - keep LT's portfolio as a compact native-shell proof collage with large whole photos, center balance, and no wholesale prototype styling.
- [frappe-public-storefront-security](recipes/frappe-public-storefront-security.md) - review and harden public Frappe/Webshop inputs, uploads, form spam gates, receipt pages, preview bridges, and checkout trust boundaries.
- [frappe-public-nav-business-route-contract](recipes/frappe-public-nav-business-route-contract.md) - keep public nav/header/footer route links, mobile drawer search, and approved business lanes aligned while blocking unapproved route replacements.
- [frappe-sitewide-visual-overhaul](recipes/frappe-sitewide-visual-overhaul.md) - ship a Frappe/Webshop visual redesign with cache-busts, route checks, screenshots, and launch-safe receipts.
- [public-site-microinteraction-contract](recipes/public-site-microinteraction-contract.md) - keep small public-site interactions such as card-wide navigation launch-safe, accessible, and free of prototype/demo source drift.
- [lt-brand-copy-audience-pages](recipes/lt-brand-copy-audience-pages.md) - keep event audience-page copy company-first, buyer-aware, proof-led, and quote-led without founder-only, product-purchase, or removed-hub drift.
- [lt-seo-geo-aeo-contract](recipes/lt-seo-geo-aeo-contract.md) - keep canonical routes, sitemap, metadata, JSON-LD, FAQ visible questions, selective indexing/noindex gates, and technical discovery verifiers in parity.
- [lt-brand-style-guide-consolidation](recipes/lt-brand-style-guide-consolidation.md) - consolidate LT visual authority, delete conflicting style references, and verify old font/pastel/icon drift is gone.
- [cross-browser-motion-visual-verification](recipes/cross-browser-motion-visual-verification.md) - verify animated, marquee, carousel, reduced-motion, and browser-session visual behavior across Chrome/Brave and media-query branches.
- [compact-hero-contract](recipes/compact-hero-contract.md) - keep public page heroes compact, same-height per viewport family, and protected by Playwright checks instead of route-local oversized padding.
- [responsive-container-audit](recipes/responsive-container-audit.md) - audit public routes and stateful UI across breakpoint edges so text, controls, menus, forms, cards, and product selectors stay inside their containers.
- [take-live-coordinated-workflows](recipes/take-live-coordinated-workflows.md) - coordinate multi-agent launch lanes with controller ownership, review gates, and release verification.
- [visual-debugging](recipes/visual-debugging.md) - see what the user sees without asking them to describe it.
- [deploy-static-site-to-cloudflare](recipes/deploy-static-site-to-cloudflare.md) - get a Hugo/Astro/Next-static site live on a custom domain.
- [Capability Evidence And Promotion](recipes/capability-evidence-and-promotion.md) - promote, upvote, downvote, verify, staple, or deprecate capabilities.
- [Organic Capability Growth](recipes/organic-capability-growth.md) - use optional flat metadata and read-only reports to surface valuable new combinations.
- [Perfect Bite Contest Layer](recipes/perfect-bite-contest-layer.md) - score high-bar combination candidates without auto-promoting or writing trusted roots.
- [Source Provenance And Adoption](recipes/source-provenance-and-adoption.md) - preserve origin, attribution, rights, and local-adoption boundaries for borrowed or researched learning.
- [Capability Graduation Sweep](recipes/capability-graduation-sweep.md) - audit LT capabilities for support-system graduation candidates without mutating trust state.
- [Cross-Project Capability Composition](recipes/cross-project-capability-composition.md) - link and compose capabilities across roots, projects, agents, and subjects.
- [Failure Cascade And Watch Status](recipes/failure-cascade-and-watch-status.md) - retest lower layers and watch affected dependents after composed capability failures.
- [Probationary Revalidation](recipes/probationary-revalidation.md) - put repaired dependency chains on probation until three verified uses restore trust.
- [Hub/Spoke Capability Indexing](recipes/hub-spoke-capability-indexing.md) - keep capability indexes slim and token-protective as roots grow.
- [Cross-Root Meal Placement And Trust](recipes/cross-root-meal-placement-and-trust.md) - place meals with the consuming capability root and propagate trust changes across dependencies.
- [Capability Registry Generation](recipes/capability-registry-generation.md) - generate compact retrieval indexes without reading every card.
- [Visible Capability Root Contract](recipes/visible-capability-root-contract.md) - label every capability root and keep new roots visible instead of buried.

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
- [provider-dashboard-work-bounced-to-gl](failures/provider-dashboard-work-bounced-to-gl.md) - prevents Frappe Cloud, Cloudflare, Stripe, DNS, and hosting dashboard work from being handed back to GL after account access/session is available.
- [ad-dashboard-research-vs-control-drift](failures/ad-dashboard-research-vs-control-drift.md) - prevents Google Ads/Meta account-control requests from turning into Gmail, Drive, report, or public-search research loops.
- [frappe-cloud-sitemap-public-domain-drift](failures/frappe-cloud-sitemap-public-domain-drift.md) - prevents live Cloudflare/Frappe Cloud route health from being mistaken for Search Console readiness when sitemap/canonical URLs still advertise the Frappe Cloud vanity host.
- [frappe-cloud-release-site-migration-drift](failures/frappe-cloud-release-site-migration-drift.md) - prevents Frappe Cloud app deploy hashes from being treated as live release proof before site update/migration, source-owned schema, and live route/form verifiers pass.
- [frappe-cloud-app-mirror-release-scope-drift](failures/frappe-cloud-app-mirror-release-scope-drift.md) - prevents clean final commits or dirty-worktree audits from being mistaken for full app-mirror release scope; compare old live app hash to target mirror commit.
- [frappe-cloud-staging-website-settings-drift](failures/frappe-cloud-staging-website-settings-drift.md) - prevents staging root/login Website Settings drift from being mistaken for live breakage or source-code failure.
- [frappe-cloud-staging-stripe-secret-drift](failures/frappe-cloud-staging-stripe-secret-drift.md) - prevents staging product/cart route proof from being mistaken for owner-ready payment proof when encrypted Stripe settings cannot decrypt in the staging site context.
- [stripe-checkout-one-time-promo-param-drift](failures/stripe-checkout-one-time-promo-param-drift.md) - prevents one-time live Stripe Checkout promotion-code work from reintroducing `payment_method_collection` or relying on local kwargs capture instead of live Stripe acceptance.
- [frappe-cloud-staging-email-secret-drift](failures/frappe-cloud-staging-email-secret-drift.md) - prevents paid checkout and queued receipt rows from being mistaken for email delivery proof when encrypted staging Email Account passwords cannot decrypt.
- [frappe-cloud-staging-email-scheduler-stale](failures/frappe-cloud-staging-email-scheduler-stale.md) - prevents queued paid-order receipt/operator rows from being mistaken for delivered emails when staging scheduler/workers stop flushing Email Queue.
- [stale-provider-surface-poison](failures/stale-provider-surface-poison.md) - prevents stale Frappe Cloud benches, staging labels, app mirrors, temp clones, and old runbook blockers from being treated as current truth or deleted by label.
- [public-header-contrast-safe-area-regression](failures/public-header-contrast-safe-area-regression.md) - prevents deep-navy header banner color, hover/focus contrast, and mobile safe-area side-order regressions.
- [public-form-stale-email-queue-idempotency](failures/public-form-stale-email-queue-idempotency.md) - prevents old Lead-reference Email Queue or Communication rows from suppressing current public-form confirmations.
- [public-form-repeat-email-lead-conflict](failures/public-form-repeat-email-lead-conflict.md) - prevents ERPNext Email Address uniqueness from turning legitimate repeat same-email public inquiries into 409 failures.
- [public-form-photo-storage-owner-attachment-gap](failures/public-form-photo-storage-owner-attachment-gap.md) - prevents private Lead File uploads from being mistaken for CRM photo storage or owner Email Queue attachment delivery.
- [playwright-in-file-parallel-fixture-race](failures/playwright-in-file-parallel-fixture-race.md) - keeps LT Playwright specs serial by default unless backend fixture isolation is proven.
- [variant-media-overgating-regression](failures/variant-media-overgating-regression.md) - prevents media safety gates from hiding already-approved simple checkout variant Item images while still holding complex/unclassified media.
- [product-gallery-projection-regression](failures/product-gallery-projection-regression.md) - prevents source-approved product gallery media, Product Setup rows, Website Slideshow rows, and rendered thumbnail rails from drifting apart.
- [ecommerce-variant-price-source-drift](failures/ecommerce-variant-price-source-drift.md) - prevents variant shape, price existence, or Stripe/ERPNext agreement from being mistaken for source-correct ecommerce pricing.
- [webshop-guest-party-cleanup-regression](failures/webshop-guest-party-cleanup-regression.md) - prevents fake-data cleanup from deleting the `Guest` anonymous Webshop Customer/Portal User/Contact chain and breaking public product pricing/variant calls.
- [product-fulfillment-copy-lane-drift](failures/product-fulfillment-copy-lane-drift.md) - prevents product-page pickup/delivery copy from using category fallback when the Website Item runtime lane is quote-first or needs-review.
- [capability-context-gate-bypass-drift](failures/capability-context-gate-bypass-drift.md) - prevents agents from skipping capabilities, loading unrelated capability files, broadening scope, or treating source/app-mirror/local proof as live proof.
- [owner-catalog-guard-live-disable-drift](failures/owner-catalog-guard-live-disable-drift.md) - prevents approved live product hide/disable work from being mislabeled as external cybersecurity or from weakening the owner catalog guard.
- [ready-order-menu-product-dump](failures/ready-order-menu-product-dump.md) - prevents the public Ready-to-Order menu/search/drawer from drifting back to product lists or ERPNext/backend copy instead of Item Group category discovery.
- [frappe-password-reset-silent-generic-drift](failures/frappe-password-reset-silent-generic-drift.md) - prevents known-account reset work from being reported from public UI success or generic Frappe copy instead of branded, current Email Queue proof.

## Evidence And Registry

- [evidence/](evidence/) - compact append-only events for use, upvotes, downvotes, failures, fixes, and promotions.
- [registry/](registry/) - generated compact retrieval indexes.
- [../verifier-manifest.json](../verifier-manifest.json) - manual-only LT
  verifier bundle tiers and approval boundaries.

## Reading Order On Arrival

1. Skim this index.
2. Open the layer folder that matches today's task.
3. When in doubt, check `kitchen/` for in-progress notes that might help.
4. Before pursuing an approach that feels familiar, changing a guard/verifier,
   or touching a known-risk surface, check `failures/`.
5. Before trusting a capability as proven, check maturity and evidence.
