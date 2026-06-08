---
name: Codex Browser Verification Surface
level: recipe
last_verified: 2026-05-29
scope: Locally Twisted Codex browser and web verification
---

## What it does

Keeps agents from mixing up three different evidence types:

- internet lookup/read access
- browser-rendered proof
- LT route-contract verification
- app connector access

## When to use it

- A task depends on current public internet facts.
- A task needs proof of what a browser actually renders.
- A route, form, checkout path, menu, animation, responsive layout, or Webshop surface is being claimed as working.
- Browser Use, Playwright, or web lookup availability is uncertain.
- A connector fails but another browser, provider, API, or public internet lane
  could still verify the customer path.

## Verified baseline

On 2026-05-09, Codex verified:

- `web.run` can search the public internet and open/read `https://www.example.org/`.
- repo-local Playwright can launch headless Chromium silently, load `https://example.org/`, read the title and H1, confirm visible body text, and capture a `1280x720` screenshot buffer.
- the Browser Use in-app path was not available in that session because the required Node REPL JavaScript execution tool was not exposed after tool discovery.

On 2026-05-29, hosted staging checkout email verification exposed a connector
boundary: the Gmail connector returned `token_revoked`, but ERPNext/Frappe API
evidence still proved the paid-order emails remained in `Email Queue` as `Not
Sent`. Connector failure blocked inbox-visible Gmail proof only; it did not
block internet access, staging API/browser proof, Frappe Cloud/provider repair,
or the core email-queue diagnosis.

## Tool order

1. Use `web.run` for current public facts, outside-source lookup, citations, and page text.
2. Use LT's npm verifier scripts when the behavior is covered by a route contract.
3. Use direct headless Playwright when a route-specific verifier does not exist or when isolating a visual/browser symptom.
4. Use a headed browser only when silent/headless verification cannot reproduce the issue or GL explicitly needs a visible window.
5. Use app connectors for account data when they work, but treat connector
   errors such as `token_revoked` as an access-lane failure. Switch to an
   authenticated browser session, provider dashboard/API, ERPNext/Frappe API, or
   public web proof when that lane can answer the same customer question.

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
- Stopping at a Gmail, Drive, Chrome, or provider connector token failure when a
  normal browser session, provider dashboard, staging API, or public internet
  request can still prove or repair the path.
- Treating a connector failure as proof that the underlying customer email,
  payment, checkout, or provider path failed.

## Closeout rule

When the task touches customer-facing behavior, report exactly which surface proved the claim:

- public internet lookup/read
- headless browser render
- repo verifier
- visible/manual browser
- app connector
- provider dashboard/API
- staging or ERPNext/Frappe API

If one surface was unavailable, say so directly and do not imply it passed.
If a connector was unavailable, name the alternate surface used or mark only
the connector-specific proof as blocked.
