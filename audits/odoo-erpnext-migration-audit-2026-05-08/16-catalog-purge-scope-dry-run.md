# Catalog Purge Scope Dry Run

Read-only dry run from saved snapshot. No ERPNext connection and no deletes.

- Generated: `2026-05-17T23:23:10Z`
- Snapshot: `audits\odoo-erpnext-migration-audit-2026-05-08\current-state-snapshot-2026-05-17-2132-clean-odoo-products`
- Import subset rule: include Odoo-imported products that fit the current ERPNext backend schema; variants and high-variant products are allowed; exclude only proven schema/backend blockers.
- Variants, cups, and high-variant products are products and are not blanket exclusions.

## Import source subset

- Included products: 53
- Excluded products: 0
- Excluded by primary reason: none
- Excluded by all reason flags: none

## Proposed generated catalog purge scope

- Website Items: 53
- Item templates: 53
- Item variants: 10617
- Item Prices: 10652
- Item Variant Attribute rows: 32028
- Product-related File rows attached to purge items/templates: 2522
- Existing excluded Website Item templates held out of purge scope: 0

## Protected service item codes

- None of the Website Item templates matched protected service item codes.

## Template item codes in purge scope

- `6-color-rainbow-arch`
- `6-graduation-stands`
- `7-butterfly-column`
- `7-epic-column`
- `baby-shower-combination-photo-opt`
- `baby-shower-garland`
- `baby-table-decor`
- `balloon-drop`
- `bandage-get-well-bouquet-latex-free`
- `basketball-arch`
- `birthday-deliveries`
- `butterfly-get-well-bouquet-latex-free`
- `classic-arch`
- `classic-column`
- `classic-organic-arch`
- `classic-organic-balloon-garland`
- `classic-organic-columns`
- `classic-organic-for-easel`
- `easter-arch`
- `easter-balloon-arch-bunny-ear`
- `easter-balloon-cups`
- `elsa-bouquet`
- `encanto-bouquet`
- `flamingo-bouquet`
- `football-bouquet`
- `graduation-grab-n-go`
- `halloween-arch`
- `holy-cow-bouquet`
- `large-garland`
- `large-head-missionary`
- `large-organic-column`
- `logo-3-layered-bouquet`
- `marble-table-decor`
- `mickey-mouse-bouquet`
- `minion-bouquet`
- `mothers-day-bouquet`
- `mothers-day-front-yard-7-column`
- `number-balloon-columns`
- `organic-grab-n-go`
- `over-the-hill-bouquet`
- `paw-patrol-bouquet`
- `pemium-organic-column`
- `premium-organic-arch`
- `premium-organic-garland`
- `pride-arch`
- `pride-progress-rainbow-balloon-arch`
- `shooting-star-get-well-bouquet-latex-free`
- `sleepy-baby-column`
- `soccer-bouquet`
- `space-bouquet`
- `star-column`
- `stitch-bouquet`
- `unicorn-bouquet`

## Excluded source products held out of import


## Safety interpretation

This dry run defines only the product-catalog-owned demolition set for the corrected import subset. Service items remain protected. It does not include Customers, Leads, Quotations, Sales Orders, Sales Invoices, Payment records, tax setup, workspaces, fixtures, or non-catalog business records.

Before real destructive mode, rerun against live DB with backup/export and exact allowlist confirmation.

## Gate result

**DRY-RUN ONLY. Destructive purge still requires explicit approval.**
