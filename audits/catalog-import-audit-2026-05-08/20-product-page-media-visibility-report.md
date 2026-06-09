# Product Page Media Visibility Report

This read-only report checks media evidence for the two reusable product-page template types.
It does not assign, move, approve, delete, or upload images.

## Summary

- Source products checked: 51
- Products with source primary image: 51
- Products with source extra images: 47
- Source extra images: 68
- Approved gallery images: 68
- Approved variant images: 0
- Reference images: 0
- Held-back ignored artifacts: 0
- Unsafe unclassified source extra images: 0
- Website Items with live primary image: 51
- Website Items with slideshow field set: 47
- Website Slideshow records: 47
- Website Slideshow Item records: 68
- Active variants: 10186
- Active variants with image: 1750
- Products with active variant images: 34

## Gate Result

**PASS for media visibility readiness.**

## Interpretation

Live ERPNext primary images and some variant images are evidence of current stored media, not proof that source media is fully classified.
Source extras marked ignored_artifact are intentionally held back and are non-blocking because product pages must not render them.
Gallery, variant_image, and reference media may render only when the backend/source contract approves that role.
The current public ecommerce pause means rendered product-page media proof must use authenticated/internal access or explicitly report the pause as the blocker.

## Product Coverage

| Slug | Template | Lane | Source primary | Source extras | Gallery | Variant | Reference | Held ignored | Unsafe unclassified | Live primary | Live slideshow | Active variants | Variant images | Distinct variant images |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---:|
| baby-shower-combination-photo-opt | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 51 | 0 | 0 |
| classic-organic-balloon-garland | Configurable product page | Internal checkout hold | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 153 | 0 | 0 |
| basketball-arch | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 1 | 1 |
| number-balloon-columns | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 357 | 0 | 0 |
| easter-balloon-arch-bunny-ear | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 1 | 1 |
| graduation-grab-n-go | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 4 | 0 | 0 |
| halloween-arch | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 204 | 51 | 1 |
| large-head-missionary | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 30 | 15 | 1 |
| premium-organic-garland | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 153 | 51 | 1 |
| premium-organic-arch | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 408 | 51 | 1 |
| pemium-organic-column | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 612 | 51 | 1 |
| pride-progress-rainbow-balloon-arch | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 4 | 1 | 1 |
| classic-arch | Configurable product page | Internal checkout hold | 1 | 11 | 11 | 0 | 0 | 0 | 0 | yes | yes | 816 | 816 | 4 |
| classic-column | Configurable product page | Internal checkout hold | 1 | 3 | 3 | 0 | 0 | 0 | 0 | yes | yes | 1836 | 357 | 3 |
| classic-organic-columns | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 306 | 51 | 1 |
| baby-shower-garland | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 153 | 51 | 1 |
| balloon-drop | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 153 | 51 | 1 |
| classic-organic-arch | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 612 | 51 | 1 |
| unicorn-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| mickey-mouse-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| minion-bouquet | Ready-to-order page | Online checkout | 1 | 3 | 3 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| encanto-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| stitch-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| flamingo-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| football-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| soccer-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| space-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| over-the-hill-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| 7-butterfly-column | Configurable product page | Internal checkout hold | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 51 | 0 | 0 |
| 7-epic-column | Configurable product page | Internal checkout hold | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 51 | 0 | 0 |
| organic-grab-n-go | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 150 | 50 | 1 |
| birthday-deliveries | Configurable product page | Online checkout | 1 | 7 | 7 | 0 | 0 | 0 | 0 | yes | yes | 2430 | 1 | 1 |
| easter-balloon-cups | Ready-to-order page | Online checkout | 1 | 2 | 2 | 0 | 0 | 0 | 0 | yes | yes | 7 | 1 | 1 |
| star-column | Configurable product page | Online checkout | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 1160 | 0 | 0 |
| sleepy-baby-column | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 51 | 0 | 0 |
| baby-table-decor | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 0 | 0 |
| logo-3-layered-bouquet | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 51 | 0 | 0 |
| 6-color-rainbow-arch | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 1 | 1 |
| mothers-day-front-yard-7-column | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 0 | 0 | 0 |
| marble-table-decor | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 10 | 1 | 1 |
| paw-patrol-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| elsa-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| holy-cow-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 3 | 3 | 3 |
| butterfly-get-well-bouquet-latex-free | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 0 | 0 |
| bandage-get-well-bouquet-latex-free | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 0 | 0 |
| shooting-star-get-well-bouquet-latex-free | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 2 | 0 | 0 |
| 6-graduation-stands | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 8 | 0 | 0 |
| classic-organic-for-easel | Configurable product page | Internal checkout hold | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 51 | 0 | 0 |
| mothers-day-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 0 | 0 | 0 |
| large-garland | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 87 | 29 | 1 |
| large-organic-column | Configurable product page | Online checkout | 1 | 1 | 1 | 0 | 0 | 0 | 0 | yes | yes | 174 | 29 | 1 |