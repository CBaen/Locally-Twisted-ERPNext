---
name: Visual Debugging
level: recipe
last_verified: 2026-04-25
---

## What it does

Lets the agent see what the user sees without asking them to describe it. Combines screen capture with image reading to close the loop on UI work.

## When to reach for it

- The user says "the button looks wrong" / "the layout is broken" / "it's not lining up."
- After making any frontend change where the result has a visual component.
- Before declaring frontend work done.

## How to use it

1. Take a screenshot using [screenshot](../ingredients/screenshot.md).
2. `Read` the resulting image file.
3. Describe what you see, name the discrepancy, propose the fix.
4. Make the change, repeat the loop until the screenshot matches the intent.

The loop is the point. One screenshot is not visual debugging — *iterating against what the screen actually shows* is.

## What it depends on

- [screenshot](../ingredients/screenshot.md) — the capture mechanism.

## Failure modes

- **Hidden state.** A screenshot shows the rendered page, not the React tree, network panel, or console. If the bug is interaction-driven, you also need devtools — see `browser-devtools-debugging` (when added).
- **The user moved the window.** A screenshot taken seconds ago may not match the current state. Take a fresh one before claiming a fix worked.

## Examples

A dashboard's stat cards were misaligned. Three rounds: screenshot → notice the right column was 8px short → grep for the grid definition → fix the gap → screenshot again → confirm. The user never had to describe what they were looking at.
