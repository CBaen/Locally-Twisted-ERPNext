# Homepage Review Platform Proof - 2026-05-11

## Outcome

The homepage review proof strip shows three review platforms as logos, not
cards and not framed containers:

- GigSalad
- Google
- Facebook

The strip does not show exact review counts and does not render the visible
word `reviews` under the logos. GigSalad and Google show five-star proof.
Facebook shows the platform logo plus recommendation proof because Facebook's
review UI is recommendation-oriented.

## Trigger

GL asked to add GigSalad and Facebook beside Google, then corrected the first
implementation: no cards, no containers, no visible counts, no small/logo-poor
assets, and no invented visible label such as `reviews`.

## Files Owned By This Slice

- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/public/icons/gigsalad-logo-2025.png`
- `apps/locally_twisted/locally_twisted/public/icons/google-logo.png`
- `apps/locally_twisted/locally_twisted/public/icons/facebook.svg`
- `scripts/verify/interactive_layout.spec.js`

## Contract

- Logos are the visual proof, not text cards.
- No visible review counts.
- No visible `reviews` label under the platform logos.
- No `.card`-style wrappers, borders, shadows, padded boxes, or container
  treatments around individual platforms.
- Do not make the non-Google platforms smaller than Google unless a responsive
  mobile fit rule requires proportional shrinkage.
- Do not hardcode exact current ratings/counts unless reverified in the same
  run and GL approves showing them.

## Verification

Use focused homepage review checks plus a screenshot or live DOM inspection:

```powershell
python scripts/dev/clear_website_cache.py --restart
npm run test:interactive-layout -- --grep "homepage review marquee|mobile review proof" --workers=1
npm run test:layout-fit -- --grep "home" --workers=1
```

Also inspect the live homepage and confirm the platform strip has only the
three logo links plus their star/recommendation proof, with no visible review
counts and no visible `reviews` label.

## Rules For Future Agents

- If a platform changes its rating display model, match that platform honestly
  instead of forcing it into Google-style copy.
- If logos are replaced, use current official brand assets or clean local
  source assets and keep the result transparent/unboxed.
- Do not add explanatory helper text under the logos. The logo and proof mark
  are the UI.
