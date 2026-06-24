---
id: lt-photoreal-balloon-homepage-hero-contract
name: LT Photoreal Balloon Homepage Hero Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted homepage and audience-lane generated hero image option sets
currently_true: local_only
verification_level: 2
last_verified: 2026-06-24
evidence_quality: direct
successful_uses: 2
failed_uses: 0
regressions: 0
depends_on:
  - homepage-launch-proof-contract
  - compact-hero-contract
  - responsive-container-audit
  - codex-browser-verification-surface
used_by:
  - homepage-hero-photoreal-refresh-2026-06-24
tags:
  - Locally Twisted
  - homepage
  - generated images
  - photoreal
  - balloons
  - hero
---

# LT Photoreal Balloon Homepage Hero Contract

Use this recipe when generating, reviewing, storing, or shipping generated
Locally Twisted homepage hero images, especially audience-lane options for
civic/community, schools/campuses, and private celebrations.

This is a project capability, not a blanket approval to publish generated art.
Generated images are representative marketing visuals. They are not proof
photos, portfolio work, customer event evidence, or literal installed-work
claims unless the source is an approved real photo and documented as such.

## Hard Quality Bar

Reject an option before public use when it has any of these traits:

- cartoon, illustration, CGI, plastic-render, toy, glossy 3D, or flat novelty
  art;
- impossible balloon physics such as floating unsupported arches, garlands with
  no attachment path, columns with no base/weight, balloons intersecting hard
  surfaces, or structures that block normal event access;
- fake readable text, fake logos, fake school names, fake city seals, posters,
  watermarks, labels, signage, or brand marks;
- malformed hands, faces, bodies, cords, seams, knots, tables, chairs, doors,
  windows, or architecture;
- black borders, letterboxing, transparent edges, distorted aspect ratio,
  low-resolution softness, heavy blur, or noisy compression artifacts;
- scene mismatch, such as corporate ballroom imagery for private celebrations
  or staged product-pack photography for an installed event decor hero.

## Construction Realism Guards

Prompt and review for real balloon-installation behavior:

- arches anchor at both ends or to a visible frame;
- garlands attach to a wall, backdrop, railing, truss, arch frame, or ceiling
  point;
- columns stand on weighted bases or stable posts;
- organic clusters have varied but plausible balloon sizes with visible depth,
  not impossible repeated spheres;
- large installs leave usable walk paths, doors, stages, booths, or photo areas
  unobstructed;
- outdoor scenes should show wind-safe restraint through frames, bases, or
  protected placement;
- no helium-looking floating masses unless strings/weights make the lift
  plausible.

Prefer mid-distance event photography with no close hands or faces. People may
be distant background scale only when useful, but the decor must be the subject.

## Candidate Option Standard

For a homepage hero refresh, create 3 or 4 distinct options per requested lane.
Each option must have a different scene concept, not just a color variation.

## Generation Surface Standard

Use Codex's built-in `image_gen` tool first. For LT homepage hero option work,
normal Codex image generation is OAuth/session backed and does not require
`OPENAI_API_KEY`.

On Wardenclyffe, built-in image outputs may appear only in the Codex session
JSONL as an `image_generation_call.result` base64 payload. If no normal file
appears under `$CODEX_HOME/generated_images/`, extract the latest built-in
output with:

```bash
python scripts/dev/save_latest_codex_image.py --out <workspace-image-path>
```

The local convenience command `/home/guidingl/.local/bin/codex-save-latest-image`
may also exist on Wardenclyffe, but the repo-tracked helper above is the source
to cite in LT docs.

Do not default to the API-key CLI fallback for ordinary LT hero images. The CLI
path calls the OpenAI API directly, can hit platform billing limits, and should
be used only when GL explicitly approves API-backed generation or a CLI-only
feature is genuinely required.

Store candidate sources under:

```text
_resources/generated-hero-sources/YYYY-MM-DD/homepage-photoreal-options/
```

Use clear filenames:

```text
<lane-slug>-option-01-<scene-slug>-source.webp
<lane-slug>-option-02-<scene-slug>-source.webp
<lane-slug>-option-03-<scene-slug>-source.webp
<lane-slug>-option-04-<scene-slug>-source.webp
```

Also keep a manifest in the same folder:

```text
homepage-photoreal-hero-options-manifest.json
```

The manifest records lane, option number, scene slug, prompt, generation mode,
review status, rejection notes, source filename, and whether the option has
been owner-approved for final crops.

2026-06-24 evidence: this recipe produced a stored homepage review pack with
3 options each for Civic & Community, Schools & Campuses, and Private
Celebrations. The pack includes source WebPs, desktop/tablet/mobile previews,
per-lane review sheets, and a manifest under
`_resources/generated-hero-sources/2026-06-24/homepage-photoreal-options/`.
No public references were changed because GL selection is still required.

2026-06-24 follow-up evidence: GL selected Schools & Campuses option 03 and
Private Celebrations option 02, rejected Civic & Community options 01-03, and
requested a Civic redo. This recipe then produced 4 new Civic redo options
04-07 with source WebPs, desktop/tablet/mobile previews,
`review-sheet-civic-community-redo.webp`, current-review desktop/mobile contact
sheets, and a manifest decision log. Public homepage references still did not
change because Civic selection remains pending and the grouped homepage hero
set must ship together after full approval.

## Final Crop Standard

Only owner-approved options become public assets. Public assets belong under:

```text
apps/locally_twisted/locally_twisted/public/images/heroes/
```

Use breakpoint-specific WebP crops:

```text
homepage-<lane-slug>-hero-desktop.webp
homepage-<lane-slug>-hero-tablet.webp
homepage-<lane-slug>-hero-mobile.webp
```

Default current homepage crop sizes:

- desktop: `1920x560`
- tablet: `1400x560`
- mobile: `900x660`

Use cover-crop resizing without distortion. The subject must survive all three
breakpoints under the black readability overlay. Do not ship a single crop for
all breakpoints.

## Required Review Before Publish

Before wiring public hero references:

1. Inspect each source option visually.
2. Reject obvious AI/physics/artifact failures.
3. Present the remaining candidate option set to GL for selection.
4. Generate final breakpoint crops only for approved options.
5. Verify served assets return `200 image/webp`.
6. Verify the rendered homepage at desktop, tablet, 375px mobile, and 320px
   mobile with screenshots.
7. Run the homepage/container/interactive/layout gates required by
   `homepage-launch-proof-contract`.

Do not publish or deploy generated hero replacements without explicit GL
selection or a written owner-approved exception.

## Prompt Pattern

Use the project image-generation tool first. Keep prompts explicit:

```text
Use case: photorealistic-natural
Asset type: Locally Twisted homepage hero candidate
Primary request: photoreal professional event photography of realistic balloon decor for <lane>.
Scene/backdrop: <specific scene>.
Subject: installed balloon decor with plausible frames, anchors, bases, or wall/backdrop attachment.
Style/medium: high-end event photography, realistic latex and mylar balloon surfaces, natural lens perspective.
Composition/framing: wide horizontal hero composition, decor centered enough to survive desktop/tablet/mobile cover crops, no black borders.
Lighting/mood: cinematic but natural event lighting.
Text: no readable text.
Constraints: representative marketing image only; no fake logos, signage, school names, city seals, watermarks, flags as the main subject, close faces, or malformed anatomy.
Avoid: cartoon, illustration, CGI, toy render, impossible floating balloon structures, distorted architecture, low quality, blur, black edges.
```

## Closeout Language

Closeout must state:

- how many options were generated for each lane;
- where the sources and manifest live;
- which options were rejected before GL review, if any;
- whether GL approval is still needed;
- whether public hero references were changed;
- which browser/screenshot surface proved the final rendering.
