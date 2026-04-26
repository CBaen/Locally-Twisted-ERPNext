"""
Landing page seed for the LT site.

STATUS 2026-04-26: This script's `build()` produced a non-visible / non-responsive
page (made-up copy, broken render). It is RETIRED as a build artifact pending
the theme + content expedition. The `rollback()` function below restores the
Web Page record to a placeholder state so the broken build is not in production.

Use rollback() to clean up after the failed build:
    bench --site frontend execute locally_twisted.setup_pages.landing.rollback

The build() function is kept for historical reference but should NOT be re-run
in its current form. A new build() will be authored after the expedition's
findings are reviewed.
"""

from __future__ import annotations

import frappe


def rollback() -> None:
    """Restore the homepage Web Page to a clean placeholder state."""
    page_name = "locally-twisted"
    page = frappe.get_doc("Web Page", page_name)
    page.content_type = "Rich Text"
    page.main_section = (
        '<div style="text-align: center; padding: 4rem 1rem;">'
        '<p style="font-size: 1rem; color: #888;">Site under construction.</p>'
        "</div>"
    )
    page.page_blocks = []
    page.header = ""
    page.full_width = 0
    page.show_title = 0
    page.title = "Locally Twisted"
    page.meta_title = "Locally Twisted"
    page.meta_description = "Custom balloon decor, balloon twisting, and face painting on Utah's Wasatch Front."
    page.save(ignore_permissions=True)
    frappe.db.commit()
    print(f"Rolled back Web Page '{page_name}' to placeholder state.")
    print(f"  content_type: {page.content_type}")
    print(f"  page_blocks: {len(page.page_blocks)}")
    print(f"  header: {len(page.header)} chars")
