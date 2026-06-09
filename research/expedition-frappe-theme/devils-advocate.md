# Devil's Advocate Challenge: Frappe v15 Theme + Approved Content
## Date: 2026-04-26

---

### Frame Challenge

**The question asked was: "How do we build a polished, mobile-responsive customer-facing website ON Frappe v15?"**

This is a constrained question. It assumes Frappe v15 is the right vehicle for the customer-facing website. The research team accepted that constraint and worked within it. Every option they evaluated was a Frappe option.

The frame should have been: "What is the right platform for LT's customer-facing website, and is Frappe v15 it?"

That reframe is not academic. It is the actual decision GL and Jeff are facing. The convergence analysis hints at it in its "Synthesis for Devil's Advocate" section but does not follow through — it names the discomfort and then continues recommending the Frappe path anyway. That is the tell. A clean convergence should not need to preemptively address its own off-ramp.

**What the frame change surfaces:** GL has now had two consecutive failed build attempts on Frappe. The convergence analysis found that no real small business runs a polished customer-facing marketing site on Frappe (only Frappe's own properties do). Every "polished Frappe site" example found was built by Frappe engineers, for Frappe. The research question was answered honestly: the ecosystem has no turnkey themes, the Page Builder is legacy, the polished path requires real CSS work. These findings, taken together, do not obviously lead to "and therefore we should keep building on Frappe." They lead to "and therefore we need to decide whether this is the right tool."

That decision was never put on the table.

---

### Convergence Challenges

| Finding | Challenge | What Changes If Wrong |
|---------|-----------|----------------------|
| **C1: Custom Frappe app + hooks.py + web_include_css is the correct baseline architecture** | All three sources agree this is the RIGHT primitive. But the codebase already HAS this architecture — and the site is still a placeholder. "Architecture exists" and "site works" are different claims. No source measured the gap between current state and "polished, browser-tested, mobile-responsive." The convergence proves architectural soundness, not build readiness. | If the gap is larger than assumed (and the two failed attempts suggest it is), the "correct architecture" conclusion provides false confidence that the next attempt will succeed where the last two failed. |
| **C2: No polished turnkey Frappe theme exists** | All three sources agree. But the convergence uses this finding to argue FOR the custom build path rather than AGAINST the platform. The conventional wisdom the team converged on is: "no themes exist, so we build it ourselves." The equally valid conclusion is: "no themes exist, so Frappe is not the right customer-facing platform." The team never examined that fork. | If "build it ourselves" is the wrong response to ecosystem thinness — if the real signal is "use a platform designed for customer-facing sites" — then six sessions of Frappe work is the wrong direction. |
| **C3: Page Builder is effectively abandoned** | Converged correctly on the failure. But the convergence says the REASON for prior failures might be solvable (Published flag? nginx Origin header? CSS cascade?). This is offered as a caveat, not as an action item. If Page Builder failures were caused by known fixable issues, they should be fixed and confirmed — not used as evidence against Page Builder. The team cannot have it both ways: either the failures were fundamental (in which case Page Builder is ruled out) or they were fixable (in which case the root cause must be found before ruling it out). | The team's go/no-go on Page Builder is based on observed failures whose root cause is explicitly unknown. If the root cause is the nginx Origin header patch that is already documented in the agency's stack-bringup recipe — a patch that must be applied on first install — then Page Builder may work fine and was never properly tested. |
| **C4: www/ Jinja pages are valid and documented** | All three sources confirmed this works. But the convergence notes that Jeff cannot self-edit www/ pages from the Desk UI, and calls it "acceptable for Phase 1" without examining what Phase 2 looks like. The content management problem is deferred, not solved. | If Jeff eventually needs to update his own homepage copy without a developer deploy, www/ pages create a permanent dependency on Cameron. For a business handoff this is a structural problem, not a Phase 2 footnote. |
| **C5: Website Theme DocType is thin and has v15 bugs** | The team converged on "don't activate a Website Theme; use web_include_css only." This is the correct choice given the conflict. But the recommendation to NOT use the Website Theme means LT's design tokens (colors, fonts) are entirely in a manually maintained CSS file that survives zero upgrade automation. The Website Theme exists precisely to give upgrade durability to brand settings. | If a Frappe upgrade breaks the lt-theme.css cascade ordering (a documented failure mode: head_html renders before Frappe's bundle, defeating equal-specificity overrides), there is no recovery path except manually debugging the cascade after every upgrade. |

---

### Overlooked Options

These are approaches NO researcher found. They are the most important section.

---

**Option A: Frappe as backend only — WordPress or Webflow as the customer-facing front**

- **What it is:** ERPNext v15 handles lead intake, inventory, invoicing, contacts, and workflow. The customer-facing marketing site and webshop-equivalent run on WordPress (with WooCommerce) or Webflow (with Stripe-direct checkout). The two systems connect via webhooks or REST API: a form submission on WordPress creates a Lead in ERPNext; a Stripe payment updates an ERPNext order record.
- **Why it was missed:** The research brief explicitly framed the constraint as "system-native first — work within Frappe." The constraint was accepted without questioning it. All three researchers searched within the Frappe ecosystem by design. The brief ruled out the most important option before the research started.
- **Why it matters:** WordPress has 10,000+ responsive themes in the $30-80 range. Webflow has a mature visual editor. Either platform can produce a polished, mobile-responsive customer-facing site in one-third the time of custom Frappe CSS work. The "polished site in the next build attempt" problem disappears. The Frappe webshop (which has its own documented problems and architectural criticism per the July 2025 community thread) is replaced by a mature commerce layer. Jeff's content self-management problem (he cannot edit www/ pages) is replaced by a WordPress or Webflow editor he CAN use.
- **The cost:** The Frappe webshop integration work done so far becomes partial rework. The webshop app, product catalog import, and cart/checkout flows would be replaced by WooCommerce or Stripe payment links. But those are not yet built — the webshop app is installed but no products are live. The switching cost is low NOW and grows with each session spent on Frappe's commerce layer.
- **How to verify:** Estimate the hours to get a polished LT homepage on WordPress vs. Frappe. The ecosystem evidence already suggests an order-of-magnitude difference. A single conversation with GL about whether the ERPNext-backend-only model satisfies Jeff's actual needs would resolve this. Jeff does not need a unified platform — he needs a site that looks professional, a way to take leads, and a way to send invoices. These requirements do not require the webshop and marketing site to live in the same codebase.

---

**Option B: Frappe Builder, tested this session in the actual Docker stack**

- **What it is:** Install Frappe Builder into the existing LT Docker environment right now. Build one page. Test whether it works with webshop installed. Resolve the routing question by observation, not speculation.
- **Why it was missed:** The convergence analysis lists Builder as "PARTIAL" — two sources recommend it, Ground Truth has no data. The recommendation leans away from Builder because the routing question is unresolved. But the resolution is a 20-minute test, not a research gap. The team treated an empirical question as a theoretical one. "We don't know if Builder coexists with webshop" is a testable claim. The team recommended against testing it.
- **Why it matters:** If Builder works cleanly alongside webshop on LT's stack, it changes the build approach significantly. Builder + LT brand CSS + legacy_source XML content could produce a polished homepage in one session. frappe.io looks professional specifically because Frappe Builder was used to build it. If that tool is available and works, the "we must hand-code everything in www/ pages" conclusion is wrong.
- **How to verify:** `bench get-app builder --branch main && bench --site frontend install-app builder`. Build a Builder page at route `/`. Check that `/all-products` still routes to webshop. Check that the Frappe asset bundle builds cleanly. This is a 20-minute test with a definitive answer.

---

**Option C: Web Page DocType with content_type="HTML" (not Page Builder)**

- **What it is:** Use the Web Page DocType but set content_type to "HTML" and write the homepage as raw HTML in `main_section_html`. This is NOT the legacy Page Builder path — it is the raw HTML path that the Web Page DocType explicitly supports. The rendered output is exactly the HTML written, wrapped in Frappe's `web.html` base template (which provides the navbar, footer, `web_include_css` CSS, and Bootstrap 4 responsive grid).
- **Why it was missed:** The team conflated "Web Page DocType" with "Page Builder content_type." These are different things. The prior failed attempt (landing.py) used content_type="Page Builder." content_type="HTML" was never attempted. The convergence analysis found all four Web Page content types in the schema (Rich Text, Markdown, HTML, Page Builder) but never examined whether the HTML content type would produce the visible, responsive output that Page Builder failed to produce.
- **Why it matters:** If `main_section_html` with content_type="HTML" renders correctly — and there is no documented reason it should not — it provides full HTML control without the custom app www/ deployment requirement, without Builder installation risk, and without Jeff losing desk-UI access entirely. The page lives in the database, editable from the ERPNext desk UI. The legacy_source XML snippets are already structured as HTML and could be directly pasted into `main_section_html`. The convergence analysis's Ground Truth section actually identifies this as the approach for the client crawl and the CTA section ("embed as main_section_html"), but never flags it as an option for the ENTIRE homepage.
- **The catch:** This approach is barely better than Page Builder for Jeff's self-service needs — he would need to edit raw HTML, which he cannot do. But for Phase 1 ("get something polished on screen"), it removes one layer of risk (Web Template rendering bugs) while keeping content in the database rather than in code.
- **How to verify:** Create a Web Page with content_type="HTML" and a small piece of markup. Open in a real browser. Verify it renders. This is a 5-minute test that no one has run.

---

**Option D: Frappe's built-in Homepage DocType (not the Web Page at route "/")**

- **What it is:** ERPNext ships a dedicated `Homepage` DocType (Website > Homepage) that is distinct from the Web Page DocType and the current "home" web page record. Ground Truth confirmed the current home_page setting is "home" — a Web Page record. But the Homepage DocType supports "Homepage Sections" with title, subtitle, CTA links, and image — a purpose-built homepage builder separate from Page Builder.
- **Why it was missed:** The Docs & Standards researcher documented its URL (https://docs.frappe.io/erpnext/user/manual/en/homepage) and listed it as an official source consulted. But none of the three researchers examined whether Homepage DocType could produce the LT homepage. The convergence analysis does not mention it at all. It fell through the gap between "research brief asks about themes" and "codebase inspection focused on Web Page."
- **Why it matters:** If the Homepage DocType has different rendering characteristics than the Web Page + Page Builder path — and it is specifically designed for homepage use — it may avoid the rendering failures the prior attempt hit. It may also provide a simpler desk-UI for Jeff to update content. Worth 10 minutes of investigation before committing to www/ pages.
- **How to verify:** Open the Homepage DocType in the running LT ERPNext instance. Set the site homepage to use it. Build one section. Check rendering in a real browser.

---

### Shared Assumptions

**Assumption 1: The current ERPNext/webshop architecture is the right foundation**

- **Evidence it's an assumption:** The research brief's first constraint is "system-native first — work WITHIN Frappe and ERPNext." This is a directive from GL, dated 2026-04-26. It was set AFTER the second build failure. It may have been set because the prior failures were caused by fighting the system (head_html + !important), not because ERPNext is the right platform for the customer-facing site.
- **What changes if wrong:** If the ERPNext webshop is replaced by a different commerce layer, the webshop app installation, catalog import, and routing all become moot. The LT project simplifies dramatically. ERPNext handles CRM, invoicing, contacts. A separate system handles the customer-facing website and checkout. This is how most mature small businesses run — Shopify + QuickBooks, for example.

**Assumption 2: Two failed build attempts indicate a "how to build" problem, not a "whether to build here" problem**

- **Evidence it's an assumption:** The convergence analysis explains both failures (head_html CSS ordering, Page Builder rendering mystery) as technique failures, not platform failures. This framing keeps the platform question closed. But each failed attempt also matches the pattern the convergence found in the ecosystem: no real small business runs a polished customer-facing marketing site on Frappe. The failures may be technique, or they may be a signal that the tool is not suited to the task.
- **What changes if wrong:** If the failures are a platform signal, the next build attempt on Frappe will fail a third time, and GL's trust will be further eroded. The cost of being wrong about this assumption is not one session — it is the relationship with GL and Jeff.

**Assumption 3: The approved legacy_source XML content is the right content for the ERPNext site**

- **Evidence it's an assumption:** The legacy_source content was built carefully, per the convergence analysis. It has WCAG-correct aria attributes, Bootstrap 5 syntax, Quiet Confidence voice. But it was built for legacy_source's website module with legacy_source's rendering assumptions. Some structures map cleanly to Frappe. Others do not — specifically the carousel (Bootstrap 4 API bug in webshop's Hero Slider), the category circles (legacy_source category IDs won't match ERPNext Item Group IDs), and the photo carousels (legacy_source ir.attachment IDs, not local files). The team treats "content is ready" as equivalent to "content can be ported." Those are not the same claim.
- **What changes if wrong:** A "direct translation" build attempt fails because the legacy_source XML structures assume legacy_source rendering primitives. The team would need a translation layer that takes longer than acknowledged.

**Assumption 4: Jeff cannot and will not update raw HTML**

- **Evidence it's an assumption:** The team concluded that Jeff cannot edit www/ pages (he would need a developer) and that this is "acceptable for Phase 1." But no one has talked to Jeff about his content management expectations. Jeff has been running his business for 28 years, updating his WordPress site himself (locallytwisted.com is on WordPress). He may be comfortable with a simple CMS, or he may expect to update his own copy. Neither has been confirmed.
- **What changes if wrong:** If Jeff expects to update his own homepage copy — as he does on WordPress — the www/ page path creates a permanent dependency on Cameron that Jeff did not sign up for. This is a handoff problem at Phase 6. The convergence analysis flags it as "long-term limitation" but does not measure its impact on the project's stated goal: "build → sell → transfer."

**Assumption 5: The Phase 1 off-ramp condition is "can Frappe produce a polished site"**

- **Evidence it's an assumption:** The research brief mentions the Phase 1 off-ramp: "if ERPNext can't deliver a polished customer-facing site, GL will pivot away from ERPNext." The team interpreted this as "we need to prove Frappe can produce a polished site." But the off-ramp condition is not just visual quality — it is whether GL and Jeff want to KEEP BUILDING on Frappe after seeing the effort required.
- **What changes if wrong:** Even if the next build attempt produces a polished homepage, Jeff may look at the complexity and ongoing maintenance burden and prefer a WordPress or Webflow site. The off-ramp has two gates: "did it look good" AND "did the process feel trustworthy." The second gate is not addressed by the convergence analysis.

---

### Strongest Challenge

**The entire recommendation optimizes for "what is technically possible on Frappe" rather than "what is right for Jeff Kimber's balloon business." Every finding the team reached — no turnkey themes, Page Builder is legacy, custom code is the path — adds development complexity to a project where two consecutive build attempts have already failed visibly. The convergence analysis correctly identifies that no real small business runs a polished customer-facing marketing site on Frappe except Frappe's own properties. That finding should trigger a platform decision. Instead, it was absorbed as local color and the custom-code path was recommended. If the most honest summary of the Frappe website ecosystem is "you build it yourself," then the correct question for GL is whether Jeff's business should be on a platform where that is not the answer.**

---

### Role-Switching: Steelman

**The strongest possible case FOR the convergence recommendation:**

The custom Frappe app + hooks.py + web_include_css + Jinja overrides + www/ pages approach is not just "what works" — it is the only option that preserves everything that has already been built. The ERPNext platform handles lead intake, invoicing, contacts, and ecommerce in a single system. Splitting the customer-facing site onto WordPress or Webflow creates TWO systems to maintain, two places where data can fail silently, two systems Jeff eventually needs to understand. The webshop is already installed. The LT app is already wired. The legacy_source XML content is translated and ready. The custom app approach adds no new dependencies, no AGPL licensing questions, no webshop routing unknowns. It is boring, stable, and transferable to Frappe Cloud as a single package.

The two prior build failures are explained by specific, correctable mistakes: (1) CSS injection at the wrong cascade layer (head_html before Frappe's bundle); (2) Page Builder rendering that was never root-caused and may have been a simple Published flag or nginx Origin header. Neither failure proves Frappe cannot produce a polished site — they prove those specific approaches were wrong. The custom app path was never actually executed correctly. The www/ Jinja page approach has never been tried on LT at all. The baseline architecture the convergence recommends is not what failed — it is what nobody tried.

The ecosystem thinness finding is uncomfortable but irrelevant if the team can execute. frappe.io looks professional. It runs on Frappe. The same code that builds frappe.io is available to LT. The gap between "no turnkey theme" and "can't build a professional site" is real CSS work, which is the same real CSS work that would be required on any platform. WordPress themes need customization too. The `lt-theme.css` already has 616 lines of LT design tokens in place. The content is ready from the legacy_source XML. The architecture is correct. The next attempt, if it starts with Step 0 (fix the !important chains, fix the navbar toggler), uses the correct content, and builds a www/index.html rather than a Page Builder record, has a legitimate chance of working.

Jeff's business will eventually need CRM, invoicing, payroll, and inventory — all of which are in ERPNext. WordPress + WooCommerce adds a commerce layer that duplicates ERPNext's native capability and adds a sync problem. The "ERPNext as backend only" model requires building and maintaining an API bridge that is itself a loud-failure surface. Every payment processed in WooCommerce that fails to create an ERPNext order is a silent failure. That is the exact failure mode the loud-failure rule exists to prevent. One integrated system is harder to theme but simpler to operate.

---

### After Switching: Do My Challenges Hold?

| Challenge | Survives Steelman? | Assessment |
|-----------|-------------------|------------|
| **Frame: should we be building customer-facing site on Frappe at all?** | Weakened but alive | The steelman makes the integration argument well. But it does not address the execution track record: two failures, both visible to GL, with a frustrated client relationship. The steelman requires believing the next attempt will succeed. That requires evidence the prior attempts did not provide. **Survives as a question that needs an honest answer with GL, not as a technical finding.** |
| **The "correct architecture" claim provides false confidence** | Weakened | The steelman correctly points out the architecture was never executed correctly. But "it has not been tried correctly" is the justification that has presumably supported each of the two failed attempts too. **Survives as a caution: state clearly what has and has not been tested, before claiming confidence.** |
| **Platform option A (WordPress/Webflow as front)** | Partially rebutted | The steelman's two-system maintenance and API bridge argument is real. Silent failure risk across a WooCommerce-to-ERPNext sync is real. But the switching cost is still low NOW because nothing is built yet in webshop. And Jeff already self-manages on WordPress. **Survives as an option that should be explicitly put to GL as a choice, not ruled out by the instance.** |
| **Option B (test Builder this session)** | Not rebutted at all | The steelman does not address Builder. The recommendation leans away from Builder because the webshop routing question is unresolved. But the resolution is a 20-minute test. The steelman's argument for stability cuts equally for and against Builder — it is an official Frappe product. **Survives fully: test Builder before ruling it out.** |
| **Option C (Web Page + HTML content type)** | Not rebutted | The steelman praises the existing architecture but never addresses whether the Web Page DocType with content_type="HTML" avoids the Page Builder rendering failure. **Survives: 5-minute test that no one has run.** |
| **Assumption: Jeff cannot edit content without a developer** | Not addressed | The steelman ignores the content-management question entirely. The "build → sell → transfer" stated goal requires Jeff to own the site after handoff. **Survives as a conversation GL needs to have with Jeff before committing to www/ pages.** |

---

### What I'd Research Next

**One more researcher: a practitioner who has actually shipped a Frappe customer-facing site for a small service business (NOT a Frappe employee).**

Every "Frappe success story" the research team found was from Frappe's own properties (frappe.io, fossunited.org) or Frappe's own employees (Suraj Shetty building FOSS United's website as a Builder demo). These are not independent third-party validations. They are the tool's creators demonstrating their own tool.

The research question that would change the recommendation: **Has anyone shipped a Frappe v15 marketing site for a non-technical service business owner and handed it off successfully?** Not "can Frappe do this in theory" — the theory has been established. "Has it happened in practice, who did it, and what did they do?"

If the answer is yes and the practitioner can be found, their approach (what they actually built, what they avoided, what surprised them) is worth more than the entire convergence analysis combined.

If the answer is no — if there is genuinely no documented case of this handoff succeeding — that is the clearest possible signal that Frappe is the wrong vehicle for the customer-facing site of a small service business.

**Specifically:** Search discuss.frappe.io for "built for client" OR "handed off" OR "non-technical owner" OR "small business" combined with "website." Look for conversations where someone is not building for themselves but building FOR a client who will take over. That use case is qualitatively different from Frappe employees building Frappe's own site.
