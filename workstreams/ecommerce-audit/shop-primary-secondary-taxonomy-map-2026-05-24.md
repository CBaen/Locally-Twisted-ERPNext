# Shop Primary And Secondary Taxonomy Map - 2026-05-24

## Status

Approved direction from GL for documentation and future implementation planning.
This packet does not change ERPNext data, product names, slugs, routes, prices,
images, checkout behavior, payment settings, staging, live, DNS, Stripe, or
Search Console.

Verified local source before writing:

- Local ERPNext published `Website Item` count: `51`.
- Current Ready-to-Order menu source: visible `Item Group` children of
  `Shop Items`.
- Current secondary `Website Item Group` rows: `0`; secondary taxonomy is not
  yet implemented in the local catalog data.

## Taxonomy Contract

Primary category answers: **what physical product type is this?**

Secondary category answers: **what broad occasion or use case is this for?**

Product names are frozen for this taxonomy pass. Do not rename products as part
of the category cleanup.

Do not use any of these as primary or secondary categories:

- Delivery
- Pickup
- Latex-free
- Color
- Size
- Add-ons
- Foil numbers
- Grab & Go
- Specific holiday names such as Easter, Halloween, Mother's Day, or Pride
- Character/theme names
- Product option values

Specific terms such as Easter, Halloween, Mother's Day, Pride, latex-free,
delivery-eligible, and pickup-eligible belong in product names, product copy,
search keywords, product options, checkout fulfillment, or future tags. They do
not belong in the two-level category model.

## Approved Secondary Categories

- Any Occasion
- Birthday
- Holiday
- Graduation
- Baby Shower
- Sports
- Get Well
- Religious
- Corporate

## Approved Mapping

| Item code | Product name | Current primary | Approved primary | Approved secondary |
|---|---|---|---|---|
| `6-color-rainbow-arch` | 6 color rainbow arch | Arches | Arches | Any Occasion |
| `6-graduation-stands` | 6' Graduation stands | Stands & Easels | Stands & Easels | Graduation |
| `7-butterfly-column` | 7' Butterfly Column | Columns | Columns | Any Occasion |
| `7-epic-column` | 7' Epic Column | Columns | Columns | Any Occasion |
| `baby-shower-combination-photo-opt` | Baby Shower Combination Photo opt | Table Decor | Photo Ops & Backdrops | Baby Shower |
| `baby-shower-garland` | Baby Shower Garland | Garlands | Garlands | Baby Shower |
| `baby-table-decor` | Baby Table decor | Table Decor | Table Decor | Baby Shower |
| `balloon-drop` | Balloon Drop | Drops | Balloon Drops | Any Occasion |
| `bandage-get-well-bouquet-latex-free` | Bandage "GET WELL" Bouquet (Latex free) | Get-Well Bouquets | Bouquets | Get Well |
| `basketball-arch` | Basketball Arch | Arches | Arches | Sports |
| `birthday-deliveries` | Birthday Deliveries | Deliveries | Bouquets | Birthday |
| `butterfly-get-well-bouquet-latex-free` | Butterfly "GET WELL" Bouquet (Latex free) | Get-Well Bouquets | Bouquets | Get Well |
| `classic-arch` | Classic Arch | Arches | Arches | Any Occasion |
| `classic-column` | Classic Column | Columns | Columns | Any Occasion |
| `classic-organic-arch` | Classic Organic Arch | Arches | Arches | Any Occasion |
| `classic-organic-balloon-garland` | Classic Organic Balloon Garland | Garlands | Garlands | Any Occasion |
| `classic-organic-columns` | Classic Organic columns | Columns | Columns | Any Occasion |
| `classic-organic-for-easel` | classic organic for easel | Stands & Easels | Stands & Easels | Any Occasion |
| `easter-balloon-arch-bunny-ear` | Easter Balloon Arch - Bunny Ear | Arches | Arches | Holiday |
| `easter-balloon-cups` | Easter Balloon Cups | Seasonal & Specialty | Table Decor | Holiday |
| `elsa-bouquet` | Elsa Bouquet | Bouquets | Bouquets | Birthday |
| `encanto-bouquet` | Encanto Bouquet | Bouquets | Bouquets | Birthday |
| `flamingo-bouquet` | Flamingo Bouquet | Bouquets | Bouquets | Birthday |
| `football-bouquet` | Football Bouquet | Bouquets | Bouquets | Sports |
| `graduation-grab-n-go` | Graduation Grab n Go | Grab & Go | Garlands | Graduation |
| `halloween-arch` | Halloween arch | Arches | Arches | Holiday |
| `holy-cow-bouquet` | Holy COW!! Bouquet | Bouquets | Bouquets | Birthday |
| `large-garland` | Large Garland | Garlands | Garlands | Any Occasion |
| `large-head-missionary` | Large head Missionary | Bouquets | Bouquets | Religious |
| `large-organic-column` | Large Organic Column | Columns | Columns | Any Occasion |
| `logo-3-layered-bouquet` | Logo 3 layered bouquet | Bouquets | Bouquets | Corporate |
| `marble-table-decor` | Marble table decor | Table Decor | Table Decor | Any Occasion |
| `mickey-mouse-bouquet` | Mickey Mouse Bouquet | Bouquets | Bouquets | Birthday |
| `minion-bouquet` | Minion Bouquet | Bouquets | Bouquets | Birthday |
| `mothers-day-bouquet` | Mother's Day Bouquet | Bouquets | Bouquets | Holiday |
| `mothers-day-front-yard-7-column` | Mother's day front yard 7' Column | Columns | Columns | Holiday |
| `number-balloon-columns` | Number Balloon Columns | Columns | Columns | Birthday |
| `organic-grab-n-go` | Organic Grab n' Go | Grab & Go | Garlands | Any Occasion |
| `over-the-hill-bouquet` | Over the Hill Bouquet | Bouquets | Bouquets | Birthday |
| `paw-patrol-bouquet` | Paw Patrol Bouquet | Bouquets | Bouquets | Birthday |
| `pemium-organic-column` | Pemium Organic Column | Columns | Columns | Any Occasion |
| `premium-organic-arch` | Premium Organic Arch | Arches | Arches | Any Occasion |
| `premium-organic-garland` | Premium Organic Garland | Garlands | Garlands | Any Occasion |
| `pride-progress-rainbow-balloon-arch` | Pride progress Rainbow Balloon Arch | Arches | Arches | Holiday |
| `shooting-star-get-well-bouquet-latex-free` | Shooting star "GET WELL" Bouquet (Latex free) | Get-Well Bouquets | Bouquets | Get Well |
| `sleepy-baby-column` | Sleepy Baby Column | Columns | Columns | Baby Shower |
| `soccer-bouquet` | Soccer Bouquet | Bouquets | Bouquets | Sports |
| `space-bouquet` | Space Bouquet | Bouquets | Bouquets | Birthday |
| `star-column` | Star Column | Columns | Columns | Any Occasion |
| `stitch-bouquet` | Stitch Bouquet | Bouquets | Bouquets | Birthday |
| `unicorn-bouquet` | Unicorn Bouquet | Bouquets | Bouquets | Birthday |

## Primary Category Cleanup

These current primary groups should be removed or demoted during the eventual
implementation:

- `Deliveries` is fulfillment, not a product category.
- `Get-Well Bouquets` is an occasion/use-case grouping; approved primary is
  `Bouquets`, approved secondary is `Get Well`.
- `Grab & Go` is not a product category. It can be a marketing/menu concept,
  but the approved primary for those current products is `Garlands`.
- `Seasonal & Specialty` is not a product type. The current product maps to
  `Table Decor` with secondary `Holiday`.
- `Drops` should become `Balloon Drops` if route and redirect planning approves
  that primary label change.

New or confirmed primary categories needed by the approved mapping:

- Arches
- Balloon Drops
- Bouquets
- Columns
- Garlands
- Photo Ops & Backdrops
- Stands & Easels
- Table Decor

## Implementation Notes For Future Agents

Do not implement this by manually editing random Desk records. The safe path is:

1. Create a source-owned taxonomy mapping artifact from this approved packet.
2. Add a verifier that fails if banned primary or secondary category terms
   appear in the product taxonomy.
3. Add or confirm any needed primary `Item Group` records.
4. Apply primary category changes through the reviewed seed/sync path.
5. Add secondary categories through the Webshop `Website Item Group` child table
   or an equivalent source-owned projection, then update menu/category/search
   code only after the data model is verified.
6. Plan route and redirect behavior before changing any primary category that
   affects public URLs.
7. Clear website cache and verify `/shop`, `/shop-items/<group>`, product pages,
   header menu/search, cart, and checkout smoke paths.

No staging/live/provider mutation is approved by this packet. Promotion must use
the normal Frappe Cloud staging release gate and protect production data,
payment settings, DNS, Search Console, and live Stripe.
