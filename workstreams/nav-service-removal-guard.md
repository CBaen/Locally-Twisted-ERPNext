# Nav Service Removal Guard

Last updated: 2026-05-10 by Moji/OpenClaw.

## Purpose

Prevent agents from silently removing, hiding, renaming, or replacing canonical public business lanes while doing nav/copy/conversion work.

## Trigger Incident

`Twisting & Face Painting` disappeared from customer navigation twice:

1. Earlier broad nav/style work replaced the approved BTFP lane with an unapproved `/process` route.
2. On 2026-05-10, a valid request to make quote/contact labels clearer was over-inferred into replacing the BTFP service lane with `Free Event Quote` in desktop nav, mobile drawer, and search quick links.

The route still existed, but public discovery was damaged. That counts as a significant service-removal regression.

Forensic report: `C:/Users/baenb/.openclaw/workspace/reports/lt-btfp-menu-removal-forensics-2026-05-10.md`.

## Current Contract

- `Twisting & Face Painting` is a canonical public service lane.
- It must remain visible in desktop nav, mobile drawer, and search quick links.
- It must point to `/balloon-twisting-and-face-painting`.
- `Free Event Quote` and `Contact Us` remain conversion labels to `/contact`.
- `/contact` does not replace the BTFP service lane.
- `/process` is not an approved replacement.
- The desktop top banner uses the left proof slot for `SHORT NOTICE? LET US KNOW. WE CAN OFTEN HELP WITH 24 HOURS NOTICE!`.
- The old `Prepared design, clean installs, and invoiced event support across Utah.` copy and `delivery-install.svg` icon are retired header chrome, not dormant defaults.

## Approval Marker

If GL explicitly approves removing or hiding the BTFP lane, record the exact marker below in `workstreams/nav-service-removal-approvals.md` with source/date/reason before changing code:

```text
APPROVED_NAV_SERVICE_REMOVAL: Twisting & Face Painting -> /balloon-twisting-and-face-painting
```

Do not add this marker from inference. It requires direct GL approval naming the service and action.

## Code/Verifier Surface

- Nav template: `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- Header styling: `apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css`
- Source guard: `scripts/verify/nav_ia.py`
- Rendered smoke guard: `scripts/verify/smoke_shop.py`
- Coordination board: `workstreams/menu-content-coordination.md`
- Project decision: `locally-twisted-decisions.md`
- Capability: `.codex/capabilities/recipes/frappe-public-nav-business-route-contract.md`

## Verification

Minimum after nav/chrome work:

```powershell
python scripts/verify/nav_ia.py
python scripts/dev/clear_website_cache.py
```

Then prove rendered presence when the change affects customer chrome:

- desktop header has one `Twisting & Face Painting` link to `/balloon-twisting-and-face-painting`
- mobile drawer has one `Twisting & Face Painting` link to `/balloon-twisting-and-face-painting`
- search quick links include `Twisting & Face Painting`
- top banner contains the 24-hour short-notice line
- top banner does not contain the retired prepared-design proof copy, `lt-mega-header__proof`, `lt-mega-header__top-alert`, or `delivery-install.svg`

## Generalization

This is not only about nav. Use the same pattern for any service, field, route, document term, recipient, payment term, or operator status that represents business meaning. Positive replacement tests do not prove preservation; guard canonical inventory directly.
