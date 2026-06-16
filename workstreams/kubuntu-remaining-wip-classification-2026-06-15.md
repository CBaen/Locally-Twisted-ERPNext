# Kubuntu Remaining WIP Classification - 2026-06-15 MDT

## Scope

This packet classifies the dirty tree after local preservation commit
`b009760` and the later amended commit subject
`Preserve Kubuntu verifier and reset email guard`.

No broad cleanup, reset, branch deletion, push, provider action, database
mutation, payment action, DNS action, or live release action was performed for
this classification.

## Current Git State

- Branch: `main`
- Upstream relationship: `origin/main...HEAD` is `0 1`.
- Local preservation commit at close of the prior slice:
  `b009760 Preserve Kubuntu verifier and reset email guard`.
- Staged changes: none.
- Remaining dirty tree: 141 modified tracked files and 1 untracked file.
- Untracked file: `scripts/verify/run_playwright.js`.

Note: the commit hash may change if the local preservation commit is amended
again before it is pushed or otherwise archived. The stable identifier is the
commit subject above.

## Key Finding

Most remaining WIP is not real content drift.

`git diff --ignore-cr-at-eol --name-only` reports only two files with content
changes after ignoring Windows carriage returns:

- `apps/locally_twisted/locally_twisted/www/login.html`
- `playwright.config.js`

The other 139 modified tracked files appear to be CRLF/LF-only working-tree
churn from the Windows-to-Kubuntu migration.

`git diff --numstat` shape:

| Shape | Count |
|---|---:|
| Equal insert/delete counts | 140 |
| Unequal insert/delete counts | 1 |

`playwright.config.js` is the only unequal insert/delete file. `login.html` has
real copy changes, but its changed lines happen to keep equal insert/delete
counts.

## Real Content Diffs

### `playwright.config.js`

Adds Linux browser executable candidates before the old Windows Chrome/Edge
paths:

- `/usr/bin/brave-browser`
- `/usr/bin/chromium`
- `/usr/bin/chromium-browser`
- `/usr/bin/google-chrome`
- `/usr/bin/microsoft-edge`

This is aligned with the Kubuntu transition and should be preserved in the
Kubuntu tooling lane.

### `apps/locally_twisted/locally_twisted/www/login.html`

Changes forgot-password copy from generic password language to Locally Twisted
website account language:

- Heading becomes "Reset your Locally Twisted website password".
- Helper text clarifies the email must be the address connected to the Locally
  Twisted website account and that the reset link is for that account only.
- Button becomes "Send Locally Twisted reset link".

This aligns with the reset-email guard in the preservation commit and should be
preserved with the password/reset UX lane.

## Line-Ending-Only Buckets

The line-ending-only files span:

| Bucket | Count |
|---|---:|
| Catalog source/code/verifiers | 15 |
| Catalog audit/resource artifacts | 66 |
| Ecommerce workstreams | 32 |
| Paperwork/backend templates | 6 |
| Public site/brand/shop docs and routes | 15 |
| Other verifier/config | 1 |
| Other | 6 |

Do not commit this as-is. It would create a multi-million-line diff with almost
no content value.

## Untracked Wrapper

`scripts/verify/run_playwright.js` is a local Node wrapper around
`node_modules/@playwright/test/cli.js`.

The local preservation commit changed `package.json` to call
`node node_modules/@playwright/test/cli.js ...` directly, so this wrapper is not
needed by the npm scripts now. Keep it untracked until an explicit delete or
adoption decision; do not silently remove it.

## Recommended Next Slice

1. Decide line-ending policy before touching the 139 line-ending-only files:
   - either restore their original tracked line endings to reduce dirty noise,
   - or add a deliberate `.gitattributes`/normalization plan and commit it as a
     standalone repository hygiene slice.
2. Preserve the two real content diffs separately:
   - Kubuntu browser discovery: `playwright.config.js`
   - password reset UX copy: `www/login.html`
3. Leave `scripts/verify/run_playwright.js` alone unless explicitly adopting it
   or deleting it. Current package scripts do not need it.

## Verification Commands Used

- `git status --short --untracked-files=all`
- `git diff --ignore-cr-at-eol --name-only`
- `git diff --ignore-cr-at-eol --stat --compact-summary`
- `git diff --numstat`
- `git diff --ignore-cr-at-eol -- playwright.config.js apps/locally_twisted/locally_twisted/www/login.html`
