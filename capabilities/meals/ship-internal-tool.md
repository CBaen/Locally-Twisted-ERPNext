---
name: Ship an Internal Tool
level: meal
last_verified: 2026-04-25
---

## What it does

Takes "I need a thing that does X for my team" from idea to deployed artifact a colleague can use without you in the room. End-to-end, opinionated, boring on purpose.

## When to reach for it

- Someone described a manual process they want automated.
- You have a clear input → output transformation but no UI yet.
- The goal is "stop doing this by hand," not "build a product."

## How to use it

1. **Name the input and output in one sentence.** If you can't, you're not ready to build. Loop until you can.
2. **Pick the thinnest viable shell.** Web form, CLI, Slack slash command, Google Sheet trigger. Reach for whichever is closest to where the user already lives.
3. **Build the transform as a pure function first.** No UI. No deployment. Just `input → output`. Test it on real data before wiring anything.
4. **Wrap the transform in the chosen shell.** Form posts to a handler, CLI parses args, Slack command hits a webhook. Keep the wrapper boring.
5. **Deploy via the matching recipe:**
   - Web form / static frontend: [deploy-static-site-to-cloudflare](../recipes/deploy-static-site-to-cloudflare.md).
   - CLI: package as a single-file binary or a `pip install`-able wheel.
   - Slack/webhook: deploy as a Cloudflare Worker or a small Fly.io app.
6. **Hand it over with a 5-line README.** What it does, how to run it, where it lives, who to ask if it breaks, where the source is.
7. **Watch one real use.** The first colleague who tries it will surface every assumption you made. Sit with them for 10 minutes the first time.

## What it depends on

- [deploy-static-site-to-cloudflare](../recipes/deploy-static-site-to-cloudflare.md) — for the web-form shell.

## Failure modes

- **You skip step 1 and start building.** The tool ends up doing three things badly instead of one thing well. Symptom: the README needs more than 5 lines.
- **You skip step 7.** The tool sits unused because nobody knows it exists or how to start. Symptom: a month later, the colleague is still doing it by hand.
- **You build a UI before the transform works.** You spend three days on the form and one hour on the actual logic. Reverse the ratio.

## Examples

Lead-routing tool for a small sales team: a Google Form posted to a Cloudflare Worker that classified the lead and dropped it into the right Notion database. Step 1 took two conversations. Steps 2–6 took an afternoon. Step 7 surfaced that "industry" needed to be a dropdown, not free text. Total elapsed: one focused day. Zero ongoing maintenance because the shell is boring.
