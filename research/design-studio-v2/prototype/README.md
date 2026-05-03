# Plan Custom Decor Prototype

Static dormant prototype for the future Locally Twisted `Plan Custom Decor` experience.

This is not a production Frappe route. It does not create Leads, save designs, share designs, quote prices, or modify ERPNext records.

## How To View

Open `index.html` in a browser.

## Review-Grade QA

Run from the repo root:

```powershell
python research/design-studio-v2/prototype/verify_prototype.py
node research/design-studio-v2/prototype/verify_review_grade.js
```

The browser verifier checks Classic arch, Classic column, Organic garland, Backdrop wall, and Balloon drop states at desktop and mobile widths. It also writes local screenshots under `output/playwright/design-studio-v2-prototype/review-grade/`.

See `REVIEW-QA.md` for the review checklist and open decisions.

## What It Proves

- Guided planning flow for larger custom decor
- Product-family controls grounded in catalog variants and product specs
- Classic arch and column structured-cluster math, including 40 balloons per 5 ft for 11 inch structured arch render estimates
- Classic two-color arch spiral as two-balloon-wide candy-cane bands with one-slot phase advance
- Organic garland doublet/filler recipe math, including 11 inch body balloons, 16/24 inch anchors, and 5 inch filler
- Backdrop wall whole-cell cluster-grid math
- Balloon drop representational mix logic
- Named balloon colors as payload truth
- Planning visualization disclaimer
- Pieces-considered sales context
- Review scenarios for GL/Jeff direction checks

## What It Does Not Prove

- Production persistence
- Share links
- Account saves
- CRM or Lead creation
- Final production engineering accuracy
- Approved color hex/Pantone mappings
- Approved final size limits
- Live Frappe route readiness
