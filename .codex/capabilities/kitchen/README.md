# Kitchen

Where capabilities get figured out before they're worth formalizing. The test kitchen — try things, taste them, decide whether they go in the cookbook or the bin.

## What goes here

- Half-formed ideas. "I think this agent can do X but I haven't proven it."
- Notes from a session where something worked once but you don't know if it's reliable.
- Hypotheses about new tools, MCPs, or workflows.
- Things you're testing before you write the schema-conforming version.

## What doesn't

- Things you've used multiple times and trust. Those graduate to a layer (`ingredients/`, `recipes/`, `meals/`).
- Things that turned out not to work. **Don't delete them — move them to `failures/`** so the next contributor doesn't repeat the experiment. See [../failures/README.md](../failures/README.md).

## Format

There isn't one. Plain Markdown. Whatever notes you'd take in a notebook.

A loose convention that works:

```markdown
# Thing I'm trying

What I tried: ...
What happened: ...
What I'm not sure about: ...
Next step if I come back to this: ...
```

## Filename convention (recommended)

Prefix kitchen files with the date and time you started them: `yyyy-mm-dd-hhmm-short-name.md` (24-hour clock, no separator between hours and minutes).

Examples:
- `2026-04-25-1430-async-skill-discovery.md`
- `2026-04-25-1437-async-skill-discovery.md`  (7 minutes later, distinct iteration)
- `2026-04-26-0915-mcp-server-introspection.md`

**Why hour and minute, not just date.** Iteration on the same idea within a single session is common — you try something at 14:30, learn from it, try a variant at 14:37. Each variant deserves its own file so you can compare them later. Date alone collides; date + time doesn't.

The timestamp isn't bookkeeping — it's a forcing function. When you scan the folder later, age is visible at a glance. Files older than a few weeks without movement are candidates for **graduate, move to failures, or delete** — not "leave for later."

## Graduate, move to failures, or delete

Three equal options. All three are wins. The kitchen only works if items exit.

- **Graduate.** The idea matured. Write the schema-conforming file in the matching layer (`ingredients/`, `recipes/`, `meals/`), add it to `INDEX.md`, delete the kitchen note. Git keeps the history.
- **Move to failures.** It didn't work. Move the file to `failures/` and rewrite it in the failure schema (see [../failures/README.md](../failures/README.md) and [../SCHEMA.md](../SCHEMA.md#failure-entries-separate-schema)). The next contributor will thank you.
- **Delete.** You no longer remember the context, the underlying tool changed, or the note is moot. Just delete it. Don't agonize.

What's *not* an option: leave it sitting forever. Items that never exit turn the kitchen into a graveyard, and graveyards get ignored — which means even the useful entries stop being read.

If you can't decide between graduate, move-to-failures, or delete: that's a fourth signal — the entry has gone cold. Default to delete.

## Why a kitchen at all

Capability discovery is messy. If the only place to write things down is the formal schema, half-formed insights don't get written down — and the next instance has to rediscover them. The kitchen is the friction-free place that catches what would otherwise be lost — *as long as the exit doors stay open*.
