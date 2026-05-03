# Plan Custom Decor Review QA

Status: review-grade static prototype quality pass.

This is still research output. It does not create Leads, save designs, share designs, quote prices, or modify ERPNext records.

## Review Scenarios

Use the scenario controls in `index.html` to review the prototype quickly:

- Classic arch: 25 ft structured arch, 11 inch balloon-size axis, two-color candy-cane spiral, 200-balloon estimate
- Classic column: 8 ft structured column, stacked quad-cluster spiral
- Organic garland: 9 ft standard-density organic recipe with mixed sizes
- Backdrop wall: 10 x 10 ft whole-cell lattice grid
- Balloon drop: 500-balloon air-filled drop mix

## QA Checklist

- Direct file open renders without a dev server
- Desktop and mobile layouts have no horizontal overflow
- All five scenario presets update preview, summary, and payload
- Keyboard Tab reaches the scenario and core controls
- Focus indicators are visible
- Color names remain visible on narrow mobile
- Color caps disable impossible extra choices
- Payload includes scenario label, product family, source product slugs, variant counts, selected variant axes, render engine, construction basis, named colors, pieces considered, declined suggestions, and disclaimer
- Structured pieces preserve whole-cluster estimates
- Organic garland preserves base count, 10-15% planning overage, 5/11/16/24 inch size mix, visual layers, and no-touching-twins constraint
- Balloon drop stores that no stable spatial pattern survives release
- No real save, share, Lead, contact, checkout, or backend behavior is implemented

## Evidence Path

Run:

```powershell
node research/design-studio-v2/prototype/verify_review_grade.js
```

Screenshots are generated under:

```text
output/playwright/design-studio-v2-prototype/review-grade/
```

These screenshots are local QA evidence for review and are not proof of production readiness.

## Open Review Decisions

- Customer-facing name: `Plan Custom Decor` or another label
- Exact disclaimer wording
- Whether Backdrop wall is a catalog-backed product or quote-rule product in ERPNext
- Whether construction and balloon counts stay internal or are customer-visible
- Approved 53-value color catalog reconciliation and hex approximations
- Approved size limits for any-size arches, columns, garlands, and walls
