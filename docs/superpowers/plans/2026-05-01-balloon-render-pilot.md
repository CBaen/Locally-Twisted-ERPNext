# Balloon Render Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a five-image pilot package for realistic Locally Twisted catalog renders before any catalog-wide generation or ERPNext media upload.

**Architecture:** Keep the pilot as source-grounded documentation first: research notes, prompt blocks, variant/media rules, review rubric, then image generation in a separate reviewed step. The generated images must be judged against LT source photos and construction rules before being attached to any ERPNext item or website item.

**Tech Stack:** Markdown docs, local LT image references under `_resources/odoo-live/images/`, ERPNext/Frappe media records later, image-generation tool later.

---

### Task 1: Research-Grounded Pilot Show Pack

**Files:**
- Create: `docs/superpowers/specs/2026-05-01-balloon-render-pilot-show-pack.md`

- [x] **Step 1: Create the show pack doc**

Write `docs/superpowers/specs/2026-05-01-balloon-render-pilot-show-pack.md` with:

```markdown
# Balloon Render Pilot Show Pack

Date: 2026-05-01

## Purpose

Create the first five render prompts that GL can review as Jeff's proxy before Locally Twisted creates generated catalog lead images.

## Required Pilot Images

1. `classic-arch` single-door scale.
2. `classic-arch` parade/truck-clearance scale.
3. `classic-column` classic spiral.
4. `classic-organic-balloon-garland` controlled organic.
5. `birthday-deliveries` premium studio catalog.
```

- [x] **Step 2: Verify the file exists**

Run:

```powershell
Test-Path docs\superpowers\specs\2026-05-01-balloon-render-pilot-show-pack.md
```

Expected: `True`.

- [x] **Step 3: Commit the show pack**

Run:

```powershell
git add -- docs/superpowers/specs/2026-05-01-balloon-render-pilot-show-pack.md
git diff --cached --check
git commit -m "Add balloon render pilot show pack"
```

Expected: the commit includes only the show pack doc.

### Task 2: Generate Five Draft Images

**Files:**
- Read: `docs/superpowers/specs/2026-05-01-balloon-render-pilot-show-pack.md`
- Read: `_resources/odoo-live/images/classic-arch.png`
- Read: `_resources/odoo-live/images/classic-column.png`
- Read: `_resources/odoo-live/images/classic-organic-balloon-garland.png`
- Read: `_resources/odoo-live/images/birthday-deliveries.png`
- Create later: `_resources/generated-renders/pilot/README.md`
- Create later: `_resources/generated-renders/pilot/*.png`

- [x] **Step 1: Create the pilot render folder**

Run:

```powershell
New-Item -ItemType Directory -Force _resources\generated-renders\pilot
```

Expected: `_resources/generated-renders/pilot` exists.

- [x] **Step 2: Generate one image per pilot prompt**

Use the prompt text from the show pack exactly. Save draft images with these names:

```text
classic-arch-single-door-v1.png
classic-arch-parade-clearance-v1.png
classic-column-spiral-v1.png
classic-organic-garland-v1.png
birthday-delivery-studio-v1.png
```

- [x] **Step 3: Create the pilot render README**

Write `_resources/generated-renders/pilot/README.md` with:

```markdown
# Balloon Render Pilot Drafts

Date: 2026-05-01

These images are generated illustrative drafts for GL/Jeff review. They are not verified real Locally Twisted installs and must not be used as customer proof images.

## Review Status

| File | Status | Notes |
|---|---|---|
| classic-arch-single-door-v1.png | pending GL review | Check single-door scale and classic cluster construction. |
| classic-arch-parade-clearance-v1.png | pending GL review | Check truck-clearance scale, anchoring, and non-misleading context. |
| classic-column-spiral-v1.png | pending GL review | Check 4-balloon quad logic, spiral consistency, topper support. |
| classic-organic-garland-v1.png | pending GL review | Check mixed-size organic logic, controlled color masses, believable rigging. |
| birthday-delivery-studio-v1.png | pending GL review | Check foil/latex structure, readable intentional text only, studio consistency. |
```

- [x] **Step 4: Commit generated pilot drafts only after visual review**

Run:

```powershell
git add -- _resources/generated-renders/pilot
git diff --cached --check
git commit -m "Add balloon render pilot drafts"
```

Expected: commit contains only pilot draft files and README.

### Task 3: ERPNext Media Mapping Plan

**Files:**
- Create: `docs/superpowers/plans/2026-05-01-balloon-media-import.md`

- [ ] **Step 1: Write the media mapping plan**

Create `docs/superpowers/plans/2026-05-01-balloon-media-import.md` with:

```markdown
# Balloon Media Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Attach approved render and gallery media to ERPNext templates and variants without misleading customers or collapsing size-specific images.

**Architecture:** Import media only after GL approval. Template lead images stay separate from size-specific variant images and real LT proof/gallery photos.

**Tech Stack:** ERPNext v15, Frappe site `frontend`, `locally_twisted` app, File records, Item images, Website Item image/gallery fields.
```

- [ ] **Step 2: Stop before DB writes**

Do not write ERPNext media records in this task. The import plan waits until GL approves pilot images.
