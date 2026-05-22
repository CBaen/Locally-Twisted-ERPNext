# Research Brief: Shop Category Generated Heroes

### 1. Want

Each `/shop-items/<category>` page needs a compact, high-quality, realistic hero image that shows the actual category shape at the LT hero aspect ratio. The image should feel intentionally art-directed for the page, not like a bad source-photo crop. Balloon colors must come from the LT owner/Odoo color system: exact source color names and swatch images first, sampled hex only as a web approximation.

### 2. Have

The local ERPNext/Frappe site runs at `http://localhost:8081`, with public hero image CSS in `apps/locally_twisted/locally_twisted/public/css/lt-photo-heroes.css`. Existing generated hero sources live under `_resources/generated-hero-sources/2026-05-10/`, with public breakpoint crops in `apps/locally_twisted/locally_twisted/public/images/heroes/`. The Odoo color source is verified through `_resources/odoo-live/catalog.json`, `apps/locally_twisted/locally_twisted/catalog_contract/odoo_color_swatch_map.json`, and `python scripts\verify\odoo_color_swatch_contract.py`, which currently reports 53 `latex colors` drawer options and owner swatches.

### 3. Won't Accept

- No reused bad product-source photo crops as category heroes.
- No generic stock-like balloon scenes that could be any balloon business.
- No image prompts that rely only on hex values.
- No model-invented colors outside the owner/Odoo swatch catalog.
- No proof-photo implication; generated heroes are representative product visualization only.
- No readable text, logos, watermarks, misspelled signage, or fake brand marks inside images.
- No hero composition that fails the compact hero crop at desktop, tablet, or mobile.

### 4. Open To

The hero generation workflow can use the existing Together AI / FLUX path, a focused repo script, and a new dated generated-source folder. Public CSS filenames can remain stable if the bad files are overwritten by better generated assets. The source manifest should preserve prompts, exact palette names, swatch references, and derivative dimensions so another agent can regenerate or audit later.

### 5. Questions

1. Which category shape must be visible in the center crop for each route?
2. Which source color names from the LT drawer best fit each category's commercial use?
3. Does the generated source image stay legible after desktop, tablet, and mobile crop derivatives?
4. Do all public assets return `200` and render through the Frappe/Webshop hero CSS?
5. Does the final proof avoid confusing representative generated imagery with real LT install proof?
