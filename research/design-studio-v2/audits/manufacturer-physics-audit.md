# Manufacturer + Physics Audit — Design Studio v2

Scope: read-only audit of `research/design-studio-v2` against public manufacturer/pro balloon-construction references for 11-inch latex balloons, classic arches, columns, and organic garland-like recipes.

Date: 2026-05-07

## 1) Executive verdict

The prototype is directionally useful as a planning visual, but its current classic-build math is not safe to reuse as quote/production math yet.

Main issue: the current classic arch/column code treats 11-inch latex as **8 balloons per foot / 2 quad clusters per foot**. Public pro references commonly put 11-inch classic arches around **6 balloons per foot** for clustered spiral arches, and one pro calculator example using 11-inch standard latex sized to 10 inches computes **one quad cluster per 10 inches** (~4.8 balloons/ft). For columns, public pro guidance commonly uses **4 balloons per tier and about 1 tier per foot** for 11-inch balloons inflated to 10 inches. Current column math is therefore roughly **2x** a common pro column count.

That over-density may be acceptable for a deliberately stylized on-screen preview, but it must be labeled as render density, not production quantity. If it flows into ERPNext quote lines, materials planning, or customer-facing “estimated balloons,” it risks overquoting and making Jeff/Locally Twisted look inaccurate.

Recommended next move: split the model into two lanes:

- **Visual packing lane:** render-friendly density, capped object counts, soft overlap, “planning visual only.”
- **Production estimate lane:** manufacturer/pro-backed formulas, explicit sizing assumptions, overage, frame/weight/labor flags, and “final install confirmed by LT.”

## 2) Manufacturer/pro construction facts relevant to 11-inch latex, arches, columns, garlands

### 11-inch latex manufacturer facts

- The local balloon visual profile records 11-inch round latex with `listed_inflated_diameter_in: 11`, `listed_gas_capacity_cuft: 0.5`, and `listed_gas_capacity_m3: 0.015`.
  - Local evidence: `event-builder-spike/src/balloon-visual-model.js`, `BALLOON_SIZE_PROFILES.round_latex_11_standard`.
- Public Qualatex helium chart search result also reports 11-inch standard/special colors at **0.5 cu ft / 0.015 m³** and average flying time around **18–24 hours** for standard/special colors, with similar 0.015 m³ capacity in the indexed chart snippet.
  - URL: https://www.balloons.com/docs/Qualatex-Helium-Chart.pdf
  - Search result evidence: `Qualatex Helium Chart Latex & Cloudbuster Balloon... 11" ... 0.5 cu ft (.015m3) ... 18-24 hours` from https://www.scribd.com/document/274349620/Qualatex-Helium-Chart
- A retail Qualatex listing independently states 11-inch capacity as **0.5 cu ft per balloon when accurately sized** and notes untreated helium float time around **12 hours**.
  - URL: https://www.click4balloons.co.uk/qualatex-11-inch-balloons---red-11-balloons-standard-100pcs-26619-p.asp

### Classic arches

- burton + BURTON describes a spiral/swirl balloon arch as **3- or 4-cluster latex balloon groups** attached to monofilament line.
  - URL: https://www.burtonandburton.com/education/basics/balloon-basics/arches.aspx
- Their build instructions for a 4-balloon quad arch say:
  - inflate uniformly with a sizing template,
  - tie two same-color balloons together,
  - tie two contrasting-color balloons together,
  - twist the two duplets into a quad,
  - secure each quad to monofilament, keeping the line tight and quads solidly packed,
  - create the swirl by moving the contrasting color **one quarter turn clockwise** as quads are packed.
  - URL: https://www.burtonandburton.com/education/basics/balloon-basics/arches.aspx
- burton + BURTON’s education page lists balloon count per foot for spiral arches:
  - 5 inch = 12/ft
  - 9 inch = 8/ft
  - **11 inch = 6/ft**
  - 14 inch = 4/ft
  - 16 inch = 4/ft
  - URL: https://www.burtonandburton.com/education/basics/balloon-basics/arches.aspx
- burton + BURTON’s newer arch quote article uses 11-inch standard latex **sized to 10 inches** and calculates clusters by dividing arch length in inches by 10 inches, then multiplying by 4 or 5 balloons per cluster. That implies a 4-balloon clustered arch density of about **4.8 balloons/ft** at 10-inch sizing.
  - URL: https://www.burtonandburton.com/blog/calculate-balloon-arch.aspx
- Balloon Decoration Guide gives a similar rule of thumb: **11 inch balloons = 6 per foot**, so a 10 ft arch uses 60 balloons / 15 four-balloon clusters.
  - URL: https://www.balloon-decoration-guide.com/how-many-balloons-for-an-arch.html

### Columns

- A public column calculator states the standard column formula as **4 balloons per tier, one tier per foot** when using 11-inch balloons inflated to 10 inches. It also describes the physical build as tiers/quads arranged around a central pole, each tier offset/rotated from the one below.
  - URL: https://hicomemphis.com/academy/balloon-column-calculator/
- The same source states air-filled columns on a central pole are the normal/pro recommendation; helium columns are more expensive, shorter-lived, and structurally worse for most situations.
  - URL: https://hicomemphis.com/academy/balloon-column-calculator/

### Organic garlands

- The local prototype treats garlands as organic recipes rather than fixed quads: “Doublets on a strip with 5 inch filler and controlled randomness,” with size mix including 5/11/16/24 inch balloons and a 10–15% planning overage.
  - Local evidence: `prototype/js/rules.js`, `DESIGNS_BY_FAMILY.garland`, `estimateOrganicRecipe()`.
- That broad construction assumption is plausible: organic garlands are not classic quad-count math. They need a recipe/density lane, not a cluster-count lane. However, the exact densities (`standard = 9.5 balloons/ft`, `lush = 12`, `mixed_premium = 14`) are local assumptions and need LT approval before quoting.
  - Local evidence: `prototype/js/rules.js`, `DENSITY_TIERS`.

## 3) Current build physics/model issues

### A. 11-inch arch density is likely too high for production math

Local facts:

- `event-builder-spike/src/classic-construction.js` sets 11-inch `diameter_ft: 0.9167`, `balloons_per_foot: 8`, `clusters_per_foot: 2`.
- `createClassicArch()` estimates balloons as `lengthFt * balloons_per_foot`, rounded to a whole quad.
- Test evidence locks 25 ft arch to **50 clusters / 200 balloons**.
  - Local evidence: `event-builder-spike/test/classic-construction.test.js`.

Why this is an issue:

- 25 ft × 6 balloons/ft = **150 balloons / 37.5 clusters**, likely rounded to 38 clusters / 152 balloons.
- 25 ft at 10-inch sizing and 4 balloons per 10-inch cluster = about **30 clusters / 120 balloons**.
- Current 25 ft arch = **200 balloons**, which is 33% higher than the 6/ft reference and 67% higher than the 10-inch-sizing example.

Conclusion: current arch count is probably a render-density choice, not a quote-ready manufacturer/pro count.

### B. Column math is probably double-density

Local facts:

- `createClassicColumnPair()` uses `heightFt * 8` balloons per column.
- Default 8 ft column pair yields **64 balloons per column / 128 balloons per pair**.
- Test evidence locks 8 ft column pair to **16 clusters per column / 32 clusters per pair / 128 balloons total**.
  - Local evidence: `event-builder-spike/test/classic-construction.test.js`.

Public pro comparison:

- A common 11-inch column formula is **4 balloons per tier and about 1 tier per foot**, so an 8 ft column is **32 balloons**, plus optional topper.
- Current code makes an 8 ft column **64 balloons**, or 2 tiers/ft.

Conclusion: current column math is visually lush but not quote-safe unless LT specifically approves double-density columns.

### C. Arch geometry uses path length as semicircle circumference but does not expose width/height

Local facts:

- `createArchObjects()` uses `radius = piece.render_facts.length_ft / Math.PI`, then lays clusters on a semicircle. That makes the semicircle arc length equal the requested length.
  - Local evidence: `event-builder-spike/src/classic-scene.js`, `createArchObjects()`.

Issue:

- Pro arch estimating usually starts from **height + width formulas**, then derives approximate total arch length. Current UI asks for length directly, which is okay internally, but customer/pro workflows usually ask width and height.
- A 25 ft semicircle has radius ~7.96 ft, width ~15.9 ft, apex ~8.68 ft above the prototype’s 0.72 ft base offset. That may be plausible, but it is implicit.

Recommendation: store arch `frame_shape`, `opening_width_ft`, `opening_height_ft`, and derived `path_length_ft`, even if the UI still shows “25 ft arch.”

### D. Render object sizes and spacing are not physically tied to production counts

Local facts:

- Arch clusters: 50 clusters spread along 25 ft gives ~0.51 ft between cluster centers along the path.
- Render balloons use 11-inch radius (`0.9167 / 2`) and quad offsets around +/-0.26–0.33 ft.
- Column clusters are stacked every `0.5 ft` in `createColumnPairObjects()`.
  - Local evidence: `event-builder-spike/src/classic-scene.js`, `createArchObjects()` and `createColumnPairObjects()`.

Issue:

- 0.5 ft vertical/path spacing with 11-inch balloons implies strong overlap/compression. That can look full on screen, but it should not be interpreted as real cluster spacing.
- The visual model includes pressure/contact metadata in `classic-cluster-geometry.js`, but the actual v2 PlayCanvas render path uses simpler object offsets and does not consume the tested nested quad geometry directly.

Recommendation: expose `render_density_multiplier` separately from `production_density_per_ft`.

### E. Prototype and v2 spike disagree with pro references and each other

Local facts:

- Static prototype `BALLOON_SIZES` uses 11-inch `balloons_per_foot: 8`.
- Static prototype README says classic arch math includes “40 balloons per 5 ft for 11 inch structured arch render estimates.” That is 8/ft.
- v2 spike uses same 8/ft for classic arches/columns.
  - Local evidence: `prototype/js/rules.js`, `prototype/README.md`, `event-builder-spike/src/classic-construction.js`.

Issue:

- This makes the over-dense value look like a deliberate standard. It should be renamed if it is only render math.

### F. Quote/payload wording currently says “estimated_balloons”

Local facts:

- `createClassicPayload()` includes `render_facts.estimated_balloons` and `sales_summary`.
- The README says the prototype does not quote prices or write ERPNext data, but payload naming is easy to misuse later.
  - Local evidence: `event-builder-spike/src/classic-scene.js`, `event-builder-spike/README.md`, `prototype/README.md`.

Issue:

- “estimated_balloons” sounds production-facing. For over-dense visual models, use `visual_estimated_balloons` or `render_balloon_count`, and add a separate `production_estimate` object once approved.

## 4) Safety/quote honesty risks

- **Overquote risk:** 8/ft for 11-inch classic arches and columns can materially overstate balloon quantity versus public references. If multiplied into quote pricing, it could inflate customer price or stock planning.
- **Under-disclosed install hardware risk:** arches need line/frame/weights/anchors; columns need pole/base/weight; organic garlands need strip/line/attachment points. Balloon count alone is not enough for production or safety.
- **Helium/air confusion:** 11-inch latex gas capacity and float times matter for helium, but classic columns and many framed arches are normally air-filled. UI/payload should record fill method.
- **Outdoor/environment risk:** heat, wind, sun, surfaces, and venue rules can change feasibility. Customer-facing render should not imply outdoor stability without review.
- **Stage/edge hazard:** current warning only catches near stage edge and overlap. Real decor needs trip-path, egress, fire sprinkler, ceiling, lighting, rigging, and weighted-base checks before installation.
- **Customer promise risk:** burton + BURTON explicitly warns decorators not to promise what they cannot deliver and to disclose capability/expense from the start. The app should keep that humility: “planning visualization; final design and install confirmed by Locally Twisted.”

## 5) Concrete next-version recommendations

1. **Split render math from production math immediately.**
   - Rename current 8/ft values to `render_balloons_per_foot` or `visual_density_per_foot`.
   - Add `production_estimate.status: "pending_lt_approval"` until Jeff/LT chooses official formulas.

2. **Use pro-backed default production formulas as the first candidate.**
   - Classic 11-inch arch candidate: default to **6 balloons/ft** for classic spiral, rounded to whole quads, plus 10–15% overage.
   - Alternative strict 10-inch sizing candidate: one quad per 10 inches (~4.8 balloons/ft), if LT confirms that is how they build.
   - Classic 11-inch column candidate: **4 balloons/ft per column** plus optional topper, unless LT confirms double-density/lush columns.

3. **Store arch dimensions as shape, width, height, and derived path length.**
   - Example fields: `arch_shape: "equal" | "wide" | "tall" | "custom_path"`, `opening_width_ft`, `opening_height_ft`, `path_length_ft`, `formula_source`.

4. **Add explicit construction/fill fields.**
   - `fill_method: "air" | "helium" | "mixed"`
   - `support: "frame" | "monofilament" | "pole_and_base" | "garland_strip"`
   - `requires_weights: true`
   - `venue_review_required: true`

5. **Keep organic garland as recipe math, but mark densities unapproved.**
   - Current `standard = 9.5/ft`, `lush = 12/ft`, `mixed_premium = 14/ft` may be reasonable render recipes, but should become LT-approved recipe presets before quote use.

6. **Change payload labels for honesty.**
   - Current: `estimated_balloons` inside `render_facts`.
   - Safer: `render_balloon_count`, `visual_density_basis`, and separately `production_balloon_estimate` only when approved.

7. **Add a quote-readiness gate.**
   - `quote_ready: false` until all are present: approved formula source, fill method, support/anchor method, overage policy, labor/install assumptions, and venue safety review flag.

8. **Use the tested cluster geometry in the renderer or document why not.**
   - `classic-cluster-geometry.js` has duplet/quad/nested metadata with tie points and contacts; the live v2 render uses simpler offsets. Either wire the tested geometry into render objects or mark it as model-only evidence.

9. **Add tests that protect the distinction.**
   - Test that render counts can remain dense.
   - Test that production estimates use approved pro formulas.
   - Test that customer/export payload includes the disclaimer and does not expose unapproved production counts as final quote facts.

10. **Recommended customer-facing disclaimer.**
    - “Planning visualization only. Balloon counts, install method, pricing, and safety details are confirmed by Locally Twisted before booking.”
