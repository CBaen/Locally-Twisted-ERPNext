# Plan Custom Decor Dormant Prototype Implementation Plan

> **Correction note, 2026-05-02:** This plan was the original narrow build plan. The implemented prototype has since been corrected after GL review to use product-family controls and construction engines for Classic arch, Classic column, Organic garland, Backdrop wall, and Balloon drop. Do not use the older "organic garland deferred" boundary below as current scope without re-checking `prototype/README.md` and `prototype/REVIEW-QA.md`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or an equivalent bounded worker flow to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dormant, static, Frappe-compatible prototype of the future `Plan Custom Decor` experience without touching V1 launch routes or production Frappe app files.

**Architecture:** The prototype lives entirely under `research/design-studio-v2/prototype/` as plain HTML, CSS, and vanilla JavaScript. It proves the first interaction model, renderer rules, color-name payload, and summary output for classic arch, paired columns, and backdrop/photo-op wall. It does not create DocTypes, public routes, share links, Leads, checkout behavior, or production assets.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript modules, inline SVG rendering, local Python verification script.

---

## Source Specs

Workers must read these before editing:

- `AGENTS.md`
- `workstreams/design-studio-v2.md`
- `research/design-studio-v2/README.md`
- `research/design-studio-v2/design-studio-physics-rules.md`
- `research/design-studio-v2/plan-custom-decor-flow.md`
- `research/design-studio-v2/design-studio-visual-direction.md`
- `research/design-studio-v2/frappe-native-design-studio-architecture.md`
- `research/design-studio-v2/design-studio-risk-audit.md`

## Non-Negotiable Scope Rules

- Do not edit `apps/`.
- Do not edit current route files.
- Do not edit current CSS/JS used by the live site.
- Do not edit checkout, contact, `/book`, `/shop`, policy, or launch files.
- Do not modify `C:\Users\baenb\projects\locally-twisted-odoo\`.
- Do not create a public Frappe route.
- Do not implement real save/share/account/Lead behavior.
- Do not claim the prototype is production-ready.
- Use concrete project-state wording such as active work in progress, uncommitted changes, possible overlap, or needs reconciliation. Do not use loaded shorthand.

## Target File Structure

Create only these prototype files unless the controller approves more:

```text
research/design-studio-v2/prototype/
  README.md
  index.html
  styles.css
  verify_prototype.py
  js/
    app.js
    colors.js
    payload.js
    renderer-svg.js
    rules.js
    state.js
```

Responsibilities:

| File | Responsibility |
|---|---|
| `README.md` | How to open the prototype, what it proves, and what it does not prove |
| `index.html` | Static accessible shell and DOM targets |
| `styles.css` | Responsive Utah Event Authority Studio visual shell |
| `js/colors.js` | Demo Locally Twisted color-name catalog and approximate swatches |
| `js/rules.js` | Structured construction math and validation helpers |
| `js/renderer-svg.js` | SVG rendering for arch, paired columns, and backdrop |
| `js/state.js` | Prototype state, choices, and update helpers |
| `js/payload.js` | Summary JSON and pieces-considered payload |
| `js/app.js` | DOM binding and step flow |
| `verify_prototype.py` | Static verification for file presence, refs, accessibility hooks, and forbidden production coupling |

## Team Dispatch Model

Use one controller and five bounded implementation agents:

| Agent | Owns | Must not touch |
|---|---|---|
| UI Shell Agent | `README.md`, `index.html`, `styles.css` | JS logic beyond data attributes |
| Rules Agent | `js/colors.js`, `js/rules.js` | HTML layout, app flow |
| Renderer Agent | `js/renderer-svg.js` | State/payload modules |
| Flow Agent | `js/state.js`, `js/app.js` | Rules formulas, payload schema |
| Payload/QA Agent | `js/payload.js`, `verify_prototype.py` | Production app files |

Recommended implementation order:

1. UI Shell and Rules can run in parallel.
2. Renderer starts after Rules has file shape in place.
3. Flow starts after UI Shell and Rules exist.
4. Payload/QA starts after Flow and Renderer exist.
5. Controller runs final verification and reconciles handoff notes.

## Acceptance Criteria

The prototype is successful when:

- It opens from `research/design-studio-v2/prototype/index.html` without a dev server.
- The first screen clearly says `Plan Custom Decor`.
- Customer can choose event context, primary piece, style, scale, and named colors.
- Supported pieces are classic arch, paired columns, and backdrop/photo-op wall.
- Organic garland is visibly deferred, not implemented as a fake renderer.
- SVG preview updates when piece, style, scale, or colors change.
- Preview includes a plain-language disclaimer: `Planning visualization. Final design and installation details are confirmed by Locally Twisted.`
- Summary panel shows selected pieces, color names, event context, and pieces considered.
- Payload panel outputs valid JSON with schema version, selected pieces, color names, declined suggestions, and disclaimer.
- UI is keyboard usable for core controls.
- Long color names do not break mobile layout.
- `python research/design-studio-v2/prototype/verify_prototype.py` passes.

## Verification Commands

Run from repo root:

```powershell
python research/design-studio-v2/prototype/verify_prototype.py
git -c safe.directory='C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted' diff --check -- research/design-studio-v2/prototype research/design-studio-v2/prototype-build-plan.md
Select-String -Path 'research/design-studio-v2/prototype/**/*.js','research/design-studio-v2/prototype/*.html','research/design-studio-v2/prototype/*.css','research/design-studio-v2/prototype/*.md' -Pattern '\\bdirty\\b' -CaseSensitive:$false
```

Expected:

- Verifier prints `Design Studio prototype static verification passed.`
- `git diff --check` prints no output.
- `Select-String` prints no matches.

## Task 1: UI Shell

**Owner:** UI Shell Agent

**Files:**

- Create: `research/design-studio-v2/prototype/README.md`
- Create: `research/design-studio-v2/prototype/index.html`
- Create: `research/design-studio-v2/prototype/styles.css`

- [ ] **Step 1: Create the prototype README**

Write `research/design-studio-v2/prototype/README.md` with this structure:

```markdown
# Plan Custom Decor Prototype

Static dormant prototype for the future Locally Twisted `Plan Custom Decor` experience.

This is not a production Frappe route. It does not create Leads, save designs, share designs, quote prices, or modify ERPNext records.

## How To View

Open `index.html` in a browser.

## What It Proves

- Guided planning flow for larger custom decor
- Classic arch, paired columns, and backdrop/photo-op wall as first pieces
- Named balloon colors as payload truth
- Planning visualization disclaimer
- Pieces-considered sales context

## What It Does Not Prove

- Production persistence
- Share links
- Account saves
- CRM or Lead creation
- Final engineering accuracy
- Live Frappe route readiness
```

- [ ] **Step 2: Create the HTML shell**

Create `index.html` with:

- `<main data-lt-design-studio>`
- event context controls
- piece controls
- style controls
- scale controls
- color controls
- SVG preview mount
- summary panel
- payload panel
- disclaimer text

Required IDs and data hooks:

```html
<main class="studio" data-lt-design-studio>
  <section class="studio-panel studio-intro" aria-labelledby="studio-title">
    <p class="eyebrow">Locally Twisted</p>
    <h1 id="studio-title">Plan Custom Decor</h1>
    <p class="lede">Build a starting point for a larger event installation.</p>
    <p class="studio-disclaimer">Planning visualization. Final design and installation details are confirmed by Locally Twisted.</p>
  </section>

  <section class="studio-panel" aria-labelledby="event-title">
    <h2 id="event-title">Event context</h2>
    <div class="segmented" data-control="eventContext"></div>
  </section>

  <section class="studio-panel" aria-labelledby="piece-title">
    <h2 id="piece-title">Starting piece</h2>
    <div class="choice-grid" data-control="pieceType"></div>
  </section>

  <section class="studio-panel" aria-labelledby="style-title">
    <h2 id="style-title">Style and scale</h2>
    <div class="choice-grid" data-control="style"></div>
    <div class="segmented" data-control="scale"></div>
  </section>

  <section class="studio-panel" aria-labelledby="color-title">
    <h2 id="color-title">Organization colors</h2>
    <p class="help-text">Color names are the planning reference. Swatches are approximate.</p>
    <div class="swatch-grid" data-control="colors"></div>
  </section>

  <section class="studio-stage" aria-labelledby="preview-title">
    <div class="stage-header">
      <h2 id="preview-title">Planning preview</h2>
      <p data-summary-line></p>
    </div>
    <div class="preview-frame" data-preview aria-live="polite"></div>
  </section>

  <aside class="studio-summary" aria-labelledby="summary-title">
    <h2 id="summary-title">Plan summary</h2>
    <div data-summary></div>
    <h3>Design payload</h3>
    <pre data-payload-output>{}</pre>
  </aside>
</main>
```

- [ ] **Step 3: Create responsive styles**

Create `styles.css` with:

- neutral premium shell
- dark slate header area
- brass/gold accent variables
- responsive grid that stacks below 760px
- stable preview frame
- visible focus states
- readable swatches with color names

Minimum CSS variables:

```css
:root {
  --lt-ink: #101820;
  --lt-slate: #263446;
  --lt-paper: #f7f4ef;
  --lt-white: #ffffff;
  --lt-brass: #b89158;
  --lt-berry: #8a1e3f;
  --lt-teal: #0f3d3e;
  --lt-border: rgba(16, 24, 32, 0.16);
  --lt-shadow: 0 18px 50px rgba(16, 24, 32, 0.12);
}
```

- [ ] **Step 4: Verify UI shell scope**

Run:

```powershell
Test-Path research/design-studio-v2/prototype/index.html
Test-Path research/design-studio-v2/prototype/styles.css
```

Expected:

```text
True
True
```

## Task 2: Rules And Colors

**Owner:** Rules Agent

**Files:**

- Create: `research/design-studio-v2/prototype/js/colors.js`
- Create: `research/design-studio-v2/prototype/js/rules.js`

- [ ] **Step 1: Create demo color catalog**

Create `colors.js` exporting an approved-for-prototype subset. Use names from the research catalog. Hex values are approximations.

```javascript
export const LT_COLORS = [
  { name: "White", hex: "#f8f7f2", family: "neutral" },
  { name: "Black", hex: "#101010", family: "neutral" },
  { name: "Reflex Gold", hex: "#b89158", family: "metallic" },
  { name: "Reflex Silver", hex: "#c4c8cc", family: "metallic" },
  { name: "Deep Teal", hex: "#0f3d3e", family: "deep" },
  { name: "Blue Slate", hex: "#2f3f53", family: "muted" },
  { name: "Royal Blue", hex: "#234ea4", family: "bright" },
  { name: "Forest", hex: "#1f4f36", family: "deep" },
  { name: "Raspberry", hex: "#b21f59", family: "bright" },
  { name: "Blush", hex: "#e8b8b0", family: "soft" },
  { name: "Dusk Cream", hex: "#efe2ce", family: "muted" },
  { name: "Empowermint", hex: "#9ed7c2", family: "soft" }
];

export function getColorByName(name) {
  return LT_COLORS.find((color) => color.name === name) || LT_COLORS[0];
}
```

- [ ] **Step 2: Create construction rules**

Create `rules.js` with pure functions only:

```javascript
export const PIECES = [
  { id: "classic_arch", label: "Classic arch", suggestion: "classic_columns" },
  { id: "classic_columns", label: "Pair of classic columns", suggestion: "backdrop_wall" },
  { id: "backdrop_wall", label: "Backdrop/photo-op wall", suggestion: "classic_arch" }
];

export const STYLES = [
  { id: "solid", label: "Solid" },
  { id: "spiral", label: "Spiral" },
  { id: "banded", label: "Color-blocked" },
  { id: "stripe", label: "Stripe" }
];

export const SCALES = [
  { id: "door", label: "Door / entry", feet: 20 },
  { id: "stage", label: "Stage moment", feet: 25 },
  { id: "gym", label: "Gym / venue", feet: 30 }
];

export function gcd(a, b) {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y) {
    const temp = y;
    y = x % y;
    x = temp;
  }
  return x || 1;
}

export function minimumClusterRepeat(colorCount) {
  return colorCount / gcd(colorCount, 4);
}

export function estimateArchClusters(lengthFt, balloonsPerFoot = 7) {
  return Math.ceil((lengthFt * balloonsPerFoot) / 4);
}

export function estimateColumnClusters(heightFt, balloonsPerFoot = 8) {
  return Math.ceil((heightFt * balloonsPerFoot) / 4);
}

export function estimateBackdropClusters(widthFt, heightFt) {
  return widthFt * heightFt;
}

export function colorForCluster(clusterIndex, slotIndex, colorNames, style) {
  const colors = colorNames.length ? colorNames : ["White"];
  if (style === "solid") return colors[0];
  if (style === "banded") return colors[Math.floor(clusterIndex / 2) % colors.length];
  if (style === "stripe") return colors[slotIndex % colors.length];
  if (colors.length === 3) {
    const repeat = [
      [colors[0], colors[0], colors[1], colors[2]],
      [colors[0], colors[1], colors[1], colors[2]],
      [colors[0], colors[1], colors[2], colors[2]]
    ];
    return repeat[clusterIndex % 3][slotIndex];
  }
  return colors[(clusterIndex + slotIndex) % colors.length];
}
```

- [ ] **Step 3: Verify module syntax**

Run:

```powershell
node --check research/design-studio-v2/prototype/js/colors.js
node --check research/design-studio-v2/prototype/js/rules.js
```

Expected: no output and exit code `0`.

## Task 3: SVG Renderer

**Owner:** Renderer Agent

**Files:**

- Create: `research/design-studio-v2/prototype/js/renderer-svg.js`

- [ ] **Step 1: Create SVG utility functions**

Create `renderer-svg.js` importing from `colors.js` and `rules.js`.

Required exports:

```javascript
export function renderPreview(state) {}
export function renderArch(state) {}
export function renderColumns(state) {}
export function renderBackdrop(state) {}
```

- [ ] **Step 2: Implement classic arch renderer**

Rules:

- Use repeated 4-balloon clusters.
- Render no more than 32 visible clusters for performance.
- Preserve true estimated cluster count in payload, not SVG count.
- Use color names through `getColorByName`.
- Include scale cues: floor line and doorway/stage frame.

Required SVG root pattern:

```javascript
function svgFrame(inner) {
  return `
    <svg viewBox="0 0 760 420" role="img" aria-label="Planning visualization preview" xmlns="http://www.w3.org/2000/svg">
      <rect width="760" height="420" fill="#f7f4ef"/>
      <line x1="70" y1="350" x2="690" y2="350" stroke="#c8beb0" stroke-width="3"/>
      ${inner}
    </svg>
  `;
}
```

- [ ] **Step 3: Implement paired columns renderer**

Rules:

- Render two columns on either side of the scene.
- Each column shows stacked quads as four visible balloons per row.
- Stripe colors must remain stable by side.
- Include a center doorway/stage reference.

- [ ] **Step 4: Implement backdrop renderer**

Rules:

- Render a grid of whole cells.
- Use 8x8 demo grid for `door`, 10x8 for `stage`, 12x8 for `gym`.
- No stripes thinner than one cell.
- Show intentional color regions, not random loose circles.

- [ ] **Step 5: Verify module syntax**

Run:

```powershell
node --check research/design-studio-v2/prototype/js/renderer-svg.js
```

Expected: no output and exit code `0`.

## Task 4: State And Flow

**Owner:** Flow Agent

**Files:**

- Create: `research/design-studio-v2/prototype/js/state.js`
- Create: `research/design-studio-v2/prototype/js/app.js`
- Modify only if needed: `research/design-studio-v2/prototype/index.html`

- [ ] **Step 1: Create initial state**

Create `state.js`:

```javascript
export const initialState = {
  schema_version: "design-studio-prototype-v1",
  event_context: "Corporate",
  piece_type: "classic_arch",
  style: "spiral",
  scale: "door",
  selected_color_names: ["Reflex Gold", "Deep Teal"],
  pieces_considered: ["classic_columns"],
  disclaimer: "Planning visualization. Final design and installation details are confirmed by Locally Twisted."
};

export function createStore(initial = initialState) {
  let state = { ...initial };
  const listeners = new Set();
  return {
    getState: () => ({ ...state, selected_color_names: [...state.selected_color_names], pieces_considered: [...state.pieces_considered] }),
    setState: (patch) => {
      state = { ...state, ...patch };
      listeners.forEach((listener) => listener(state));
    },
    subscribe: (listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);
    }
  };
}
```

- [ ] **Step 2: Create app bootstrap**

Create `app.js`:

- Import colors, rules, renderer, payload, and state.
- Populate controls from arrays.
- Use `<button type="button">` for choices.
- Use `aria-pressed` for selected choices.
- Limit color selection to 4 colors.
- Re-render preview, summary, and payload on state change.

Required bootstrap guard:

```javascript
const root = document.querySelector("[data-lt-design-studio]");
if (!root) {
  throw new Error("Plan Custom Decor prototype root not found.");
}
```

- [ ] **Step 3: Wire script imports**

Add to the end of `index.html`:

```html
<script type="module" src="./js/app.js"></script>
```

- [ ] **Step 4: Verify module syntax**

Run:

```powershell
node --check research/design-studio-v2/prototype/js/state.js
node --check research/design-studio-v2/prototype/js/app.js
```

Expected: no output and exit code `0`.

## Task 5: Payload And Summary

**Owner:** Payload/QA Agent

**Files:**

- Create: `research/design-studio-v2/prototype/js/payload.js`
- Create: `research/design-studio-v2/prototype/verify_prototype.py`

- [ ] **Step 1: Create payload builder**

Create `payload.js`:

```javascript
import { PIECES, SCALES } from "./rules.js";

function labelFor(list, id) {
  const found = list.find((item) => item.id === id);
  return found ? found.label : id;
}

export function buildDesignPayload(state) {
  return {
    schema_version: state.schema_version,
    source: "research_prototype",
    customer_facing_path: "Plan Custom Decor",
    event_context: state.event_context,
    selected_pieces: [
      {
        piece_type: state.piece_type,
        display_label: labelFor(PIECES, state.piece_type),
        style: state.style,
        scale: labelFor(SCALES, state.scale),
        selected_color_names: state.selected_color_names
      }
    ],
    pieces_considered: state.pieces_considered,
    render_summary: {
      type: "planning_visualization",
      disclaimer: state.disclaimer
    },
    sales_summary: `${state.event_context} decor starting point with ${labelFor(PIECES, state.piece_type)} using ${state.selected_color_names.join(", ")}.`
  };
}

export function renderSummaryHtml(state) {
  const payload = buildDesignPayload(state);
  return `
    <dl class="summary-list">
      <dt>Event context</dt><dd>${payload.event_context}</dd>
      <dt>Starting piece</dt><dd>${payload.selected_pieces[0].display_label}</dd>
      <dt>Colors</dt><dd>${payload.selected_pieces[0].selected_color_names.join(", ")}</dd>
      <dt>Pieces considered</dt><dd>${payload.pieces_considered.join(", ") || "None yet"}</dd>
      <dt>Status</dt><dd>Prototype only. No Lead, quote, save, or share action is created.</dd>
    </dl>
  `;
}
```

- [ ] **Step 2: Create static verifier**

Create `verify_prototype.py` that checks:

- all expected files exist
- `index.html` references `styles.css` and `./js/app.js`
- required data hooks exist
- disclaimer exists
- no production app paths are referenced
- no loaded project-state shorthand appears
- JS files contain no `frappe.call`, `/api/method`, or `fetch(` calls

Required success output:

```python
print("Design Studio prototype static verification passed.")
```

- [ ] **Step 3: Verify syntax and static checks**

Run:

```powershell
node --check research/design-studio-v2/prototype/js/payload.js
python research/design-studio-v2/prototype/verify_prototype.py
```

Expected:

```text
Design Studio prototype static verification passed.
```

## Task 6: Controller Review

**Owner:** Controller

**Files:**

- Modify: `workstreams/design-studio-v2.md`
- Modify: `research/design-studio-v2/README.md`

- [ ] **Step 1: Run complete verification**

Run:

```powershell
node --check research/design-studio-v2/prototype/js/colors.js
node --check research/design-studio-v2/prototype/js/rules.js
node --check research/design-studio-v2/prototype/js/renderer-svg.js
node --check research/design-studio-v2/prototype/js/state.js
node --check research/design-studio-v2/prototype/js/payload.js
node --check research/design-studio-v2/prototype/js/app.js
python research/design-studio-v2/prototype/verify_prototype.py
git -c safe.directory='C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted' diff --check -- research/design-studio-v2
```

Expected:

- all `node --check` commands exit `0`
- verifier prints `Design Studio prototype static verification passed.`
- `git diff --check` prints no output

- [ ] **Step 2: Browser visual check**

Open:

```text
C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\research\design-studio-v2\prototype\index.html
```

Check:

- desktop layout has no overlapping controls
- mobile/narrow viewport stacks cleanly
- preview changes for all three pieces
- summary and payload update
- Tab reaches all controls
- visible focus indicator appears
- color names remain visible

- [ ] **Step 3: Update research README**

Add the prototype link to `research/design-studio-v2/README.md`:

```markdown
## Dormant Prototype

Prototype plan:

- `prototype-build-plan.md`

Prototype folder, once built:

- `prototype/`

This prototype is static research output. It is not a public Frappe route and does not prove production save/share/CRM behavior.
```

- [ ] **Step 4: Update controller workstream**

In `workstreams/design-studio-v2.md`, update `Next Action` to reflect whether the prototype was:

- not started
- in progress under `research/design-studio-v2/prototype/`
- built and awaiting GL review
- rejected or paused

Use this wording when built:

```markdown
Prototype status: dormant static prototype built under `research/design-studio-v2/prototype/`. It is not production-integrated and does not touch V1 launch routes.
```

## Worker Prompt Template

Use this template for each implementation worker:

```text
You are working in:
C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted

You are not alone in the codebase. Other agents may be working in different files. Do not revert or rewrite edits made by others. Stay inside your assigned write scope.

Task:
[paste the exact task section from research/design-studio-v2/prototype-build-plan.md]

Required reads:
- AGENTS.md
- workstreams/design-studio-v2.md
- research/design-studio-v2/prototype-build-plan.md
- research/design-studio-v2/design-studio-physics-rules.md
- research/design-studio-v2/plan-custom-decor-flow.md
- research/design-studio-v2/design-studio-visual-direction.md
- research/design-studio-v2/frappe-native-design-studio-architecture.md
- research/design-studio-v2/design-studio-risk-audit.md

Rules:
- Do not edit apps/.
- Do not edit V1 launch-critical files.
- Do not create a Frappe route.
- Do not implement real save/share/Lead behavior.
- Do not modify C:\Users\baenb\projects\locally-twisted-odoo\.
- Use concrete wording for project state: active work in progress, uncommitted changes, possible overlap, or needs reconciliation.

Return:
- Files read
- Files changed
- Verification commands run and output summary
- Any blockers
- Any decisions that need controller or GL approval
```

## Plan Self-Review

Spec coverage:

- Physics constraints are covered by Task 2 and Task 3.
- UX flow is covered by Task 1 and Task 4.
- Visual direction is covered by Task 1 and Task 3.
- Frappe-native boundary is covered by scope rules and Task 6.
- Payload and pieces-considered are covered by Task 5.
- Risk audit blockers are covered by acceptance criteria and verification commands.

Scope check:

- This plan builds only a dormant static prototype.
- Production Frappe integration is deliberately excluded.
- Save/share/account/Lead behavior is deliberately excluded.
- Organic garland is deliberately excluded from first prototype implementation.

No known placeholders remain in this plan. If a worker finds an ambiguity, they should stop and ask the controller instead of widening scope.
