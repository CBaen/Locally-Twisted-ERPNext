# Visual, Gameplay, Mobile, and Desktop Audit

Scope: read-only audit of `prototype/`, `event-builder-spike/`, `design-studio-visual-direction.md`, `playcanvas-crown-jewel-research.md`, and `plan-custom-decor-flow.md`. No external web used.

## 1) Executive verdict

The current work has a strong product spine: professional planning language, supplier-actionable color names, clear planning disclaimers, construction-aware payloads, and a PlayCanvas spike that proves direct manipulation can become memorable. But the active prototypes are split between two different product models: the Frappe-friendly SVG guided prototype says the first serious flow should be guided and low-choice, while the PlayCanvas spike is already an open stage game. That contradiction is the main risk.

Verdict: keep the guided `Plan Custom Decor` flow as the production UX baseline, and treat the PlayCanvas stage as a crown-jewel research lane until it satisfies the stage-root, picking, mobile, visual-fidelity, and verification gates called out in `playcanvas-crown-jewel-research.md` lines 338-381 and 451-468.

## 2) Desktop user gameplay issues

1. **The two prototypes disagree on core gameplay.** `plan-custom-decor-flow.md` says the multi-piece composition should be a planning board and explicitly says "No drag-and-drop in the first prototype unless the architecture lane approves it" (lines 240-247). The PlayCanvas spike is centered on add, drag, rotate, duplicate, delete, stage-turn, and direct canvas manipulation (`event-builder-spike/src/main-event-playground.js` lines 118-159 and 477-505). Recommendation: define the open stage as research/demo mode, not the default customer journey, until approved.

2. **Desktop direct manipulation uses screen deltas rather than the recommended ray-to-stage pipeline.** The research guide says never infer production placement from raw screen delta after camera/stage changes; pointer input should raycast/intersect the stage plane and convert to stage-local coordinates (`playcanvas-crown-jewel-research.md` lines 153-167). Current move code maps `dx/dy` directly through camera right/forward vectors (`event-builder-spike/src/main-event-playground.js` lines 490-522). This will feel wrong once the stage/camera rotates.

3. **Stage turning is visually useful but not yet architecturally trustworthy.** The guide's Transform Law requires stage turn to change `stageRoot` yaw while piece payload placement survives unchanged (`playcanvas-crown-jewel-research.md` lines 105-127). Current spike does set `stageRoot` yaw (`main-event-playground.js` lines 259-279), but the research diagnosis still flags stage-root anchoring, picking, and first-class piece roots as not acceptable yet (`playcanvas-crown-jewel-research.md` lines 426-443). Desktop gameplay should not be sold as production-accurate until this is verified.

4. **Selection/picking is underbuilt for a crown-jewel desktop interaction.** The guide calls for picking colliders, selected-piece handles, and pointer ray conversion (`playcanvas-crown-jewel-research.md` lines 221-237 and 451-461). Current picking creates a half-resolution `pc.Picker` and selects mesh hits (`main-event-playground.js` lines 468-483), but there are no larger handles; the selection marker is a floor rectangle (`main-event-playground.js` lines 637-640). Fine for spike, too fragile for customers.

5. **Gameplay loop is mostly tool buttons, not guided confidence.** Good gameplay is defined as immediate response, anchored drag, useful duplicate, warnings, and a summary that captures effort (`playcanvas-crown-jewel-research.md` lines 279-292). The PlayCanvas UI has tools/actions, but no visible warning system or ghost preview in the inspected code; it does produce a handoff summary (`main-event-playground.js` lines 528-585). Add warnings and preview affordances before expanding features.

6. **The Frappe/SVG prototype overloads one desktop screen with many panels.** Desktop layout is three columns: controls, sticky preview, sticky summary (`prototype/styles.css` lines 43-51, 361-414). It is clear for internal QA, but customer-facing desktop will feel like a control dashboard unless the flow is broken into guided steps as specified in `plan-custom-decor-flow.md` lines 80-232.

7. **Review/debug controls are visible in the customer prototype.** `prototype/index.html` exposes "Review states," "Design payload," and "Open review decisions" directly in the UI (lines 17-24 and 70-83). Useful for audit, but these must be hidden behind an internal/debug mode before customer review.

8. **Duplicate behavior is functional but not delightful.** Duplicates offset by fixed +1/-0.8 ft (`event-playground-state.js` lines 349-358). The research guide recommends animated duplicate offset and useful next-piece placement (`playcanvas-crown-jewel-research.md` lines 293-301). Fixed offsets can pile up or overlap in desktop sessions.

## 3) Mobile user gameplay issues

9. **Mobile PlayCanvas layout likely covers the playfield.** At <=760px, the topbar stacks, palette moves to `top: 190px`, and drawer consumes up to `43vh` at the bottom (`event-playground-styles.css` lines 262-324). With a full-screen canvas behind it, the customer has little unobstructed touch area for stage/piece manipulation.

10. **The mobile shell has a fixed minimum height and hidden body overflow.** `body { overflow: hidden; }`, `.epg-shell { min-height: 620px; }`, and mobile `.epg-shell { min-height: 720px; }` (`event-playground-styles.css` lines 23-41 and 262-265). On smaller phones this risks clipped controls instead of scrollable recovery.

11. **Touch input is disabled for browser gestures, but the UX does not yet replace them well.** Both canvas styles use `touch-action: none` (`event-playground-styles.css` lines 43-53; `event-builder-spike/src/styles.css` lines 115-119). The guide warns touch targets must stay usable and Chrome touch/mouse duplication must be verified (`playcanvas-crown-jewel-research.md` lines 221-237). The inspected code does not show mobile-specific gesture verification or handle sizing.

12. **Four-column mobile button grids create tiny labels.** Mobile `.epg-tools` and `.epg-button-grid` become four equal columns, with font sizes reduced to 0.72rem/0.7rem (`event-playground-styles.css` lines 282-324). This works for a tech demo but is risky for non-technical customers trying to plan an event.

13. **The guided SVG prototype is mobile safer but still linear-scroll heavy.** At <=760px it switches to block layout, one-column controls, and non-sticky preview (`prototype/styles.css` lines 493-529). That is robust, but the preview appears after many controls in DOM order (`prototype/index.html` lines 17-67), so customers may configure for a while before seeing the visual payoff.

14. **Mobile flow spec has not been converted into concrete bottom-sheet behavior.** `playcanvas-crown-jewel-research.md` requires mobile bottom sheet/control usability and no horizontal overflow as browser verification gates (lines 363-374). The CSS has a drawer, but no inspected test evidence in this lane proving the mobile flow survives real thumb use.

## 4) Visual direction issues

15. **Current primitive balloons are explicitly below the intended quality bar.** The research guide says primitive spheres are acceptable only for behavior tests, not crown-jewel visuals (`playcanvas-crown-jewel-research.md` lines 238-266). Current PlayCanvas balloons are sphere body/neck/knot primitives (`main-event-playground.js` lines 426-444) with simple specular materials (`main-event-playground.js` lines 644-679). Good construction cue, not customer-ready latex.

16. **The PlayCanvas stage still reads like a developer grid.** The visual standard says the stage should feel like a venue surface, not a developer grid (`playcanvas-crown-jewel-research.md` lines 248-256). Current level rendering adds floor grids every 2 ft (`main-event-playground.js` lines 291-300). Keep the grid for debug or subtle scale mode, not the main brand surface.

17. **The guided SVG prototype is more brand-aligned but still diagrammatic.** It uses restrained slate/brass/berry/paper styling (`prototype/styles.css` lines 1-12), names colors clearly (`prototype/index.html` lines 51-54), and includes disclaimers (`prototype/index.html` lines 14-15). But renderer output uses circles with highlights (`prototype/js/renderer-svg.js` lines 42-58), so it communicates planning math more than premium event atmosphere.

18. **Open visual decisions remain unresolved.** `design-studio-visual-direction.md` lists unknowns for black/gold mode, approved color mappings, approved scale references, and mountain/territory cues (lines 51-54 and 237-243). Do not harden a final art direction until these are decided.

19. **The prototypes risk toy/card language if not restrained.** The visual direction explicitly rejects color-first framing, large rounded toy cards, and coloring-book framing (`design-studio-visual-direction.md` lines 158-160 and 205-214). Current controls are calmer than contest mockups, but the open palette/tool-button stage could drift into "coloring game" unless copy and hierarchy stay consultative.

20. **Color names are preserved, but the PlayCanvas swatches hide names visually.** The spec says color names should be shown beside swatches and in final summaries (`design-studio-visual-direction.md` lines 194-197). The guided prototype does this (`prototype/js/app.js` lines 174-199). PlayCanvas color buttons use visual swatches with `title`/`aria-label` only (`main-event-playground.js` lines 177-190), which is weaker for customer confidence and accessibility.

## 5) What to preserve

21. **Preserve the `Plan Custom Decor` positioning and disclaimers.** The prototype title and disclaimer are on-message (`prototype/index.html` lines 9-15), and the flow spec says the customer must understand this is a planning visualization, not final engineering (`plan-custom-decor-flow.md` lines 9-18 and 458-467).

22. **Preserve supplier-actionable color-name payloads.** Both visual direction and flow specs identify Locally Twisted color names as load-bearing, with hex as approximate only (`design-studio-visual-direction.md` lines 38-39 and 192-197; `plan-custom-decor-flow.md` lines 162-177). The guided prototype follows this with labeled swatches (`prototype/js/app.js` lines 174-199).

23. **Preserve construction-aware preview/payload separation.** The guided prototype shows render facts internally (`prototype/js/app.js` lines 204-218) and builds a payload; the PlayCanvas spike includes construction engines, dimensions, colors, placement, suggestions, contact handoff, and caveats (`event-playground-state.js` lines 395-455). This is the right business value.

24. **Preserve optional suggestions and pieces-considered context.** The visual direction says suggestions should feel helpful, not upsell pressure (`design-studio-visual-direction.md` lines 149-154), and the flow says skipped suggestions are sales context, not customer failure (`plan-custom-decor-flow.md` lines 224-236 and 458-467). The PlayCanvas state already tracks accepted/ignored suggestions (`event-playground-state.js` lines 381-393 and 439-442).

25. **Preserve scale cues.** Visual direction requires every customer-facing preview to include at least one scale cue after selection (`design-studio-visual-direction.md` lines 188-190). The SVG renderer includes a reference person (`prototype/js/renderer-svg.js` lines 84-95 and 222-226), and the PlayCanvas spike includes props like person, table, chair, sign, and car (`event-playground-state.js` lines 147-196).

## 6) Concrete next-version recommendations

- **Recommended UX default:** make the next customer-facing prototype a guided wizard/planning-board, not the open PlayCanvas stage. Use PlayCanvas as a hidden/demo branch until architecture gates pass.
- **Desktop:** move debug/review/payload panels out of the customer surface; lead with event context, primary piece, style/scale, named colors, then preview.
- **Mobile:** design a true bottom-sheet flow: preview visible early, one primary action per step, large touch targets, no four-column compressed tool grids, and scrollable recovery on short screens.
- **Interaction architecture:** implement the stage-root anchoring refactor, pick colliders/handles, and ray-to-stage placement before trusting drag/rotate data.
- **Visual:** keep the neutral professional shell, but replace developer grids and ball primitives with one believable 11-inch latex primitive, proper neck/knot orientation, contact compression hints, and material variants.
- **Payload:** continue storing color names, construction engines, dimensions, warnings, suggestions accepted/ignored, and planning disclaimers; keep exact pricing/engineering out.
- **Verification:** add browser checks for desktop and mobile load, no console errors, no blank canvas, no horizontal overflow, stage turn, piece move/spin, duplicate/delete, and screenshot capture before any stakeholder demo.
