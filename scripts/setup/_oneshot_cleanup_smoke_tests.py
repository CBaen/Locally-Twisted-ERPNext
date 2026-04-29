"""Delete smoke-test records from the LT site.

Removes the Sales Orders, Payment Requests, Customers, Contacts, and
Addresses that were created by the guest-checkout smoke tests on
2026-04-28/29 (sessions building Stripe integration). Idempotent —
re-running after the data is gone is a no-op.

Run from the host: python scripts/setup/_oneshot_cleanup_smoke_tests.py

Designed to be deleted after one successful run (it's a one-shot
named with leading underscore per repo convention).
"""
import json
import subprocess

CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

TEST_CUSTOMER_NAMES = [
    "Test Guest", "Stripe Smoke", "Stripe Smoke - 1",
    "Stripe Smoke 2", "Stripe Smoke 3", "Stripe Smoke Final",
    "URL Test", "Trace Test",
]


def bench_execute(method, kwargs):
    cmd = [
        "docker", "exec", CONTAINER,
        "bench", "--site", SITE, "execute", method,
        "--kwargs", json.dumps(kwargs),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode


def cancel_submitted_then_delete(doctype, filters):
    """For any docs matching filters: cancel if submitted, delete."""
    docs_out, _, _ = bench_execute(
        "frappe.client.get_list",
        {"doctype": doctype, "filters": filters,
         "fields": ["name", "docstatus"], "limit_page_length": 100},
    )
    try:
        docs = json.loads(docs_out)
    except Exception:
        print(f"  could not parse {doctype} list:", docs_out[-200:])
        return

    for d in docs:
        name = d["name"]
        if int(d.get("docstatus", 0)) == 1:
            print(f"  cancelling {doctype} {name}")
            bench_execute("frappe.client.cancel", {"doctype": doctype, "name": name})
        print(f"  deleting {doctype} {name}")
        bench_execute("frappe.client.delete", {"doctype": doctype, "name": name})


def main():
    # 1. Payment Requests linked to test customers (cancel + delete)
    print("=== Payment Requests ===")
    cancel_submitted_then_delete(
        "Payment Request",
        [["party_type", "=", "Customer"], ["party", "in", TEST_CUSTOMER_NAMES]],
    )

    # 2. Sales Orders for test customers (cancel submitted + delete)
    print("=== Sales Orders ===")
    cancel_submitted_then_delete(
        "Sales Order",
        [["customer", "in", TEST_CUSTOMER_NAMES]],
    )

    # 3. Addresses linked to test customers
    print("=== Addresses ===")
    cancel_submitted_then_delete(
        "Address",
        [["address_title", "in", TEST_CUSTOMER_NAMES + [n.strip() for n in TEST_CUSTOMER_NAMES]]],
    )

    # 4. Contacts (find by Dynamic Link)
    print("=== Contacts ===")
    for cust in TEST_CUSTOMER_NAMES:
        out, _, _ = bench_execute(
            "frappe.client.get_list",
            {"doctype": "Dynamic Link",
             "filters": [["link_doctype", "=", "Customer"],
                         ["link_name", "=", cust],
                         ["parenttype", "=", "Contact"]],
             "fields": ["parent"], "limit_page_length": 10},
        )
        try:
            for link in json.loads(out):
                contact = link.get("parent")
                if contact:
                    print(f"  deleting Contact {contact}")
                    bench_execute("frappe.client.delete",
                                  {"doctype": "Contact", "name": contact})
        except Exception:
            pass

    # 5. Customers
    print("=== Customers ===")
    cancel_submitted_then_delete(
        "Customer",
        [["customer_name", "in", TEST_CUSTOMER_NAMES]],
    )

    print()
    print("Cleanup complete.")


if __name__ == "__main__":
    main()
