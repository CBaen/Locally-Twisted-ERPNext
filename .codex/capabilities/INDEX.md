# Capabilities - What This Agent Instance Can Do

This file is the project capability index for Locally Twisted. Read it on
arrival, then open only the capability files needed for the current task.

## How To Use This

- Skim the layers below. Know the territory.
- When you reach for help, scan the layer that fits. Do not read every file.
- When you discover or verify a new capability, add the file in the matching
  layer folder and add the one-liner here.
- Half-formed ideas go in `kitchen/`.
- Things you tried that did not work go in `failures/`.
- Evidence-backed use, upvotes, downvotes, and promotions go in `evidence/`.

## Capability Lifecycle

This root follows the machine-wide capability schema v2.0. Older files remain
usable as legacy cards, but `currently_true`, `verified`, and `staple` require
new evidence in the stated scope. Do not promote old LT cards from memory alone.

## Ingredients

The smallest reusable units. One tool, one command, one MCP server, or a thin
combination.

- [screenshot](ingredients/screenshot.md) - capture the live screen to a file you can read.

## Recipes

Workflows. Multi-step. Clear start and finish.

- [claude-reference-library](recipes/claude-reference-library.md) - safely consult older Claude skills/rules as reference material without treating them as truth or copying them wholesale.
- [balloon-material-visual-physics](recipes/balloon-material-visual-physics.md) - model balloons as sized latex objects with inflation, finish, tension, contact, knots, and construction-unit deformation instead of generic spheres.
- [event-playground-construction-truth](recipes/event-playground-construction-truth.md) - keep Event Playground balloon geometry tied to tested construction facts, including classic quad tie-center neck/knot orientation.
- [erpnext-finance-controlled-automation](recipes/erpnext-finance-controlled-automation.md) - build ERPNext finance/payroll migration surfaces with review queues and accountant approval gates before automation.
- [erpnext-category-media-approval](recipes/erpnext-category-media-approval.md) - prepare, approve, dry-run, and apply ERPNext Item Group category images without assigning browse media by guess.
- [erpnext-checkout-commerce-rules](recipes/erpnext-checkout-commerce-rules.md) - keep mixed goods/service checkout, delivery fees, deposits, and taxable-line rules aligned in ERPNext/Frappe.
- [erpnext-crm-pipeline-safety](recipes/erpnext-crm-pipeline-safety.md) - translate client-friendly CRM/Kanban stages without corrupting ERPNext native status, finance, or reporting behavior.
- [erpnext-intake-form-parity](recipes/erpnext-intake-form-parity.md) - keep public inquiry forms, ERPNext Lead fields, submit mapping, and Desk operator UX aligned.
- [erpnext-simplified-role-verification](recipes/erpnext-simplified-role-verification.md) - verify a simplified ERPNext backend role from login through workspace, shortcuts, permissions, and real records.
- [external-design-reference-translation](recipes/external-design-reference-translation.md) - translate Claude/designer/prototype reference code into Frappe-owned production files without silently changing the approved visual contract.
- [frappe-public-container-contract](recipes/frappe-public-container-contract.md) - keep Frappe/Webshop page lifecycle while making every LT public section choose contained workflow/reading mode or deliberate full-bleed band mode.
- [frappe-shop-showroom-symmetry](recipes/frappe-shop-showroom-symmetry.md) - keep shop/category/product showcase layouts photo-led, with rail/dropdown category navigation and no avoidable single-card orphan rows.
- [frappe-portfolio-proof-reel](recipes/frappe-portfolio-proof-reel.md) - translate a proof-gallery design reference into a Frappe-native natural-ratio portfolio reel while keeping raw reference artifacts only during active critique.
- [frappe-sitewide-visual-overhaul](recipes/frappe-sitewide-visual-overhaul.md) - ship a Frappe/Webshop visual redesign with cache-busts, route checks, screenshots, and launch-safe receipts.
- [lt-brand-style-guide-consolidation](recipes/lt-brand-style-guide-consolidation.md) - consolidate LT visual authority, delete conflicting style references, and verify old font/pastel/icon drift is gone.
- [cross-browser-motion-visual-verification](recipes/cross-browser-motion-visual-verification.md) - verify animated, marquee, carousel, reduced-motion, and browser-session visual behavior across Chrome/Brave and media-query branches.
- [playcanvas-event-builder-stage-physics](recipes/playcanvas-event-builder-stage-physics.md) - keep the PlayCanvas event-builder game anchored through stage-root and piece-root hierarchy, transform math, pointer input, and browser verification.
- [prototype-engine-spike-verification](recipes/prototype-engine-spike-verification.md) - compare browser rendering engines in isolated research packages with shared payload facts and real browser verification.
- [responsive-container-audit](recipes/responsive-container-audit.md) - audit public routes and stateful UI across breakpoint edges so text, controls, menus, forms, cards, and product selectors stay inside their containers.
- [take-live-coordinated-workflows](recipes/take-live-coordinated-workflows.md) - coordinate multi-agent launch lanes with controller ownership, review gates, and release verification.
- [visual-debugging](recipes/visual-debugging.md) - see what the user sees without asking them to describe it.
- [deploy-static-site-to-cloudflare](recipes/deploy-static-site-to-cloudflare.md) - get a Hugo/Astro/Next-static site live on a custom domain.

## Meals

End-to-end compositions of recipes. The shape of a complete piece of work.

- [ship-internal-tool](meals/ship-internal-tool.md) - go from "I need a thing" to "the thing is in production and I can hand it to a colleague."

## Kitchen

[kitchen/](kitchen/) - capabilities being figured out. Promote to a layer when
ready, or move to `failures/` if it did not pan out.

## Failures

Things that were tried and did not work. Read this layer when an idea feels
familiar but you cannot remember why.

- [failures/](failures/) - see the README inside for the convention.

## Evidence And Registry

- [evidence/](evidence/) - compact append-only events for use, upvotes, downvotes, failures, fixes, and promotions.
- [registry/](registry/) - generated compact retrieval indexes.

## Reading Order On Arrival

1. Skim this index.
2. Open the layer folder that matches today's task.
3. When in doubt, check `kitchen/` for in-progress notes that might help.
4. Before pursuing an approach that feels familiar, check `failures/`.
5. Before trusting a capability as proven, check maturity and evidence.
