# No-Monolith Operating Contract

Last updated: 2026-05-08 by Codex after GL made no monoliths a system-wide law.

## Status

Standing operating contract created. The rule is documented in this repo,
agency docs, machine-wide Codex/OpenClaw guidance, and capability roots.

## Contract

NO MONOLITHS. Do not create or expand hand-authored production files that become
giant catch-all modules, templates, stylesheets, scripts, verifiers, tests, or
project docs.

Research/reference artifacts are the intentional long-form exception. Generated,
vendor, lock, cache, and export files are artifacts, not design precedent.

## How To Apply It

Before adding to a large file, name the file's current job.

If the new work crosses unrelated concerns, split it first into a module,
partial, helper, recipe, workstream doc, or focused verifier. If the split is
too risky during an urgent fix, keep the change surgical and add the split to
the queue or this handoff.

## Current Split Candidates

This quick audit looked only at hand-authored production/project surfaces and
excluded `_resources/`, `research/`, assets, generated output, screenshots, and
runtime/vendor-style directories. It is not a demand to split every file
immediately; it is a warning list for future agents before they add more.

- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` - 3,510 lines.
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py` - 1,637 lines.
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html` - 1,065 lines.
- `scripts/verify/render_outbound_document_previews.py` - 1,030 lines.
- `apps/locally_twisted/locally_twisted/www/checkout.py` - 1,011 lines.
- `apps/locally_twisted/locally_twisted/www/home.py` - 973 lines.
- `scripts/verify/smoke_shop.py` - 775 lines.
- `scripts/verify/interactive_layout.spec.js` - 772 lines.
- `scripts/verify/layout_helpers.js` - 702 lines.
- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py` - 675 lines.
- `apps/locally_twisted/locally_twisted/public/css/lt-product-polish.css` - 664 lines.
- `apps/locally_twisted/locally_twisted/www/checkout.html` - 659 lines.
- `apps/locally_twisted/locally_twisted/seed/sync_invoice_branding.py` - 611 lines.
- `apps/locally_twisted/locally_twisted/www/book.py` - 593 lines.
- `apps/locally_twisted/locally_twisted/seed/sync_backend_workspaces.py` - 579 lines.
- `scripts/setup/scrape_legacy_source_live.py` - 571 lines.
- `apps/locally_twisted/locally_twisted/www/shop.py` - 556 lines.
- `apps/locally_twisted/locally_twisted/maintenance/heartbeat.py` - 502 lines.

Vendor/upstream app files under `apps/webshop` and `apps/payments` were visible
in the raw audit but are not LT split targets unless the project has already
forked and owns the behavior.

## Verification

This contract is a documentation and structure gate. Use `git diff --check`
after edits. For any actual split, run the feature verifier that owns that file:
public visual/layout gates for templates/CSS, synthetic/business automation
contracts for backend verifiers, and targeted Python/Node syntax checks for
extracted modules.

## Next Work

- Split only when a feature naturally touches one of the candidate files.
- Do not do a broad refactor without a focused verifier and rollback path.
- When a split lands, update this handoff by removing or shrinking the matching
  candidate entry.
