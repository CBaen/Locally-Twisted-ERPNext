## Plan-Deepen Result: **Adjust**

The current plan is directionally right, but it needs more explicit **logic gates** and **stop conditions** before any import/build.

---

## 1. Core correction

This is not:

- “import products”
- “make product pages”
- “copy catalog_data fields”
- “style ERPNext ecommerce”

This is:

> Build a native ERPNext ecommerce logic layer capable of receiving catalog_data-conceptual product data and integrating it everywhere in the ERPNext ecosystem without silent failure.

---

## 2. Required plan additions

### A. Field existence gate

Before importing any product field:

- Does ERPNext already have the field?
- If yes, does it behave correctly for ecommerce?
- If no, do we need:
  - custom field,
  - custom child table,
  - custom DocType,
  - contract JSON,
  - cart metadata,
  - Sales Order Item metadata,
  - invoice description logic?

**Stop condition:** if the destination field does not exist, no import.

---

### B. Logic ownership gate

Every product behavior must have an owner:

- backend contract
- ERPNext Item / Website Item
- custom DocType
- pricing service
- frontend renderer
- cart API
- checkout validation
- invoice/order writer

**Stop condition:** if logic only exists in frontend JS, it is not safe.

---

### C. catalog_data concept mapping gate

For each catalog_data ecommerce concept:

- variants
- option groups
- add-ons
- conditional choices
- dynamic pricing
- variant images
- product descriptions/details
- checkout fields

Decide:

1. Native ERPNext supports it.
2. ERPNext supports it only with customization.
3. ERPNext cannot support it safely yet.
4. Business/design decision required.

**Stop condition:** “AI can migrate the data” is irrelevant unless ERPNext can use the data.

---

### D. Ecosystem integration gate

A product is not “received” until it works in:

- import records
- backend fields
- product page
- desktop journey
- mobile journey
- add-to-cart
- cart summary
- checkout
- payment/tax/fulfillment logic
- Sales Order
- invoice/order meaning
- operator fulfillment view
- verifier report

**Stop condition:** if it only works on the product page, it is not received.

---

### E. Fail-loud gate

Missing or awkward data must produce:

- import blocker,
- verifier failure,
- visible admin report,
- customer-safe block,
- or GL decision queue.

Not allowed:

- hidden missing fields
- fallback copy that looks correct
- frontend-only pricing
- unavailable options still purchasable
- invoice lines that lose configuration meaning

---

## 3. Concrete blast-radius categories

Each missing ecommerce feature needs a mini design review before build.

Required blast-radius notes:

1. **Variant logic**
   - affects Item variants, selectors, price, image, cart item code, invoice line.

2. **Add-on logic**
   - affects product contract, UI, cart lines, pricing, tax, invoice grouping.

3. **Dynamic pricing**
   - affects catalog_data resolver comparison, ERPNext Item Price, cart total, checkout total, invoice.

4. **Variant image/media logic**
   - affects product gallery and customer visibility only when source provides variant-linked image data.

5. **Custom option dependencies**
   - affects selector order, disabled options, invalid combinations, quote-required behavior.

6. **Product template type**
   - affects whether the product uses simple or complex flow across desktop/mobile/backend.

7. **Invoice/order preservation**
   - affects whether the business can fulfill what the customer actually selected.

8. **Mobile journey**
   - affects whether complex products remain usable without hiding required fields.

---

## 4. Revised sequence

### Step 1 — Research brief
Use the research-brief skill. Verify current stack/code facts. No bloat.

### Step 2 — Expedition
Research ERPNext/Frappe ecommerce architecture + catalog_data ecommerce concepts relevant to our exact stack and problem.

### Step 3 — Capability model
Define what ERPNext ecommerce must become capable of before import.

### Step 4 — Mapping matrix
catalog_data concept → ERPNext native/custom/missing/unsafe.

### Step 5 — Missing-feature blast-radius register
One entry per missing feature before building.

### Step 6 — Template logic contracts
Simple product flow + complex custom product flow.

### Step 7 — Verifier spec
Import, frontend, pricing, cart, checkout, invoice, mobile/desktop.

### Step 8 — GL checkpoint
No build/import until we agree on the architecture.

---

## 5. Key non-negotiable

No product migration is meaningful until ERPNext can safely receive and use the product everywhere.

Test imports are allowed only to prove architecture. Real imports wait.