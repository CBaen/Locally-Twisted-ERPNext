# Capability File Schema

Every capability is one Markdown file. Filename is kebab-case. The three layers are folders.

## Frontmatter (required)

```yaml
---
name: Human-readable name
level: ingredient | recipe | meal
last_verified: YYYY-MM-DD
---
```

- **name** — what to call this when Claude references it conversationally.
- **level** — which layer it lives in. Must match the parent folder.
- **last_verified** — date the capability was last confirmed working. If older than ~90 days, treat as suspect until reverified.

## Body sections (required, in this order)

### `## What it does`
One or two sentences. Plain language. No marketing.

### `## When to reach for it`
The trigger conditions. "When you need to ___" or "If you see ___, this is the move." Specific enough that another instance can pattern-match.

### `## How to use it`
The actual instructions. Commands, code, file paths, prompts to use. Copy-pasteable where possible.

### `## What it depends on`
Links to other capability files this builds on. Ingredients link to nothing or to other ingredients. Recipes link to ingredients (and sometimes to other recipes for shared substeps). Meals link to recipes.

Format: `- [name](../ingredients/foo.md) — what role this dependency plays`

## Body sections (optional)

### `## Failure modes`
What goes wrong, what it looks like, how to recover. Capabilities without limitations rot fastest — fill this in when you know.

### `## Examples`
Worked examples. Real situations. What got done.

### `## Adapter notes`
Use only when the same capability behaves differently across agents. Keep the core capability agent-neutral, then add short subsections such as:

```markdown
### Claude Code
Use `@path` imports when this must load at session start.

### Codex
Route from `AGENTS.md` and read the detailed file on demand.
```

Do not add adapter notes when the normal `How to use it` section is enough.

## The three layers

| Layer | What it is | Example |
|---|---|---|
| **ingredient** | One tool, one command, one MCP server, or a thin combination of them. The smallest reusable unit. | `screenshot`, `gh-cli`, `ripgrep`, `web-research` (search + fetch) |
| **recipe** | A workflow with a clear start and finish. Multi-step. | `visual-debugging`, `deploy-static-site-to-cloudflare`, `set-up-stripe-checkout` |
| **meal** | An end-to-end composition of recipes. The shape of a complete piece of work. | `ship-internal-tool`, `launch-marketing-site` |

If you're not sure which layer something belongs to: drop it in `kitchen/` first. Decide later.

## Filename rules

- kebab-case, lowercase, `.md` extension.
- Folder matches `level`. A file in `recipes/` has `level: recipe`.
- One capability per file. Splitting is cheap; merging is expensive.

## What's not in the schema (on purpose)

- No tags taxonomy. Frontmatter stays small. Use the body and dependency links.
- No scoring or "quality" field. The two states are *verified recently* and *not*.
- No "author" field. Git history records that. Capabilities outlive their authors.

---

## Failure entries (separate schema)

Files in `capabilities/failures/` use a different shape because they describe what *not* to do. Same Markdown + frontmatter format, different fields and sections.

### Frontmatter (required)

```yaml
---
name: Human-readable name of the failed approach
type: failure
date_discovered: YYYY-MM-DD
---
```

### Body sections (required)

#### `## What was tried`
The approach. Concrete enough that a reader can pattern-match against their own idea.

#### `## Why it didn't work`
Root cause if known. "Don't know yet, but symptom is X" is acceptable — beats no record.

#### `## What to do instead`
The working alternative. Link to a capability file if one exists.

### Body sections (optional)

#### `## Recurrence risk`
Is this evergreen, or tied to a specific tool/version that might be fixed? Lets future readers judge whether to retest.

### Why a separate schema

Failures aren't capabilities. They don't have layers, don't compose, and don't carry "last verified" semantics — they carry "last tried." Treating them as a different shape rather than a "level: failure" capability avoids the indignity of failed approaches showing up in capability counts and recipe graphs.
