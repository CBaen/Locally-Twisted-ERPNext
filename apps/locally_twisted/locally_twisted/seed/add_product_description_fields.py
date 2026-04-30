"""Add the two product description Custom Fields to Website Item.

Two-field discipline (GL directive 2026-04-30):
- lt_brand_description — Quiet Confidence voice copy. Evocative, present-tense.
- lt_product_details   — Plain-language factual specs. What's included, options, format.

Both render on every product page as two distinct sections.

Idempotent. Run once:
    docker exec locally-twisted-erpnext-v15-backend-1 \\
        bench --site frontend execute \\
        locally_twisted.seed.add_product_description_fields.run
"""

import frappe


FIELDS = [
    {
        "doctype": "Custom Field",
        "dt": "Website Item",
        "fieldname": "lt_brand_description",
        "label": "About This Design",
        "fieldtype": "Text Editor",
        "insert_after": "web_long_description",
        "description": "Quiet Confidence voice. Evocative, present-tense. Renders ABOVE 'What's Included' on the product page.",
    },
    {
        "doctype": "Custom Field",
        "dt": "Website Item",
        "fieldname": "lt_product_details",
        "label": "What's Included",
        "fieldtype": "Text Editor",
        "insert_after": "lt_brand_description",
        "description": "Plain-language factual specs. Renders BELOW 'About This Design' on the product page.",
    },
]


def run():
    for spec in FIELDS:
        name = f"{spec['dt']}-{spec['fieldname']}"
        if frappe.db.exists("Custom Field", name):
            print(f"[skip] {name} already exists")
            continue
        frappe.get_doc(spec).insert(ignore_permissions=True)
        print(f"[create] {name}")
    frappe.db.commit()
    print("done.")
