# Product Add-on Approval Packet

This packet is source-backed and read-only. It does not approve checkout add-ons.
Every row defaults to quote-only until GL/Locally Twisted approves a product-family mapping.

## Summary

- Source products: 53
- Review axes: 4
- Affected products: 9
- Approved for checkout: 0

## Review Rows

| Axis | Product count | Values | Decision needed | Safe default |
|---|---:|---|---|---|
| Add Bouquet | 1 | 5 balloon bouquet, 7 balloon bouquet, Small 3 balloon bouquet | Decide whether companion bouquets are product bundles, separate checkout lines, quote-only upsells, or removed from import. | quote_only_until_approved |
| Add ons | 3 | Foil stars, themed foils, None | Decide whether each value is a priced add-on, included decor choice, quote-only prompt, or source artifact to drop. | quote_only_until_approved |
| Orbz toppers | 2 | Black/gold, Blue Marble, Blue/gold, Blue/Green, Fantacy, Gold Marble, Pink Marble, Pink/gold, Purple, Red | Decide topper eligibility, visual/media treatment, price, fulfillment notes, and quote-vs-checkout behavior. | quote_only_until_approved |
| Plush add ons | 3 | Teddy Bear, None | Decide product eligibility, supplier/stock behavior, price, quantity rule, and whether plush should ever be paid checkout. | quote_only_until_approved |

## Affected Products

### Add Bouquet

- `birthday-deliveries`: Birthday Deliveries (Quote request first); values: 5 balloon bouquet, 7 balloon bouquet, Small 3 balloon bouquet

### Add ons

- `premium-organic-arch`: Premium Organic Arch (Quote request first); values: Foil stars, themed foils
- `pemium-organic-column`: Pemium Organic Column (Quote request first); values: Foil stars, themed foils
- `classic-organic-arch`: Classic Organic Arch (Quote request first); values: Foil stars, themed foils, None

### Orbz toppers

- `star-column`: Star Column (Quote request first); values: Black/gold, Blue Marble, Blue/gold, Blue/Green, Fantacy, Gold Marble, Pink Marble, Pink/gold, Purple, Red
- `marble-table-decor`: Marble table decor (Quote request first); values: Black/gold, Blue Marble, Blue/gold, Blue/Green, Fantacy, Gold Marble, Pink Marble, Pink/gold, Purple, Red

### Plush add ons

- `butterfly-get-well-bouquet-latex-free`: Butterfly "GET WELL" Bouquet (Latex free) (Quote request first); values: Teddy Bear, None
- `bandage-get-well-bouquet-latex-free`: Bandage "GET WELL" Bouquet (Latex free) (Quote request first); values: Teddy Bear, None
- `shooting-star-get-well-bouquet-latex-free`: Shooting star "GET WELL" Bouquet (Latex free) (Quote request first); values: Teddy Bear, None
