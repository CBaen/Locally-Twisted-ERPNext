from __future__ import annotations

from urllib.parse import quote

import frappe

from locally_twisted.owner_business_access import action_center_context


no_cache = 1
sitemap = 0


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = f"/login?redirect-to={quote('/owner-actions')}"
        raise frappe.Redirect
    context.show_sidebar = False
    context.hide_website_banner = True
    context.hide_website_footer = True
    context.hide_website_navbar = True
    context.no_cache = 1
    context.owner_action_center = action_center_context(limit=12)
    context.title = "Owner Actions | Locally Twisted"
    context.metatags = {
        "robots": "noindex, nofollow",
        "description": "Locally Twisted owner action center.",
    }
    context.page_css = PAGE_CSS
    return context


PAGE_CSS = """
:root {
  color-scheme: light;
}
.lt-owner-actions {
  min-height: 100vh;
  background: #f6f7f9;
  color: #16181d;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
.lt-owner-actions__shell {
  width: min(1120px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 44px;
}
.lt-owner-actions__top {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: end;
  padding: 24px 0 18px;
}
.lt-owner-actions__eyebrow {
  margin: 0 0 8px;
  color: #6b3a42;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}
.lt-owner-actions__title {
  margin: 0;
  font-size: clamp(2rem, 5vw, 4.4rem);
  line-height: 0.95;
  letter-spacing: 0;
}
.lt-owner-actions__lede {
  max-width: 680px;
  margin: 12px 0 0;
  color: #555d69;
  font-size: 1rem;
}
.lt-owner-actions__desk-link {
  display: inline-flex;
  min-height: 44px;
  align-items: center;
  justify-content: center;
  border: 1px solid #c8ced7;
  border-radius: 8px;
  padding: 0 14px;
  color: #1f2937;
  font-weight: 800;
  text-decoration: none;
  background: #ffffff;
}
.lt-owner-actions__metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 4px 0 22px;
}
.lt-owner-actions__metric {
  border: 1px solid #dfe4ea;
  border-radius: 8px;
  background: #ffffff;
  padding: 12px;
}
.lt-owner-actions__metric strong {
  display: block;
  font-size: 1.7rem;
  line-height: 1;
}
.lt-owner-actions__metric span {
  display: block;
  margin-top: 6px;
  color: #68717d;
  font-size: 0.88rem;
}
.lt-owner-actions__layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(300px, 0.75fr);
  gap: 16px;
  align-items: start;
}
.lt-owner-actions__panel {
  border: 1px solid #dfe4ea;
  border-radius: 8px;
  background: #ffffff;
  overflow: hidden;
}
.lt-owner-actions__panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid #eef1f4;
  padding: 16px;
}
.lt-owner-actions__panel-head h2 {
  margin: 0;
  font-size: 1.05rem;
}
.lt-owner-actions__panel-head span {
  color: #68717d;
  font-size: 0.88rem;
}
.lt-owner-actions__list {
  display: grid;
  gap: 0;
}
.lt-owner-actions__card {
  display: grid;
  gap: 12px;
  border-bottom: 1px solid #eef1f4;
  padding: 16px;
}
.lt-owner-actions__card:last-child {
  border-bottom: 0;
}
.lt-owner-actions__card-main {
  min-width: 0;
}
.lt-owner-actions__status {
  display: inline-flex;
  width: fit-content;
  margin-bottom: 8px;
  border-radius: 999px;
  padding: 4px 9px;
  background: #f6e7eb;
  color: #7a2130;
  font-size: 0.78rem;
  font-weight: 800;
}
.lt-owner-actions__card h3 {
  margin: 0;
  font-size: 1.12rem;
}
.lt-owner-actions__meta,
.lt-owner-actions__draft {
  margin: 6px 0 0;
  color: #56606d;
  font-size: 0.93rem;
}
.lt-owner-actions__draft {
  border-left: 3px solid #d4a017;
  padding-left: 10px;
}
.lt-owner-actions__actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}
.lt-owner-actions__button {
  display: inline-flex;
  min-height: 48px;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 1px solid #cfd6df;
  padding: 0 12px;
  text-align: center;
  color: #111827;
  font-weight: 900;
  text-decoration: none;
  background: #ffffff;
}
.lt-owner-actions__button--primary {
  border-color: #801f2f;
  color: #ffffff;
  background: #9f2638;
}
.lt-owner-actions__button--secondary {
  border-color: #2f6f5e;
  color: #ffffff;
  background: #327a67;
}
.lt-owner-actions__empty {
  margin: 0;
  padding: 18px;
  color: #68717d;
}
@media (max-width: 840px) {
  .lt-owner-actions__shell {
    width: min(100% - 20px, 620px);
    padding-top: 12px;
  }
  .lt-owner-actions__top,
  .lt-owner-actions__layout,
  .lt-owner-actions__metrics {
    grid-template-columns: 1fr;
  }
  .lt-owner-actions__actions {
    grid-template-columns: 1fr 1fr;
  }
  .lt-owner-actions__button {
    min-height: 54px;
  }
}
"""
