"""Customer-facing product quote acceptance route."""
from __future__ import annotations

import frappe

from locally_twisted.product_quote_acceptance import product_quote_acceptance_preview


no_cache = 1
sitemap = 0

SAFE_ACCEPTANCE_ERROR = (
    "Tiny snag: this quote approval link could not be opened. "
    "Please ask us for a fresh link."
)


def get_context(context):
    token = str(frappe.form_dict.get("token") or "").strip()
    context.title = "Review your quote | Locally Twisted"
    context.metatags = {
        "description": "Review and approve a Locally Twisted product quote.",
        "robots": "noindex, nofollow",
    }
    context.token = token
    context.page_css = PAGE_CSS
    context.preview = None
    context.acceptance_error = ""
    if not token:
        context.acceptance_error = (
            "Tiny snag: this quote link is missing its approval code. "
            "Please ask us for a fresh link."
        )
        return context
    try:
        context.preview = product_quote_acceptance_preview(token)
    except frappe.ValidationError as exc:
        context.acceptance_error = str(exc) or SAFE_ACCEPTANCE_ERROR
    except Exception:
        _log_unexpected_preview_error()
        context.acceptance_error = SAFE_ACCEPTANCE_ERROR
    return context


def _log_unexpected_preview_error() -> None:
    try:
        frappe.log_error(
            title="LT quote accept preview failed",
            message=frappe.get_traceback(),
        )
    except Exception:
        pass


PAGE_CSS = """
.lt-quote-accept {
  min-height: 58vh;
  background: linear-gradient(135deg, #faf7f2 0%, #fff 58%, rgba(14, 34, 64, 0.08) 100%);
  padding: clamp(2.5rem, 8vw, 5rem) 1rem;
}
.lt-quote-accept__inner {
  box-sizing: border-box;
  width: min(100%, 860px);
  margin: 0 auto;
  border: 1px solid rgba(14, 34, 64, 0.16);
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 18px 36px rgba(10, 10, 11, 0.06);
  padding: clamp(1.5rem, 5vw, 3rem);
}
.lt-quote-accept__eyebrow {
  margin: 0 0 0.75rem;
  color: var(--lt-crimson);
  font-family: var(--lt-font-body);
  font-size: 0.75rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.lt-quote-accept__title {
  margin: 0 0 1rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(2.05rem, 7vw, 4rem);
  font-weight: 700;
  line-height: 1;
}
.lt-quote-accept__copy,
.lt-quote-accept__status {
  max-width: 54rem;
  margin: 0 0 1rem;
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.6;
}
.lt-quote-accept__summary {
  display: grid;
  gap: 0.65rem;
  margin: 1.35rem 0;
  border-top: 1px solid rgba(14, 34, 64, 0.12);
  border-bottom: 1px solid rgba(14, 34, 64, 0.12);
  padding: 1rem 0;
}
.lt-quote-accept__row {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-body);
  font-size: 0.98rem;
}
.lt-quote-accept__row strong {
  color: var(--lt-navy);
}
.lt-quote-accept__form {
  display: grid;
  gap: 0.85rem;
  margin-top: 1.35rem;
}
.lt-quote-accept__field {
  display: grid;
  gap: 0.35rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-body);
  font-size: 0.95rem;
  font-weight: 800;
}
.lt-quote-accept__field input,
.lt-quote-accept__field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid rgba(14, 34, 64, 0.24);
  border-radius: 3px;
  padding: 0.8rem 0.9rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-body);
  font-size: 1rem;
}
.lt-quote-accept__button {
  width: fit-content;
  min-height: 44px;
  border: 1px solid var(--lt-navy);
  border-radius: 3px;
  background: var(--lt-navy);
  color: #fff;
  padding: 0.75rem 1.25rem;
  font-family: var(--lt-font-body);
  font-size: 0.95rem;
  font-weight: 900;
}
.lt-quote-accept__button:hover,
.lt-quote-accept__button:focus-visible {
  background: var(--lt-crimson);
  border-color: var(--lt-crimson);
}
.lt-quote-accept__button[disabled] {
  opacity: 0.65;
}
.lt-quote-accept__error {
  border-left: 4px solid var(--lt-crimson);
  background: rgba(161, 32, 42, 0.08);
  color: var(--lt-ink);
  padding: 1rem;
}
.lt-quote-accept__success {
  display: grid;
  gap: 0.8rem;
  margin-top: 1.35rem;
  border-left: 4px solid var(--lt-brass);
  background: rgba(199, 147, 57, 0.12);
  color: var(--lt-ink);
  padding: 1rem;
}
.lt-quote-accept__success[hidden] {
  display: none;
}
.lt-quote-accept__success h2 {
  margin: 0;
  color: var(--lt-navy);
  font-family: var(--lt-font-heading);
  font-size: clamp(1.45rem, 5vw, 2.25rem);
  line-height: 1.08;
}
.lt-quote-accept__success p {
  margin: 0;
  color: var(--lt-ink);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.55;
}
"""
