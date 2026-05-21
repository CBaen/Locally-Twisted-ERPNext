# Lane 02 - Recreate Deploy Durability

## Decision Question

What exact proof sequence shows the Locally Twisted Webshop asset fix survives image rebuild, forced container recreate, cache clearing, and Frappe Cloud staging deployment; and what storefront surfaces must be quarantined if any part of that proof fails?

## Primary Sources

- Research brief: `research/expedition-webshop-breakage-hardening/research-brief.md:3-31`.
- Frappe asset model: [Asset Bundling](https://docs.frappe.io/framework/user/en/basics/asset-bundling), [Static Assets](https://docs.frappe.io/framework/user/en/basics/static-assets), [Sites](https://docs.frappe.io/framework/user/en/basics/sites).
- Frappe Docker source/docs: [Build Setup](https://github.com/frappe/frappe_docker/blob/main/docs/02-setup/02-build-setup.md), [Setup Overview](https://github.com/frappe/frappe_docker/blob/main/docs/02-setup/01-overview.md), [FAQ](https://github.com/frappe/frappe_docker/wiki/Frequently-Asked-Questions).
- Frappe Cloud deploy facts: [Installing an app](https://docs.frappe.io/cloud/installing-an-app), [Update an app/site on a private bench](https://docs.frappe.io/cloud/sites/how-to-update-an-app-site-on-a-private-bench), [Private Benches](https://docs.frappe.io/cloud/benches), [Debugging](https://docs.frappe.io/cloud/benches/debugging).
- Local source/config: `docker/Dockerfile`, `Locally-Twisted-Backend/frappe_docker/pwd.yml`, `Locally-Twisted-Backend/frappe_docker/compose.yaml`, `scripts/dev/build_webshop_assets.py`, `scripts/dev/clear_website_cache.py`, `scripts/verify/public_asset_integrity.py`, `scripts/verify/public_network_integrity.spec.js`, `scripts/verify/website_launch_verify.py`, `package.json`.

## Local Evidence

- Current local stack is running `locally-twisted-erpnext:v15` for LT backend/frontend/worker services, with frontend exposed on `8081`; read-only check on 2026-05-21 showed Frappe `15.106.0`, ERPNext `15.105.0`, Payments/Webshop/LT `0.0.1`.
- Current manifest points to Webshop bundles: `/assets/webshop/dist/css/webshop-web.bundle.KIQY4ZII.css` and `/assets/webshop/dist/js/web.bundle.WLOGYSZO.js`; matching files exist under `apps/webshop/webshop/public/dist/...` inside the backend container. This proves current local runtime health, not recreate or staging durability.
- Current non-mutating verifiers passed on localhost: `python scripts/verify/public_asset_integrity.py` passed `31` routes and `291` unique local asset URLs; `npm run test:public-network` passed `31/31` Playwright network/MIME checks.
- `docker/Dockerfile:20-23` pins the ERPNext base image plus Payments/Webshop commits. `docker/Dockerfile:31-34` installs Node/Yarn during image build, `:63-73` installs/registers apps, and `:93-95` runs `bench build --app payments --production` and `bench build --app webshop --production`.
- `docker/Dockerfile:75-95` intentionally bakes compiled upstream bundles into `apps/<app>/public/dist`, while `:112-113` notes the base image keeps `sites` and logs as volumes.
- `Locally-Twisted-Backend/frappe_docker/pwd.yml:3`, `:26`, `:62`, `:125`, `:158`, `:184`, `:228`, `:249` all use `locally-twisted-erpnext:v15`. The same file mounts `sites:/home/frappe/frappe-bench/sites` and bind-mounts only `../../apps/locally_twisted`, leaving upstream `webshop` and `payments` image-owned (`pwd.yml:9-18`, `:144-153`).
- `scripts/dev/build_webshop_assets.py:40-45` separates `--durable-rebuild` from `--runtime-only`; `:129-147` rebuilds the image, recreates the compose stack with `--force-recreate`, then syncs the manifest; `:152-154` warns runtime-only repair is not launch proof.
- `scripts/dev/clear_website_cache.py:18-20` clears site cache, website cache, and Redis `assets_json`; `:84-95` implements those exact local cache steps.
- `scripts/verify/public_asset_integrity.py:20-30`, `:200-259` checks public routes for missing assets, wrong MIME, CSS dependencies, and raw spaces. `scripts/verify/public_network_integrity.spec.js:56-83` adds browser console/page error and same-origin response checks.
- `scripts/verify/website_launch_verify.py:135-180` includes public asset, network, layout, ecommerce, shop, product, variant, and checkout gates, and `:273-315` supports `--base-url` / `LT_BASE_URL`.
- `scripts/deploy.py:38-45`, `:165-171` is not sufficient for this lane as written: it still references stale `/book` and `/all-products` assumptions and does `migrate` plus `clear-website-cache` without proving image rebuild, forced recreate, asset manifest regeneration, or staging provider deployment.

## Findings

1. The correct durable local direction is image-owned Webshop/Payments assets, not `bench build` inside a running production container. Frappe Docker's FAQ explicitly warns that production containers should not run `bench get-app` or `bench build`; assets belong in the image build, and container replacement plus migration is the update path.
2. Frappe's asset contract makes `sites/assets` and `assets.json` launch-critical. Frappe docs say `sites/assets` is generated by `bench build` and served by nginx, and bundled assets resolve under `/assets/[app]/dist/...`. A local pass that only has files in `apps/webshop/public/dist` is incomplete unless the manifest and nginx-served URLs are also proven.
3. The current local script is close but not fully launch-grade evidence. `--durable-rebuild` rebuilds/recreates, but then runs a manual manifest sync into the `sites` volume. That may be acceptable as a local materialization step, but it does not prove a fresh volume or Frappe Cloud staging deploy will generate the same manifest without a rescue step.
4. `--runtime-only` must be treated as emergency repair only. It writes bundles into a running frontend container and is explicitly not durable across recreate.
5. Frappe Cloud cannot be proven by localhost Docker evidence. Official Cloud docs require private bench app updates/deploy-and-update flow, and Cloud debugging docs warn that SSH-installed apps and frontend edits/`bench build` can break or fail to persist across bench updates.
6. Current localhost asset/network checks are green, but they are baseline health checks. They are not rebuild proof, not fresh-volume proof, and not staging proof.

## Resolution Recommendation

**Refresh with quarantine.**

Support the image-baked Webshop asset direction, but refresh the proof harness before using it as a release gate. Eliminate `--runtime-only` as any kind of launch proof. Quarantine staging/live readiness, ready-to-order navigation, product/category pages, cart, and checkout if rebuild/recreate/cache/staging asset proof fails.

Rebuild the deployment path only if a clean image or Frappe Cloud staging deploy cannot reproduce correct `assets.json` entries and served `/assets/webshop/dist/...` CSS/JS without SSH edits, running `bench build` on Cloud, or container-writable-layer repairs.

## Required Tests

1. Baseline evidence: record date, git commit, image tag/id, `docker ps`, `bench --site frontend version`, `installed_apps`, Website Item count, Item Price count, current `assets.json` Webshop bundle paths, and HEAD/MIME results for those bundle URLs.
2. Image build proof: run the durable image build from `docker/Dockerfile` and save the full command/output. Prove the image contains Webshop CSS/JS under `apps/webshop/webshop/public/dist` before any runtime repair.
3. Forced recreate proof: run compose `up -d --force-recreate` for the LT project, wait for readiness, and prove the same image tag is used by backend/frontend/worker services. No `--runtime-only` repair may run.
4. Manifest proof: after recreate, prove `sites/assets/assets.json` and `assets-rtl.json` contain Webshop bundle keys pointing at existing `/assets/webshop/dist/...` files. If a manifest sync script is used, its output must be retained and named as part of the proof, not hidden as cache clearing.
5. Cache proof: run `scripts/dev/clear_website_cache.py`, then rerun manifest and served-asset checks. Cache clearing must not erase or stale the Webshop bundle paths.
6. Public asset proof: run `python scripts/verify/public_asset_integrity.py` and save output with route count, base URL, date, and command.
7. Browser network proof: run `npm run test:public-network` and save Playwright output. A pass must cover shop, category, product, cart, and checkout routes or explain explicit paused-route exclusions.
8. Commerce smoke proof: run `npm run test:ecommerce-full` or the named subset from `website_launch_verify.py` needed for the release mode. If public ecommerce is paused, prove the pause contract and quote fallback. If open, prove category, variant selector, direct cart, cart, checkout, fulfillment, and lead conversion.
9. Fresh-volume or disposable-stack proof: before launch, repeat the rebuild/recreate/asset sequence in an isolated disposable compose project or staging clone so the result is not dependent on this workstation's existing `sites` volume.
10. Frappe Cloud staging proof: deploy the app through the private bench group/site update flow, keep `lt_ecommerce_paused=1`, and run the same asset/network/launch verifiers with `LT_BASE_URL=<staging https url>`. Do not use SSH `bench build` or frontend file edits as the success path.

## Remaining Gaps

- This lane did not run destructive rebuilds, forced recreates, cache clears, fresh-volume tests, or staging deploys.
- There is no retained evidence bundle yet for rebuild/recreate/cache/staging durability.
- The local durable script still performs a post-recreate manifest sync; that needs to be either proven as intentional volume materialization or replaced by a cleaner build/deploy manifest path.
- Frappe Cloud staging URL, bench group, deployed app commit, and provider deploy logs were not available in this lane.
- `scripts/deploy.py` is stale for this asset durability question and should stay quarantined from launch proof until refreshed.
