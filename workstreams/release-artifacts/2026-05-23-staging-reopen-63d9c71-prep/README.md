# LT Staging Reopen Prep

Status: **prep-only; not controller-consumable; not mutation-capable**.

Source commit: `63d9c711af68b762f2ed463c644a2fa70569b1c1`
Rollback hash context: `181076c239b2d1d3d508a41ac471c71f9d2b5158`

This folder reduces post-approval setup ambiguity. It does not
authorize app mirror sync, Frappe Cloud deploy/update, staging
bootstrap/import, migrate, cache clear, live release, DNS, Stripe,
Search Console, indexing, checkout, or provider mutation.

Only prep files belong here:

- `README.md`
- `packet-prep-manifest.json`
- `missing-release-artifacts.md`
- `freeze-reopen-approval-preview.json`

Do not rename prep files into final release artifacts. Generate the real
artifacts only when their source proof exists and the active release
controller requires them.
