D:2026-05-10 | Check:local legacy_source-source audit JSON + media packet + price packet 2026-05-10 | Confidence:[LOCAL-PROOF]

# Ecommerce Product Proof Matrix — legacy_source → ERPNext

Purpose: one product-row matrix for launch/rebuild planning. This is not import approval, price approval, media approval, or go-live approval.

## Summary

- Source products: 53
- Checkout-lane products in source contract: 15
- Quote-first products in source contract: 38
- Candidate sale units: 290
- Live snapshot units used for price review: 273
- Review units: 273
- Products with extra images: 49
- Source extra images: 95; unclassified: 95; approved gallery: 0; assigned variant images: 0

## Launch rule

A row marked `checkout` is only a candidate lane, not launch approval. Public checkout requires product-row price approval, option/add-on approval, media decision, cart/checkout/backend proof, and GL/Jeff signoff. Quote-first rows must not show paid checkout until those gates clear.

## Product matrix

| # | Product | legacy_source ID | Lane | Required axes | Customization axes | Add-ons | Price status | Units | Media | Purge/import status | Immediate action |
|---:|---|---:|---|---|---|---|---|---:|---|---|---|
| 1 | `baby-shower-combination-photo-opt` Baby Shower Combination Photo opt | 14 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 2 | `classic-organic-balloon-garland` Classic Organic Balloon Garland | 19 | quote_first | Garland Length | latex colors | — | PASS_PRICE_ENRICHMENT | 3 | none listed | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; customization proof |
| 3 | `basketball-arch` Basketball Arch | 21 | quote_first | Arch Size | — | — | PASS_PRICE_ENRICHMENT | 2 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify |
| 4 | `number-balloon-columns` Number Balloon Columns | 22 | quote_first | — | Number colors, latex colors | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 5 | `easter-balloon-arch-bunny-ear` Easter Balloon Arch - Bunny Ear | 30 | quote_first | Arch Size | — | — | PASS_PRICE_ENRICHMENT | 2 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify |
| 6 | `graduation-grab-n-go` Graduation Grab n Go | 38 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 7 | `halloween-arch` Halloween arch | 39 | quote_first | Arch Size | latex colors | — | PASS_PRICE_ENRICHMENT | 4 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 8 | `large-head-missionary` Large head Missionary | 45 | quote_first | Missionary, skin color, Hair color | — | — | PASS_PRICE_ENRICHMENT | 30 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify |
| 9 | `premium-organic-garland` Premium Organic Garland | 52 | quote_first | Garland Length | latex colors | — | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 10 | `premium-organic-arch` Premium Organic Arch | 53 | quote_first | Arch Size | latex colors | — | PASS_PRICE_ENRICHMENT | 4 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof; axis review |
| 11 | `pemium-organic-column` Pemium Organic Column | 54 | quote_first | Column Height | latex colors | — | PASS_PRICE_ENRICHMENT | 6 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof; axis review |
| 12 | `pride-progress-rainbow-balloon-arch` Pride progress Rainbow Balloon Arch | 55 | quote_first | Arch Size | — | — | PASS_PRICE_ENRICHMENT | 4 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify |
| 13 | `classic-arch` Classic Arch | 57 | quote_first | Arch Size, Design, LED Lights | latex colors | — | PASS_PRICE_ENRICHMENT | 16 | 22 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 14 | `classic-column` Classic Column | 58 | quote_first | Column Height, topper | latex colors | — | PASS_PRICE_ENRICHMENT | 36 | 5 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 15 | `classic-organic-columns` Classic Organic columns | 65 | quote_first | Column Height | latex colors | — | PASS_PRICE_ENRICHMENT | 6 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 16 | `baby-shower-garland` Baby Shower Garland | 71 | quote_first | Garland Length | latex colors | — | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 17 | `balloon-drop` Balloon Drop | 74 | quote_first | Drop Size | latex colors | — | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 18 | `classic-organic-arch` Classic Organic Arch | 99 | quote_first | Arch Size | latex colors | — | PASS_PRICE_ENRICHMENT | 4 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof; axis review |
| 19 | `unicorn-bouquet` Unicorn Bouquet | 115 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 20 | `mickey-mouse-bouquet` Mickey Mouse Bouquet | 116 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 21 | `minion-bouquet` Minion Bouquet | 117 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 6 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 22 | `encanto-bouquet` Encanto Bouquet | 118 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 23 | `stitch-bouquet` Stitch Bouquet | 119 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 24 | `flamingo-bouquet` Flamingo Bouquet | 120 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 25 | `football-bouquet` Football Bouquet | 121 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 26 | `soccer-bouquet` Soccer Bouquet | 122 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 27 | `space-bouquet` Space Bouquet | 123 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 28 | `over-the-hill-bouquet` Over the Hill Bouquet | 124 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 29 | `7-butterfly-column` 7' Butterfly Column | 125 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | none listed | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; customization proof |
| 30 | `7-epic-column` 7' Epic Column | 126 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | none listed | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; customization proof |
| 31 | `organic-grab-n-go` Organic Grab n' Go | 127 | quote_first | Garland Length | latex colors | — | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 32 | `birthday-deliveries` Birthday Deliveries | 128 | quote_first | Delivery Size, Delivery themes | — | foil_number | PASS_PRICE_ENRICHMENT | 81 | 14 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; axis review |
| 33 | `easter-balloon-cups` Easter Balloon Cups | 130 | checkout | Easter Designs | — | — | PASS_PRICE_ENRICHMENT | 7 | 4 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 34 | `star-column` Star Column | 131 | quote_first | Column Height | Color Palette | — | PASS_PRICE_ENRICHMENT | 4 | none listed | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; customization proof; axis review |
| 35 | `sleepy-baby-column` Sleepy Baby Column | 132 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 36 | `baby-table-decor` Baby Table decor | 133 | quote_first | — | Baby color | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 37 | `logo-3-layered-bouquet` Logo 3 layered bouquet | 134 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 38 | `6-color-rainbow-arch` 6 color rainbow arch | 135 | quote_first | Arch Size | — | — | PASS_PRICE_ENRICHMENT | 2 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify |
| 39 | `mothers-day-front-yard-7-column` Mother's day front yard 7' Column | 137 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PASS_PURGE_REIMPORT_PRICE_GATE | keep quote-first; media classify |
| 40 | `marble-table-decor` Marble table decor | 140 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; axis review |
| 41 | `paw-patrol-bouquet` Paw Patrol Bouquet | 141 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 42 | `elsa-bouquet` Elsa Bouquet | 142 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 43 | `holy-cow-bouquet` Holy COW!! Bouquet | 143 | checkout | Bouquet Size | — | foil_number | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | checkout candidate only; price review; media classify |
| 44 | `butterfly-get-well-bouquet-latex-free` Butterfly "GET WELL" Bouquet (Latex free) | 144 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; axis review |
| 45 | `bandage-get-well-bouquet-latex-free` Bandage "GET WELL" Bouquet (Latex free) | 146 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; axis review |
| 46 | `shooting-star-get-well-bouquet-latex-free` Shooting star "GET WELL" Bouquet (Latex free) | 147 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; axis review |
| 47 | `6-graduation-stands` 6' Graduation stands | 149 | quote_first | Graduation stands | — | — | PASS_PRICE_ENRICHMENT | 2 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify |
| 48 | `classic-organic-for-easel` classic organic for easel | 152 | quote_first | — | latex colors | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; media classify; customization proof |
| 49 | `easter-arch` Easter Arch | 158 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PASS_PURGE_REIMPORT_PRICE_GATE | keep quote-first; media classify |
| 50 | `mothers-day-bouquet` Mother's Day Bouquet | 165 | checkout | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PASS_PURGE_REIMPORT_PRICE_GATE | checkout candidate only; media classify |
| 51 | `large-garland` Large Garland | 177 | quote_first | Garland Length | Color Palette | — | PASS_PRICE_ENRICHMENT | 3 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 52 | `large-organic-column` Large Organic Column | 178 | quote_first | Column Height | Color Palette | — | PASS_PRICE_ENRICHMENT | 6 | 1 extra / hold | PRICE_ENRICHABLE_BUT_PURGE_BLOCKED | keep quote-first; price review; media classify; customization proof |
| 53 | `pride-arch` Pride Arch | 179 | quote_first | — | — | — | PASS_PRICE_ENRICHMENT | 1 | 1 extra / hold | PASS_PURGE_REIMPORT_PRICE_GATE | keep quote-first; media classify |

## Blockers carried on every row unless proven otherwise

- Business price approval is not granted by this matrix.
- Media/gallery/variant-photo claims are not approved while source extra images remain `review_needed`.
- Quote-first rows must remain quote-first until cart/checkout/backend proof exists for that exact product family.
- Checkout candidate rows still need representative browser/cart/backend proof and GL/Jeff signoff before public use.
- Destructive purge/import remains blocked until source/version, price, media, axis, add-on, and rollback gates clear.

## Source artifacts

- `audits/catalog-import-audit-2026-05-08/21-product-page-price-enrichment-candidates.json`
- `audits/catalog-import-audit-2026-05-08/23-product-page-media-classification-packet.json`
- `audits/catalog-import-audit-2026-05-08/24-product-page-price-review-packet.md`
- `workstreams/ecommerce-audit/legacy_source-source-commerce-map-2026-05-10.md`
