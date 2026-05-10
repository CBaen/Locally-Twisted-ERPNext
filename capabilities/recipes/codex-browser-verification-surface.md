---
name: Codex Browser Verification Surface
level: recipe
last_verified: 2026-05-09
scope: Locally Twisted Codex browser and web verification
---

## What it does

Keeps agents from mixing up three different evidence types:

- internet lookup/read access
- browser-rendered proof
- LT route-contract verification

## When to use it

- A task depends on current public internet facts.
- A task needs proof of what a browser actually renders.
- A route, form, checkout path, menu, animation, responsive layout, or Webshop surface is being claimed as working.
- Browser Use, Playwright, or web lookup availability is uncertain.

## Verified baseline

On 2026-05-09, Codex verified:

- `web.run` can search the public internet and open/read `https://www.example.org/`.
- repo-local Playwright can launch headless Chromium silently, load `https://example.org/`, read the title and H1, confirm visible body text, and capture a `1280x720` screenshot buffer.
- the Browser Use in-app path was not available in that session because the required Node REPL JavaScript execution tool was not exposed after tool discovery.

## Tool order

1. Use `web.run` for current public facts, outside-source lookup, citations, and page text.
2. Use LT's npm verifier scripts when the behavior is covered by a route contract.
3. Use direct headless Playwright when a route-specific verifier does not exist or when isolating a visual/browser symptom.
4. Use a headed browser only when silent/headless verification cannot reproduce the issue or GL explicitly needs a visible window.

## LT verifier preference

Prefer the narrowest executable gate that owns the claim:

- `npm run test:layout-fit`
- `npm run test:container-contract`
- `npm run test:interactive-layout`
- `npm run test:public-verify`
- `npm run test:launch-verify`
- route-specific gates such as `test:portfolio-reel`, `test:shop-smoke`, `test:checkout-experience`, and `test:desk-owner`

Use raw Playwright as investigation evidence, not as a replacement for an existing LT contract.

## Failure modes

- Treating `web.run` page text as proof that the rendered browser route works.
- Treating a headless screenshot as proof of the user's persistent Chrome/Brave session when cache, extensions, reduced-motion, or account state are relevant.
- Claiming Browser Use plugin access works because the plugin exists, without confirming the Node REPL control tool is available in the current session.
- Opening a physical browser window when a silent Playwright run would answer the question.

## Closeout rule

When the task touches customer-facing behavior, report exactly which surface proved the claim:

- public internet lookup/read
- headless browser render
- repo verifier
- visible/manual browser

If one surface was unavailable, say so directly and do not imply it passed.
