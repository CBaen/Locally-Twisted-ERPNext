# Product-page architecture readiness verifier failure diagnosis — 2026-05-10

## Scope
Diagnose the fresh failure from:

```powershell
python scripts\verify\product_page_architecture_readiness.py --report output\product-page-architecture-readiness-infrastructure-research-20260510.json
```

Observed prior symptom from handoff: `[PRODUCT PAGE ARCHITECTURE READINESS] FAIL - bench execute failed`.

## Repo state note
The worktree already had many unrelated modified/untracked files before diagnosis. I did not modify application code and did not stage anything. The only intentional new/updated outputs from this diagnosis are:

- `output/product-page-architecture-readiness-infrastructure-research-20260510.json` — created by rerunning the exact verifier command.
- `workstreams/ecommerce-audit/product-page-architecture-readiness-failure-diagnosis-2026-05-10.md` — this diagnosis artifact.

Relevant pre-existing diff on the app verifier:

```diff
-                ".codex/capabilities/recipes/erpnext-ecommerce-receiving-architecture.md",
+                "capabilities/recipes/erpnext-ecommerce-receiving-architecture.md",
```

That evidence-path change is not a runtime blocker.

## What the wrapper does
Host wrapper: `scripts/verify/product_page_architecture_readiness.py`

- Hard-coded container: `locally-twisted-erpnext-v15-backend-1`
- Hard-coded site: `frontend`
- Bench method: `locally_twisted.verify.product_page_architecture_readiness.run`
- It fails with `bench execute failed` only when `docker exec ... bench --site frontend execute ...` exits non-zero.
- If the Frappe method returns JSON with `ok: false`, the wrapper prints `BLOCKED` and exits `2`, not `bench execute failed`.

## Environment checks

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Output showed the expected backend container running:

```text
locally-twisted-erpnext-v15-backend-1       Up About an hour
locally-twisted-erpnext-v15-db-1            Up 25 hours (healthy)
```

```powershell
docker inspect locally-twisted-erpnext-v15-backend-1 --format "Started={{.State.StartedAt}} Status={{.State.Status}} Restarting={{.State.Restarting}} ExitCode={{.State.ExitCode}} RestartCount={{.RestartCount}}"
```

Output:

```text
Started=2026-05-10T18:56:53.786615446Z Status=running Restarting=false ExitCode=0 RestartCount=0
```

Backend logs around the reported failure window had no matching output:

```powershell
docker logs --since 2026-05-10T19:50:00Z --until 2026-05-10T20:06:00Z locally-twisted-erpnext-v15-backend-1
```

Output: no lines.

## Reproduction attempts

### Exact verifier command

```powershell
python scripts\verify\product_page_architecture_readiness.py --report output\product-page-architecture-readiness-infrastructure-research-20260510.json
```

Result: **PASS**, exit code `0`.

Key output:

```text
[PRODUCT PAGE ARCHITECTURE READINESS] wrote output\product-page-architecture-readiness-infrastructure-research-20260510.json
[PRODUCT PAGE ARCHITECTURE READINESS] PASS
  technical_architecture_ok: True
  import_reopen_ok: True
  generated_at: 2026-05-10T14:03:36.831449
  pass: 14
  blocked: 0
  partial: 0
  deferred: 1
  info: 0
```

Generated report summary:

```json
{
  "ok": true,
  "technical_architecture_ok": true,
  "import_reopen_ok": true,
  "generated_at": "2026-05-10T14:03:36.831449",
  "summary": {
    "pass": 14,
    "blocked": 0,
    "partial": 0,
    "deferred": 1,
    "info": 0
  },
  "technical_architecture_blockers": [],
  "import_reopen_blockers": [],
  "blockers": [],
  "unexpected_contract_failures": []
}
```

### Direct bench execute

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.product_page_architecture_readiness.run
```

Result: **exit code `0`** and JSON report with `ok: true`.

The command emitted cssutils noise before/alongside the JSON in the combined captured process log:

```text
ERROR   PropertyValue: Missing token for production Choice(...): ('HASH', '#0000001a', 1, 3212)
ERROR   PropertyValue: Unknown syntax or no value: 0 3px 6px #0000001a
ERROR   CSSStyleDeclaration: Syntax Error in Property: box-shadow:0 3px 6px #0000001a
WARNING Property: Unknown Property name. [1:69: word-break]
```

Those warnings/errors did **not** cause a non-zero bench exit and did **not** prevent the wrapper from parsing JSON, because the exact wrapper command passed.

## Existing related reports

```powershell
Get-ChildItem output -Filter "*architecture-readiness*" | Select-Object Name,Length,LastWriteTime
```

Relevant files:

```text
product-page-architecture-readiness-current.json                           12299 5/10/2026 7:38:03 AM
product-page-architecture-readiness-audit.json                             12299 5/10/2026 10:32:07 AM
product-page-architecture-readiness-infrastructure-research-20260510.json  12292 5/10/2026 2:03:37 PM
product-page-architecture-readiness-lane-b-20260510.json                   25660 5/10/2026 10:00:50 AM
product-page-architecture-readiness.json                                   12522 5/10/2026 7:15:14 AM
```

Historical failures were not the same as the reported fresh `bench execute failed`:

- `product-page-architecture-readiness.json` at 07:15 had `ok: false` because public ecommerce was paused. That would produce wrapper status `BLOCKED`, not `bench execute failed`.
- `product-page-architecture-readiness-lane-b-20260510.json` at 10:00 had `ok: false` due to a caught MariaDB deadlock in `product_quote_customer_delivery_contract`. That was captured inside JSON as a contract blocker, not a non-zero bench execution failure.

## Current conclusion

I could **not reproduce** the reported `bench execute failed`. The current verifier, site, container, and direct bench method all work now.

Most likely classification: **transient environment/runtime failure**, not a current product-page architecture blocker and not a report-path issue.

Possible transient causes consistent with the wrapper's failure mode:

1. Backend container unavailable/restarting at the earlier run.
2. Bench/site temporarily unavailable.
3. A one-off unhandled import/runtime error that is no longer present.
4. Host Docker invocation glitch.

No evidence currently supports an application-code fix.

## Safe next fix / recommendation

Do **not** change application code for this failure based on current evidence.

Recommended small hardening if this recurs: improve `scripts/verify/product_page_architecture_readiness.py` failure reporting to include the exact docker command, return code, and captured stdout/stderr in a persisted failure artifact when `bench execute` exits non-zero. The wrapper already prints stdout/stderr, but the prior handoff preserved only the short headline, which made the original root cause unrecoverable.

If it fails again, rerun this immediately before any restart:

```powershell
docker ps --format "table {{.Names}}\t{{.Status}}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.product_page_architecture_readiness.run
docker inspect locally-twisted-erpnext-v15-backend-1 --format "Started={{.State.StartedAt}} Status={{.State.Status}} Restarting={{.State.Restarting}} ExitCode={{.State.ExitCode}} RestartCount={{.RestartCount}}"
```
