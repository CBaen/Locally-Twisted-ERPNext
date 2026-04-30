# Offboarding Check

**Purpose:** Verify the client's repo is self-contained and the four portable gates fire correctly without any dependency on Built_by_Cameron tooling. Run this before any handoff (to a contractor, to the client themselves, to another agency). Run it again on install. If it passes both times, the kit's portability promise is verified.

---

## When to run this check

- **At install time** — immediately after copying the gate kit into a new client repo. If the check fails, fix the failure before declaring install complete.
- **At handoff time** — before transferring repo ownership or providing a contractor with access. The check must pass cleanly.
- **At quarterly intervals** — even if no handoff is imminent. Drift accumulates.

---

## The check

A clean checkout of this repo, on a machine that has NEVER had `~/.claude/`, must be able to:

1. Run all four gates (lint, schema-parity, smoke-forms, screenshot)
2. Run the deploy orchestrator end-to-end in `--dry-run` mode
3. Run the CI workflow
4. Render the framework-traps documentation

If any of those fail, the kit has acquired a dependency on agency tooling and is no longer truly portable. Find and remove the dependency.

---

## Step-by-step verification

### Step 1: Clone fresh

On a machine without any BBC-specific tooling installed:

```bash
git clone <client-repo-url> /tmp/client-offboard-test
cd /tmp/client-offboard-test
```

### Step 2: Confirm no `~/.claude/` references

```bash
grep -rn "\.claude" scripts/ docs/ .github/ 2>/dev/null
```

**Expected:** zero results, or only references inside comments explicitly framed as "agency-side, does not apply to this repo."

**If any non-comment references appear:** the kit has leaked an agency dependency. Find the file. Replace the reference with a self-contained equivalent.

### Step 3: Install dependencies

```bash
pip install playwright requests
playwright install chromium
```

If the client repo has a `requirements.txt`, this should be a one-liner: `pip install -r requirements.txt`.

### Step 4: Run lint

```bash
python scripts/lint/migration_broad_write.py
```

**Expected:** PASS, or specific findings if the repo legitimately contains broad-write patterns. Either is acceptable; "could not run" is not.

### Step 5: Run schema parity (skip if no DB access)

```bash
python scripts/verify/schema_parity.py --site CLIENT_SITE_NAME
```

**Expected (with DB access):** PASS, or specific drift findings. **Expected (no DB access):** SKIP gracefully with the message "LIVE schema unavailable" — this is correct CI behavior.

### Step 6: Run smoke forms shape-only

```bash
python scripts/verify/smoke_forms.py --base-url https://CLIENT.com --form-path /book --shape-only
```

**Expected:** "FORM SHAPE OK" against any reachable URL. If the URL is unreachable in the offboarding-test environment, that's fine — the gate ran.

### Step 7: Run screenshot against any reachable URL

```bash
python scripts/verify/playwright_screenshot.py --base-url https://example.com --paths /
```

**Expected:** PASS — screenshot saved to `scripts/verify/_screenshots/<timestamp>/home.png`.

### Step 8: Run deploy orchestrator dry-run

```bash
python scripts/deploy.py --dry-run
```

**Expected:** Pre-deploy gates report PASS / SKIP, then "DRY RUN — STOPPING BEFORE DEPLOY" — exit code 0.

### Step 9: Verify CI workflow

```bash
cat .github/workflows/ci.yml | python -c "import yaml, sys; yaml.safe_load(sys.stdin); print('CI YAML valid')"
```

**Expected:** "CI YAML valid"

### Step 10: Verify framework-traps documentation renders

```bash
ls -la docs/framework-traps.md
wc -l docs/framework-traps.md
```

**Expected:** File exists, > 50 lines (substantive content).

---

## Pass criteria

The offboarding check PASSES when:

- Step 2 returns zero non-comment `~/.claude/` references
- Steps 4, 6, 7, 8, 9, 10 all complete with exit code 0
- Step 5 either passes or skips gracefully

If ALL of those are true, the kit is portable. The client can take this repo to a contractor, to themselves, or to another agency, and the gates will continue to fire.

---

## Pass criteria for the kit's PROMISE

A passing offboarding check means: a contractor on a fresh laptop, with no Built_by_Cameron tooling, can clone this repo, install dependencies, and run `python scripts/deploy.py` to deploy this client's work — including all framework-protective gates — without anything breaking due to a missing agency dependency.

That is the kit's deliverable promise.

---

*If the check fails, do not hand off. Fix the failure first. Document it in lessons-learned for the next client install.*
