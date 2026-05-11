# Event Balloons Hub Route Removal - 2026-05-11

## Outcome

`/event-balloons` is not a launch route. It has no page file, no controller,
no route alias, no canonical mapping, no sitemap entry, and no redirect.

The four event audience routes remain the approved discovery paths:

- `/civic-community`
- `/corporate-events`
- `/schools-campuses`
- `/private-celebrations`

The header may use an event-audience dropdown, but no public link, CTA, search
quick result, footer link, hero CTA, portfolio button, canonical rule, or route
alias may point to `/event-balloons`.

## Trigger

GL explicitly rejected the standalone hub at `http://localhost:8081/event-balloons`
and asked for the page and buttons to be deleted with no redirect.

## Files Owned By This Slice

- `apps/locally_twisted/locally_twisted/www/event_balloons.html` deleted
- `apps/locally_twisted/locally_twisted/www/event_balloons.py` deleted
- `apps/locally_twisted/locally_twisted/hooks.py`
- `apps/locally_twisted/locally_twisted/seo.py`
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`
- `apps/locally_twisted/locally_twisted/www/home.html`
- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/www/portfolio.html`
- `scripts/verify/nav_ia.py`
- `scripts/verify/seo_contract.spec.js`
- `scripts/verify/interactive_layout.spec.js`
- `scripts/verify/layout_helpers.js`
- `scripts/verify/smoke_shop.py`
- `scripts/verify/ecommerce_pause_contract.py`
- `scripts/verify/white_label_customer_surfaces.py`

## Verification Receipt

Fresh checks from 2026-05-11:

- `rg -n "/event-balloons|event_balloons" apps\locally_twisted\locally_twisted`
  returned no live app-source matches.
- Direct no-redirect HTTP check returned `404` with no `Location` header for
  both `/event-balloons` and `/event_balloons`.
- `/sitemap.xml` did not contain `event-balloons` or `event_balloons`.
- Browser link checks on `/`, `/portfolio`, `/contact`, and `/faq` found zero
  `a[href="/event-balloons"]`.
- `python scripts/verify/nav_ia.py` passed.
- `npm run test:seo-contract -- --grep "removed Event Balloons|sitemap" --workers=1`
  passed 2/2.
- `npm run test:interactive-layout -- --grep "search opens as an overlay|event mega panel links" --workers=1`
  passed 3/3.
- `npm run test:layout-fit -- --grep "home|portfolio|civic|corporate|schools|private" --workers=1`
  passed 78/78.

Known unrelated shared-worktree failures at closeout:

- The broader compact hero grep had an existing `/civic-community` desktop
  content-fit failure outside this slice.
- The broader container-contract home grep had existing homepage visibility
  expectations for hidden/restored blocks outside this slice.

## Rules For Future Agents

- Do not add a redirect for `/event-balloons`.
- Do not add the route back as a hidden compatibility page.
- Do not add sitemap, canonical, search, footer, portfolio, or hero links to
  `/event-balloons`.
- If a hub page is desired later, it needs a new explicit GL route decision.
- Treat Search Console "Not Found" records after launch as expected crawl
  cleanup, not as a reason to recreate or redirect the route.
