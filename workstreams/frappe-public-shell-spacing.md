# Frappe Public Shell Spacing Lesson

Date: 2026-05-08
Source: Codex handoff via GL.

## Context

Locally Twisted ERPNext/Frappe v15 public pages are bootstrapped through the shared Frappe public shell. Route templates are not isolated HTML documents.

## Symptom

Some public pages show a blank strip between the site header/menu and the first hero. Other pages look flush, making the issue appear route-specific.

## Root cause

Normal public pages may be wrapped in:

```html
main.container.my-4
```

Bootstrap's `.my-4` adds vertical margin, often with `!important`. If one route has a local override and another does not, the gap appears inconsistent across routes.

## Lesson

Before fixing hero padding, inspect the rendered Frappe shell. The first visible gap may belong to the shared wrapper, not the hero, menu, or route template.

## Preferred fix

Patch shared shell spacing in app-owned CSS, scoped to the Frappe wrapper, instead of adding page-by-page hero hacks.

Example:

```css
.page-content-wrapper main.container.my-4 {
  margin-top: 0 !important;
  margin-bottom: 0 !important;
}
```

Use `!important` only when needed to beat Bootstrap utility classes that already use it.

## Cleanup

Remove stale route-local overrides once shared shell spacing owns the behavior. Otherwise one page can mask the bug while others continue failing.

## Verification

Measure rendered page, not just CSS files:

- header bottom;
- main wrapper top;
- first hero/content top;
- computed `margin-top`.

Expected:

```text
gapHeaderToMain=0
gapHeaderToHero=0
mainMarginTop=0px
```

After CSS/Jinja/controller changes, cache-bust the CSS include and clear/restart Frappe website cache.

## Product-page rebuild implication

For the product page rebuild, do not chase top spacing in the gallery/story components until the shared public shell wrapper has been inspected. The rebuilt product page should assume Frappe may add wrapper structure around route content.
