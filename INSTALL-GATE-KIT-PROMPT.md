---
title: Prompt — Install the Gate Kit at the LT Frappe Target
date: 2026-04-26
audience: GL — copy-paste into a fresh Opus session
---

# How to use this file

Copy everything between the BEGIN and END markers below and paste it as the first message in a fresh Opus session. The instance will install the gate kit, configure it for the LT Frappe stack, document what they did, and be able to explain it back to you.

If they finish in one session, the install is complete. If they hit a blocker, they'll surface it cleanly rather than band-aiding around it.

The prompt is self-contained. They do not need any prior context from this conversation.

---

## BEGIN PROMPT

You are an Opus instance starting a fresh session at the Locally Twisted Frappe migration target. Your task is to install the agency's portable gate kit into this client repo, configure it for the Frappe v15 / ERPNext v15.105.0 stack, document what you did, and verify the install passes the offboarding check.

**This task is bounded.** It has a clear start, a clear end, and a verification step you can run. It is not open-ended. Stay in scope.

---

## Context (read first; do not skip)

Yesterday GL completed an 8-lane retrospective expedition on two months of legacy_source work. The expedition's central finding: **documentation alone produced zero behavior change; mechanical gates held when they existed.** The expedition produced three deliverables, plus a reusable gate-kit template. Your job today is to install that template into the LT Frappe migration target.

The gates split into two categories per the architectural principle GL established:

- **`[PORTABLE]` gates** ship inside the client repo (`<repo>/scripts/`, `<repo>/.github/`, `<repo>/docs/`). They have no dependency on `~/.claude/` or any agency tooling. They travel with the codebase if Jeff (or any future contractor) ever takes the repo elsewhere.
- **`[AGENCY-ONLY]` gates** stay at `C:\Users\baenb\.claude\`. They protect Claude Code instances under task pressure; a contractor with a normal IDE doesn't have those instances and doesn't need those gates.

You are installing the portable subset today. The agency-only side already exists.

---

## Required reading before you start (in order)

Read each `[Complete]` unless size makes that impractical, in which case report `[Incomplete: lines A-B of N total]` so GL can see what you actually read.

1. `C:\Users\baenb\projects\Built_by_Cameron\AGENCY-WISDOM.md` — Part 3 specifically (The Portability Principle + the six gates). 10 minutes.
2. `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\MIGRATION-PRIORITIES.md` — full file. 15 minutes.
3. `C:\Users\baenb\projects\Built_by_Cameron\_TEMPLATES\client-repo-gate-kit\README.md` — full file. 5 minutes.
4. `C:\Users\baenb\projects\Built_by_Cameron\_TEMPLATES\client-repo-gate-kit\INSTALL.md` — full file. The step-by-step you will follow. 5 minutes.
5. `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\CLAUDE.md` — to learn the stack, site name, current state of the migration target.
6. `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\HANDOFF.md` — to understand what the prior instance(s) left.

After reading: **before any tool use that modifies files, name in plain language what you understand the gate kit to be, what it protects against, and what success looks like for this session.** This is the discipline check. If you cannot articulate the kit's purpose, re-read.

---

## Hard protocols (non-negotiable)

These are GL's two named failure modes from the retrospective. Comply with both.

1. **Completeness markers on every file you read.** `[Complete]` (you read all N lines) or `[Incomplete: lines A-B of N total]`. Track this in a Sources Read appendix at the end of any document you write. Lying about partial reads is the failure GL specifically named.

2. **Receipts before claims.** Every assertion cites file path + line range, commit hash, or other concrete receipt. No prose-only claims of "the kit does X."

Plus a third from the retrospective's load-bearing finding:

3. **Run the verification, then report.** Do not type "installed" or "configured" before observing the gate fire. The verification step that should have preceded the claim is what you run first — not the apology, not the explanation.

---

## Your task — six steps

### Step 1: Copy the kit into the LT Frappe target

```bash
# Working directory:
cd C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/

# Copy the kit (overlay; do NOT delete existing files):
cp -rn C:/Users/baenb/projects/Built_by_Cameron/_TEMPLATES/client-repo-gate-kit/scripts ./scripts
cp -rn C:/Users/baenb/projects/Built_by_Cameron/_TEMPLATES/client-repo-gate-kit/docs/framework-traps.md ./docs/framework-traps.md
cp -rn C:/Users/baenb/projects/Built_by_Cameron/_TEMPLATES/client-repo-gate-kit/docs/offboarding-check.md ./docs/offboarding-check.md
cp -rn C:/Users/baenb/projects/Built_by_Cameron/_TEMPLATES/client-repo-gate-kit/.github ./.github
```

The `-n` flag means "no clobber" — if a file already exists in the target, it is NOT overwritten. This protects any prior instance's work. If files already exist that conflict, surface them — do NOT silently skip.

After copying: list every file under `scripts/`, `docs/`, and `.github/` to confirm what landed.

### Step 2: Configure `scripts/deploy.py`

Open `scripts/deploy.py`. Find the `CONFIG` block at the top. Replace `CHANGE_ME` placeholders with the actual Frappe values for LT. You'll find them in:

- `_CLIENTS/locally-twisted/CLAUDE.md` — site name, app name, URL
- `_CLIENTS/locally-twisted/HANDOFF.md` — current Frappe state

If a value isn't documented yet (e.g., the site has no production URL yet), set it to a placeholder like `https://staging.locally-twisted.local` and add a `# TODO: update before first prod deploy` comment. Do not invent values.

### Step 3: Install Python dependencies

```bash
pip install playwright requests
playwright install chromium
```

If the LT Frappe repo has a `requirements.txt`, add `playwright>=1.40` and `requests>=2.31` there. Do NOT pin to a specific patch version — let pip resolve.

### Step 4: Run the offboarding check end-to-end

`docs/offboarding-check.md` has 10 steps. Run all of them, in order. Track outcomes in your Sources Read appendix.

A few will SKIP gracefully (e.g., schema parity if no DB access yet, smoke test if no form yet). SKIP is acceptable; SILENT FAILURE is not. Each step must produce an explicit PASS, FAIL, or SKIP outcome.

### Step 5: Document what you set up

Create `docs/GATE-KIT-INSTALL-NOTES.md` with:

- **What this is** — one paragraph in plain language. Audience: future you, or future Opus, or Jeff if he reads it.
- **What was installed** — list of files added and their purpose.
- **What was configured** — the values you set in CONFIG, with rationale for any TODO placeholders.
- **What passed / SKIPPED / failed during verification** — outcomes from Step 4, with the reason for each SKIP.
- **What is NOT yet wired** — explicit list of gaps. The booking form smoke test cannot run until the booking form exists; the schema parity check cannot run until DB access is configured; etc. Naming the gaps now prevents them from becoming silent gaps later.
- **Sources Read** appendix with completeness markers.

This file is the offboarding artifact. If GL or Jeff reads it six months from now, they should be able to understand what's there and what's pending.

### Step 6: Update HANDOFF.md and the queue

In `_CLIENTS/locally-twisted/HANDOFF.md` — append a section titled "Gate Kit Installed" with: date, what was done, what's pending, pointer to `docs/GATE-KIT-INSTALL-NOTES.md`.

In `_CLIENTS/locally-twisted/locally-twisted-queue.md` — add the unwired gates as explicit queue items (e.g., "Configure smoke_forms.py against booking form when it ships"). One queue item per gate that needs follow-up.

---

## Success criteria

The session is complete when:

- [ ] Steps 1-6 are all done
- [ ] `docs/GATE-KIT-INSTALL-NOTES.md` exists and contains a Sources Read appendix with completeness markers on every file you opened
- [ ] `python scripts/deploy.py --dry-run` exits 0 OR exits with explicit PASS/SKIP/FAIL per gate (not crashed)
- [ ] You can explain back to GL, in three sentences or fewer, what the kit protects against and what is currently unwired
- [ ] HANDOFF.md and the queue are updated

The session is NOT complete if:

- You declared "installed" without observing the gates fire
- A SKIP outcome has no documented reason
- A file was overwritten that contained prior work
- You typed "fixed" or "ready" before running the verification

If you hit a blocker — a script doesn't run, a path is wrong, a stack assumption breaks — surface it cleanly. Name it. Do not band-aid past it. The retrospective's most documented failure mode was building before reading the framework. If something feels off, read the source first.

---

## When you finish

Tell GL, in plain language:

1. What you installed (one sentence)
2. What's wired and works (one sentence)
3. What's not yet wired and what blocks each piece (one sentence per item)
4. The path to `docs/GATE-KIT-INSTALL-NOTES.md` for the long version

Do not summarize the retrospective. Do not list the six gates from memory. Stay in scope on this session's deliverable.

If GL asks "did the kit install cleanly?", the honest answer is: "All the portable files are in place. Of the four portable gates, X are runnable today, Y are SKIP-pending blocker Z, all are documented in install notes." That phrasing is honest about both what's done and what isn't.

---

## END PROMPT

---

## Notes for GL on using this prompt

- **The prompt is self-contained.** Paste it whole; don't trim. Each section earns its place in catching one failure mode the retrospective named.
- **The instance will read 6 files before acting.** If they skip the reads, they'll say so via completeness markers, and you'll see immediately. If they lie about reading, the gap will show in the install notes.
- **Expect partial completion.** Some gates can't be verified until the booking form exists or the prod URL is set up. The instance should SKIP those gracefully and document the SKIP — that's the correct outcome, not a failure.
- **If you want them to explain it back to you before doing the install** (a comprehension check), tell them at the start of the session: "Read the six required files, then explain back what the gate kit is and what success looks like, before doing any tool calls." They'll comply if asked. The prompt as written assumes they go straight to execution after reading.

---

*Generated 2026-04-26. Adapt as needed for non-LT clients — the prompt template generalizes by swapping `locally-twisted` and `Frappe` for the relevant client and stack.*
