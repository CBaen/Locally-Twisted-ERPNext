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
- [erpnext-finance-controlled-automation](recipes/erpnext-finance-controlled-automation.md) - build ERPNext finance/payroll migration surfaces with review queues and accountant approval gates before automation.
- [erpnext-crm-pipeline-safety](recipes/erpnext-crm-pipeline-safety.md) - translate client-friendly CRM/Kanban stages without corrupting ERPNext native status, finance, or reporting behavior.
- [erpnext-intake-form-parity](recipes/erpnext-intake-form-parity.md) - keep public inquiry forms, ERPNext Lead fields, submit mapping, and Desk operator UX aligned.
- [erpnext-simplified-role-verification](recipes/erpnext-simplified-role-verification.md) - verify a simplified ERPNext backend role from login through workspace, shortcuts, permissions, and real records.
- [frappe-sitewide-visual-overhaul](recipes/frappe-sitewide-visual-overhaul.md) - ship a Frappe/Webshop visual redesign with cache-busts, route checks, screenshots, and launch-safe receipts.
- [lt-brand-style-guide-consolidation](recipes/lt-brand-style-guide-consolidation.md) - consolidate LT visual authority, delete conflicting style references, and verify old font/pastel/icon drift is gone.
- [prototype-engine-spike-verification](recipes/prototype-engine-spike-verification.md) - compare browser rendering engines in isolated research packages with shared payload facts and real browser verification.
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
