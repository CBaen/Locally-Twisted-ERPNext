"""Sync simplified Desk workspaces for Locally Twisted operators.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_backend_workspaces.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.seed import sync_crm_pipeline


OWNER_HOME = "LT Owner Home"
MANAGER_HOME = "LT Manager Home"
EMPLOYEE_HOME = "LT Employee Home"
OWNER_WORKSPACE_ROLE = "LT Owner Access"
OWNER_DEFAULT_WORKSPACE_USERS = [
    "cameron@builtbycameron.com",
    "locallytwisted@gmail.com",
]
PERSONA_DEFAULT_WORKSPACE_USERS = {
    "lt-owner-temp@example.com": OWNER_HOME,
    "lt-manager-temp@example.com": MANAGER_HOME,
    "lt-employee-temp@example.com": EMPLOYEE_HOME,
}
PLATFORM_NAMED_WORKSPACES_TO_HIDE = [
    "ERPNext Settings",
    "ERPNext Integrations",
]

BOOKING_CALENDAR = {
    "doctype": "Calendar View",
    "name": "Sales Order",
    "reference_doctype": "Sales Order",
    "subject_field": "customer_name",
    "start_date_field": "delivery_date",
    "end_date_field": "delivery_date",
    "all_day": 1,
}

DESIRED_SHORTCUTS = {
    "Booking Calendar": {
        "label": "Booking Calendar",
        "link_to": "Sales Order",
        "doc_view": "Calendar",
        "color": "Green",
    },
    "Customers": {
        "label": "Customers",
        "link_to": "Customer",
        "doc_view": "List",
        "color": "Blue",
    },
    "People to Contact": {
        "label": "People to Contact",
        "link_to": "Contact",
        "doc_view": "List",
        "color": "Grey",
    },
}

STALE_SHORTCUT_LABELS = {
    "Event Calendar": "Booking Calendar",
    "Clients & Customers": "Customers",
    "Contacts": "People to Contact",
}

WORKSPACES_TO_NORMALIZE = [
    OWNER_HOME,
    MANAGER_HOME,
    EMPLOYEE_HOME,
]

OWNER_REQUIRED_ROLES = [
    "Accounts Manager",
    "Accounts User",
    "Item Manager",
    "Newsletter Manager",
    "System Manager",
    "Website Manager",
]
OWNER_ROLE_PROFILE = "LT Owner"
MANAGER_ROLE_PROFILE = "LT Manager"
MANAGER_FORBIDDEN_ROLES = [
    "Accounts Manager",
    "Accounts User",
    "Item Manager",
    "Newsletter Manager",
    "Purchase Master Manager",
    "Sales Master Manager",
    "System Manager",
    "Website Manager",
]
STANDARD_DOCTYPE_PERMISSION_ROLE_REMOVALS = {
    "Address": {"All"},
    "Contact": {"All"},
}
OWNER_PROTECTED_USER_ROLES = {
    "cameron@builtbycameron.com": ["System Manager", "Website Manager"],
}

OWNER_NUMBER_CARDS = {
    "New Inquiries": {
        "label": "New Inquiries",
        "document_type": "Lead",
        "function": "Count",
        "filters_json": [["Lead", "custom_pipeline_stage", "=", "New Inquiry"]],
        "color": "#155e75",
        "background_color": "#ecfeff",
    },
    "Bookings": {
        "label": "Bookings",
        "document_type": "Sales Order",
        "function": "Count",
        "filters_json": [],
        "color": "#166534",
        "background_color": "#f0fdf4",
    },
    "Customers": {
        "label": "Customers",
        "document_type": "Customer",
        "function": "Count",
        "filters_json": [["Customer", "disabled", "=", 0]],
        "color": "#1d4ed8",
        "background_color": "#eff6ff",
    },
    "Overdue Follow-ups": {
        "label": "Overdue Follow-ups",
        "document_type": "Task",
        "function": "Count",
        "filters_json": [["Task", "status", "=", "Overdue"]],
        "color": "#b45309",
        "background_color": "#fffbeb",
    },
}

OWNER_DASHBOARD_CHART = {
    "chart_name": "LT Incoming Inquiries",
    "chart_type": "Count",
    "module": "Selling",
    "document_type": "Lead",
    "based_on": "creation",
    "time_interval": "Weekly",
    "timespan": "Last Quarter",
    "timeseries": 1,
    "type": "Bar",
    "is_public": 1,
    "filters_json": [],
    "dynamic_filters_json": [],
    "custom_options": {
        "axisOptions": {"shortenYAxisNumbers": 1},
        "barOptions": {"stacked": 0},
        "tooltipOptions": {},
    },
}

OWNER_HOME_SHORTCUTS = [
    {
        "label": "Call or Text",
        "type": "URL",
        "url": "/owner-actions",
        "color": "Green",
    },
    {
        "label": "Events Inquiry Inbox",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "List",
        "stats_filter": {"custom_pipeline_stage": "New Inquiry"},
        "color": "Blue",
        "format": "{} New",
    },
    {
        "label": "Inquiry Board",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "Kanban",
        "kanban_board": "LT Inquiry Board",
        "color": "Blue",
    },
    {
        "label": "Booking Calendar",
        "type": "DocType",
        "link_to": "Sales Order",
        "doc_view": "Calendar",
        "color": "Green",
    },
    {
        "label": "Bookings",
        "type": "DocType",
        "link_to": "Sales Order",
        "doc_view": "List",
        "color": "Yellow",
    },
    {
        "label": "Customers",
        "type": "DocType",
        "link_to": "Customer",
        "doc_view": "List",
        "color": "Blue",
    },
    {
        "label": "People to Contact",
        "type": "DocType",
        "link_to": "Contact",
        "doc_view": "List",
        "color": "Grey",
    },
    {
        "label": "Event Jobs",
        "type": "DocType",
        "link_to": "Project",
        "doc_view": "List",
        "stats_filter": {"status": "Open"},
        "color": "Green",
        "format": "{} Open",
    },
    {
        "label": "Task Board",
        "type": "DocType",
        "link_to": "Task",
        "doc_view": "Kanban",
        "kanban_board": "LT Task Board",
        "color": "Orange",
    },
    {
        "label": "Products",
        "type": "DocType",
        "link_to": "LT Product Blueprint",
        "doc_view": "List",
        "color": "Purple",
    },
    {
        "label": "Add Product",
        "type": "DocType",
        "link_to": "LT Product Blueprint",
        "doc_view": "New",
        "color": "Green",
    },
    {
        "label": "Product Prices",
        "type": "DocType",
        "link_to": "Item Price",
        "doc_view": "List",
        "color": "Purple",
    },
    {
        "label": "Add New Inquiry",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "New",
        "color": "Green",
    },
    {
        "label": "Add Customer",
        "type": "DocType",
        "link_to": "Customer",
        "doc_view": "New",
        "color": "Green",
    },
]

MANAGER_HOME_SHORTCUTS = [
    {
        "label": "Events Inquiry Inbox",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "List",
        "stats_filter": {"custom_pipeline_stage": "New Inquiry"},
        "color": "Blue",
        "format": "{} New",
    },
    {
        "label": "Inquiry Board",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "Kanban",
        "kanban_board": "LT Inquiry Board",
        "color": "Blue",
    },
    {
        "label": "Booking Calendar",
        "type": "DocType",
        "link_to": "Sales Order",
        "doc_view": "Calendar",
        "color": "Green",
    },
    {
        "label": "Bookings",
        "type": "DocType",
        "link_to": "Sales Order",
        "doc_view": "List",
        "color": "Yellow",
    },
    {
        "label": "Customers",
        "type": "DocType",
        "link_to": "Customer",
        "doc_view": "List",
        "color": "Blue",
    },
    {
        "label": "People to Contact",
        "type": "DocType",
        "link_to": "Contact",
        "doc_view": "List",
        "color": "Grey",
    },
    {
        "label": "Event Jobs",
        "type": "DocType",
        "link_to": "Project",
        "doc_view": "List",
        "stats_filter": {"status": "Open"},
        "color": "Green",
        "format": "{} Open",
    },
    {
        "label": "Task Board",
        "type": "DocType",
        "link_to": "Task",
        "doc_view": "Kanban",
        "kanban_board": "LT Task Board",
        "color": "Orange",
    },
    {
        "label": "Add New Inquiry",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "New",
        "color": "Green",
    },
    {
        "label": "Add Customer",
        "type": "DocType",
        "link_to": "Customer",
        "doc_view": "New",
        "color": "Green",
    },
]

EMPLOYEE_HOME_SHORTCUTS = [
    {
        "label": "My Tasks",
        "type": "DocType",
        "link_to": "Task",
        "doc_view": "List",
        "color": "Orange",
    },
    {
        "label": "Event Jobs",
        "type": "DocType",
        "link_to": "Project",
        "doc_view": "List",
        "stats_filter": {"status": "Open"},
        "color": "Green",
        "format": "{} Open",
    },
    {
        "label": "Task Board",
        "type": "DocType",
        "link_to": "Task",
        "doc_view": "Kanban",
        "kanban_board": "LT Task Board",
        "color": "Orange",
    },
]


def execute() -> str:
    summary = {
        "ensured_calendar_views": [],
        "ensured_dashboard_charts": [],
        "ensured_number_cards": [],
        "synced_crm_pipeline": {},
        "updated_role_profiles": [],
        "removed_doctype_permission_roles": [],
        "removed_role_profile_roles": [],
        "removed_user_roles": [],
        "updated_user_roles": [],
        "updated_users": [],
        "updated_workspaces": [],
        "white_label_hidden_workspaces": [],
    }
    summary["synced_crm_pipeline"] = sync_crm_pipeline.sync()
    _ensure_booking_calendar(summary)
    _ensure_owner_roles(summary)
    _prune_manager_roles(summary)
    _harden_standard_contact_permissions(summary)
    _ensure_owner_home_building_blocks(summary)
    for workspace in WORKSPACES_TO_NORMALIZE:
        _normalize_workspace(workspace, summary)
    _set_owner_home_command_center(summary)
    _set_persona_workspace(
        MANAGER_HOME,
        MANAGER_HOME_SHORTCUTS,
        _manager_home_content(),
        summary,
    )
    _set_persona_workspace(
        EMPLOYEE_HOME,
        EMPLOYEE_HOME_SHORTCUTS,
        _employee_home_content(),
        summary,
    )
    _ensure_persona_default_workspaces(summary)
    _ensure_default_owner_workspace(summary)
    _hide_platform_named_workspaces(summary)
    frappe.clear_cache()
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_booking_calendar(summary: dict) -> None:
    if frappe.db.exists("Calendar View", "Sales Order"):
        doc = frappe.get_doc("Calendar View", "Sales Order")
        changed = False
        for key, value in BOOKING_CALENDAR.items():
            if key in {"doctype", "name"}:
                continue
            if getattr(doc, key) != value:
                setattr(doc, key, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_calendar_views"].append("Sales Order")
        return

    frappe.get_doc(BOOKING_CALENDAR).insert(ignore_permissions=True)
    summary["ensured_calendar_views"].append("Sales Order")


def _ensure_owner_roles(summary: dict) -> None:
    if not frappe.db.exists("Role Profile", "LT Owner"):
        return
    doc = frappe.get_doc("Role Profile", "LT Owner")
    existing = {row.role for row in doc.roles}
    changed = False
    for role in OWNER_REQUIRED_ROLES:
        if role not in existing:
            doc.append("roles", {"role": role})
            changed = True
    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_role_profiles"].append("LT Owner")


def _prune_manager_roles(summary: dict) -> None:
    _remove_roles_from_role_profile(MANAGER_ROLE_PROFILE, MANAGER_FORBIDDEN_ROLES, summary)
    if not frappe.db.exists("Role Profile", MANAGER_ROLE_PROFILE):
        return

    users = frappe.get_all(
        "User",
        filters={"role_profile_name": MANAGER_ROLE_PROFILE},
        pluck="name",
    )
    for user_name in users:
        _remove_roles_from_user(user_name, MANAGER_FORBIDDEN_ROLES, summary)


def _remove_roles_from_role_profile(role_profile: str, roles: list[str], summary: dict) -> None:
    if not frappe.db.exists("Role Profile", role_profile):
        return

    role_set = set(roles)
    doc = frappe.get_doc("Role Profile", role_profile)
    existing = [row.role for row in doc.roles]
    removed = sorted(set(existing) & role_set)
    if not removed:
        return

    doc.set("roles", [row.as_dict() for row in doc.roles if row.role not in role_set])
    doc.save(ignore_permissions=True)
    summary["removed_role_profile_roles"].append(
        {"role_profile": role_profile, "roles": removed}
    )


def _remove_roles_from_user(user_name: str, roles: list[str], summary: dict) -> None:
    if not frappe.db.exists("User", user_name):
        return

    role_set = set(roles)
    doc = frappe.get_doc("User", user_name)
    existing = [row.role for row in doc.roles]
    removed = sorted(set(existing) & role_set)
    if not removed:
        return

    doc.set("roles", [row.as_dict() for row in doc.roles if row.role not in role_set])
    doc.save(ignore_permissions=True)
    summary["removed_user_roles"].append({"user": user_name, "roles": removed})


def _harden_standard_contact_permissions(summary: dict) -> None:
    for doctype, roles in STANDARD_DOCTYPE_PERMISSION_ROLE_REMOVALS.items():
        if not frappe.db.exists("DocType", doctype):
            continue

        rows = frappe.get_all(
            "DocPerm",
            filters={
                "parent": doctype,
                "parenttype": "DocType",
                "permlevel": 0,
                "role": ["in", sorted(roles)],
            },
            fields=["name", "role"],
        )
        if not rows:
            continue

        removed = sorted({row.role for row in rows})
        for row in rows:
            frappe.delete_doc("DocPerm", row.name, ignore_permissions=True)
        frappe.clear_cache(doctype=doctype)
        summary["removed_doctype_permission_roles"].append(
            {"doctype": doctype, "roles": removed}
        )


def _ensure_owner_home_building_blocks(summary: dict) -> None:
    for name, spec in OWNER_NUMBER_CARDS.items():
        _ensure_number_card(name, spec, summary)
    _ensure_dashboard_chart(OWNER_DASHBOARD_CHART, summary)


def _ensure_number_card(name: str, spec: dict, summary: dict) -> None:
    fields = {
        "is_standard": 0,
        "module": "Selling",
        "label": spec["label"],
        "type": "Document Type",
        "function": spec["function"],
        "document_type": spec["document_type"],
        "is_public": 1,
        "show_percentage_stats": 0,
        "filters_json": json.dumps(spec["filters_json"]),
        "dynamic_filters_json": None,
        "color": spec.get("color"),
        "background_color": spec.get("background_color"),
    }

    if frappe.db.exists("Number Card", name):
        doc = frappe.get_doc("Number Card", name)
        changed = _set_fields(doc, fields)
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_number_cards"].append(name)
        return

    doc = frappe.get_doc({"doctype": "Number Card", "name": name, **fields})
    doc.insert(ignore_permissions=True)
    summary["ensured_number_cards"].append(name)


def _ensure_dashboard_chart(spec: dict, summary: dict) -> None:
    name = spec["chart_name"]
    fields = {
        "is_standard": 0,
        "module": spec["module"],
        "chart_name": spec["chart_name"],
        "chart_type": spec["chart_type"],
        "document_type": spec["document_type"],
        "based_on": spec["based_on"],
        "time_interval": spec["time_interval"],
        "timespan": spec["timespan"],
        "timeseries": spec["timeseries"],
        "type": spec["type"],
        "is_public": spec["is_public"],
        "filters_json": json.dumps(spec["filters_json"]),
        "dynamic_filters_json": json.dumps(spec["dynamic_filters_json"]),
        "custom_options": json.dumps(spec["custom_options"]),
    }

    if frappe.db.exists("Dashboard Chart", name):
        doc = frappe.get_doc("Dashboard Chart", name)
        changed = _set_fields(doc, fields)
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_dashboard_charts"].append(name)
        return

    doc = frappe.get_doc({"doctype": "Dashboard Chart", "name": name, **fields})
    doc.insert(ignore_permissions=True)
    summary["ensured_dashboard_charts"].append(name)


def _normalize_workspace(name: str, summary: dict) -> None:
    if not frappe.db.exists("Workspace", name):
        return

    doc = frappe.get_doc("Workspace", name)
    changed = False
    changed_shortcuts: list[str] = []

    for shortcut in doc.shortcuts:
        desired_label = STALE_SHORTCUT_LABELS.get(shortcut.label, shortcut.label)
        desired = DESIRED_SHORTCUTS.get(desired_label)
        if not desired:
            continue
        for key, value in desired.items():
            if getattr(shortcut, key) != value:
                setattr(shortcut, key, value)
                changed = True
        changed_shortcuts.append(desired["label"])

    content = _load_content(doc.content)
    for block in content:
        data = block.get("data") or {}
        shortcut_name = data.get("shortcut_name")
        desired_label = STALE_SHORTCUT_LABELS.get(shortcut_name, shortcut_name)
        if desired_label in DESIRED_SHORTCUTS and shortcut_name != desired_label:
            data["shortcut_name"] = desired_label
            changed = True

    if changed:
        doc.content = json.dumps(content)
        doc.save(ignore_permissions=True)
        summary["updated_workspaces"].append(
            {"workspace": name, "shortcuts": sorted(set(changed_shortcuts))}
        )


def _set_owner_home_command_center(summary: dict) -> None:
    if not frappe.db.exists("Workspace", OWNER_HOME):
        return

    doc = frappe.get_doc("Workspace", OWNER_HOME)
    changed = False
    changed = _ensure_shortcuts(doc, OWNER_HOME_SHORTCUTS) or changed

    desired_content = _owner_home_content()
    desired_number_cards = [
        {"number_card_name": name, "label": spec["label"]}
        for name, spec in OWNER_NUMBER_CARDS.items()
    ]
    desired_charts = [
        {
            "chart_name": OWNER_DASHBOARD_CHART["chart_name"],
            "label": "Visual Pulse: Incoming Inquiries",
        }
    ]

    if _load_content(doc.content) != desired_content:
        doc.content = json.dumps(desired_content)
        changed = True

    if _child_table_rows(doc.number_cards, ["number_card_name", "label"]) != desired_number_cards:
        doc.set("number_cards", [])
        for row in desired_number_cards:
            doc.append("number_cards", row)
        changed = True

    if _child_table_rows(doc.charts, ["chart_name", "label"]) != desired_charts:
        doc.set("charts", [])
        for row in desired_charts:
            doc.append("charts", row)
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_workspaces"].append(
            {"workspace": OWNER_HOME, "layout": "command-center-with-start-here"}
        )


def _set_persona_workspace(
    workspace_name: str,
    desired_shortcuts: list[dict],
    desired_content: list[dict],
    summary: dict,
) -> None:
    if not frappe.db.exists("Workspace", workspace_name):
        return

    doc = frappe.get_doc("Workspace", workspace_name)
    changed = False
    changed = _ensure_shortcuts(doc, desired_shortcuts) or changed

    if _load_content(doc.content) != desired_content:
        doc.content = json.dumps(desired_content)
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_workspaces"].append(
            {"workspace": workspace_name, "layout": "persona-focused"}
        )


def _ensure_default_owner_workspace(summary: dict) -> None:
    if not frappe.db.exists("Workspace", OWNER_HOME):
        return

    for user_name in OWNER_DEFAULT_WORKSPACE_USERS:
        if not frappe.db.exists("User", user_name):
            continue

        doc = frappe.get_doc("User", user_name)
        changed = False

        if doc.default_workspace != OWNER_HOME:
            doc.default_workspace = OWNER_HOME
            changed = True

        if getattr(doc, "role_profile_name", None):
            doc.role_profile_name = None
            changed = True

        existing_roles = {row.role for row in doc.roles}
        desired_roles = set(_get_owner_operator_roles())
        desired_roles.update(
            role
            for role in OWNER_PROTECTED_USER_ROLES.get(user_name, [])
            if frappe.db.exists("Role", role)
        )
        for role in sorted(desired_roles):
            if role in existing_roles:
                continue

            doc.append("roles", {"role": role})
            existing_roles.add(role)
            changed = True
            summary["updated_user_roles"].append({"user": user_name, "role": role})

        if changed:
            doc.save(ignore_permissions=True)
            summary["updated_users"].append(
                {"user": user_name, "default_workspace": OWNER_HOME}
            )


def _ensure_persona_default_workspaces(summary: dict) -> None:
    for user_name, workspace_name in PERSONA_DEFAULT_WORKSPACE_USERS.items():
        if not frappe.db.exists("User", user_name):
            continue
        if not frappe.db.exists("Workspace", workspace_name):
            continue

        doc = frappe.get_doc("User", user_name)
        if doc.default_workspace == workspace_name:
            continue

        doc.default_workspace = workspace_name
        doc.save(ignore_permissions=True)
        summary["updated_users"].append(
            {"user": user_name, "default_workspace": workspace_name}
        )


def _get_owner_operator_roles() -> list[str]:
    roles = {OWNER_WORKSPACE_ROLE, *OWNER_REQUIRED_ROLES}
    if frappe.db.exists("Role Profile", OWNER_ROLE_PROFILE):
        profile = frappe.get_doc("Role Profile", OWNER_ROLE_PROFILE)
        roles.update(row.role for row in profile.roles)

    return sorted(role for role in roles if frappe.db.exists("Role", role))


def _hide_platform_named_workspaces(summary: dict) -> None:
    for workspace_name in PLATFORM_NAMED_WORKSPACES_TO_HIDE:
        if not frappe.db.exists("Workspace", workspace_name):
            continue

        doc = frappe.get_doc("Workspace", workspace_name)
        if doc.is_hidden:
            continue

        doc.is_hidden = 1
        doc.save(ignore_permissions=True)
        summary["white_label_hidden_workspaces"].append(workspace_name)


def _owner_home_content() -> list[dict]:
    blocks = [
        _header(
            "lt-owner-title",
            '<span class="h4"><b>Today at Locally Twisted</b></span>',
            12,
        ),
        _header(
            "lt-owner-subtitle",
            '<span class="text-muted">Start here: answer inquiries, check bookings, finish follow-ups, then touch products only when needed.</span>',
            12,
        ),
    ]

    for idx, card_name in enumerate(OWNER_NUMBER_CARDS, start=1):
        blocks.append(_number_card(f"lt-owner-card-{idx}", card_name, 3))

    blocks.extend(
        [
            _spacer("lt-owner-spacer-1"),
            _header(
                "lt-owner-next-title",
                '<span class="h4"><b>What Jeff does next</b></span>',
                12,
            ),
            _header(
                "lt-owner-step-1",
                '<span class="h5"><b>1. Call or text the next person</b></span><br><span class="text-muted">Open Call or Text and reach the newest people first.</span>',
                9,
            ),
            _shortcut("lt-owner-step-1-open", "Call or Text", 3),
            _header(
                "lt-owner-step-2",
                '<span class="h5"><b>2. Check upcoming bookings</b></span><br><span class="text-muted">Look at this week, confirm delivery or pickup notes, and catch surprises early.</span>',
                9,
            ),
            _shortcut("lt-owner-step-2-calendar", "Booking Calendar", 3),
            _header(
                "lt-owner-step-3",
                '<span class="h5"><b>3. Finish follow-ups</b></span><br><span class="text-muted">See tasks waiting on Jeff, the team, or a customer response.</span>',
                9,
            ),
            _shortcut("lt-owner-step-3-tasks", "Task Board", 3),
            _header(
                "lt-owner-step-4",
                '<span class="h5"><b>4. Update products only when needed</b></span><br><span class="text-muted">Catalog work stays available, but it does not compete with today\'s bookings.</span>',
                9,
            ),
            _shortcut("lt-owner-step-4-products", "Products", 3),
            _spacer("lt-owner-spacer-2"),
            _header(
                "lt-owner-pulse-title",
                '<span class="h4"><b>Visual pulse</b></span><br><span class="text-muted">Enough data to orient, not enough to bury him.</span>',
                12,
            ),
            _chart("lt-owner-inquiry-chart", OWNER_DASHBOARD_CHART["chart_name"], 12),
            _spacer("lt-owner-spacer-3"),
            _header(
                "lt-owner-fast-paths",
                '<span class="h4"><b>Fast paths</b></span>',
                12,
            ),
            _shortcut("lt-owner-fast-call-text", "Call or Text", 3),
            _shortcut("lt-owner-fast-inquiries", "Events Inquiry Inbox", 3),
            _shortcut("lt-owner-fast-calendar", "Booking Calendar", 3),
            _shortcut("lt-owner-fast-customers", "Customers", 3),
            _shortcut("lt-owner-fast-contacts", "People to Contact", 3),
            _header(
                "lt-owner-catalog-title",
                '<span class="h4"><b>Catalog tools</b></span><br><span class="text-muted">For product and pricing work after today\'s customer work is handled.</span>',
                12,
            ),
            _shortcut("lt-owner-catalog-add-product", "Add Product", 3),
            _shortcut("lt-owner-catalog-prices", "Product Prices", 3),
            _shortcut("lt-owner-catalog-add-inquiry", "Add New Inquiry", 3),
            _shortcut("lt-owner-catalog-add-customer", "Add Customer", 3),
        ]
    )
    return blocks


def _manager_home_content() -> list[dict]:
    return [
        _header(
            "lt-manager-title",
            '<span class="h4"><b>Manager Home</b></span>',
            12,
        ),
        _header(
            "lt-manager-subtitle",
            '<span class="text-muted">Keep inquiries, bookings, customers, and job follow-up moving without catalog tools.</span>',
            12,
        ),
        _header(
            "lt-manager-work-title",
            '<span class="h4"><b>Today&apos;s work</b></span>',
            12,
        ),
        _shortcut("lt-manager-inquiries", "Events Inquiry Inbox", 3),
        _shortcut("lt-manager-board", "Inquiry Board", 3),
        _shortcut("lt-manager-calendar", "Booking Calendar", 3),
        _shortcut("lt-manager-tasks", "Task Board", 3),
        _header(
            "lt-manager-records-title",
            '<span class="h4"><b>Customer and event records</b></span>',
            12,
        ),
        _shortcut("lt-manager-bookings", "Bookings", 3),
        _shortcut("lt-manager-customers", "Customers", 3),
        _shortcut("lt-manager-contacts", "People to Contact", 3),
        _shortcut("lt-manager-jobs", "Event Jobs", 3),
        _header(
            "lt-manager-add-title",
            '<span class="h4"><b>Add only what the team needs</b></span>',
            12,
        ),
        _shortcut("lt-manager-add-inquiry", "Add New Inquiry", 3),
        _shortcut("lt-manager-add-customer", "Add Customer", 3),
    ]


def _employee_home_content() -> list[dict]:
    return [
        _header(
            "lt-employee-title",
            '<span class="h4"><b>My Jobs</b></span>',
            12,
        ),
        _header(
            "lt-employee-subtitle",
            '<span class="text-muted">See assigned work and event jobs without customer, finance, or catalog administration.</span>',
            12,
        ),
        _header(
            "lt-employee-work-title",
            '<span class="h4"><b>Work to do</b></span>',
            12,
        ),
        _shortcut("lt-employee-my-tasks", "My Tasks", 3),
        _shortcut("lt-employee-task-board", "Task Board", 3),
        _shortcut("lt-employee-jobs", "Event Jobs", 3),
    ]


def _ensure_shortcuts(doc, desired_shortcuts: list[dict]) -> bool:
    fields = [
        "label",
        "type",
        "link_to",
        "url",
        "doc_view",
        "kanban_board",
        "color",
        "format",
        "report_ref_doctype",
        "stats_filter",
    ]
    desired_rows = []
    for spec in desired_shortcuts:
        row = {field: spec.get(field) for field in fields}
        if spec.get("stats_filter") is not None:
            row["stats_filter"] = json.dumps(spec["stats_filter"])
        desired_rows.append(row)

    if _child_table_rows(doc.shortcuts, fields) == desired_rows:
        return False

    doc.set("shortcuts", [])
    for row in desired_rows:
        doc.append("shortcuts", row)
    return True



def _set_fields(doc, fields: dict) -> bool:
    changed = False
    for key, value in fields.items():
        if getattr(doc, key, None) != value:
            setattr(doc, key, value)
            changed = True
    return changed


def _child_table_rows(rows, fields: list[str]) -> list[dict]:
    return [{field: getattr(row, field, None) for field in fields} for row in rows]


def _header(block_id: str, text: str, col: int) -> dict:
    return {"id": block_id, "type": "header", "data": {"text": text, "col": col}}


def _shortcut(block_id: str, shortcut_name: str, col: int) -> dict:
    return {
        "id": block_id,
        "type": "shortcut",
        "data": {"shortcut_name": shortcut_name, "col": col},
    }


def _number_card(block_id: str, number_card_name: str, col: int) -> dict:
    return {
        "id": block_id,
        "type": "number_card",
        "data": {"number_card_name": number_card_name, "col": col},
    }


def _chart(block_id: str, chart_name: str, col: int) -> dict:
    return {"id": block_id, "type": "chart", "data": {"chart_name": chart_name, "col": col}}


def _spacer(block_id: str) -> dict:
    return {"id": block_id, "type": "spacer", "data": {"col": 12}}


def _load_content(value: str | None) -> list[dict]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []
