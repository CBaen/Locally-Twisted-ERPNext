# Design Studio V2 Agent Briefs

Last updated: 2026-05-02 by Codex.

Use these prompts for background agents working on the future `Plan Custom Decor` design studio.

These are first-wave spec prompts. They are not implementation prompts. The goal is to design the system clearly enough that a later prototype can be built Frappe-native without guesswork.

## Controller Note

Do not send agents to edit the same files at the same time.

Recommended first wave:

1. Physics Agent
2. UX/Product Agent
3. Visual Brand Agent
4. Frappe Architecture Agent
5. QA/Audit Agent

Each agent writes one spec under `research/design-studio-v2/`. After all return, the controller reconciles the work into `workstreams/design-studio-v2.md`.

Create `research/design-studio-v2/` before dispatch if it does not exist.

## Shared Context For Every Agent

Paste this block at the top of each agent prompt.

```text
You are working in:
C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted

Project: Locally Twisted ERPNext v15.105.0 + Frappe v15 website and business system.

You are working on a background V2 concept called "Design Studio" or "Plan Custom Decor." This is not a V1 launch blocker. Do not edit V1 launch-critical files or routes.

Read first:
- AGENTS.md
- workstreams/design-studio-v2.md
- research/contest-customizable-event-decor-tool/FINAL-SURFACE.md
- research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md
- workstreams/brand-audience-style-reset.md

Important framing:
- Ready to Order is for simple ecommerce products.
- Plan Custom Decor is for larger, consultative, multi-piece event installations.
- The future production tool should stay Frappe-native if possible.
- Treat old contest artifacts as source material, not final direction.
- Do not make Jeff the customer-facing brand. Locally Twisted is the brand.
- Distinguish balloon decor construction from balloon twisting.
- Do not modify C:\Users\baenb\projects\locally-twisted-odoo\.
- Say what is verified, inferred, and still needing GL/Jeff approval.
- When describing git or project state, do not use loaded shorthand. Say the concrete state instead: active work in progress, uncommitted changes, existing edits, needs review before editing, not launch-ready, possible overlap, or reconciliation needed.

Return format:
- Files read
- Output file changed or proposed
- Key decisions
- Risks or contradictions
- Questions for GL/Jeff
- Verification or source evidence
```

## Physics Agent Prompt

```text
Use the shared context.

Role: Physics and professional balloon decor construction agent.

Goal:
Create a construction-rule spec for the future Plan Custom Decor / Design Studio renderer.

Write scope:
- Create or update only: research/design-studio-v2/design-studio-physics-rules.md

Do not edit:
- apps/
- workstreams/website-launch.md
- workstreams/brand-audience-style-reset.md
- launch-critical route files
- catalog seed scripts

Primary sources:
- research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md
- research/contest-customizable-event-decor-tool/FINAL-SURFACE.md
- any existing physics-render-reference files under the contest folder

Focus:
1. Classic arch construction rules using 4-balloon clusters/quads.
2. Classic column rules using stacked clusters around a pole.
3. Backdrop/wall rules using a 4-balloon cluster grid.
4. Organic garland rules as controlled randomness, not fixed 4-cluster math.
5. Color distribution rules, including spiral, layered/chunk, stripe, and balanced repeat constraints.
6. Scale references and common sizing constraints.
7. Rules for what the renderer must not show because it would be unbuildable or misleading.

Important:
- Do not design the UI.
- Do not implement code.
- Do not invent exact pricing or legal claims.
- Use plain language and include formulas where they matter.

Return:
- The written spec path.
- The 5-10 most important renderer constraints.
- Anything that needs Jeff approval because it affects real-world build accuracy.
```

## UX/Product Agent Prompt

```text
Use the shared context.

Role: UX and product flow agent.

Goal:
Design the customer journey for Plan Custom Decor as a consultative design studio, while keeping Ready to Order as the simpler ecommerce path.

Write scope:
- Create or update only: research/design-studio-v2/plan-custom-decor-flow.md

Do not edit:
- apps/
- current shop templates
- contact form files
- workstreams/website-launch.md

Primary sources:
- workstreams/design-studio-v2.md
- research/contest-customizable-event-decor-tool/FINAL-SURFACE.md
- research/contest-customizable-event-decor-tool/_render/contestant-1/
- research/contest-customizable-event-decor-tool/_render/contestant-2/
- research/contest-customizable-event-decor-tool/_render/contestant-3/
- research/contest-customizable-event-decor-tool/_render/contestant-4/

Focus:
1. Entry flow for corporate, school, civic, venue, and premium private buyers.
2. Difference between Ready to Order and Plan Custom Decor.
3. Multi-piece composition flow: primary piece, suggested complementary piece, skip/add behavior.
4. Stakeholder share/save flow.
5. Organization color matching flow.
6. Completion summary that serves both customer and Locally Twisted sales follow-up.
7. What information should become CRM payload, including pieces considered but not selected.

Important:
- This should feel consultative, not like a kids' coloring game.
- Keep customer cognitive load low.
- Avoid making the tool promise a final engineering drawing.
- Use "Locally Twisted" or "we/us," not "Jeff" as the brand.

Return:
- The written spec path.
- Recommended V1 teaser or guided-inquiry relationship.
- Recommended V2 prototype flow.
- What the customer sees versus what Locally Twisted receives.
```

## Visual Brand Agent Prompt

```text
Use the shared context.

Role: Visual brand and interface direction agent.

Goal:
Define the visual direction for the future Design Studio so it fits the new Locally Twisted premium/civic/professional brand direction.

Write scope:
- Create or update only: research/design-studio-v2/design-studio-visual-direction.md

Do not edit:
- apps/
- CSS files
- current style guide
- current launch pages

Primary sources:
- workstreams/brand-audience-style-reset.md
- workstreams/design-studio-v2.md
- research/contest-customizable-event-decor-tool/_render/contestant-1/
- research/contest-customizable-event-decor-tool/_render/contestant-2/
- research/contest-customizable-event-decor-tool/_render/contestant-3/
- research/contest-customizable-event-decor-tool/_render/contestant-4/

GL's current direction:
- Move away from pastel/rainbow-first brand colors for the main company identity.
- Preferred synthesis includes civic/professional Utah authority, slate/blue/berry photo treatment, mountains/territory cues, black/gold professionalism, and high-trust event-business energy.
- Do not copy Zurchers visually. Borrow only retail clarity where useful.
- The studio should not feel like a toy.

Focus:
1. Interface tone.
2. Color and material direction.
3. Rendering style for balloons and scale references.
4. What to keep or reject from the contest renders.
5. How to make the tool feel premium while still interactive and approachable.
6. Visual rules for image/canvas/SVG output.

Important:
- Do not generate images unless explicitly asked by the controller.
- Do not implement CSS.
- Do not rewrite the main style guide.

Return:
- The written spec path.
- 3 acceptable visual directions, with one recommendation.
- 3 visual failure modes to avoid.
- Any questions for GL before image generation or UI mockups.
```

## Frappe Architecture Agent Prompt

```text
Use the shared context.

Role: Frappe architecture agent.

Goal:
Design the Frappe-native technical architecture for a future Plan Custom Decor / Design Studio implementation.

Write scope:
- Create or update only: research/design-studio-v2/frappe-native-design-studio-architecture.md

Do not edit:
- DocTypes
- hooks.py
- apps/
- fixtures
- patches
- launch-critical files

Primary sources:
- AGENTS.md
- workstreams/design-studio-v2.md
- apps/locally_twisted/locally_twisted/hooks.py
- apps/locally_twisted/locally_twisted/www/
- apps/locally_twisted/locally_twisted/api/
- apps/locally_twisted/locally_twisted/lead_cascade.py
- apps/locally_twisted/locally_twisted/product_options.py

Focus:
1. Recommended route structure.
2. Public JS/CSS structure.
3. Whether the prototype should live under research or a hidden/unlinked Frappe route.
4. Future DocType shape for saved design sessions.
5. Guest save/share token behavior.
6. Account save behavior.
7. Lead/CRM submission payload.
8. Loud failure behavior.
9. Verification commands or checks needed before production integration.

Important:
- Prefer Frappe-native patterns.
- Avoid a separate app, separate service, or external frontend build unless you can prove it is needed.
- Do not implement anything yet.

Return:
- The written spec path.
- Recommended technical shape for prototype and production.
- A proposed data contract for design payloads.
- Risks around guest sharing, privacy, spam, and CRM payload quality.
```

## QA/Audit Agent Prompt

```text
Use the shared context.

Role: QA, risk, and contradiction audit agent.

Goal:
Find weak assumptions before the design studio becomes implementation work.

Write scope:
- Create or update only: research/design-studio-v2/design-studio-risk-audit.md

Do not edit:
- apps/
- launch workstreams
- current route files
- current CSS/JS

Primary sources:
- workstreams/design-studio-v2.md
- research/contest-customizable-event-decor-tool/FINAL-SURFACE.md
- research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md
- workstreams/launch-v1-success-contract.md
- workstreams/website-launch.md
- workstreams/brand-audience-style-reset.md

Focus:
1. Scope risks.
2. Launch interference risks.
3. UX risks for non-technical customers.
4. Accessibility risks.
5. Mobile layout risks.
6. Frappe-native feasibility risks.
7. Misleading-render risks.
8. Business/brand risks.
9. Data/privacy/share-link risks.

Important:
- Be direct.
- Do not propose a giant rebuild.
- Separate V1 launch blockers from V2 design-studio risks.

Return:
- The written audit path.
- Top 10 risks, ordered by severity.
- What should block prototype work.
- What can wait until production integration.
```

## Future Prototype Agent Prompt

Do not use this until the first spec wave has been reconciled.

```text
Use the shared context.

Role: Prototype implementation agent.

Goal:
Build a narrow, dormant, Frappe-compatible prototype of the Design Studio based on the reconciled specs.

Required before starting:
- workstreams/design-studio-v2.md has been updated after the first spec wave
- research/design-studio-v2/design-studio-physics-rules.md exists
- research/design-studio-v2/plan-custom-decor-flow.md exists
- research/design-studio-v2/design-studio-visual-direction.md exists
- research/design-studio-v2/frappe-native-design-studio-architecture.md exists
- Controller has explicitly approved prototype implementation

Likely write scope:
- research/design-studio-v2/prototype/

Do not edit production Frappe app files unless the controller gives explicit approval.

Prototype target:
- Classic arch
- Pair of classic columns
- Simple backdrop/photo-op wall
- Organization color matching stub
- Scale reference stub
- Summary payload stub
- Pieces considered capture

Return:
- Changed files
- How to run/view the prototype
- Known gaps
- Verification evidence
```
