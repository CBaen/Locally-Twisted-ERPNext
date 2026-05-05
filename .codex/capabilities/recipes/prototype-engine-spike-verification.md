---
id: prototype-engine-spike-verification
name: Prototype Engine Spike Verification
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted browser rendering research spikes
currently_true: unknown
verification_level: 1
last_verified: 2026-05-03
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on: []
used_by: []
tags:
  - Locally Twisted
  - prototype
  - PlayCanvas
  - Babylon
  - browser verification
---

# Prototype Engine Spike Verification

Use this recipe when comparing browser rendering engines for a future LT feature while keeping the work out of production routes.

## When To Use

- The work is a research-only prototype.
- Two or more rendering engines need an apples-to-apples comparison.
- The feature could later affect customer trust, scale, pricing, or CRM payloads.
- The prototype must not touch Frappe routes, Leads, checkout, save/share, or live ERPNext data.

## Pattern

1. Put the spike in a nested research package with its own `package.json`.
2. Keep production routes and `apps/` untouched.
3. Put product facts, payload shape, and construction math in shared code or shared data.
4. Keep each engine renderer thin: it should consume the same scene objects and return the same payload facts.
5. Add a verifier before calling the spike complete.
6. Capture desktop and mobile screenshots for every engine.
7. Choose the default engine using the pre-agreed decision rule, not preference after the fact.

## Verifier Checklist

- Starts the local prototype server itself.
- Fails if required entry pages are missing.
- Fails on console or page errors.
- Checks canvas output is nonblank.
- Checks fixed camera/runtime facts.
- Checks visible 1 ft scale.
- Checks product math facts that matter to customer trust.
- Checks payload parity between engines except the engine identifier.
- Checks at least one interaction changes the payload.
- Checks mobile width has no horizontal overflow.

## LT Receipt

The first successful use is `research/design-studio-v2/event-builder-spike/`, which compares PlayCanvas and Babylon.js for the future design-studio event builder. Both engines passed; PlayCanvas is the recommended default for the next hidden-route spike.
