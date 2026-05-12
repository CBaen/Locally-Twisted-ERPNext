# Product Page Media Visibility Report

This read-only report checks media evidence for the two reusable product-page template types.
It does not assign, move, approve, delete, or upload images.

## Summary

- Source products checked: 53
- Products with source primary image: 53
- Products with source extra images: 49
- Source extra images: 95
- Approved gallery images: 0
- Approved variant images: 0
- Reference images: 0
- Held-back ignored artifacts: 95
- Unsafe unclassified source extra images: 0
- Website Items with live primary image: 53
- Website Items with slideshow field set: 0
- Website Slideshow records: 0
- Website Slideshow Item records: 0
- Active variants: 10227
- Active variants with image: 1751
- Products with active variant images: 35

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
| baby-shower-combination-photo-opt | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 51 | 0 | 0 |
| classic-organic-balloon-garland | Custom quote page | Quote request first | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 153 | 0 | 0 |
| basketball-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 1 | 1 |
| number-balloon-columns | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 357 | 0 | 0 |
| easter-balloon-arch-bunny-ear | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 1 | 1 |
| graduation-grab-n-go | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 51 | 0 | 0 |
| halloween-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 204 | 51 | 1 |
| large-head-missionary | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 30 | 15 | 1 |
| premium-organic-garland | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 153 | 51 | 1 |
| premium-organic-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 408 | 51 | 1 |
| pemium-organic-column | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 612 | 51 | 1 |
| pride-progress-rainbow-balloon-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 4 | 1 | 1 |
| classic-arch | Custom quote page | Quote request first | 1 | 22 | 0 | 0 | 0 | 22 | 0 | yes | no | 816 | 816 | 4 |
| classic-column | Custom quote page | Quote request first | 1 | 5 | 0 | 0 | 0 | 5 | 0 | yes | no | 1836 | 357 | 3 |
| classic-organic-columns | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 306 | 51 | 1 |
| baby-shower-garland | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 153 | 51 | 1 |
| balloon-drop | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 153 | 51 | 1 |
| classic-organic-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 612 | 51 | 1 |
| unicorn-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| mickey-mouse-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| minion-bouquet | Ready-to-order page | Online checkout | 1 | 6 | 0 | 0 | 0 | 6 | 0 | yes | no | 3 | 3 | 3 |
| encanto-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| stitch-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| flamingo-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| football-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| soccer-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| space-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| over-the-hill-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| 7-butterfly-column | Custom quote page | Quote request first | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 51 | 0 | 0 |
| 7-epic-column | Custom quote page | Quote request first | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 51 | 0 | 0 |
| organic-grab-n-go | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 150 | 50 | 1 |
| birthday-deliveries | Custom quote page | Quote request first | 1 | 14 | 0 | 0 | 0 | 14 | 0 | yes | no | 2430 | 1 | 1 |
| easter-balloon-cups | Ready-to-order page | Online checkout | 1 | 4 | 0 | 0 | 0 | 4 | 0 | yes | no | 7 | 1 | 1 |
| star-column | Custom quote page | Quote request first | 1 | 0 | 0 | 0 | 0 | 0 | 0 | yes | no | 1160 | 0 | 0 |
| sleepy-baby-column | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 51 | 0 | 0 |
| baby-table-decor | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 0 | 0 |
| logo-3-layered-bouquet | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 51 | 0 | 0 |
| 6-color-rainbow-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 1 | 1 |
| mothers-day-front-yard-7-column | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 0 | 0 | 0 |
| marble-table-decor | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 10 | 1 | 1 |
| paw-patrol-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| elsa-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| holy-cow-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 3 | 3 | 3 |
| butterfly-get-well-bouquet-latex-free | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 0 | 0 |
| bandage-get-well-bouquet-latex-free | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 0 | 0 |
| shooting-star-get-well-bouquet-latex-free | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 0 | 0 |
| 6-graduation-stands | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 2 | 1 | 1 |
| classic-organic-for-easel | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 51 | 0 | 0 |
| easter-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 0 | 0 | 0 |
| mothers-day-bouquet | Ready-to-order page | Online checkout | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 0 | 0 | 0 |
| large-garland | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 87 | 29 | 1 |
| large-organic-column | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 174 | 29 | 1 |
| pride-arch | Custom quote page | Quote request first | 1 | 1 | 0 | 0 | 0 | 1 | 0 | yes | no | 0 | 0 | 0 |