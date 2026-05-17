# Product Page Price Readiness Report

This read-only report compares source product-page template classifications, current backend Website Item lanes, and live ERPNext Item Price coverage.
It does not mutate ERPNext. It also does not declare the source artifact safe for destructive purge/import.

## Summary

- Source products checked: 53
- Source-template online checkout products: 53
- Current backend online checkout products: 53
- Current backend quote-first products: 0
- Source/backend lane differences: 0
- Backend checkout products with live ERPNext price coverage: 53 / 53
- Checkout sale units with live ERPNext prices: 290 / 290
- Products still blocked for source resolver-backed reimport prices: 36

## Checkout Price Gate

**PASS for current live ERPNext checkout price coverage.**

This means the current live database has server-owned Item Price coverage for the backend checkout-classified Website Item rows.
It does not mean source data can be purged/reimported safely; source resolver-backed prices remain a separate blocker.

## Source / Backend Lane Differences

- None

## Product Coverage

| Slug | Source template | Source lane | Current backend template | Current backend lane | Required axes | Expected sale units | Source resolver-priced units | Live priced units | Live price range | Missing live units |
|---|---|---|---|---|---|---:|---:|---:|---|---|
| baby-shower-combination-photo-opt | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $650.00 |  |
| classic-organic-balloon-garland | Configurable product page | Online checkout | Configurable product page | Online checkout | Garland Length | 3 | 0 | 3 | $150.00 |  |
| basketball-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 2 | 0 | 2 | $340.00 |  |
| number-balloon-columns | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $55.00 |  |
| easter-balloon-arch-bunny-ear | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 2 | 0 | 2 | $375.00 |  |
| graduation-grab-n-go | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $85.00 |  |
| halloween-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 4 | 0 | 4 | $300.00 |  |
| large-head-missionary | Configurable product page | Online checkout | Configurable product page | Online checkout | Missionary, skin color, Hair color | 30 | 0 | 30 | $175.00 |  |
| premium-organic-garland | Configurable product page | Online checkout | Configurable product page | Online checkout | Garland Length | 3 | 0 | 3 | $216.00 |  |
| premium-organic-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 4 | 0 | 4 | $720.00 |  |
| pemium-organic-column | Configurable product page | Online checkout | Configurable product page | Online checkout | Column Height | 6 | 0 | 6 | $180.00 |  |
| pride-progress-rainbow-balloon-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 4 | 0 | 4 | $260.00 |  |
| classic-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size, Design, LED Lights | 16 | 0 | 16 | $260.00 |  |
| classic-column | Configurable product page | Online checkout | Configurable product page | Online checkout | Column Height, topper | 36 | 0 | 36 | $65.00 |  |
| classic-organic-columns | Configurable product page | Online checkout | Configurable product page | Online checkout | Column Height | 6 | 0 | 6 | $125.00 |  |
| baby-shower-garland | Configurable product page | Online checkout | Configurable product page | Online checkout | Garland Length | 3 | 0 | 3 | $150.00 |  |
| balloon-drop | Configurable product page | Online checkout | Configurable product page | Online checkout | Drop Size | 3 | 0 | 3 | $375.00 |  |
| classic-organic-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 4 | 0 | 4 | $500.00 |  |
| unicorn-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| mickey-mouse-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| minion-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| encanto-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| stitch-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| flamingo-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| football-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| soccer-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| space-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| over-the-hill-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| 7-butterfly-column | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $120.00 |  |
| 7-epic-column | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $100.00 |  |
| organic-grab-n-go | Configurable product page | Online checkout | Configurable product page | Online checkout | Garland Length | 3 | 0 | 3 | $70.00 |  |
| birthday-deliveries | Configurable product page | Online checkout | Configurable product page | Online checkout | Delivery Size, Delivery themes | 81 | 0 | 81 | $70.00 |  |
| easter-balloon-cups | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Easter Designs | 7 | 0 | 7 | $13.00 |  |
| star-column | Configurable product page | Online checkout | Configurable product page | Online checkout | Column Height | 4 | 0 | 4 | $90.00 |  |
| sleepy-baby-column | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $220.00 |  |
| baby-table-decor | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $30.00 |  |
| logo-3-layered-bouquet | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $90.00 |  |
| 6-color-rainbow-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | Arch Size | 2 | 0 | 2 | $340.00 |  |
| mothers-day-front-yard-7-column | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $140.00 |  |
| marble-table-decor | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $75.00 |  |
| paw-patrol-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| elsa-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| holy-cow-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 3 | $35.00 - $85.00 |  |
| butterfly-get-well-bouquet-latex-free | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $35.00 |  |
| bandage-get-well-bouquet-latex-free | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $35.00 |  |
| shooting-star-get-well-bouquet-latex-free | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $35.00 |  |
| 6-graduation-stands | Configurable product page | Online checkout | Configurable product page | Online checkout | Graduation stands | 2 | 0 | 2 | $45.00 |  |
| classic-organic-for-easel | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $100.00 |  |
| easter-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $250.00 |  |
| mothers-day-bouquet | Ready-to-order page | Online checkout | Ready-to-order page | Online checkout | (single SKU) | 1 | 1 | 1 | $65.00 |  |
| large-garland | Configurable product page | Online checkout | Configurable product page | Online checkout | Garland Length | 3 | 0 | 3 | $216.00 |  |
| large-organic-column | Configurable product page | Online checkout | Configurable product page | Online checkout | Column Height | 6 | 0 | 6 | $180.00 |  |
| pride-arch | Configurable product page | Online checkout | Configurable product page | Online checkout | (single SKU) | 1 | 1 | 1 | $325.00 |  |