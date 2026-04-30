app_name = "locally_twisted"
app_title = "Locally Twisted"
app_publisher = "Built by Cameron"
app_description = "ERPNext customizations and theme for Locally Twisted (BBC client)"
app_email = "cameron@builtbycameron.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "locally_twisted",
# 		"logo": "/assets/locally_twisted/logo.png",
# 		"title": "Locally Twisted",
# 		"route": "/locally_twisted",
# 		"has_permission": "locally_twisted.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/locally_twisted/css/locally_twisted.css"
# app_include_js = "/assets/locally_twisted/js/locally_twisted.js"

# include js, css files in header of web template
# Brand foundation theme — sourced at apps/locally_twisted/locally_twisted/public/css/lt-theme.css
# Symlinked into sites/assets/locally_twisted/ by Frappe install-app, served by nginx.
#
# CACHE-BUST QUERY STRING — bump this on every lt-theme.css edit.
# Frappe's `web_include_css` injects a static URL; nginx serves it with
# Last-Modified / ETag, but browsers cache aggressively and often serve
# stale CSS even after a server-side update. The version param invalidates
# the browser cache for everyone, no hard-refresh required.
# Format: YYYYMMDD-N (date + edit-number-that-day).
# Receipt: 2026-04-29 — drawer overlay edit shipped server-side but old
# CSS stayed cached in GL's browser; drawer rendered inline on every page
# because the cached rules didn't have `position: fixed`.
web_include_css = "/assets/locally_twisted/css/lt-theme.css?v=20260430-4"

# Guest cart engine — overrides webshop's broken-for-guest cart functions
# at runtime, exposes window.LT_CART, and keeps cart count badges live.
# Loaded on every website page so cart actions work from anywhere.
# Cache-bust query string follows the same convention as web_include_css.
#
# lt-megamenu.js — desktop hover mega menu + mobile drawer accordion engine.
#   Replaces the inline <script> block removed from navbar.html.
#   Exposes window.LT.megamenu (init, openPanel, closePanel, closeAll)
#   and window.LT.drawer (open, close).
#
# lt-newsletter.js — footer newsletter form auto-binder + loud-failure handler.
#   Exposes window.LT.newsletter.submit(email) → Promise.
#   Auto-binds to form[data-lt-newsletter] on DOMContentLoaded.
web_include_js = [
    "/assets/locally_twisted/js/lt-guest-cart.js?v=20260429-1",
    "/assets/locally_twisted/js/lt-megamenu.js?v=20260430-1",
    "/assets/locally_twisted/js/lt-newsletter.js?v=20260430-1",
]

# Friendly-URL aliases. Frappe's www/ router doesn't auto-translate
# underscored Python module filenames into dashed URLs, so we alias
# explicitly. Python module names (used for the @whitelist API path)
# stay underscored.
website_route_rules = [
    {"from_route": "/balloon-twisting-and-face-painting",
     "to_route": "balloon_twisting_and_face_painting"},
    {"from_route": "/refund-policy",
     "to_route": "refund_policy"},
    {"from_route": "/thank-you",
     "to_route": "thank_you"},
    # Override Frappe payments' /payment-success — see www/payment_success.py
    # for why (upstream URL malformation + guest 403 on Payment Request read).
    {"from_route": "/payment-success",
     "to_route": "payment_success"},
    # Override webshop's bundled /cart — webshop's requires login, ours
    # is localStorage-backed and works for guests. Renamed to lt_cart to
    # avoid a name collision with webshop's templates/pages/cart.html
    # that was winning resolution even with the route rule in place.
    {"from_route": "/cart",
     "to_route": "lt_cart"},
    # Odoo's default contact route — the Hetzner mirror has links pointing
    # at /contactus throughout the navbar. Redirect to our /contact.
    {"from_route": "/contactus",
     "to_route": "contact"},
]

# ---------------------------------------------------------------
# Lead create cascade — auto-title + Contact dedup + auto-ack email.
# Module: locally_twisted/lead_cascade.py
# Receipts: 2026-04-29 Hetzner /book spec session.
# ---------------------------------------------------------------
doc_events = {
    "Lead": {
        "before_insert": "locally_twisted.lead_cascade.before_insert",
        "after_insert": "locally_twisted.lead_cascade.after_insert",
    },
}

# ---------------------------------------------------------------
# Website context — inject Shop categories into the navbar template
# Module: locally_twisted/navbar_context.py
# Source: 2026-04-30 mega-menu build
# ---------------------------------------------------------------
update_website_context = ["locally_twisted.navbar_context.update_website_context"]

# ---------------------------------------------------------------
# Fixtures — code-owned schema records that travel with the app.
# Per BBC fixture-discipline: Item Group children + Item Attribute
# records are SEED state. At Phase 6 cutover the operator-owned
# subset gets removed from this list (per NOUPDATE-DRIFT.md, TBD).
# Receipts: 2026-04-30 catalog rebuild from live Odoo.
# ---------------------------------------------------------------
fixtures = [
    {
        "dt": "Item Group",
        "filters": [["name", "in", [
            "Shop Items",
            "Arches",
            "Columns",
            "Bouquets",
            "Get-Well Bouquets",
            "Garlands",
            "Drops",
            "Grab & Go",
            "Table Decor",
            "Stands & Easels",
            "Deliveries",
            "Seasonal & Specialty",
        ]]],
    },
    {
        "dt": "Item Attribute",
        "filters": [["name", "in", [
            "Add Bouquet",
            "Add Foil Number",
            "Add ons",
            "Arch Size",
            "Baby color",
            "Bouquet Size",
            "Color Palette",
            "Column Height",
            "Delivery Size",
            "Delivery themes",
            "Design",
            "Drop Size",
            "Easter Designs",
            "Garland Length",
            "Graduation stands",
            "Hair color",
            "LED Lights",
            "Missionary",
            "Number colors",
            "Orbz toppers",
            "Plush add ons",
            "latex colors",
            "skin color",
            "topper",
        ]]],
    },
]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "locally_twisted/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "locally_twisted/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "locally_twisted.utils.jinja_methods",
# 	"filters": "locally_twisted.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "locally_twisted.install.before_install"
# after_install = "locally_twisted.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "locally_twisted.uninstall.before_uninstall"
# after_uninstall = "locally_twisted.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "locally_twisted.utils.before_app_install"
# after_app_install = "locally_twisted.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "locally_twisted.utils.before_app_uninstall"
# after_app_uninstall = "locally_twisted.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "locally_twisted.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"locally_twisted.tasks.all"
# 	],
# 	"daily": [
# 		"locally_twisted.tasks.daily"
# 	],
# 	"hourly": [
# 		"locally_twisted.tasks.hourly"
# 	],
# 	"weekly": [
# 		"locally_twisted.tasks.weekly"
# 	],
# 	"monthly": [
# 		"locally_twisted.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "locally_twisted.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "locally_twisted.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "locally_twisted.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["locally_twisted.utils.before_request"]
# after_request = ["locally_twisted.utils.after_request"]

# Job Events
# ----------
# before_job = ["locally_twisted.utils.before_job"]
# after_job = ["locally_twisted.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"locally_twisted.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

