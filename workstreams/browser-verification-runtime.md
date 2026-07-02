# Browser Verification Runtime

Status: verified 2026-05-09
Owner: Codex
Scope: agent web access and browser-rendered verification for LT work

## What changed

Codex verified two separate access paths in the LT workspace:

- Public internet lookup/read access works through the `web.run` layer. It can search public pages and open/read page content.
- Silent real-browser verification works through repo-local Playwright. A headless Chromium launch loaded `https://example.org/`, read the title and H1, confirmed visible body text, and captured a `1280x720` screenshot buffer without opening a physical browser window.

The in-app Browser Use plugin path was not usable in this session because the required Node REPL JavaScript execution tool was not exposed after tool discovery. Do not claim that path works in a future session without re-testing it directly.

## Current operating rule

Use the tool that matches the evidence needed:

- Use `web.run` for current public internet facts, public page source checks, links, and citations.
- Use repo-local Playwright for rendered browser proof, screenshots, localhost checks, responsive layout, forms, checkout, menus, and JavaScript-heavy surfaces.
- Use LT's existing verifier scripts before raw one-off Playwright when a route contract exists.
- Use a visible/headed browser only when the silent path cannot reproduce the issue or when GL explicitly needs to watch.

## Verified command shape

The successful check used Node plus the installed `playwright` package from this repo, launched Chromium headless, navigated to `https://example.org/`, and inspected DOM plus screenshot bytes. No file artifact was written.

Confirmed output facts:

- launch: `Chromium bundled/default`
- title: `Example Domain`
- H1: `Example Domain`
- expected body text visible: true
- screenshot size: `1280x720`

## Use this for LT closeout

For website, shop, cart, checkout, contact, portfolio, BTFP, public-nav, security, or visual work, prefer the project gates documented in `capabilities/recipes/codex-browser-verification-surface.md` and the route-specific capability recipe. Do not use a generic page fetch as proof that a browser-rendered route works.

## Not done

- No product, route, CSS, Jinja, or ERPNext behavior changed.
- No new screenshot/output directory was created.
- No in-app Browser Use automation was proven; only its missing control-tool blocker was observed.

## Deferred Chrome Plugin Repair

2026-05-21 update: Chrome 148.0.7778.179 is installed and running, the Codex
Chrome Extension is installed/enabled in profile `Default`, and the native host
manifest at `/home/guidingl/.config/OpenAI/extension/com.openai.codexextension.json`
matches the expected extension origin. The bridge still fails before tab access
with `browser-client is not trusted`. Save this for a later session when Chrome
and Codex are logged into only the intended account/profile context, then retry
the Chrome plugin bridge before claiming extension-backed console debugging
works.
