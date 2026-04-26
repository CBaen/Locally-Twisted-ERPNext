# Lessons Learned — Locally Twisted

**Append-only.** Newest entries at the top. Each entry: what happened, what was learned, what to do differently next time.

LT-specific patterns. Cross-client / agency-wide lessons go to `Built_by_Cameron/lessons-learned.md`. If a lesson is broadly applicable across all ERPNext builds, it ALSO goes to the global `C:\Users\baenb\.claude\lessons-learned.md`.

---

## 2026-04-26 — "Jeff doesn't know" needs more precision than the standing docs gave it

**What happened:** Inherited HANDOFF.md and CLAUDE.md framing that read, in effect, "Jeff Kimber doesn't know about the prior failed Odoo attempt; no artifact on disk should leak that." Operated under that assumption for the first part of this session. GL corrected the framing directly: Jeff knows about the Odoo attempt and has lived its failures over months of paid work. What Jeff does not yet know is that GL has decided to migrate infrastructure entirely to ERPNext. The hidden piece is the platform pivot, not the existence of the prior work.

**What was learned:**

1. **One-line summaries of trust dynamics lose load-bearing nuance.** "Jeff doesn't know about the prior Odoo attempt" is a paraphrase that erased months of paid work Jeff has been watching firsthand. A future instance reading the cleaner version might guard the wrong fact and either over-disclose (treating the prior work as something to confess) or under-disclose (acting in conversation as if Odoo never existed, which would be jarring against Jeff's actual experience).

2. **The actual operating rule (per GL 2026-04-26):** Jeff knows the Odoo work happened and watched it struggle. He does not know that GL is migrating off Odoo entirely. The platform pivot stays internal until Phase 1 (customer-facing site + storefront) is demo-ready. The recovery move is showing Jeff a working customer-facing site as the result of months of work, not announcing a do-over.

3. **Operational implication:** Phase 1's bar is not "functional." It is "visibly polished enough that Jeff's reaction is 'oh, this is real.'" The visual quality is what makes the platform pivot land as "I built you something good" rather than "I had to throw it all out." Functional-but-ugly fails the demo even if every test passes.

**Generalizable lesson:** When standing docs use "X doesn't know Y" to encode a trust-state, ask whether Y is the precise fact being protected or a paraphrase of one. Paraphrases compound: each instance restates them slightly cleaner, and over a few sessions the actual nuance is lost. For load-bearing trust dynamics, ask GL once for the precise statement and write that verbatim. Don't tidy. (This receipt also lives in project memory at `<memory>/jeff_trust_and_phase_1_demo_stakes.md` — auto-injected on session start.)

---

## 2026-04-26 — A project frame can be wrong, not just labels. Reframe early, propagate everywhere, delete the old.

**What happened:** Inherited a project framed as "Odoo → ERPNext migration." Spent half a session deepening planning artifacts on top of that framing (PROJECT.md, ROADMAP.md, queue, decisions log, HANDOFF, scripts, capability docs). Then GL revealed: there is no production Odoo — it failed in testing, never went live, Jeff doesn't know. The frame wasn't just labeled wrong; it was structurally wrong. The 10-phase ROADMAP organized work around model translations from a system that's reference material, not a system being migrated. The "stealth migration / trust damage from prior failures" Core Value referenced damage Jeff never experienced.

**What was learned:**
1. **Surface framing assumptions BEFORE building artifacts on top of them.** The first instance who built the planning machinery never asked "wait, is this even a migration?" because the standing files said it was. Cost: significant churn to undo.
2. **A wrong frame deepens its own debt.** Every artifact written under the wrong frame must either be rewritten or deleted. The cost compounds with every layer.
3. **Reframing requires deletion, not just rewriting.** Stale REQUIREMENTS.md tied to old phases. Stale `phases/01-inventory/` research from a deferred-then-renamed phase. Empty `Locally-Twisted-Frontend/` placeholder. All deleted in this session. GitHub is the archive; we store nothing unnecessary.
4. **The reframe needs a "Reference Disposition" section in CLAUDE.md** so future instances can't accidentally re-introduce the old framing by reaching into the prior dir for resources. Make it explicit: these things will be retired; future instances must NOT assume they exist.

**Generalizable lesson:** When inheriting a project, sanity-check the frame against the human's current reality before extending the planning artifacts. Three honest questions cover most cases: "Who is this FOR (and do they know what we're doing for them)?" "What is this REPLACING (vs. building from scratch)?" "What does success LOOK LIKE on demo day?" If any of the answers contradicts what the standing docs assume, stop and reframe. The cost of pausing is low; the cost of compounding the wrong frame is high.

---

## 2026-04-26 — Don't trust API silent success — verify the field landed where you think

**What happened:** Set ERPNext Website Settings.`website_theme_css` via the Frappe `set_value` API. API returned `{"message": {...}}` — looked like success. Curled the served homepage; CSS wasn't in the head. Tried again with stronger parsing; still nothing. Spent two cycles debugging "why isn't my CSS appearing" before checking the DocType field list and finding `website_theme_css` doesn't exist as a field on Website Settings. The right field is `head_html`. Frappe's set_value silently accepted the write to the non-existent field.

**Generalizable lesson:** When a write API returns success but the visible state doesn't change, before re-trying the write, **list the actual fields available on the DocType**. Don't trust field names from memory or pattern-matching. The Frappe API for inspecting a DocType: `GET /api/resource/DocType/<NAME>` returns the full schema including the field list. Spend 30 seconds checking the schema before another 5 minutes debugging the wrong field.

---

## 2026-04-26 — WebFetch failure ≠ site down. Verify with a second tool before alarming the human.

**What happened:** WebFetch tool returned `ECONNREFUSED` for `http://5.78.136.133/`. Reported to GL "the live site is DOWN." This was wrong — `curl -sI` returned HTTP 200 immediately. The WebFetch tool just doesn't handle raw-IP URLs through its proxy layer; it has nothing to do with the site's actual reachability.

**Generalizable lesson:** When a network-dependent tool fails, the failure could be the tool, the network path, the URL format, or the actual server. Reach for a second tool (curl, ping, browser screenshot) before reporting a server outage to the human. **The cost of a false-alarm-then-correction is the same anti-pattern as "report without watching" — it withdraws trust from your reporting.**

---

## 2026-04-26 — Cloudflare blocks default Python urllib User-Agent

**What happened:** First call to `https://api.together.xyz/v1/images/generations` returned HTTP 403 with Cloudflare error code 1010. Worked immediately after adding a real browser User-Agent header.

**Generalizable lesson:** When a third-party API returns 403 + Cloudflare error, the User-Agent is the first thing to check. Default urllib UA looks like `Python-urllib/3.x` and is blocked by many Cloudflare-protected APIs as a generic-bot signature. Always pass `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (or similar real-browser string) for any API call from Python.

---

## 2026-04-26 — `bench set-config host_name` is not enough — `frappe_docker` nginx rewrites the Origin header BEFORE socketio sees it

**What happened:** GL still saw `socketio_client.js:69 Error connecting to socket.io: Invalid origin` after Trellis's earlier fix. Server-side `bench --site frontend show-config` showed `host_name: http://localhost:8081` set correctly. `curl /socket.io/?EIO=4&transport=polling` returned HTTP 200 from the host. The websocket service itself was up and listening. Yet the browser kept rejecting.

**Root cause:** `frappe_docker`'s nginx config at `/etc/nginx/conf.d/frappe.conf:47` contains:
```
proxy_set_header Origin $proxy_x_forwarded_proto://frontend;
```
That line REWRITES the browser's `Origin: http://localhost:8081` header to `Origin: http://frontend` (the internal Docker service hostname) before proxying to the socketio upstream. The socketio Node service is configured with `origin: true` (echo whatever Origin you receive back as `Access-Control-Allow-Origin`). So the response comes back as `Access-Control-Allow-Origin: http://frontend` — which doesn't match the browser's actual origin → CORS rejection → "Invalid origin" surface in the JS client. **Trellis's earlier `bench set-config host_name` fix targeted the wrong layer entirely.**

**Fix (verified working):** Patch the in-container nginx config to pass through the original Origin:
```
proxy_set_header Origin $http_origin;
```
Then `nginx -s reload` (no container restart needed → no DNS cache trap).

This project ships the patch as `scripts/fix/patch_nginx_socketio_origin.py` (run via `docker cp` + `docker exec`). The patch is NOT persistent across container recreation — it edits the in-container file. For permanent fix, mount a custom `frappe.conf` via a docker-compose override.

**Verify:**
```bash
curl -sS -i "http://localhost:8081/socket.io/?EIO=4&transport=polling" -H "Origin: http://localhost:8081" | grep -i access-control-allow-origin
# Expected: Access-Control-Allow-Origin: http://localhost:8081  (matches what you sent)
```

**Why the upstream `frappe_docker` design rewrites Origin:** the assumption is TLS terminated at a load balancer in front of nginx, with consistent internal hostname `frontend`. For browser-direct localhost access (no LB, no TLS), pass-through is correct. Production deployments to Frappe Cloud won't hit this because Frappe Cloud uses its own nginx layer.

**Generalizable lesson:** When a CORS / origin error persists after the obvious config fix, check whether nginx is rewriting headers BEFORE the upstream sees them. `proxy_set_header` lines are easy to miss — but they silently override what the upstream thinks the request looks like. (Also captured in global lessons-learned 2026-04-26.)

---

## 2026-04-25 evening — Frappe socket.io throws "Invalid origin" when site is on a non-default port

**What happened:** Opened the LT ERPNext UI at `http://localhost:8081`. Browser console showed `Error connecting to socket.io: Invalid origin` and `GET /socket.io/... → 400`. Real-time UI features (notifications, live updates, multi-tab sync) silently broken.

**Root cause (incomplete — see 2026-04-26 entry above for the actual fix):** `frappe_docker`'s `pwd.yml` brings the site up assuming Frappe's default port 8080. We map host port 8081→8080 inside the container for LT (so BBC and LT can both run). The `host_name` in the site's config was unset, so Frappe's `get_allowed_origins()` defaulted to something that didn't include `http://localhost:8081`. The socketio server (Node, separate container) rejects mismatched Origin headers as a CSRF defense.

**The trap that bit me on first attempt:** I restarted only the websocket container. That fixed the origin check (it re-read host_name from site config), but Docker assigned the websocket container a *new internal IP* on restart. The frontend (nginx) container had cached the OLD IP from its initial DNS resolution and kept trying to proxy `/socket.io/` to the dead address — producing **502 Bad Gateway** with `connect() failed (113: No route to host)` in nginx's error log. Restarting the websocket without restarting nginx turned an "Invalid origin / 400" symptom into a "No route to host / 502" symptom. nginx in `frappe_docker` does not use a `resolver` directive, so it never re-resolves on its own.

The compose-level `restart` (or restarting frontend + websocket together) avoids this entirely because Docker re-establishes the network and nginx re-resolves on its first proxy attempt.

**What to do for any future site spinup at non-default port:** Run the `set-config host_name` step immediately after `bench new-site` finishes, BEFORE the user touches the UI. AND apply the nginx Origin patch (per 2026-04-26 entry).

**Generalizable lesson:** in `frappe_docker` (and similar nginx + Compose stacks), restarting an upstream container without also bouncing nginx will give you a confusing 502 because nginx caches DNS at startup. Default to `docker compose restart` for the whole project, not single-container `docker restart`, when troubleshooting the data plane.

---

## 2026-04-25 — `gsd-tools commit` returns "nothing_to_commit" because the post-Write auto-commit hook beats it

**What happened:** `node gsd-tools.cjs commit "..." --files PROJECT.md` repeatedly returned `{"committed": false, "reason": "nothing_to_commit"}` even though the file was clearly new. Confused me into staging manually.

**Root cause:** This workspace has a post-Write hook that auto-commits files after the Write/Edit tool succeeds. By the time the GSD `commit` call runs, the file is already in HEAD with an "auto: Write ..." commit message. There's nothing for `gsd-tools commit` to commit.

**What to do:** When `nothing_to_commit` returns, run `git log --oneline -3` to confirm the auto-commit happened (look for `auto: Write FILENAME`). If yes, the workflow can proceed — the file IS in version control, just under a different commit message than the GSD workflow expected. The workflow's commit calls are belt-and-suspenders; the auto-hook is the suspenders.

---

## 2026-04-25 — `git status` on Windows hides freshly-staged dotfiles in the porcelain output

**What happened:** Staged `.gitignore` and `.planning/PROJECT.md` via `git add`. `git ls-files --stage` showed both files indexed with their hashes. `git status --short` and `git status` showed neither as staged — and showed all the OTHER files as untracked. Misleading.

**Root cause:** Unknown — possibly Git Bash + Windows interaction with first-commit-on-empty-repo state. The plumbing (ls-files, commit, ls-tree) was correct; only the porcelain (status) lied.

**What to do:** Trust `git ls-files --stage` and `git ls-tree -r HEAD --name-only` over `git status` when verifying first-commit state on Windows. The actual commit succeeds; status display is unreliable.

---

## 2026-04-25 — Frappe `pwd.yml` defaults to v16.15.1 image; v15 line is stable but you must pin manually

**What happened:** Cloned `frappe_docker`, expected to bring up ERPNext v15. The default `pwd.yml` pinned all 8 service images to `frappe/erpnext:v16.15.1`. Had to swap them all to `frappe/erpnext:v15.105.0` before starting.

**What to do:** When installing Frappe via `frappe_docker`, immediately edit `pwd.yml` to pin the desired tag *before* `docker compose up`. The rolling `v15` tag exists and points to the latest patch (currently `v15.105.0`), but pin to a specific patch for reproducibility — rolling tags will silently pull a newer patch on next `up`. (Also see agency-level v15-stability standing rule in `Built_by_Cameron/CLAUDE.md`.)

---

## 2026-04-25 — Frappe images are large; cache them on the first install, second site comes up in seconds

**What happened:** First `docker compose up` for a Frappe stack took several minutes (image pull, layer extraction). The second compose project for LT used the same `frappe/erpnext:v15.105.0` image and came up in 18 seconds — Docker recognized the layers and just retagged.

**What to do:** When spinning up multiple ERPNext sites locally, reuse the same image tag across compose projects. Each site gets its own volumes (named differently per project) but shares the image. This is fast and disk-efficient.

---

## 2026-04-25 — WSL2 default RAM allocation is below ERPNext's working set; bump `.wslconfig` to 8 GB before installing

**What happened:** Initial WSL2 had 1.5 GB RAM cap (set in `.wslconfig` from a prior expedition). Frappe stack runs MariaDB + Redis + web + socketio + scheduler + 2 worker queues — 1.5 GB was below ERPNext's 4 GB minimum. Visible in `docker info` as `MemTotal: ~1.47 GB`.

**What to do:** Edit `C:\Users\baenb\.wslconfig` `[wsl2]` section to `memory=8GB processors=4 swap=2GB` (the machine has 47.7 GB total — 8 GB is conservative). After edit, `wsl --shutdown` then run any docker command to wake the daemon with the new limits. Verify with `docker info | grep MemTotal`.

---

## 2026-04-25 — Frappe Cloud Sites plan is $5/mo per site, not $25-100; transfer is self-service

**What happened:** Quoted GL "$25-100/mo per client" early in a Frappe Cloud cost discussion based on bad memory of the pricing. GL was about to make decisions on bad numbers. Re-checked the actual pricing page.

**Real numbers (2026-04, verified at frappe.io/cloud/pricing):**
- **Sites plan**: starts at $5/month per site, includes custom apps, custom domain, SSH access
- **Servers plan**: starts at $20/month for the whole server, unlimited sites/benches
- **Free trial**: 14 days, no payment method

**Site transfer mechanism (verified at discuss.frappe.io/t/transfer-ownership-on-frappe-cloud/122800):** Self-service via the dashboard's Actions tab. Receiving Frappe Cloud team must exist (have GL's client create their own account first). Server-level transfer requires a support ticket; site-level does not.

**What to do:** When quoting hosting costs, verify against the live pricing page. Frappe's pricing has changed; training-data memory is unreliable. The cheap-and-transferable model is the right fit for the agency's "build → sell → transfer ownership" pattern.

---

## 2026-04-25 — When GL forbids touching one file, the boundary is the file (don't extrapolate to "GL must do the work")

**What happened:** GL said "leave odoo specific scripts and skills alone — we need to create ERPNext specific ones." I extrapolated this to "GL must be the executor of any production-touching work" and drafted a human-in-the-loop pattern where GL would paste production query results back to me. GL corrected: "the standard process is YOU preparing the script and executing it once it's been researched and built correctly."

**What to do:** When GL sets a boundary on a *file*, the boundary is on that file. Build new tooling elsewhere. The standard process — agent builds, agent tests, agent executes — still applies. Don't outsource execution to GL based on a misread of the boundary's scope.

---

## 2026-04-25 — Building infrastructure ≠ building the thing GL asked for

**What happened:** Spent significant tokens scaffolding GSD project structure (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, config), then planning Phase 1 with research + planner + checker + revision iterations + threat models + validation strategies. Two ERPNext sites running but completely empty. Zero translation from Odoo had occurred. GL: "you haven't even rebuilt the site in ERPNext?! Focus on the rebuild."

**What to do:** When GL asks for a *thing*, the score is "is the thing built yet?" not "is there a beautiful planning artifact for the thing." Set up the minimum scaffolding required to start building, then start building. The planning machinery is meant to *serve* the build, not to *be* the build. If you find yourself iterating planner-checker loops on a phase that hasn't moved one bit closer to the deliverable, stop and start doing the deliverable.

This is the global anti-pattern #2 (Drift from GL's actual ask). Receipt added to `anti-gl-patterns.md` (project-local).
