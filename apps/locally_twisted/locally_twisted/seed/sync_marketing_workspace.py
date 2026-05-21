"""Sync LT internal marketing workspace.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_marketing_workspace.execute
"""
from __future__ import annotations

import json

import frappe


MARKETING_HOME = "LT Marketing Home"
MARKETING_HOME_TITLE = "Marketing Home"
MARKETING_ROLES = [
    "LT Owner Access",
    "Website Manager",
    "Newsletter Manager",
    "System Manager",
]
EXTERNAL_REVIEW_ROLE = "LT Marketing Review Access"

MARKETING_NUMBER_CARDS = {
    "New Inquiries": {
        "label": "New Inquiries",
        "document_type": "Lead",
        "function": "Count",
        "filters_json": [["Lead", "custom_pipeline_stage", "=", "New Inquiry"]],
    },
    "Newsletter Signups": {
        "label": "Newsletter Signups",
        "document_type": "LT Newsletter Signup",
        "function": "Count",
        "filters_json": [],
    },
    "Live Shop Items": {
        "label": "Live Shop Items",
        "document_type": "Website Item",
        "function": "Count",
        "filters_json": [["Website Item", "published", "=", 1]],
    },
    "Blog Posts": {
        "label": "Blog Posts",
        "document_type": "Blog Post",
        "function": "Count",
        "filters_json": [],
    },
}

MARKETING_SHORTCUTS = [
    {"label": "Marketing Review Page", "type": "URL", "url": "/marketing-review", "color": "Purple"},
    {"label": "Homepage", "type": "URL", "url": "/", "color": "Blue"},
    {"label": "Portfolio", "type": "URL", "url": "/portfolio", "color": "Blue"},
    {"label": "Contact Page", "type": "URL", "url": "/contact", "color": "Green"},
    {"label": "Shop", "type": "URL", "url": "/shop", "color": "Green"},
    {"label": "Web Pages", "type": "DocType", "link_to": "Web Page", "doc_view": "List", "color": "Blue"},
    {"label": "Website Items", "type": "DocType", "link_to": "Website Item", "doc_view": "List", "color": "Purple"},
    {"label": "Blog Posts", "type": "DocType", "link_to": "Blog Post", "doc_view": "List", "color": "Blue"},
    {"label": "Newsletters", "type": "DocType", "link_to": "Newsletter", "doc_view": "List", "color": "Orange"},
    {"label": "Email Groups", "type": "DocType", "link_to": "Email Group", "doc_view": "List", "color": "Grey"},
    {"label": "Campaigns", "type": "DocType", "link_to": "Campaign", "doc_view": "List", "color": "Orange"},
    {
        "label": "New Inquiries",
        "type": "DocType",
        "link_to": "Lead",
        "doc_view": "List",
        "stats_filter": {"custom_pipeline_stage": "New Inquiry"},
        "color": "Blue",
        "format": "{} New",
    },
]


def execute() -> str:
    summary = {
        "ensured_number_cards": [],
        "missing_roles": [],
        "updated_workspace": False,
    }
    for name, spec in MARKETING_NUMBER_CARDS.items():
        _ensure_number_card(name, spec, summary)
    _ensure_marketing_workspace(summary)
    frappe.clear_cache()
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_number_card(name: str, spec: dict, summary: dict) -> None:
    fields = {
        "is_standard": 0,
        "module": "Locally Twisted",
        "label": spec["label"],
        "type": "Document Type",
        "function": spec["function"],
        "document_type": spec["document_type"],
        "is_public": 1,
        "show_percentage_stats": 0,
        "filters_json": json.dumps(spec["filters_json"]),
        "dynamic_filters_json": None,
        "aggregate_function_based_on": None,
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


def _ensure_marketing_workspace(summary: dict) -> None:
    if frappe.db.exists("Workspace", MARKETING_HOME):
        doc = frappe.get_doc("Workspace", MARKETING_HOME)
        changed = False
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Workspace",
                "name": MARKETING_HOME,
                "label": MARKETING_HOME,
                "title": MARKETING_HOME_TITLE,
                "module": "Website",
                "icon": "website",
                "indicator_color": "purple",
                "public": 1,
                "is_hidden": 0,
                "hide_custom": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        changed = True

    fields = {
        "label": MARKETING_HOME,
        "title": MARKETING_HOME_TITLE,
        "module": "Website",
        "icon": "website",
        "indicator_color": "purple",
        "public": 1,
        "is_hidden": 0,
        "hide_custom": 1,
    }
    changed = _set_fields(doc, fields) or changed
    changed = _ensure_roles(doc, summary) or changed
    changed = _ensure_shortcuts(doc, MARKETING_SHORTCUTS) or changed

    number_cards = [
        {"number_card_name": name, "label": spec["label"]}
        for name, spec in MARKETING_NUMBER_CARDS.items()
    ]
    if _child_table_rows(doc.number_cards, ["number_card_name", "label"]) != number_cards:
        doc.set("number_cards", [])
        for row in number_cards:
            doc.append("number_cards", row)
        changed = True

    desired_content = _marketing_home_content()
    if _load_content(doc.content) != desired_content:
        doc.content = json.dumps(desired_content)
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_workspace"] = True


def _ensure_roles(doc, summary: dict) -> bool:
    desired_roles = []
    for role in MARKETING_ROLES:
        if frappe.db.exists("Role", role):
            desired_roles.append({"role": role})
        elif role not in summary["missing_roles"]:
            summary["missing_roles"].append(role)

    current_roles = _child_table_rows(doc.roles, ["role"])
    if current_roles == desired_roles:
        return False

    doc.set("roles", [])
    for row in desired_roles:
        doc.append("roles", row)
    return True


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
    desired_rows = [
        {field: _normalize_shortcut_value(spec.get(field)) for field in fields}
        for spec in desired_shortcuts
    ]
    current_rows = [
        {field: _normalize_shortcut_value(getattr(row, field, None)) for field in fields}
        for row in doc.shortcuts
    ]
    if current_rows == desired_rows:
        return False

    doc.set("shortcuts", [])
    for row in desired_rows:
        doc.append("shortcuts", row)
    return True


def _marketing_home_content() -> list[dict]:
    blocks = [
        _header(
            "lt-marketing-title",
            '<span class="h4"><b>Marketing Home</b></span>',
            12,
        ),
        _header(
            "lt-marketing-subtitle",
            '<span class="text-muted">Public-site review, inquiry pulse, newsletter tools, and campaign links without opening the external marketing reviewer role to Desk.</span>',
            12,
        ),
    ]

    for idx, card_name in enumerate(MARKETING_NUMBER_CARDS, start=1):
        blocks.append(_number_card(f"lt-marketing-card-{idx}", card_name, 3))

    blocks.extend(
        [
            _spacer("lt-marketing-spacer-1"),
            _header(
                "lt-marketing-review-title",
                '<span class="h4"><b>Public review links</b></span>',
                12,
            ),
            _shortcut("lt-marketing-review-page", "Marketing Review Page", 3),
            _shortcut("lt-marketing-homepage", "Homepage", 3),
            _shortcut("lt-marketing-portfolio", "Portfolio", 3),
            _shortcut("lt-marketing-contact", "Contact Page", 3),
            _shortcut("lt-marketing-shop", "Shop", 3),
            _header(
                "lt-marketing-content-title",
                '<span class="h4"><b>Content and shop surfaces</b></span>',
                12,
            ),
            _shortcut("lt-marketing-web-pages", "Web Pages", 3),
            _shortcut("lt-marketing-website-items", "Website Items", 3),
            _shortcut("lt-marketing-blog-posts", "Blog Posts", 3),
            _header(
                "lt-marketing-outreach-title",
                '<span class="h4"><b>Outreach and demand</b></span>',
                12,
            ),
            _shortcut("lt-marketing-newsletters", "Newsletters", 3),
            _shortcut("lt-marketing-email-groups", "Email Groups", 3),
            _shortcut("lt-marketing-campaigns", "Campaigns", 3),
            _shortcut("lt-marketing-new-inquiries", "New Inquiries", 3),
        ]
    )
    return blocks


def _set_fields(doc, fields: dict) -> bool:
    changed = False
    for key, value in fields.items():
        if not _same_value(getattr(doc, key, None), value):
            setattr(doc, key, value)
            changed = True
    return changed


def _same_value(current, desired) -> bool:
    if current in (None, "") and desired in (None, ""):
        return True
    return current == desired


def _normalize_shortcut_value(value):
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    if value == "":
        return None
    return value


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
