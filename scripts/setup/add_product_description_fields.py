"""Add the two product description Custom Fields to Website Item.

Two-field discipline (GL directive 2026-04-30):
- lt_brand_description — Quiet Confidence voice copy. Evocative, present-tense.
- lt_product_details   — Plain-language factual specs. What's included, options, format.

Both are required on every Website Item per the directive. The product detail
template renders them as two distinct sections.

Run once (idempotent — uses ignore_if_duplicate):
    docker exec locally-twisted-erpnext-v15-backend-1 \\
        bench --site frontend execute \\
        locally_twisted.scripts.setup.add_product_description_fields.run

After running, export fixtures:
    docker exec locally-twisted-erpnext-v15-backend-1 \\
        bench --site frontend export-fixtures --app locally_twisted
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
        "description": "Quiet Confidence voice. Evocative, present-tense. What this product IS and the moment it's for. Renders ABOVE 'What's Included' on the product page.",
    },
    {
        "doctype": "Custom Field",
        "dt": "Website Item",
        "fieldname": "lt_product_details",
        "label": "What's Included",
        "fieldtype": "Text Editor",
        "insert_after": "lt_brand_description",
        "description": "Plain-language factual specs. What customers get, options available, format/setup notes. Renders BELOW 'About This Design' on the product page.",
    },
]


def run():
    for spec in FIELDS:
        name = f"{spec['dt']}-{spec['fieldname']}"
        if frappe.db.exists("Custom Field", name):
            print(f"[skip] Custom Field {name} already exists")
            continue
        doc = frappe.get_doc(spec)
        doc.insert(ignore_permissions=True)
        print(f"[create] Custom Field {name}")
    frappe.db.commit()
    print("done.")
