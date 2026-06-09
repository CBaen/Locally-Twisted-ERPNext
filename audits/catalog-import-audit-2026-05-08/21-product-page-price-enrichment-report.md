# Product Page Price Enrichment Report

This read-only report builds a candidate price map for the rebuilt product-page import contract.
It does not mutate ERPNext or `_resources/catalog-source/catalog.json`.

## Summary

- Source products checked: 53
- Online checkout products: 15
- Quote request first products: 38
- Source variant rows preserved: 10828
- Expected import sale units: 290
- Candidate-priced sale units: 290
- Source resolver-priced units: 0
- Source base-price units: 17
- Live ERPNext snapshot-priced units: 273
- Candidate units still needing business price review: 273
- Blocked products: 0
- Products still blocked for purge/reimport by review gates: 49

## Gate Result

**PASS for price-candidate coverage.**

Every expected import sale unit has a price candidate from source resolver rows, source base price, or the current live ERPNext snapshot.
This is still not business price approval; live-snapshot candidates need review before prices are promised to customers.

## Product Coverage

| Slug | Template | Lane | Required axes | Expected units | Source resolver | Source base | Live snapshot | Review units | Blockers |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| baby-shower-combination-photo-opt | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| classic-organic-balloon-garland | Custom quote page | Quote request first | Garland Length | 3 | 0 | 0 | 3 | 3 |  |
| basketball-arch | Custom quote page | Quote request first | Arch Size | 2 | 0 | 0 | 2 | 2 |  |
| number-balloon-columns | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| easter-balloon-arch-bunny-ear | Custom quote page | Quote request first | Arch Size | 2 | 0 | 0 | 2 | 2 |  |
| graduation-grab-n-go | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| halloween-arch | Custom quote page | Quote request first | Arch Size | 4 | 0 | 0 | 4 | 4 |  |
| large-head-missionary | Custom quote page | Quote request first | Missionary, skin color, Hair color | 30 | 0 | 0 | 30 | 30 |  |
| premium-organic-garland | Custom quote page | Quote request first | Garland Length | 3 | 0 | 0 | 3 | 3 |  |
| premium-organic-arch | Custom quote page | Quote request first | Arch Size | 4 | 0 | 0 | 4 | 4 |  |
| pemium-organic-column | Custom quote page | Quote request first | Column Height | 6 | 0 | 0 | 6 | 6 |  |
| pride-progress-rainbow-balloon-arch | Custom quote page | Quote request first | Arch Size | 4 | 0 | 0 | 4 | 4 |  |
| classic-arch | Custom quote page | Quote request first | Arch Size, Design, LED Lights | 16 | 0 | 0 | 16 | 16 |  |
| classic-column | Custom quote page | Quote request first | Column Height, topper | 36 | 0 | 0 | 36 | 36 |  |
| classic-organic-columns | Custom quote page | Quote request first | Column Height | 6 | 0 | 0 | 6 | 6 |  |
| baby-shower-garland | Custom quote page | Quote request first | Garland Length | 3 | 0 | 0 | 3 | 3 |  |
| balloon-drop | Custom quote page | Quote request first | Drop Size | 3 | 0 | 0 | 3 | 3 |  |
| classic-organic-arch | Custom quote page | Quote request first | Arch Size | 4 | 0 | 0 | 4 | 4 |  |
| unicorn-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| mickey-mouse-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| minion-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| encanto-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| stitch-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| flamingo-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| football-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| soccer-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| space-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| over-the-hill-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| 7-butterfly-column | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| 7-epic-column | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| organic-grab-n-go | Custom quote page | Quote request first | Garland Length | 3 | 0 | 0 | 3 | 3 |  |
| birthday-deliveries | Custom quote page | Quote request first | Delivery Size, Delivery themes | 81 | 0 | 0 | 81 | 81 |  |
| easter-balloon-cups | Ready-to-order page | Online checkout | Easter Designs | 7 | 0 | 0 | 7 | 7 |  |
| star-column | Custom quote page | Quote request first | Column Height | 4 | 0 | 0 | 4 | 4 |  |
| sleepy-baby-column | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| baby-table-decor | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| logo-3-layered-bouquet | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| 6-color-rainbow-arch | Custom quote page | Quote request first | Arch Size | 2 | 0 | 0 | 2 | 2 |  |
| mothers-day-front-yard-7-column | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| marble-table-decor | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| paw-patrol-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| elsa-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| holy-cow-bouquet | Ready-to-order page | Online checkout | Bouquet Size | 3 | 0 | 0 | 3 | 3 |  |
| butterfly-get-well-bouquet-latex-free | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| bandage-get-well-bouquet-latex-free | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| shooting-star-get-well-bouquet-latex-free | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| 6-graduation-stands | Custom quote page | Quote request first | Graduation stands | 2 | 0 | 0 | 2 | 2 |  |
| classic-organic-for-easel | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| easter-arch | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| mothers-day-bouquet | Ready-to-order page | Online checkout | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |
| large-garland | Custom quote page | Quote request first | Garland Length | 3 | 0 | 0 | 3 | 3 |  |
| large-organic-column | Custom quote page | Quote request first | Column Height | 6 | 0 | 0 | 6 | 6 |  |
| pride-arch | Custom quote page | Quote request first | (single SKU) | 1 | 0 | 1 | 0 | 0 |  |