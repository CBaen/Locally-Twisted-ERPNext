# Phase 0 Local Runtime Proof

Date: 2026-06-30

Worker: Worker A, local runtime/read-only proof builder.

Status: local runtime proof completed. This is not deployment approval, data repair approval, cache approval, payment/provider approval, or live release approval.

Capability gate: PASS.

Loaded context:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-0-1-build-brief-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-0-1-progress-2026-06-30.md`
- `scripts/dev/lt_readonly_product_db_snapshot.py`

## Scope

Assigned write files:

- `Locally-Twisted-Backend/frappe_docker/pwd.yml`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-0-local-runtime-proof-2026-06-30.md`

Actions allowed in this slice:

- fix only the local compose manual-start policy blocker;
- start the local LT Docker workshop if the policy passes;
- run the read-only local DB snapshot helper;
- stop the local LT Docker workshop before closeout;
- record proof here.

No deploy, cache clear, ERPNext product/data repair, provider/payment/DNS/Frappe Cloud setting change, migration, setup script, import, database reset, prune, volume deletion, or customer-message action was performed.

## Compose Policy Fix

Observed blocker:

- `websocket` still had `deploy.restart_policy.condition: on-failure`.
- Other visible services already had `condition: none` before this worker's edit.

Change made:

- In `Locally-Twisted-Backend/frappe_docker/pwd.yml`, changed only `websocket` restart policy from `on-failure` to `none`.

Nested repo note:

- `Locally-Twisted-Backend/frappe_docker` is its own git repo on `main`.
- The outer LT repo ignores `Locally-Twisted-Backend/`.
- The nested repo diff also shows earlier manual-start policy edits that were already present before this worker touched the file. This worker did not revert or broaden those changes.

Verification:

```bash
rg -n "condition: (on-failure|always|unless-stopped)" Locally-Twisted-Backend/frappe_docker/pwd.yml
```

Result: no matches; command exited `1` because no offending restart-policy conditions remained.

```bash
rg -n "restart_policy:|condition:" Locally-Twisted-Backend/frappe_docker/pwd.yml
```

Result:

```text
9:      restart_policy:
10:        condition: none
32:      restart_policy:
33:        condition: none
68:      restart_policy:
69:        condition: none
114:      restart_policy:
115:        condition: none
133:      restart_policy:
134:        condition: none
164:      restart_policy:
165:        condition: none
190:      restart_policy:
191:        condition: none
216:      restart_policy:
217:        condition: none
226:      restart_policy:
227:        condition: none
234:      restart_policy:
235:        condition: none
255:      restart_policy:
256:        condition: none
```

## Local Stack Run

Pre-start check:

```bash
client-stack check lt
```

Result:

```text
--- lt containers ---
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
--- lt page check: http://localhost:8081/ ---
OFFLINE http://localhost:8081/ (URLError: <urlopen error [Errno 111] Connection refused>)
```

Start command:

```bash
client-stack start lt
```

Result: exited `0`; local LT workshop containers started.

Post-start check:

```bash
client-stack check lt
```

Result:

```text
--- lt page check: http://localhost:8081/ ---
OK 200 http://localhost:8081/
```

Backend availability:

```bash
docker inspect -f '{{.State.Running}} {{.State.Status}}' locally-twisted-erpnext-v15-backend-1
```

Result:

```text
true running
```

## Read-Only DB Snapshot

Command:

```bash
python scripts/dev/lt_readonly_product_db_snapshot.py --output /tmp/lt-large-head-missionary-db-snapshot.json
```

Result:

```text
[LT PRODUCT DB SNAPSHOT] PASS
  output: /tmp/lt-large-head-missionary-db-snapshot.json
  mutation: none
```

Output file:

```bash
ls -lh /tmp/lt-large-head-missionary-db-snapshot.json
```

Result:

```text
-rw-rw-r-- 1 guidingl guidingl 121K Jun 30 01:24 /tmp/lt-large-head-missionary-db-snapshot.json
```

Snapshot summary:

```bash
jq '{generated_at, read_only, container, site, item_code, route, summary, failures}' /tmp/lt-large-head-missionary-db-snapshot.json
```

Result:

```json
{
  "generated_at": "2026-06-30T07:23:52+00:00",
  "read_only": true,
  "container": "locally-twisted-erpnext-v15-backend-1",
  "site": "frontend",
  "item_code": "large-head-missionary",
  "route": "shop-items/bouquets/large-head-missionary",
  "summary": {
    "files_by_attachment": 48,
    "files_by_url": 31,
    "item_prices": 30,
    "item_variant_attributes": 93,
    "product_blueprints": 1,
    "template_items": 1,
    "variant_items": 30,
    "website_items": 1
  },
  "failures": []
}
```

Local DB snapshot produced: yes.

## Shutdown

Because this worker started the LT local stack, this worker stopped it before closeout.

Command:

```bash
client-stack stop lt
```

Result: exited `0`; local LT workshop stopped without deleting stored data.

Final check:

```bash
client-stack check lt
```

Result:

```text
--- lt containers ---
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
--- lt page check: http://localhost:8081/ ---
OFFLINE http://localhost:8081/ (URLError: <urlopen error [Errno 111] Connection refused>)
```

## Closeout

- Compose manual-start policy blocker: fixed for `websocket`.
- Offending restart-policy conditions after fix: none found.
- Local stack start: passed.
- Read-only snapshot: passed and wrote `/tmp/lt-large-head-missionary-db-snapshot.json`.
- Local stack stop: passed.
- Deployment: none.
- Cache clear: none.
- ERPNext record repair/migration/import/setup script: none.
- Provider/payment/DNS/Frappe Cloud change: none.
- Customer-message action: none.
