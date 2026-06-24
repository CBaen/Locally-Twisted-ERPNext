# Homepage Hero Photoreal Refresh Follow-Up

Date: 2026-06-24
Status: local source/browser proof complete; full GL-selected crop set wired; pending explicit live release approval
Owner: Codex technical lead
Scope: Locally Twisted homepage hero carousel, photoreal balloon image option process, and browser screenshot runtime

## Current Outcome

GL rejected the live Fourth of July homepage hero image and asked to remove the
Fourth of July hero entirely. Local source now removes that slide from
`HOME_HERO_SLIDES`, so the homepage carousel has four slides:

1. Civic & Community
2. Corporate Events
3. Schools & Campuses
4. Private Celebrations

The carousel timing was reduced from 40s/five slides to 32s/four slides. The
first visible page-level H1 is now:

```text
Balloon moments for public events and community gatherings.
```

The old July WebP assets were left in the repo as historical/recoverable
assets, but they are no longer referenced by the local homepage source.

Follow-up in this same slice generated a stored review pack for the requested
replacement image lanes. GL selected Schools & Campuses option 03 and Private
Celebrations option 02, then rejected all first Civic & Community options and
requested a civic redo. GL later selected Civic & Community redo option 05.
Codex then created the final public crops for Civic option 05, Schools option
03, and Private option 02 as one grouped set and wired the homepage carousel to
those selected files.

Current selected public crops:

```text
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-civic-community-hero-desktop.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-civic-community-hero-tablet.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-civic-community-hero-mobile.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-schools-campuses-hero-desktop.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-schools-campuses-hero-tablet.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-schools-campuses-hero-mobile.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-private-celebrations-hero-desktop.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-private-celebrations-hero-tablet.webp
apps/locally_twisted/locally_twisted/public/images/heroes/homepage-private-celebrations-hero-mobile.webp
```

## Image Option Process

New project capability:

```text
capabilities/recipes/lt-photoreal-balloon-homepage-hero-contract.md
```

Purpose:

- require 3 or 4 distinct photoreal options per requested homepage hero lane;
- reject cartoon/CGI/toy/AI-looking output;
- require realistic balloon construction, anchors, bases, frames, wall/backdrop
  attachment, and usable event paths;
- store candidate sources in one dated folder with clear option names;
- require GL selection before public breakpoint crops are wired.

Candidate source folder:

```text
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/
```

Manifest:

```text
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/homepage-photoreal-hero-options-manifest.json
```

Generated review sheets:

```text
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/review-sheet-civic-community.webp
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/review-sheet-schools-campuses.webp
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/review-sheet-private-celebrations.webp
```

Pack contents:

- Civic & Community: 3 original generated photoreal options rejected by GL,
  plus 4 redo options. GL selected redo option 05.
- Schools & Campuses: 3 generated photoreal options.
- Private Celebrations: 3 generated photoreal options.
- Source WebPs, desktop/tablet/mobile preview crops, per-lane review sheets,
  and manifest prompts/hashes/dimensions are stored in the dated folder.
- Raw extraction PNGs were used only as conversion intermediates, then omitted
  from the durable pack to avoid redundant repository weight.
- Public homepage hero references were changed only after all three requested
  lanes had a GL-selected option.

Current GL selection state:

- Schools & Campuses: option 03 selected by GL on 2026-06-24.
- Private Celebrations: option 02 selected by GL on 2026-06-24.
- Civic & Community: options 01-03 rejected by GL on 2026-06-24; redo option
  05 selected by GL on 2026-06-24. Redo options 04, 06, and 07 remain
  preserved as not-selected review artifacts.

Current review sheets:

```text
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/review-sheet-civic-community-redo.webp
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/homepage-photoreal-options-current-review-desktop-contact-sheet.webp
_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/homepage-photoreal-options-current-review-mobile-contact-sheet.webp
```

## Built-In Codex Image Output Fix

The built-in `image_gen` tool was used once for the first Civic & Community
candidate prompt. The first troubleshooting pass found no normal local image
artifact under:

- `/home/guidingl/.codex`
- `/tmp`
- `/mnt`
- `/home/guidingl/Downloads`
- `/home/guidingl/Pictures`
- this project workspace

That was not an image-generation availability failure. GL clarified that normal
Codex image generation is subscription/OAuth backed and should not require an
API key. A follow-up test proved built-in `image_gen` works in-session and that
the image bytes are stored in Codex session JSONL as an
`image_generation_call.result` base64 payload.

Tracked extraction helper:

```text
scripts/dev/save_latest_codex_image.py
```

Local convenience command installed on Wardenclyffe:

```text
/home/guidingl/.local/bin/codex-save-latest-image
```

Use:

```bash
python scripts/dev/save_latest_codex_image.py --list
python scripts/dev/save_latest_codex_image.py --out _resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/<candidate-name>.png
```

This helper does not call the OpenAI API, does not read `.env`, and does not
need `OPENAI_API_KEY`.

The API-key CLI fallback was briefly tested after GL placed a key in `.env`.
The local SDK/key path reached OpenAI, but the provider returned
`billing_hard_limit_reached`. GL then clarified that API-key billing is not the
desired path because Codex image generation is expected to work through the
subscription/OAuth session. `.env` was blanked back to:

```text
OPENAI_API_KEY=
```

No API-generated images were produced.

Completed image-generation work: generated the requested option sets with
built-in `image_gen`, immediately extracted each output into the dated option
folder, converted source WebPs, created desktop/tablet/mobile previews, created
per-lane review sheets, and updated the manifest. Preliminary visual review
found no obvious cartoon/CGI output, fake readable logos/signage, impossible
floating installs, or corporate-event mismatch in the Private Celebrations
lane.

Completed follow-up:

1. GL selected Civic & Community redo option 05.
2. Codex created final desktop/tablet/mobile public WebP crops for selected
   Civic, Schools, and Private options together.
3. Homepage slide image references were wired as one complete approved image
   set.
4. Rendered desktop/tablet/mobile/320 screenshots and the homepage layout gates
   passed locally.

## Browser Screenshot Runtime Fix

The previous release blocker was real: Playwright 1.59.1 refused managed
Chromium download on Ubuntu 26.04 when no system Chromium was available.

Implemented locally:

- upgraded `@playwright/test` from `1.59.1` to `1.61.1`;
- installed Playwright-managed Chromium on Wardenclyffe;
- verified Playwright-managed Chromium launches on Wardenclyffe;
- verified Playwright-managed Chromium launches on Banebook over SSH from a
  temporary directory;
- removed Edge from the repo-local browser fallback list;
- local preference order is now Brave, Chromium, Chromium Browser, then Google
  Chrome.

Current machine proof:

- Wardenclyffe: `npx playwright --version` returned `Version 1.61.1`.
- Wardenclyffe: managed Chromium launched and rendered a data-URL smoke page.
- Wardenclyffe: `scripts/verify/browser_runtime.py --print-browser` returned
  `/usr/bin/brave-browser`.
- Banebook: Node/npm/npx present, Brave present, Chromium present, and
  Playwright 1.61.1 managed Chromium launched successfully from a temporary
  directory.

No Edge install was used or required.

## Local Verification

Capability gate:

```text
PASS
Loaded:
- capabilities/INDEX.md
- capabilities/recipes/homepage-launch-proof-contract.md
- capabilities/recipes/lt-photoreal-balloon-homepage-hero-contract.md
- capabilities/recipes/codex-browser-verification-surface.md
- capabilities/recipes/responsive-container-audit.md
- capabilities/recipes/compact-hero-contract.md
- capabilities/recipes/frappe-public-container-contract.md
- capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
- capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md
- capabilities/failures/capability-context-gate-bypass-drift.md
```

Checks passed:

```text
python -m py_compile apps/locally_twisted/locally_twisted/www/home.py scripts/verify/browser_runtime.py scripts/verify/smoke_shop.py
node --check playwright.config.js
node --check scripts/verify/interactive_layout.spec.js
python -m json.tool _resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/homepage-photoreal-hero-options-manifest.json
python scripts/dev/save_latest_codex_image.py --list
python scripts/dev/save_latest_codex_image.py --out output/imagegen/builtin-helper-smoke-20260624.png
codex-save-latest-image --list
Pillow processing for source WebPs, desktop/tablet/mobile previews, and review sheets
Pillow processing for Civic & Community redo options 04-07, current-review desktop/mobile contact sheets, and manifest selection/rejection state
npx playwright --version
node Playwright managed Chromium smoke
ssh banebook Playwright managed Chromium smoke
python scripts/dev/clear_website_cache.py
npm run test:interactive-layout -- --grep "homepage hero uses one visible stable headline|small mobile homepage hero|compact hero height contract" -> 62 passed
npm run test:layout-fit -- --grep "home fits" -> 13 passed
npm run test:container-contract -- --grep "home" -> 3 passed
npm run test:public-assets -> PASS (31 routes, 362 unique local asset URLs)
rendered homepage filename proof -> new Civic/Schools/Private filenames present; old `seasonal-pride-columns.webp`, `school-back-to-school-stage.webp`, `wedding-floral-half-arch.webp`, and `Fourth of July` absent
public hero asset HEAD probes -> all nine selected WebPs returned `200 image/webp`
```

Fresh screenshot artifacts:

```text
output/playwright/homepage-hero-july-removal-20260624/desktop-home.png
output/playwright/homepage-hero-july-removal-20260624/mobile-home-375.png
output/playwright/homepage-hero-july-removal-20260624/mobile-home-320.png
output/playwright/homepage-hero-selected-final-20260624/desktop-home.png
output/playwright/homepage-hero-selected-final-20260624/tablet-home.png
output/playwright/homepage-hero-selected-final-20260624/mobile-home-375.png
output/playwright/homepage-hero-selected-final-20260624/mobile-home-320.png
```

Rendered facts from the screenshot run:

- `slides = 4`
- first H1 is Civic & Community
- homepage body does not contain `Fourth of July`
- first image is now
  `homepage-civic-community-hero-desktop.webp` at desktop and the matching
  tablet/mobile public crops at smaller viewports
- final public crops use `1920x560`, `1400x560`, and `900x660`

## Live Boundary

No Frappe Cloud app mirror push, live site update, live cache clear, DNS,
Stripe, Search Console, ERPNext data mutation, product visibility change, or
customer communication was performed in this follow-up slice.

Live `https://locallytwisted.com/` remains on the prior released state until a
separate release path is approved and completed.

## Deferred Items

- Run Frappe Cloud/app-mirror/live route proof only after explicit live release
  approval for this source slice.
- Review the unrelated unstaged `AGENTS.md` local Docker runtime note later.
  It was intentionally not included in this feature slice.
