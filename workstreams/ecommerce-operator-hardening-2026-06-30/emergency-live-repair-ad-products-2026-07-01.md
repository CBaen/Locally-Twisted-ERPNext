# Emergency Live Repair - Ad-Facing Product Pages - 2026-07-01

## Scope

Guiding Light approved an urgent production repair before Meta ads for:

- `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`
- `https://locallytwisted.com/shop-items/bouquets/birthday-deliveries`

This was a production data/config repair only. It was not a source-code deploy,
schema migration, cache clear, payment change, DNS change, broad catalog fix,
or reusable ecommerce architecture completion.

## Capability Gate

Capability gate passed from the LT repo root with:

- `capabilities/INDEX.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

The active release lane was `emergency live repair`.

## Live Changes Applied

### Large Head Missionary

Problem:

- Product Setup / `LT Product Blueprint` already held the owner change to
  `125.0`.
- The customer-facing page still rendered `$ 175.00` because the live
  `Standard Selling` `Item Price` rows still held `175.0`.

Repair:

- Updated all 30 live `Standard Selling` `Item Price` rows for
  `large-head-missionary` variants from `175.0` to `125.0`.
- No Product Setup, Website Item copy, media, checkout, payment, DNS, or code
  deploy change was made for this product.

Rollback evidence:

- `/tmp/lt-emergency-live-repair-rollback-20260701.json`

Verification:

- `/tmp/lt-emergency-large-head-before-final-20260701.json`
- `/tmp/lt-emergency-large-head-after-20260701.json`
- After repair, the live audit reported:
  - Product Setup base price: `125.0`
  - Item Price row count: `30`
  - Item Price rates: `[125.0]`
  - Public page status: `200`
  - Public price strings: `["$ 125.00", "$15", "$50"]`
  - `contains_125=true`
  - `contains_175=false`
- Browser proof on the live public route also found `$ 125.00` and no `$175`.

### Birthday Deliveries

Problem:

- The `Add Foil Number` Product Setup option was incorrectly modeled as a
  one-digit, SKU-defining `Single select` variant axis with values `0` through
  `9`.
- That made the customer page represent birthdays as one digit only and also
  contributed to variant explosion.
- 2026-07-02 correction: the first emergency repair changed Product Setup, but
  the native ERPNext variant selector still rendered the old `Add Foil Number`
  dropdown because existing Birthday Deliveries variants still carry that SKU
  axis. Customer-visible reality remained wrong until the native selector was
  hidden/defaulted.

Repair:

- Updated live `LT Product Blueprint Option` `ac0ehl0540`:
  - `axis_name`: `ADD BIRTHDAY AGE`
  - `control_type`: `Number`
  - `selection_behavior`: `Measurement/Text`
  - `payload_target`: `configuration_groups`
  - `pricing_behavior`: `Included in base price`
  - `required`: `1`
  - `min_selections`: `1`
  - `max_selections`: `1`
- Widened the hidden live `values` list to numeric strings `0` through `999`
  because the current server resolver still applies `values` as an allowed
  set even for `Number` controls. This is an emergency compatibility repair,
  not the desired long-term architecture.
- Added an emergency route-scoped `Website Settings.head_html` bridge with
  marker `lt-birthday-age-variant-axis-bridge-20260702`. The bridge only runs
  on `/shop-items/bouquets/birthday-deliveries`, hides the legacy native
  `Add Foil Number` variant selector from customers, and selects the first
  currently valid hidden legacy value so ERPNext's existing variant resolver
  can still reach a priced SKU while the visible `ADD BIRTHDAY AGE` number
  field carries the customer's actual age.

Verification:

- Live Product Setup schema for `birthday-deliveries` now reports
  `ADD BIRTHDAY AGE` as:
  - `control_type=Number`
  - `selection_behavior=Measurement/Text`
  - `sku_defining=false`
  - `payload_target=configuration_groups`
  - `pricing_behavior=Included in base price`
  - `required=true`
  - `min_selections=1`
  - `max_selections=1`
- Public HTML for Birthday Deliveries returned `x-from-cache=False` and
  embedded the updated `Number` / `configuration_groups` schema.
- Browser proof on the live public route found exactly one `ADD BIRTHDAY AGE`
  configuration group rendered as `input type="number"` and found no competing
  dropdown/radio/checkbox choice inputs for that field.
- Live resolver proof using real Birthday selected options:
  - age `25`: no blockers
  - age `100`: no blockers
  - empty age: blocked with a choose-at-least-one message for the birthday age
    field
  - `abc`: blocked as an invalid birthday age value
- 2026-07-02 visible/browser proof after the bridge:
  - desktop and mobile visible text includes `ADD BIRTHDAY AGE`;
  - desktop and mobile visible text does not include `Add Foil Number`;
  - the old native `Add Foil Number` selector still exists in HTML only as a
    hidden compatibility axis with `display: none` and `aria-hidden=true`;
  - customer-visible `ADD BIRTHDAY AGE` renders as one `input type="number"`;
  - selecting Delivery Size, Delivery themes, Add Bouquet, and entering age
    `25` enabled Add to Cart with a priced variant and `$ 90.00`.
- 2026-07-02 follow-up after GL reported `Add Bouquet` price behavior:
  - live `Item Price` rows for Birthday Deliveries are not flat; there are
    2,430 variant prices with nine live price tiers:
    `90`, `100`, `110`, `120`, `130`, `140`, `155`, `165`, `175`;
  - by size and bouquet suffix, current live prices are:
    - Small + Small 3 balloon bouquet: `$90.00`
    - Small + 5 balloon bouquet: `$100.00`
    - Small + 7 balloon bouquet: `$110.00`
    - Medium + Small 3 balloon bouquet: `$120.00`
    - Medium + 5 balloon bouquet: `$130.00`
    - Medium + 7 balloon bouquet: `$140.00`
    - Large + Small 3 balloon bouquet: `$155.00`
    - Large + 5 balloon bouquet: `$165.00`
    - Large + 7 balloon bouquet: `$175.00`
  - live browser proof with theme `Mickey`, visible age `25`, and the hidden
    compatibility axis selected by the bridge showed the same nine prices and
    enabled Add to Cart for every tested size/bouquet path.
  - Earlier proof was too narrow: it checked the corrected age field and one
    selected path, not the full customer scenario matrix. Future emergency
    fixes on variant products must include at least one matrix proof across
    every customer-visible price-changing axis.

## Follow-Up Architecture Required

Do not treat this repair as the ecommerce architecture fix.

Required reusable architecture work:

- Product Setup `Number` and `Text` controls should not require or enforce
  choice-list `values`.
- The resolver should enforce control-type-specific validation:
  - `Number`: numeric format, required/min/max intent, optional numeric bounds.
  - `Text`: required/min/max length or pattern where configured.
  - choice controls: allowed values.
- Birthday age should remain a configuration/measurement input, not a
  SKU-defining variant axis and not an add-on.
- The temporary `Website Settings.head_html` bridge must be retired after the
  reusable architecture removes non-SKU human inputs from the Birthday
  Deliveries variant axis model. Do not leave this as the final ecommerce
  architecture.
- Product Setup publish/apply or direct-runtime authority must still be built
  so owner saves reach Website Item, Item, Item Price, media, cart, checkout,
  and public route authority with explicit proof.
- This incident reinforces that SKU-defining axes must be reserved for choices
  that truly determine a sellable SKU; human-entered age text/number fields
  must not explode variants.

## Boundaries

Unrelated dirty repo files were not staged or modified for this live repair.
No deploy was performed.
