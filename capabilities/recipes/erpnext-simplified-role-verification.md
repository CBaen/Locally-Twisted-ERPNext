---
name: ERPNext simplified role verification
level: recipe
last_verified: 2026-05-02
---

## What it does

Verifies that a simplified ERPNext/Frappe backend role works as a real operator experience, not just as an admin-configured workspace.

## When to reach for it

Use this when creating or changing a non-admin backend profile for an owner, manager, employee, accountant, contractor, or client user. Use it again when a user reports that a shortcut, calendar, workspace, or login link looks confusing or fails after login. If the person only needs public website review with no ERPNext operation, use [erpnext-external-review-access](erpnext-external-review-access.md) instead.

## How to use it

Check the whole chain in this order:

1. Confirm the role/profile intent in plain language.

   Write down what the person should do in the system, using business words. Example: Jeff should see new inquiries, customers, bookings, products, job boards, and the booking calendar without ERPNext module clutter.

   If the person only needs job details occasionally, consider whether they need a backend login at all. Contractors may be better served by text, email, and calendar invites unless they have a real operator workflow inside ERPNext. External website reviewers should be Website Users behind a narrow public review route, not Desk users.

2. Verify with the actual non-admin login.

   Admin success does not prove the simplified role works. Log in as the target user or use that user's session through the API.

3. Use the stable Desk entry route.

   Start with `/app/Workspaces`, not `/app/<workspace-slug>`. Direct workspace slugs can trigger Frappe Desk `frappe.desk.desk_page.getpage` 404 even when login succeeds.

4. Check visible workspace and sidebar.

   Confirm the intended workspace is first and that unrelated ERPNext modules are hidden. For LT owner testing, the target is `Owner Home`, then `Home`.

5. Check each shortcut as a business action.

   For every visible shortcut, record:

   - Label shown to the user.
   - ERPNext DocType or route it opens.
   - View type, such as List, New, Kanban, or Calendar.
   - Whether the label and backend object mean the same thing.

   Watch for friendly labels hiding the wrong backend object. Example: `Bookings` pointed at `Sales Order`, while `Event Calendar` pointed at the separate `Event` DocType and looked empty.

6. Check permission behind the button.

   A visible shortcut is not enough. If the user sees `Add Product`, the user also needs create/write permission for `Item`, usually through ERPNext's native `Item Manager` role.

7. Check that real records land where the user expects.

   Counts and calendar/list endpoints should agree with the user's mental model. Example: if there are 8 bookings, the booking calendar should show those 8 Sales Orders on their delivery date, not an empty Event calendar.

8. Verify Workspace dashboard widgets as linked backend records.

   A Workspace card or chart needs both the backend document and the Workspace child/content reference. For Number Cards, Frappe names the record from the card label/autoname; the Workspace row must point at the actual Number Card name. For Dashboard Charts, verify the `Dashboard Chart` document, the `Workspace Chart` child row, and the `chart` content block.

9. Separate console noise from the blocker.

   `socketio_client.js: Invalid origin` is a socket/realtime warning. It is worth fixing, but it is not the route blocker if `frappe.desk.desk_page.getpage` is returning 404.

10. Confirm browser/cache state after code changes.

   Frappe Desk can serve cached assets. Verify the changed JS/CSS is present in the served Desk HTML or static asset before claiming the browser has the fix.

For LT's current simplified backend lane, run the durable repo checks first:

```bash
python scripts/setup/sync_backend_workspaces.py
python scripts/verify/backend_workspace_parity.py
export LT_DESK_TEST_USER='lt-owner-temp@example.com'; export LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
```

Useful manual verification skeleton:

```bash
@'
import json, urllib.request, urllib.parse, urllib.error
from http.cookiejar import CookieJar

BASE = "http://localhost:8081"
USER = "lt-owner-temp@example.com"
PASSWORD = "LocalTemp2026!"
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

def call(path, payload=None, method="GET"):
    headers = {"X-Requested-With": "XMLHttpRequest"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
        with opener.open(req, timeout=30) as response:
            return response.status, response.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "ignore")

print(call("/api/method/login", {"usr": USER, "pwd": PASSWORD}, "POST"))
print("/app/Workspaces", call("/app/Workspaces")[0])

status, body = call("/api/method/frappe.desk.desktop.get_workspace_sidebar_items")
print("sidebar", status)
print([p.get("title") or p.get("label") or p.get("name") for p in json.loads(body).get("message", {}).get("pages", [])[:10]])

for doctype in ["Lead", "Sales Order", "Event", "Customer", "Contact", "Item"]:
    status, body = call("/api/method/frappe.client.get_count?doctype=" + urllib.parse.quote(doctype))
    print(doctype, status, body[:120])
'@ | python -
```

## What it depends on

- [visual-debugging](visual-debugging.md) - use when browser screenshots are available to verify what the user sees.
- [claude-reference-library](claude-reference-library.md) - optional read-only reference for older Frappe safety habits; verify current behavior against the running ERPNext site.

## Failure modes

- Testing only as Administrator hides missing permissions and hidden workspace problems.
- Naming a shortcut clearly does not prove it opens the right DocType.
- Adding a `New` shortcut without create permission creates a dead end for the operator.
- Creating Number Card or Dashboard Chart documents is not enough; the Workspace also needs matching child rows and content blocks.
- Number Card names follow Frappe naming rules. If the sync uses an internal name that differs from the label, link validation can fail when saving the Workspace.
- A Desk route returning HTTP 200 can still fail client-side after Frappe calls `desk_page.getpage`.
- Browser cache can make a fixed file behave like the old file until the served asset is verified or the browser is hard-refreshed.
- Effective role helpers can overstate admin membership. For least-privilege external review boundaries, verify explicit `Has Role` membership on the User record instead of broad role lookup.

## Examples

On 2026-05-02, the LT owner account had `Products` but no `Add Product`, and the owner role could read Items without the native `Item Manager` create permission. The workspace also showed 8 `Bookings` from Sales Orders while the calendar was empty because it pointed at the `Event` DocType. The fix added `Add Product`, granted `Item Manager`, renamed customer/contact labels, and changed the calendar to Sales Orders by `delivery_date`.

The same trap later appeared in `LT Manager Home` and `LT Employee Home`: Owner had been fixed, but Manager/Employee still used `Event Calendar` and `Contacts`. `scripts/setup/sync_backend_workspaces.py` now normalizes those labels and `scripts/verify/backend_workspace_parity.py` guards against regression.

Later on 2026-05-02, Owner Home became a command center with live Number Cards (`New Inquiries`, `Bookings`, `Customers`, `Overdue Follow-ups`), the `LT Incoming Inquiries` Dashboard Chart, and a guided "What Jeff does next" flow. The first sync attempt used internal Number Card names that did not match Frappe's label-based naming, so Workspace link validation failed. The durable fix made the card names match their labels and extended `backend_workspace_parity.py` plus `owner_desk_routes.spec.js` to verify the cards, chart, and visible owner text.
