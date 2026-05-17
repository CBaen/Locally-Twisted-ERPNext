# Product Source Repair Map

Read-only map from the Odoo product export to ERPNext purchasable-product repair lanes.

## Rule

There are no business quote-first products. If it is a product, the target state is purchasable. Rows that are not certified are blocked until the source data, pricing, media, and checkout cascade are proven.

## Summary

- Products mapped: 53
- Source export found: 53
- Source export missing: 0
- Certified checkout products: 18
- Blocked until certified: 35
- Repair lanes: add_on_conditional_pricing_build=20, certified_current_checkout=18, multi_color_recipe_checkout_build=6, simple_purchasable_rehearsal=4, source_backend_review=5

## Contract Failures

- None

## Products

| Product | Slug | State | Repair lane | Source evidence | Price units | Next gates |
|---|---|---|---|---|---:|---|
| Baby Shower Combination Photo opt | `baby-shower-combination-photo-opt` | blocked_until_certified | multi_color_recipe_checkout_build | found | 1 | customer-facing multi-color recipe UI<br>backend color recipe validation<br>checkout/payment/invoice/receipt cascade proof |
| Classic Organic Balloon Garland | `classic-organic-balloon-garland` | blocked_until_certified | add_on_conditional_pricing_build | found | 3 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Basketball Arch | `basketball-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 2 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Number Balloon Columns | `number-balloon-columns` | blocked_until_certified | multi_color_recipe_checkout_build | found | 1 | customer-facing multi-color recipe UI<br>backend color recipe validation<br>checkout/payment/invoice/receipt cascade proof |
| Easter Balloon Arch - Bunny Ear | `easter-balloon-arch-bunny-ear` | blocked_until_certified | add_on_conditional_pricing_build | found | 2 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Graduation Grab n Go | `graduation-grab-n-go` | certified_checkout | certified_current_checkout | found | 1 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Halloween arch | `halloween-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 4 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Large head Missionary | `large-head-missionary` | blocked_until_certified | simple_purchasable_rehearsal | found | 30 | focused source/export purchasable rehearsal<br>open-mode product UX proof<br>checkout/payment/invoice/receipt cascade proof |
| Premium Organic Garland | `premium-organic-garland` | blocked_until_certified | add_on_conditional_pricing_build | found | 3 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Premium Organic Arch | `premium-organic-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 4 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Pemium Organic Column | `pemium-organic-column` | blocked_until_certified | add_on_conditional_pricing_build | found | 6 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Pride progress Rainbow Balloon Arch | `pride-progress-rainbow-balloon-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 4 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Classic Arch | `classic-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 16 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Classic Column | `classic-column` | blocked_until_certified | add_on_conditional_pricing_build | found | 36 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Classic Organic columns | `classic-organic-columns` | blocked_until_certified | add_on_conditional_pricing_build | found | 6 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Baby Shower Garland | `baby-shower-garland` | blocked_until_certified | add_on_conditional_pricing_build | found | 3 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Balloon Drop | `balloon-drop` | blocked_until_certified | add_on_conditional_pricing_build | found | 3 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Classic Organic Arch | `classic-organic-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 4 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Unicorn Bouquet | `unicorn-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Mickey Mouse Bouquet | `mickey-mouse-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Minion Bouquet | `minion-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Encanto Bouquet | `encanto-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Stitch Bouquet | `stitch-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Flamingo Bouquet | `flamingo-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Football Bouquet | `football-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Soccer Bouquet | `soccer-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Space Bouquet | `space-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Over the Hill Bouquet | `over-the-hill-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| 7' Butterfly Column | `7-butterfly-column` | certified_checkout | certified_current_checkout | found | 1 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| 7' Epic Column | `7-epic-column` | blocked_until_certified | multi_color_recipe_checkout_build | found | 1 | customer-facing multi-color recipe UI<br>backend color recipe validation<br>checkout/payment/invoice/receipt cascade proof |
| Organic Grab n' Go | `organic-grab-n-go` | blocked_until_certified | add_on_conditional_pricing_build | found | 3 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Birthday Deliveries | `birthday-deliveries` | blocked_until_certified | source_backend_review | found | 81 | source export meaning review<br>backend product type and buying path repair<br>price/media/checkout proof |
| Easter Balloon Cups | `easter-balloon-cups` | certified_checkout | certified_current_checkout | found | 7 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Star Column | `star-column` | blocked_until_certified | add_on_conditional_pricing_build | found | 4 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Sleepy Baby Column | `sleepy-baby-column` | blocked_until_certified | multi_color_recipe_checkout_build | found | 1 | customer-facing multi-color recipe UI<br>backend color recipe validation<br>checkout/payment/invoice/receipt cascade proof |
| Baby Table decor | `baby-table-decor` | blocked_until_certified | multi_color_recipe_checkout_build | found | 1 | customer-facing multi-color recipe UI<br>backend color recipe validation<br>checkout/payment/invoice/receipt cascade proof |
| Logo 3 layered bouquet | `logo-3-layered-bouquet` | blocked_until_certified | add_on_conditional_pricing_build | found | 1 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| 6 color rainbow arch | `6-color-rainbow-arch` | blocked_until_certified | add_on_conditional_pricing_build | found | 2 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Mother's day front yard 7' Column | `mothers-day-front-yard-7-column` | blocked_until_certified | simple_purchasable_rehearsal | found | 1 | focused source/export purchasable rehearsal<br>open-mode product UX proof<br>checkout/payment/invoice/receipt cascade proof |
| Marble table decor | `marble-table-decor` | blocked_until_certified | source_backend_review | found | 1 | source export meaning review<br>backend product type and buying path repair<br>price/media/checkout proof |
| Paw Patrol Bouquet | `paw-patrol-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Elsa Bouquet | `elsa-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Holy COW!! Bouquet | `holy-cow-bouquet` | certified_checkout | certified_current_checkout | found | 3 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Butterfly "GET WELL" Bouquet (Latex free) | `butterfly-get-well-bouquet-latex-free` | blocked_until_certified | source_backend_review | found | 1 | source export meaning review<br>backend product type and buying path repair<br>price/media/checkout proof |
| Bandage "GET WELL" Bouquet (Latex free) | `bandage-get-well-bouquet-latex-free` | blocked_until_certified | source_backend_review | found | 1 | source export meaning review<br>backend product type and buying path repair<br>price/media/checkout proof |
| Shooting star "GET WELL" Bouquet (Latex free) | `shooting-star-get-well-bouquet-latex-free` | blocked_until_certified | source_backend_review | found | 1 | source export meaning review<br>backend product type and buying path repair<br>price/media/checkout proof |
| 6' Graduation stands | `6-graduation-stands` | certified_checkout | certified_current_checkout | found | 2 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| classic organic for easel | `classic-organic-for-easel` | blocked_until_certified | multi_color_recipe_checkout_build | found | 1 | customer-facing multi-color recipe UI<br>backend color recipe validation<br>checkout/payment/invoice/receipt cascade proof |
| Easter Arch | `easter-arch` | blocked_until_certified | simple_purchasable_rehearsal | found | 1 | focused source/export purchasable rehearsal<br>open-mode product UX proof<br>checkout/payment/invoice/receipt cascade proof |
| Mother's Day Bouquet | `mothers-day-bouquet` | certified_checkout | certified_current_checkout | found | 1 | keep checkout_product_family_contract green<br>keep post_import_checkout_proof green |
| Large Garland | `large-garland` | blocked_until_certified | add_on_conditional_pricing_build | found | 3 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Large Organic Column | `large-organic-column` | blocked_until_certified | add_on_conditional_pricing_build | found | 6 | explicit add-on or conditional pricing contract<br>ERPNext price provenance<br>checkout/payment/invoice/receipt cascade proof |
| Pride Arch | `pride-arch` | blocked_until_certified | simple_purchasable_rehearsal | found | 1 | focused source/export purchasable rehearsal<br>open-mode product UX proof<br>checkout/payment/invoice/receipt cascade proof |
