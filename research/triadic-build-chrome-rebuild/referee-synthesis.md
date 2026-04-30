# Epistemic Referee Synthesis — Phase 2.5

**Date:** 2026-04-30
**Build:** Chrome rebuild (triadic-construction-v2 Round 1)
**Reviewer verdicts:** Architect HOLD, SecOps FLAG, Execution FLAG

---

## Convergence taxonomy

### Active Agreement (multiple reviewers flagged same finding)

These are HIGH-confidence issues — independent reviewers landed on the same defect from different angles.

| Issue | Architect | Execution | Severity | Fix shape |
|---|---|---|---|---|
| Mobile drawer always-visible (CSS class mismatch) | F001 | F002 | CRITICAL | Rename class in template OR add CSS rules for the new class |
| Mobile accordions 2 & 3 dead (data-attr + querySelector singular bug) | F004 | F001 | CRITICAL | Align attribute name; fix `querySelector` → `querySelectorAll` |
| Cart badge has wrong positioning ancestor | F007 | F004 | IMPORTANT | Align class names |

### Singular but credibly evidenced

These got one reviewer's attention but are well-documented with file:line evidence.

| Source | ID | Issue | Severity | Fix shape |
|---|---|---|---|---|
| Architect | F002 | Mega trigger `<li>` class doesn't match CSS open-state rule | CRITICAL | Align class names |
| Architect | F003 | No CSS rules for `.lt-megamenu` panel class | CRITICAL | Add CSS or rename class |
| Architect | F005 | `.lt-utility-bar__*` namespace has zero CSS rules | IMPORTANT | Add CSS rules |
| Architect | F006 | Primary nav bar class name mismatch | IMPORTANT | Align class names |
| Architect | F008 | Newsletter button `__btn` vs `__button` class name | IMPORTANT | Align class names |
| Execution | F003 | `showError` uses `textContent` — strips pre-built `<a href="tel:">` child | IMPORTANT | Use innerHTML with safe-rendered tel link OR build error markup with textContent + DOM API |
| SecOps | F001 | Rate limit can be bypassed via X-Forwarded-For spoofing | IMPORTANT | Switch to `key="email"` rate limit OR strip XFF at nginx |
| SecOps | F002 | `hash(email)` not stable across restarts (PYTHONHASHSEED) | ADVISORY | Replace with `hashlib.sha256(...).hexdigest()[:16]` |
| SecOps | F003 | Esc key on /book navigates away from form (pre-existing bug, surfaced) | IMPORTANT | Add modal-open guard in book.html dismissModal |

### Orthogonal coverage (different reviewers, different territory — healthy divergence)

- Architect: structural class-name mismatches across templates ↔ CSS
- SecOps: rate-limit + hash stability + Esc-key UX bug
- Execution: control-flow tracing exposed accordion querySelector bug + tel-link strip

This is the divergence the triadic structure relies on. None of the three would have caught everything alone.

### Active Disagreement

None. Reviewers do not contradict each other anywhere. Convergence + orthogonality only.

---

## Root cause analysis

**The pattern across all 8 class-name / attribute-name findings (F001-F008 of Architect; F001, F004 of Execution) is a single coordination gap:**

- Builder Jinja wrote new templates with BEM class names of their choosing.
- Builder CSS preserved EXISTING `.lt-header__*` and `.lt-footer__*` BEM blocks (which were already in lt-theme.css from the prior 2026-04-30 session) AND added new `.lt-megamenu__*` / `.lt-footer-newsletter__*` blocks.
- Builder JS wrote selectors based on the API-contract data attributes.

The Build Brief's API Contract section specified high-level class namespaces (`lt-header__*`, `lt-footer__*`, etc.) and one specific data-attribute (`data-lt-megamenu-trigger`) but did NOT enumerate every specific class name per element.

When Builder CSS preserved existing class names from prior LT work and Builder Jinja wrote new templates without reading those existing rules carefully, the names diverged:

- Template wrote `lt-header__mobile-nav` ← → CSS expected `lt-header__mobile-nav-collapse`
- Template wrote `lt-header__mega-item` ← → CSS expected `lt-header__has-mega`
- Template wrote `lt-megamenu` ← → CSS had only `lt-header__mega` (no `.lt-megamenu` block)
- Template wrote `data-lt-accordion-trigger` ← → JS queried `data-lt-drawer-accordion-trigger`
- Template wrote `lt-utility-bar__cart` ← → CSS positioned via `lt-header__util-link--cart`
- Template wrote `lt-footer-newsletter__btn` ← → CSS targeted `lt-footer-newsletter__button`

The three builders independently chose different, plausible names. The Build Brief API contract was insufficient to enforce alignment. Fix Round must produce a class/attribute alignment table that Round 2 builders honor verbatim.

The remaining findings (SecOps F001, F002, F003; Execution F003) are independent of the coordination gap and need their own targeted fixes.

---

## Verdict

**FIX ROUND, not redesign.** The architecture is sound — three Hetzner-faithful chrome panels, vanilla JS engine, loud-failure newsletter, and a real DocType were all built correctly. The defects are coordination-level naming, not design-level. The pattern is well-understood, the fix is mechanical (rename class names; add the few missing CSS blocks; switch one querySelector to querySelectorAll; switch hash to sha256; fix textContent-strips-tel-link by building DOM nodes; add modal-open guard on /book Esc).

Re-validation per the skill's Selective Re-Validation rule:
- Naming alignments: NO re-validation needed (string changes only — confirms the heuristic)
- Active Agreement findings: per skill rule "Original issue was classified as Active Disagreement" triggers re-validation; Active Agreement does NOT, but for safety, re-run a single reviewer (Execution Engine, since they trace control flow) to verify the named-aligned templates render correctly.
- SecOps F001 (rate limit bypass): switching to `key="email"` (with `ip_based=False`) is a security-critical change → re-validation required. **Proxy correction 2026-04-30:** the "two-tier" framing earlier in this synthesis was mechanically wrong — Frappe's `@rate_limit` decorator combines `ip` and `key` into a single `ip:key` identity, NOT two counters. Pick ONE: Option A `@rate_limit(limit=10, seconds=3600, key="email", ip_based=False)` (email-only, accepts the "10/hr per email" enumeration trade-off as documented), OR Option B (nginx-level X-Forwarded-For strip — higher-leverage fix that protects book.py / checkout.py / btfp.py too). Builder JS picks A or B and documents.
- SecOps F003 + Execution F003: UX bugs, not security/state — single-reviewer re-validation sufficient.

---

## Fix Round assignments

**Builder Jinja** — re-align class names + data attributes per the alignment table:
1. Mobile drawer aside: `lt-header__mobile-nav` → `lt-header__mobile-nav-collapse`
2. Mega menu `<li>` wrappers: `lt-header__mega-item` → `lt-header__has-mega`
3. Mega menu panel `<div>` class: `lt-megamenu` → adjust to whatever CSS has (likely `lt-header__mega` or new CSS class)
4. Accordion triggers: `data-lt-accordion-trigger` → `data-lt-drawer-accordion-trigger`
5. Utility bar cart: `lt-utility-bar__cart` → `lt-header__util-link--cart`
6. Primary nav bar wrappers: `lt-header__nav-bar` / `lt-header__nav-inner` → `lt-header__nav` / `lt-header__nav-row`
7. Newsletter button: `lt-footer-newsletter__btn` → `lt-footer-newsletter__button`

**Builder CSS** — add missing CSS blocks:
1. Add full `.lt-utility-bar__*` block (delivery truck icon, layout, link styles, cart badge container)
2. Add `.lt-megamenu` panel CSS (positioning, background, z-index, shadow) IF the Round 2 decision is to keep that class name; otherwise no addition (Builder Jinja renames to existing `.lt-header__mega`)

**Builder JS** — three fixes:
1. `lt-megamenu.js:415-436` — change `querySelector` to `querySelectorAll` and align attribute name with template (`data-lt-drawer-accordion-trigger`)
2. `lt-newsletter.js:170` — replace `div.textContent = msg` with safe DOM construction that preserves the `<a href="tel:..">` child anchor
3. `api/newsletter.py` — replace `hash(email)` with `hashlib.sha256(email.encode()).hexdigest()[:16]`; consider `@rate_limit(key="email", ...)` to defeat XFF spoofing (or document trade-off + add IP-keyed PLUS email-keyed, two-tier)

**Pre-task #6.5 — book.html /book Esc-key bug fix** (carry-over from SecOps F003):
- Add `if (modal.classList.contains('lt-book__modal--open'))` guard around `dismissModal()` call so Esc on form doesn't navigate away when modal isn't open.

---

## Re-validation plan after fix

Per the skill's Selective Re-Validation rule:
- **One reviewer (Execution Engine) re-runs** to verify naming alignment fixed the rendering paths
- **Verification phase (Phase 4)** runs Playwright screenshots of homepage at desktop + mobile to confirm visual integrity
- No full triadic re-run unless Execution surfaces new critical findings.
