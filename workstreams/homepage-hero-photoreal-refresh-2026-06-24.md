# Homepage Hero Photoreal Refresh Follow-Up

Date: 2026-06-24
Status: local source/browser proof complete; built-in image file extraction repaired; generated option sets pending
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

Current remaining work: generate the requested option sets with built-in
`image_gen`, immediately extract each output into the dated option folder,
inspect/reject failures, and present remaining options to GL. The manifest
records the earlier attempted prompt and the planned 3-option scene set for
each of:

- Civic & Community
- Schools & Campuses
- Private Celebrations

Next steps:

1. Generate 3 or 4 distinct options per lane with built-in Codex `image_gen`.
2. Save each output with `scripts/dev/save_latest_codex_image.py` into the
   dated option folder using the manifest filename pattern.
3. Visually reject AI-looking or physically impossible options before GL
   review.
4. Present remaining options for GL selection.
5. Only after GL selection, create final desktop/tablet/mobile WebP crops and
   wire homepage references.

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
npx playwright --version
node Playwright managed Chromium smoke
ssh banebook Playwright managed Chromium smoke
python scripts/dev/clear_website_cache.py
npm run test:interactive-layout -- --grep "homepage hero uses one visible stable headline|small mobile homepage hero|compact hero height contract" -> 62 passed
npm run test:layout-fit -- --grep "home fits" -> 13 passed
npm run test:container-contract -- --grep "home" -> 3 passed
npm run test:public-assets -> PASS (31 routes, 362 unique local asset URLs)
```

Fresh screenshot artifacts:

```text
output/playwright/homepage-hero-july-removal-20260624/desktop-home.png
output/playwright/homepage-hero-july-removal-20260624/mobile-home-375.png
output/playwright/homepage-hero-july-removal-20260624/mobile-home-320.png
```

Rendered facts from the screenshot run:

- `slides = 4`
- first H1 is Civic & Community
- homepage body does not contain `Fourth of July`
- first image is still the existing Civic source
  `seasonal-pride-columns.webp`

## Live Boundary

No Frappe Cloud app mirror push, live site update, live cache clear, DNS,
Stripe, Search Console, ERPNext data mutation, product visibility change, or
customer communication was performed in this follow-up slice.

Live `https://locallytwisted.com/` remains on the prior released state until a
separate release path is approved and completed.

## Deferred Items

- Replace Civic & Community, Schools & Campuses, and Private Celebrations hero
  images after built-in Codex image options are generated, extracted, reviewed,
  and GL selects options.
- Review the unrelated unstaged `AGENTS.md` local Docker runtime note later.
  It was intentionally not included in this feature slice.
