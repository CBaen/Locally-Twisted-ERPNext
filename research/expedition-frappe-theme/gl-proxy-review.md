## Guiding Light Proxy — Review

### For the Instance

**Overview of what was reviewed:** The full six-file expedition (research brief, Web Scout, Docs & Standards, Ground Truth, Convergence, Devil's Advocate) plus HANDOFF.md, anti-gl-patterns.md, and CLAUDE.md. The review is organized by what needs action, from most critical to least.

---

**FLAG 1 — The legacy_source server conflict is unresolved and the catalog images are probably already broken (CRITICAL)**

The Convergence (D1) identifies that Web Scout got ECONNREFUSED on `http://5.78.136.133/` while Ground Truth saw the local Docker legacy_source container running. These are two different instances of legacy_source. The convergence calls this "resolved" by naming the distinction, but the practical consequence is NOT resolved: the `catalog.json` image URLs are Hetzner-pointing (`http://5.78.136.133/web/image/product.product/{id}/image_1920?...`). If the Hetzner server is down (as Web Scout found), those 48 image URLs are already 404. Ground Truth flags this in S5 and recommends export-before-decommission, but nobody verified whether the images are currently fetchable. Before any instance declares the catalog usable, someone needs to run one test fetch against an image URL in catalog.json. If the Hetzner server is truly down, product images need to be recovered from the local legacy_source Docker stack before it is decommissioned. This is time-sensitive. If this window closes, 48 product images are gone.

**Action needed:** Fetch one catalog image URL against the Hetzner address. If 404, pivot to fetching all 48 images from the local Docker legacy_source stack immediately, before that stack is taken down.

---

**FLAG 2 — The founding year discrepancy is stated as resolved but the source of truth decision was not verified with GL**

Convergence "Approved Content" section states: "The founding year has a discrepancy: locallytwisted.com says 'Over 22 years' (≈ 2002 founding). legacy_source XML says 'since 1998' (28 years). The CLAUDE.md project brief confirms '27-year-old Utah balloon decor business' which corroborates 1998."

This is correctly resolved for the new build (use 1998). However: "22 years" on the live site is not wrong — it appears stale relative to the current date. The resolution relies on the CLAUDE.md brief, which was written based on information from GL. It is not a GL-confirmed correction in this session. Given that GL has ADHD and this is the kind of detail that can absorb incorrectly at speed, the year 1998 should be confirmed once with GL before it goes live on a public page. This is low priority but non-zero risk.

---

**FLAG 3 — The Twitter social icon conflict is marked "requires GL clarification" but is treated as resolved by the Convergence**

Convergence D2 correctly names the conflict: locallytwisted.com shows 4 icons (including Twitter); legacy_source XML shows 3 (no Twitter). The Convergence recommends using 3 icons per the legacy_source XML and then adds "Verify with GL." The recommendation is reasonable, but the resolution is not complete until GL actually confirms it. This one is specifically sensitive because: (a) the prior setup script erroneously added Twitter and this is known; (b) GL would need to know that choice was made. Neither is blocking work but both should surface in the report to GL before the footer gets built.

---

**FLAG 4 — The !important chains are still in lt-theme.css and this is confirmed by Ground Truth; the HANDOFF calls this "Step 0" but it has not been done**

Ground Truth audit confirmed: 28 `!important` occurrences, lines 388-415 contain the broken data URI SVG for the navbar toggler icon, using the non-standard `utf8` encoding prefix that silently fails in real Chromium and Firefox. The lessons-learned.md documents this. The HANDOFF identifies it as Step 0 (prerequisite for any browser-visible work). The Convergence (S2) flags it as an "immediate blocker."

Despite all of this: the broken code is still in `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` as of the Ground Truth audit. No instance removed it.

The danger here is the documented GL pattern: instances describe things as "done" that are not pixel-verified in a real browser. If the next instance starts building a homepage on top of a broken navbar toggler and takes Playwright screenshots, the broken hamburger icon will not be obvious in the screenshot output but will be obvious to GL the moment they open their phone browser. This is exactly the failure mode that has burned GL twice.

Step 0 must be done and browser-verified before any new visible work begins. Not described-as-done. Browser-verified.

**Action needed:** Strip the navbar toggler data URI SVG block (lines 388-415 in lt-theme.css). Replace with an SVG file in `public/icons/` or Font Awesome `fa-bars`. Run `playwright_home_screenshot.py` at 375px mobile width. Read the screenshot output and describe specifically what the hamburger icon looks like. Only then proceed to homepage build.

---

**FLAG 5 — No Jinja template overrides exist yet; HANDOFF treats this as "the path forward" but it is a plan, not an implementation**

Ground Truth (S3) confirmed: the `locally_twisted` app has no `templates/` directory. The footer that currently renders is Frappe's default. The header is Frappe's default. The HANDOFF describes overriding the Jinja partials as the Slice 2 redo path and frames it as the unblocked plan.

The gap: this is a significant piece of work that has never been attempted in this project. There are no prior attempts to learn from, no screenshots of an in-progress version, no confirmation that the override mechanism actually works in the current Docker setup. The HANDOFF reads confidently about what to do — but that confidence is based on documented Frappe architecture, not on observed behavior in the LT environment.

The convergence is honest about this (C1 notes "all three confirm this is valid; Ground Truth confirms none exist yet"). But the transition from "valid per documentation" to "works in our Docker stack" requires a verification step that no one has taken. Before GL is shown a footer or header built via Jinja override, someone needs to confirm the override path resolves correctly in this specific Docker container configuration.

**Action needed:** Before building the full footer, create a minimal test: place a single file at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` with a visible test string (e.g., a comment or a div with a distinctive color). Clear the cache and check whether the override resolves. If it does not, the override path needs root-causing before any real work goes into the Jinja templates.

---

**FLAG 6 — The platform question is named but not surfaced as a real decision for GL**

The Devil's Advocate makes the strongest challenge in the entire expedition: two consecutive failed build attempts on a platform where no real small business has been documented successfully running a polished customer-facing marketing site, with an ecosystem that has zero turnkey themes, where every path to a professional-looking result requires custom CSS work that a non-technical operator cannot maintain.

The Convergence synthesis notes this but routes past it: "absorbs it as local color and recommends the custom-code path." The Devil's Advocate names this as the tell.

The expedition output does not surface the platform question as a decision GL needs to make. It surfaces it as a concern and then steelmans it away.

This is a proxy concern because GL said "if ERPNext can't deliver this visual + UX bar, GL pivots away from ERPNext." That condition is exactly what the Devil's Advocate is questioning — not "can Frappe do it in theory" but "has it happened in practice, at what cost, and is that cost acceptable for a balloon business?"

The Option A alternative (ERPNext as backend only, WordPress or Webflow for the customer-facing site) is real and currently low-cost to switch to because nothing has been built in the webshop yet. Option B (test Frappe Builder in the LT Docker stack today, 20-minute test) is real and currently untested.

Before this expedition output reaches GL as "here's the plan," the platform question needs to be explicitly surfaced. Not buried in a Devil's Advocate document GL may never read. GL needs to know: two approaches have failed, the ecosystem has no turnkey themes, there is a viable alternative (WordPress front + ERPNext back), and the switch is low-cost now and high-cost in three sessions. Would GL like to make this choice consciously?

**Action needed:** The summary that reaches GL must include this as a clear, single question — not a technical implementation choice, but a direction choice. "Do you want to keep building the customer site inside ERPNext, or do you want to explore a different front door?" GL has said this question is real. Keeping it in the research archive rather than surfacing it to GL would be routing them past a decision they said they wanted to make.

---

**FLAG 7 — The "approved content" source-of-truth question appears resolved but has a live ambiguity the instance needs to confirm**

CLAUDE.md states the legacy_source XML is the canonical source for the new build. The convergence correctly applies this. However: the legacy_source XML category URLs contain legacy_source numeric IDs (`/shop/category/balloon-arches-27`, `/shop/category/organic-garlands-31`, etc.) that will not match ERPNext Item Group routes. The client crawl works. The hero copy works. The trust bar works. But the category circles and any product-linked content require mapping legacy_source slugs → ERPNext Item Group names before the content is "ready to use."

Ground Truth surfaces this but it does not appear in the convergence recommendations as a pre-build step. The next instance may treat "content is ready from legacy_source XML" as meaning everything is plug-and-play, when the links within category-touching content need a translation pass first.

**Action needed:** Before using legacy_source XML category content, map legacy_source category slugs to their corresponding ERPNext Item Group routes. This is probably a 15-minute exercise once Item Groups are configured, but it is not trivial and should not be assumed done.

---

**FLAG 8 — One factual claim pattern deserves scrutiny: the Frappe Builder AGPL assertion is single-source and has downstream implications**

Web Scout (S4 in the Convergence) states: "Frappe Builder is AGPL-3.0. Under AGPL, if software is modified and used over a network, modifications must be made available."

This is stated as fact. The AGPL license on the Builder repository is verifiable. However, the legal analysis of what it means for a client-hosted ERPNext instance is a legal interpretation, not a fact. "May technically need to be open-sourced" is hedged, but the hedge is soft enough that GL might absorb it as "this creates a legal obligation." The practical enforcement likelihood for a small balloon business is low, but the legal risk profile of AGPL for a hosted service is a specialized question that the Web Scout cannot definitively answer from training knowledge.

This is not a fabrication — the AGPL license is real. The legal interpretation downstream of it is where training-knowledge leakage risk lives. If GL and Jeff are going to evaluate Builder, they should evaluate it knowing the license is AGPL and what that means in general terms, without a specific legal claim about their obligation.

The convergence presents this correctly as single-source (S4) and uses appropriately hedged language ("may require"). The risk level here is low — but flag it anyway as "this is a legal interpretation, not a verified legal opinion."

---

**FLAG 9 — The content management / Jeff-as-editor question is deferred but is load-bearing for the build-sell-transfer goal**

Devil's Advocate Assumption 4 names this: "Jeff has been running his business for 28 years, updating his WordPress site himself. No one has talked to Jeff about his content management expectations." The CLAUDE.md project brief states the goal as "build → sell → transfer." The www/ Jinja pages path (currently the recommendation) means Jeff cannot update his own homepage copy without a developer deploy.

The convergence acknowledges this as "acceptable for Phase 1" and a "long-term limitation." The Devil's Advocate correctly notes that the convergence does not measure this against the stated transfer goal.

This is not immediately blocking Phase 1 — a placeholder or read-only homepage is fine while the site is in build. But before the team commits to a path that permanently requires Cameron's involvement for any content updates, GL needs to know that this is the trade-off being made, and whether that is acceptable for the handoff.

**Action needed:** Before the homepage approach is finalized, confirm with GL: "Jeff will not be able to update homepage copy on his own without our help. Is that acceptable for the kind of handoff we're planning?" If the answer is no, www/ pages are not the right path.

---

**No security flags found** in the research output. The expedition was research, not code production. No authentication, no secrets, no injection vectors to review.

**No time estimates found** in the research output. The expedition correctly avoids time anchors.

**Vocabulary check — passed.** No conflation of "users" (humans using the LT software) with lineage terminology.

---

### For Guiding Light

Here is what I found after looking at the research your team produced. Three things matter most.

First: the work the team put in was thorough. They went looking for ready-made tools that could give the LT website a polished look without building everything by hand — and they came back with an honest answer: those tools don't really exist for Frappe. The ecosystem is more like a frame shop that sells raw frames but no finished paintings. If the site is going to look professional, someone has to paint it. The team found this and said so, which is the right thing to do.

Second: there is a real question the team found but did not put directly in front of you. You said at the start: "if ERPNext can't deliver this, I pivot." The research found that no real small business — not a balloon company, not a restaurant, not anyone similar to Jeff — has been documented successfully running a polished customer-facing website on Frappe. Only Frappe's own employees have done it, for Frappe's own sites. That is meaningful. It does not mean it can't be done for Jeff — the team makes a good case that it can. But it does mean you have a genuine choice: keep building the public website inside ERPNext, or put a different front door on it (like WordPress or Webflow, which is what most small businesses actually use) and let ERPNext run the back office quietly behind the scenes. That switch is easy to make right now because nothing is built yet. It gets harder with every session. I want you to make that choice on purpose, not by default.

Third: before any new visible work starts, there is a known broken piece that has to be fixed first — the hamburger menu icon on mobile is using a technique that silently fails in real browsers. It has been documented and named, but no one has removed it yet. Think of it like a loose tile right at the entrance to the kitchen — the rest of the room can look beautiful, but until that tile is fixed, every test of the room includes that hazard. Your team knows it's there. It just needs to actually be removed before the next round of building, or the next time you open the site on your phone, you will see a broken icon.

The recommended action is one decision: before the next build session starts, let your team know whether you want to keep building the website inside ERPNext or explore putting a simpler front door on it. That choice shapes everything that comes next.

---

### Verdict

- [ ] CLEAR
- [x] FLAGS — 9 items need attention before this reaches GL as a plan. Most are actionable by the next instance without GL input. Two require GL input: the platform direction question (Flag 6) and the content management / handoff trade-off (Flag 9). All remaining flags are pre-build verification steps the next instance should run before declaring any work done.

**Priority order for the instance:**

1. Flag 1 — verify catalog image URLs against Hetzner; if down, export images from local legacy_source Docker now
2. Flag 4 — Step 0: strip lt-theme.css lines 388-415; verify in Playwright at 375px before any other visible work
3. Flag 5 — test the Jinja override path with a minimal file before building the full footer
4. Flag 6 — surface platform direction question to GL as a clear choice (not buried in research docs)
5. Flag 9 — confirm content management trade-off with GL before committing to www/ pages
6. Flags 2, 3, 7, 8 — lower priority; confirm with GL at natural moments; not blockers

**Note on verdict calibration:** CLEAR means "I found no flags." This verdict found nine. The expedition itself is high-quality research — the researchers were thorough, honest about gaps, and produced genuine disconfirmation searches. The flags here are about what needs to happen before this research becomes a build plan, not about the research being wrong.
