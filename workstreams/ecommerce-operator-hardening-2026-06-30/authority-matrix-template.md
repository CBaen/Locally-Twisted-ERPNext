# Product Authority Matrix Template

Date: 2026-06-30

Status: reusable non-mutating template for one product authority packet. Do not use a completed packet as write approval. A packet is complete only when each required authority, rollback target, and blocker is resolved with evidence.

## Evidence Rules

Classify every fact before using it:

| Evidence Class | Meaning | May Close Authority? |
|---|---|---|
| Public render | Customer-visible route, HTML, public API, image URL, or shop listing observed without login | No, unless the field is only public-render behavior |
| Source code | Repository code, seed data, verifier, or committed workstream source | No, unless the field is a source contract |
| Historical reference | Prior audit, import manifest, workstream, or legacy business reference | No, evidence only |
| Authenticated read-only DB/Desk | Current row-level facts from the target ERPNext site, read without mutation | Yes, when paired with public proof |
| Owner/business approval | Explicit Guiding Light or owner decision for business meaning | Yes, for scope/meaning; still needs technical proof |

If evidence is missing, write `Unknown - needs authenticated read-only DB/Desk proof` or the narrower proof needed. Do not infer current DB facts from old reports, public HTML, or source seeds.

## Packet Header

| Field | Value |
|---|---|
| Product |  |
| Packet date |  |
| Prepared by |  |
| Scope | Non-mutating authority mapping only |
| Environment checked |  |
| Public route checked |  |
| Authenticated DB/Desk checked | No / Yes with method |
| Mutation allowed by this packet | No |
| Payment/provider/live settings touched | No |

## Brand And Route Authority

| Field | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Brand lane |  |  |  |
| Public route |  |  |  |
| Route namespace/category |  |  |  |
| Canonical URL/meta URL |  |  |  |
| Old route/redirect handling |  |  |  |
| Customer-facing copy surface |  |  |  |
| Document/payment/customer-message identity |  |  |  |

## Product Record Authority

| Surface | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Website Item row |  |  |  |
| Website Item published/hidden status |  |  |  |
| Website Item linked Item |  |  |  |
| Template Item |  |  |  |
| Sellable Item/variant rows |  |  |  |
| Variant attributes |  |  |  |
| Item group/category |  |  |  |
| Product Setup record |  |  |  |
| Product Setup active uniqueness |  |  |  |
| Product Setup state |  |  |  |

## Content Authority

| Field | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Product title |  |  |  |
| Short/listing copy |  |  |  |
| Story/details copy |  |  |  |
| Standard description fallback |  |  |  |
| SEO title/description |  |  |  |
| Social metadata |  |  |  |
| Product page type |  |  |  |
| Commerce lane |  |  |  |
| Fulfillment lane |  |  |  |

## Price Authority

| Price Surface | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Business/source-approved price |  |  |  |
| Product Setup base price |  |  |  |
| Exact variant Item Prices |  |  |  |
| Price list/currency/UOM |  |  |  |
| Shop listing price |  |  |  |
| Product page starting price |  |  |  |
| Variant selector price |  |  |  |
| Cart line amount |  |  |  |
| Checkout/Sales Order amount |  |  |  |
| Payment amount/label |  |  |  |
| Invoice/receipt amount/label |  |  |  |
| Unsupported price rules |  |  |  |

## Media Authority

| Media Role | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Product Setup primary image |  |  |  |
| Website Item website image |  |  |  |
| Item image |  |  |  |
| File attachment and file visibility |  |  |  |
| Product HTML metadata/social image |  |  |  |
| Shop card image |  |  |  |
| Product page primary image |  |  |  |
| Product page gallery |  |  |  |
| Selected-option/variant image |  |  |  |
| Cart image |  |  |  |
| Payment line image |  |  |  |
| Receipt/document image |  |  |  |
| Merchandising references |  |  |  |

## Options And Add-Ons

| Option/Add-On | Classification | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|---|
|  | SKU-defining variant / configuration-only / color recipe / measurement-upload / review-only quote context / paid checkout add-on / unsupported |  |  |  |

## Listing And Cart Eligibility

| Invariant | Confirmed Authority | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Published Website Item |  |  |  |
| Linked Item enabled |  |  |  |
| Correct commerce lane |  |  |  |
| Sellable Item or selected variant |  |  |  |
| Standard Selling Item Price |  |  |  |
| Required Product Setup authority |  |  |  |
| Public route proof |  |  |  |
| Shop listing proof |  |  |  |
| Cart API proof |  |  |  |
| Checkout proof mode |  |  |  |

## Historical References

| Reference | What It Proves | What It Does Not Prove |
|---|---|---|
|  |  | Current live DB state |

## Rollback Target

| Rollback Component | Confirmed Target | Evidence | Unknowns / Required Proof |
|---|---|---|---|
| Prior-live Website Item fields |  |  |  |
| Prior-live Item/template fields |  |  |  |
| Prior-live variant rows |  |  |  |
| Prior-live Item Prices |  |  |  |
| Prior-live Product Setup state |  |  |  |
| Prior-live media/files/slideshow rows |  |  |  |
| Prior-live route/category/listing behavior |  |  |  |
| Prior-live cart/checkout behavior |  |  |  |

## Blocker List

| Blocker | Category | Blocks | Required Next Proof |
|---|---|---|---|
|  | Needs your decision / Needs manager approval / Needs a missing photo / Not safe to sell yet / Developer help required / Waiting for proof / Brand lane unclear / Payment-release gate required |  |  |

## Closure Checklist

- Brand lane resolved.
- Public route and Website Item resolved.
- Product Setup record and active uniqueness resolved.
- Template Item and sellable variant rows resolved.
- Price authority resolved from business/source intent through cart and checkout proof mode.
- Media roles resolved through at least public page, shop card, cart, and document/payment mode where relevant.
- Options and add-ons classified.
- Listing/cart eligibility invariant proved.
- Historical references preserved without treating stale artifacts as current truth.
- Rollback target defined from current row-level snapshot.
- Remaining blockers are owner-readable and assigned to a next proof step.
