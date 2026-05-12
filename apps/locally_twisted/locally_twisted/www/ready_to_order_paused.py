"""Branded pause page for public Ready-to-Order ecommerce routes."""

no_cache = 1
sitemap = 0


def get_context(context):
    context.title = "Ready-to-order is paused | Locally Twisted"
    context.metatags = {
        "description": "Ready-to-order shopping is temporarily paused while Locally Twisted polishes product pages and checkout.",
    }
    context.page_css = PAGE_CSS
    return context


PAGE_CSS = """
.lt-ecommerce-paused {
  min-height: 58vh;
  background:
    linear-gradient(135deg, rgba(250, 247, 242, 0.98) 0%, rgba(250, 247, 242, 0.94) 58%, rgba(217, 199, 179, 0.34) 100%);
  padding: clamp(2.75rem, 8vw, 5rem) 1rem;
}
.lt-ecommerce-paused__inner {
  box-sizing: border-box;
  width: min(100%, 920px);
  margin: 0 auto;
  border: 1px solid rgba(14, 34, 64, 0.16);
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 18px 36px rgba(10, 10, 11, 0.06);
  padding: clamp(1.5rem, 5vw, 3rem);
}
.lt-ecommerce-paused__eyebrow {
  margin: 0 0 0.85rem;
  color: var(--lt-crimson);
  font-family: var(--lt-font-body);
  font-size: 0.75rem;
  font-weight: 900;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.lt-ecommerce-paused__title {
  max-width: 14ch;
  margin: 0 0 1rem;
  color: var(--lt-ink);
  font-family: var(--lt-font-heading);
  font-size: clamp(2.2rem, 8vw, 4.35rem);
  font-weight: 700;
  line-height: 0.98;
}
.lt-ecommerce-paused__copy {
  max-width: 54rem;
  margin: 0 0 1rem;
  color: var(--lt-soft-gray);
  font-family: var(--lt-font-body);
  font-size: 1rem;
  line-height: 1.6;
}
.lt-ecommerce-paused__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.35rem;
}
.lt-ecommerce-paused__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  border-radius: 3px;
  padding: 0.75rem 1.2rem;
  font-family: var(--lt-font-body);
  font-size: 0.95rem;
  font-weight: 900;
  text-decoration: none;
}
.lt-ecommerce-paused__button--primary {
  background: var(--lt-navy);
  border: 1px solid var(--lt-navy);
  color: #fff;
}
.lt-ecommerce-paused__button--primary:hover,
.lt-ecommerce-paused__button--primary:focus-visible {
  background: var(--lt-crimson);
  border-color: var(--lt-crimson);
  color: #fff;
  text-decoration: none;
}
.lt-ecommerce-paused__button--secondary {
  background: transparent;
  border: 1px solid rgba(14, 34, 64, 0.24);
  color: var(--lt-ink);
}
.lt-ecommerce-paused__button--secondary:hover,
.lt-ecommerce-paused__button--secondary:focus-visible {
  border-color: var(--lt-ink);
  color: var(--lt-ink);
  text-decoration: none;
}
.lt-ecommerce-paused__help {
  margin: 1.35rem 0 0;
  color: var(--lt-navy);
  font-family: var(--lt-font-body);
  font-size: 0.95rem;
  font-weight: 800;
  line-height: 1.45;
}
.lt-ecommerce-paused__help a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 0 0.1rem;
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 0.18em;
}
"""
