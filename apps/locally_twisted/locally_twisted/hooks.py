app_name = "locally_twisted"
app_title = "Locally Twisted"
app_publisher = "Built by Cameron"
app_description = "Business system customizations and theme for Locally Twisted (BBC client)"
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
app_include_js = "/assets/locally_twisted/js/lt-desk-workspace-router.js?v=20260506-3"
doctype_js = {
    "Quotation": "public/js/lt-product-quote-quotation.js",
}

# include js, css files in header of web template
# Brand foundation theme â€” sourced at apps/locally_twisted/locally_twisted/public/css/lt-theme.css
# Symlinked into sites/assets/locally_twisted/ by Frappe install-app, served by nginx.
#
# CACHE-BUST QUERY STRING â€” bump this on every lt-theme.css edit.
# Frappe's `web_include_css` injects a static URL; nginx serves it with
# Last-Modified / ETag, but browsers cache aggressively and often serve
# stale CSS even after a server-side update. The version param invalidates
# the browser cache for everyone, no hard-refresh required.
# Format: YYYYMMDD-N (date + edit-number-that-day).
# Receipt: 2026-04-29 â€” drawer overlay edit shipped server-side but old
# CSS stayed cached in GL's browser; drawer rendered inline on every page
# because the cached rules didn't have `position: fixed`.
web_include_css = [
    "/assets/locally_twisted/css/lt-theme.css?v=20260510-btfp-cleanup-1",
    "/assets/locally_twisted/css/lt-mega-menu.css?v=20260511-blue-banner-2",
    "/assets/locally_twisted/css/lt-product-polish.css?v=20260510-product-runtime-1",
    "/assets/locally_twisted/css/lt-shop-showroom.css?v=20260508-card-click-1",
    "/assets/locally_twisted/css/lt-product-page-visual-first.css?v=20260510-standard-page-1",
    "/assets/locally_twisted/css/lt-page-containment.css?v=20260510-btfp-crawl-1",
    "/assets/locally_twisted/css/lt-photo-heroes.css?v=20260510-about-1",
    "/assets/locally_twisted/css/lt-form-experience.css?v=20260514-contact-required-1",
    "/assets/locally_twisted/css/lt-customer-portal.css?v=20260511-logout-1",
    "/assets/locally_twisted/css/lt-event-playground.css?v=20260506-event-playground-1",
    "/assets/locally_twisted/css/lt-audience-lane.css?v=20260512-faq-focus-1",
]

# Guest cart engine â€” overrides webshop's broken-for-guest cart functions
# at runtime, exposes window.LT_CART, and keeps cart count badges live.
# Loaded on every website page so cart actions work from anywhere.
# Cache-bust query string follows the same convention as web_include_css.
# lt-newsletter.js â€” footer newsletter form auto-binder + loud-failure handler.
#   Exposes window.LT.newsletter.submit(email) â†’ Promise.
#   Auto-binds to form[data-lt-newsletter] on DOMContentLoaded.
web_include_js = [
    "/assets/locally_twisted/js/lt-guest-cart.js?v=20260510-cart-line-key-1",
    "/assets/locally_twisted/js/lt-newsletter.js?v=20260430-2",
    "/assets/locally_twisted/js/lt-webshop-a11y.js?v=20260430-2",
    "/assets/locally_twisted/js/lt-site-preferences.js?v=20260510-form-inline-1",
    "/assets/locally_twisted/js/lt-inquiry-form-experience.js?v=20260515-form-layout-1",
    "/assets/locally_twisted/js/lt-megamenu.js?v=20260509-search-products-1",
    "/assets/locally_twisted/js/lt-product-card-click.js?v=20260508-1",
    "/assets/locally_twisted/js/lt-audience-ribbon.js?v=20260510-collab-slider-1",
]

# Friendly-URL aliases. Frappe's www/ router doesn't auto-translate
# underscored Python module filenames into dashed URLs, so we alias
# explicitly. Python module names (used for the @whitelist API path)
# stay underscored.
website_route_rules = [
    {"from_route": "/about-us",
     "to_route": "about"},
    {"from_route": "/civic-community",
     "to_route": "civic_community"},
    {"from_route": "/corporate-events",
     "to_route": "corporate_events"},
    {"from_route": "/schools-campuses",
     "to_route": "schools_campuses"},
    {"from_route": "/private-celebrations",
     "to_route": "private_celebrations"},
    {"from_route": "/event-playground",
     "to_route": "event_playground"},
    {"from_route": "/balloon-twisting-and-face-painting",
     "to_route": "balloon_twisting_and_face_painting"},
    {"from_route": "/refund-policy",
     "to_route": "refund_policy"},
    {"from_route": "/terms-of-service",
     "to_route": "terms_of_service"},
    {"from_route": "/thank-you",
     "to_route": "thank_you"},
    {"from_route": "/ready-to-order-paused",
     "to_route": "ready_to_order_paused"},
    {"from_route": "/quote-accept",
     "to_route": "quote_accept"},
    # Customer accounts use LT-owned routes, not ERPNext's native
    # quotation/order/invoice/address list pages.
    {"from_route": "/quotations",
     "to_route": "account/quotes"},
    {"from_route": "/orders",
     "to_route": "account/events"},
    {"from_route": "/invoices",
     "to_route": "account/billing"},
    {"from_route": "/addresses",
     "to_route": "account/events"},
    {"from_route": "/account/follow-up",
     "to_route": "account/follow_up"},
    # Override Frappe payments' /payment-success â€” see www/payment_success.py
    # for why (upstream URL malformation + guest 403 on Payment Request read).
    {"from_route": "/payment-success",
     "to_route": "payment_success"},
    # Override webshop's bundled /cart â€” webshop's requires login, ours
    # is localStorage-backed and works for guests. Renamed to lt_cart to
    # avoid a name collision with webshop's templates/pages/cart.html
    # that was winning resolution even with the route rule in place.
    {"from_route": "/cart",
     "to_route": "lt_cart"},
    # Odoo's default contact route â€” the Hetzner mirror has links pointing
    # at /contactus throughout the navbar. Redirect to our /contact.
    {"from_route": "/contactus",
     "to_route": "contact"},
    # ERPNext's root Item Group page and the old all-products alias are too
    # thin for customers; send root browse traffic to LT's full shop instead.
    {"from_route": "/shop-items",
     "to_route": "shop"},
    {"from_route": "/all-products",
     "to_route": "shop"},
]

# ---------------------------------------------------------------
# Lead create cascade â€” auto-title + Contact dedup + auto-ack email.
# Module: locally_twisted/lead_cascade.py
# Receipts: 2026-04-29 Hetzner /book spec session.
# ---------------------------------------------------------------
doc_events = {
    "Lead": {
        "before_insert": "locally_twisted.lead_cascade.before_insert",
        "after_insert": "locally_twisted.lead_cascade.after_insert",
        "on_update": "locally_twisted.stage_cascade.on_update",
    },
    "Email Queue": {
        "before_insert": "locally_twisted.email_delivery_guard.validate_email_queue_delivery",
    },
}

override_whitelisted_methods = {
    "webshop.webshop.api.get_product_filter_data": "locally_twisted.api.product_listing.get_product_filter_data",
}

# Shared website context for shop sidebars/footer defaults and the public mega menu.
update_website_context = [
    "locally_twisted.website_context.update_website_context",
    "locally_twisted.navbar_context.update_website_context",
]

# ---------------------------------------------------------------
# Fixtures â€” code-owned schema records that travel with the app.
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
    {
        "dt": "Custom Field",
        "filters": [["name", "in", [
            "Website Item-lt_brand_description",
            "Website Item-lt_product_details",
            "Website Item-lt_product_page_type",
            "Website Item-lt_commerce_lane",
            "Quotation-custom_lt_source_lead",
            "Quotation-custom_lt_product_template_item",
            "Quotation-custom_lt_product_page_type",
            "Quotation-custom_lt_commerce_lane",
            "Quotation-custom_lt_configuration_version",
            "Quotation-custom_lt_product_quote_summary",
            "Quotation-custom_lt_product_quote_payload",
            "Quotation-custom_lt_product_quote_status",
            "Quotation-custom_lt_quote_acceptance_token_hash",
            "Quotation-custom_lt_quote_acceptance_token_issued_on",
            "Quotation-custom_lt_quote_acceptance_token_expires_on",
            "Sales Order-custom_lt_source_quotation",
            "Sales Order-custom_lt_quote_acceptance_by",
            "Sales Order-custom_lt_quote_acceptance_email",
            "Sales Order-custom_lt_quote_acceptance_on",
            "Sales Order-custom_lt_quote_acceptance_reference",
            "Sales Order-custom_lt_quote_acceptance_payload",
            "Quotation Item-custom_lt_product_template_item",
            "Quotation Item-custom_lt_product_page_type",
            "Quotation Item-custom_lt_configuration_version",
            "Quotation Item-custom_lt_configuration_summary",
            "Quotation Item-custom_lt_configuration_json",
            "Sales Order Item-custom_lt_product_template_item",
            "Sales Order Item-custom_lt_product_page_type",
            "Sales Order Item-custom_lt_configuration_version",
            "Sales Order Item-custom_lt_configuration_summary",
            "Sales Order Item-custom_lt_configuration_json",
            "Sales Invoice Item-custom_lt_product_template_item",
            "Sales Invoice Item-custom_lt_product_page_type",
            "Sales Invoice Item-custom_lt_configuration_version",
            "Sales Invoice Item-custom_lt_configuration_summary",
            "Sales Invoice Item-custom_lt_configuration_json",
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
role_home_page = {
    "LT Marketing Review Access": "marketing-review",
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
jinja = {
    "methods": ["locally_twisted.product_options", "locally_twisted.commerce_rules"],
}

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
_marketing_sensitive_doctypes = [
    "Lead",
    "Customer",
    "Contact",
    "Address",
    "Quotation",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Communication",
    "Email Queue",
    "File",
    "Item",
    "Item Price",
    "Website Item",
    "Project",
    "Task",
    "Error Log",
    "Access Log",
    "Activity Log",
    "Version",
    "LT Maintenance Run",
    "LT Maintenance Health Event",
    "LT Maintenance Action Request",
    "LT Maintenance Action Log",
]

permission_query_conditions = {
    doctype: "locally_twisted.marketing_review_access.marketing_no_records_condition"
    for doctype in _marketing_sensitive_doctypes
}

has_permission = {
    doctype: "locally_twisted.marketing_review_access.has_marketing_sensitive_doc_permission"
    for doctype in _marketing_sensitive_doctypes
}

_marketing_mutation_block_doctypes = [
    doctype
    for doctype in _marketing_sensitive_doctypes
    if doctype not in {"Error Log", "Access Log", "Activity Log", "Version"}
]

for _marketing_sensitive_doctype in _marketing_mutation_block_doctypes:
    doc_events.setdefault(_marketing_sensitive_doctype, {})
    for _marketing_sensitive_event in ("before_insert", "before_save", "on_trash"):
        doc_events[_marketing_sensitive_doctype].setdefault(
            _marketing_sensitive_event,
            "locally_twisted.marketing_review_access.block_marketing_sensitive_doc_mutation",
        )

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

scheduler_events = {
    "hourly": [
        "locally_twisted.maintenance.heartbeat.scheduled_light_checkup",
    ],
    "daily": [
        "locally_twisted.verify.business_automation_index.scheduled_checkup",
        "locally_twisted.maintenance.heartbeat.scheduled_full_checkup",
    ],
}

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
before_request = ["locally_twisted.ecommerce_pause.before_request"]
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
