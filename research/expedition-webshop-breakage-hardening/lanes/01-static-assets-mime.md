# Lane 01 - Static Assets And MIME

Date: 2026-05-21

## Decision Question

What is the durable Frappe/Webshop path for static assets, built bundles, MIME correctness, cache clearing, and container recreate survival in the Locally Twisted ERPNext/Webshop stack?

## Primary Sources

- [Frappe Static Assets docs](https://docs.frappe.io/framework/v15/user/en/basics/static-assets): Frappe serves static files from `frappe-bench/sites/assets`; app `public` folders are exposed as `/assets/[appname]`; bundled assets are served from `/assets/[appname]/dist/js` and `/assets/[appname]/dist/css`.
- [Frappe Asset Bundling docs](https://docs.frappe.io/framework/v15/user/en/basics/asset-bundling): `bench build` compiles bundle entry files, appends content hashes, and `include_script` / `include_style` resolve the hashed output instead of hardcoding it.
- [Frappe Hooks docs](https://docs.frappe.io/framework/v15/user/en/python-api/hooks): `web_include_js` and `web_include_css` are portal hooks for injecting website assets.
- [Frappe `jinja_globals.py` source, version-15](https://github.com/frappe/frappe/blob/version-15/frappe/utils/jinja_globals.py): `include_script` and `include_style` call `bundled_asset`; `bundled_asset` reads logical bundle names through `get_assets_json`.
- [Frappe `get_assets_json` source, version-15](https://github.com/frappe/frappe/blob/version-15/frappe/utils/__init__.py): Frappe reads and merges `assets/assets.json` plus `assets/assets-rtl.json`; outside developer mode it caches this as shared `assets_json`.
- [Webshop `hooks.py` source, version-15](https://github.com/frappe/webshop/blob/version-15/webshop/hooks.py): Webshop declares `required_apps = ["payments", "erpnext"]`, `web_include_css = "webshop-web.bundle.css"`, and `web_include_js = "web.bundle.js"`.
- [Frappe v15 migration notes](https://github.com/frappe/frappe/wiki/Migrating-to-version-15): v15 requires Node 18 for asset builds.
- [Frappe Docker build setup](https://github.com/frappe/frappe_docker/blob/main/docs/02-setup/02-build-setup.md): custom app images are expected to be built as custom images and then selected via image/tag configuration.
- [Frappe Docker migration note](https://github.com/frappe/frappe_docker/blob/main/docs/06-migration/01-migrate-from-multi-image-setup.md): the current model mounts only `sites` at `/home/frappe/frappe-bench/sites`; a separate nested `sites/assets` volume can split asset state between containers and must be removed by recreating containers.

## Local Evidence

- `docker/Dockerfile:20-23` builds from `frappe/erpnext:v15.105.0` and pins `payments` plus `webshop` commits instead of floating branch heads.
- `docker/Dockerfile:30-36` installs Node 18 and yarn, matching the v15 build requirement.
- `docker/Dockerfile:45-66` clones and editable-installs upstream `payments`, `webshop`, and the local `locally_twisted` app into the image.
- `docker/Dockerfile:73` writes `frappe erpnext payments webshop locally_twisted` to `sites/apps.txt` so `bench build` can see the apps during image build.
- `docker/Dockerfile:75-96` builds `payments` and `webshop` assets in the image with `bench build --app ... --production`; this is the durable path, not a running-container patch.
- `scripts/dev/build_webshop_assets.py:39-48` labels `--runtime-only` as an emergency writable-layer repair and `--durable-rebuild` as the recreate-safe repair.
- `scripts/dev/build_webshop_assets.py:83-127` manually aligns `sites/assets/assets.json` and `assets-rtl.json` to the baked Webshop bundle files.
- `scripts/dev/build_webshop_assets.py:129-147` rebuilds the custom image and force-recreates the compose stack for the durable path.
- `scripts/dev/build_webshop_assets.py:170-190` verifies the Webshop manifest CSS and JS paths through the public nginx URL after cache clearing.
- `scripts/dev/clear_website_cache.py:17-21` documents the exact cache surfaces: `bench clear-cache`, `bench clear-website-cache`, and Redis `DEL assets_json`.
- `scripts/dev/clear_website_cache.py:86-95` implements those three cache clears.
- `scripts/verify/public_asset_integrity.py:20-29` includes Webshop category and product routes in asset checks.
- `scripts/verify/public_asset_integrity.py:126-155` rejects wrong MIME for CSS, JS, images, and fonts.
- `scripts/verify/public_asset_integrity.py:200-260` crawls page, preload, and CSS dependency assets and fails on missing or wrong-MIME responses.
- `scripts/verify/public_network_integrity.spec.js:38-84` checks the same public route set in a browser and fails on broken same-origin assets, wrong MIME, console warnings/errors, and page errors.
- `package.json:16-17` exposes these as `npm run test:public-assets` and `npm run test:public-network`.
- `Locally-Twisted-Backend/frappe_docker/pwd.yml:9-10` and `Locally-Twisted-Backend/frappe_docker/pwd.yml:144-145` mount only the shared `sites` volume for backend/frontend, which matches the current Frappe Docker guidance and avoids a separate `sites/assets` split.

Current read-only checks run in this lane:

- `python scripts/verify/public_asset_integrity.py` passed on 2026-05-21: `31 routes, 291 unique local asset URLs`.
- `npm run test:public-network` passed on 2026-05-21: `31 passed`.
- Current manifest entries read from the backend container:
  - `webshop-web.bundle.css=/assets/webshop/dist/css/webshop-web.bundle.KIQY4ZII.css`
  - `web.bundle.js=/assets/webshop/dist/js/web.bundle.WLOGYSZO.js`
- The current frontend container has the matching baked files under `apps/webshop/webshop/public/dist/...`.

## Findings

1. The durable Webshop contract is the logical bundle names from Webshop hooks: `webshop-web.bundle.css` and `web.bundle.js`. Frappe should resolve those through `assets.json` into hashed `/assets/webshop/dist/...` URLs. Hardcoding hashed bundle URLs is not durable because the hash is content-derived.

2. The durable physical source is the real Webshop `public/dist` bundle output created by `bench build`, served through Frappe's `/assets/webshop/...` path. Placeholder CSS/JS files can silence 404s but do not satisfy the Webshop JavaScript contract.

3. MIME failures are usually a symptom of path/manifest drift, not a separate CSS setting. If a page asks for a missing CSS/JS bundle, nginx/Frappe may return a 404 or HTML response where the browser expected `text/css` or JavaScript. The fix is to build the real bundle and point the manifest at the real file, then verify through HTTP.

4. LT's local Docker shape has one extra risk: the image can contain baked app bundles, while the shared `sites` volume owns `sites/assets/assets.json` at runtime. That makes the manifest refresh step in `build_webshop_assets.py` a necessary local bridge until a clean rebuild/recreate proves Frappe's normal asset linking alone is enough for this compose setup.

5. The current local runtime is green for asset/MIME and browser network checks. That is useful, but it is not a clean rebuild, forced recreate, Frappe Cloud, or live-provider proof.

## Resolution Recommendation

- **Support** the current durable direction: pin Webshop/Payments, install Node 18/yarn at image build time, run real `bench build --app webshop --production`, serve Webshop bundles from `/assets/webshop/dist/...`, and let Frappe resolve logical bundle names through `assets.json`.
- **Refresh** the shared runtime manifest after local image rebuild/recreate, because the `sites` volume can mask image-layer `sites/assets/assets.json`. Keep this refresh loud and verified; do not treat it as a silent fallback.
- **Rebuild** via `python scripts/dev/build_webshop_assets.py --durable-rebuild` before any local launch proof that depends on Webshop bundle durability.
- **Quarantine** `--runtime-only` to emergency local diagnosis only. It writes into the running frontend container and is not recreate-safe.
- **Eliminate** placeholder bundle shims, manual hashed URL hardcoding, and any path that makes missing Webshop assets look successful.
- **Do not accept** localhost-only asset proof as staging/live proof. Re-run the same gates against the exact staging/live base URL with retained output.

## Required Tests

Run after any Webshop asset, Docker image, app install, route, cache, or deploy-path change:

```bash
python scripts/dev/build_webshop_assets.py --durable-rebuild
python scripts/verify/public_asset_integrity.py
npm run test:public-network
```

Run after a deliberate forced recreate:

```bash
docker compose -p locally-twisted-erpnext-v15 -f Locally-Twisted-Backend/frappe_docker/pwd.yml up -d --force-recreate
python scripts/dev/clear_website_cache.py
python scripts/verify/public_asset_integrity.py
npm run test:public-network
```

For staging/live, set the real base URL and retain command output:

```bash
export LT_BASE_URL="https://<staging-or-live-host>"
python scripts/verify/public_asset_integrity.py --base-url $LT_BASE_URL
npm run test:public-network
```

Minimum pass criteria:

- Webshop manifest keys exist for `webshop-web.bundle.css` and `web.bundle.js`.
- Manifest paths return HTTP 200 through the public web server.
- CSS returns `text/css`; JS returns a JavaScript MIME type.
- Public and Webshop routes have no broken same-origin asset responses.
- Browser console/page errors stay empty on the checked route set.
- The same result survives a container recreate, not just a warm running container.

## Remaining Gaps

- This lane did not run `--durable-rebuild`; it is intentionally a long rebuild and was left as a required test.
- This lane did not run a clean-volume or new-machine proof. Current success may still depend on the existing named `sites` volume.
- This lane did not verify Frappe Cloud's custom-app build path or the app-root mirror install path.
- This lane did not prove Cloudflare/CDN behavior. If Cloudflare is enabled at launch, MIME and cache headers must be checked against the Cloudflare-served URL.
- The manual manifest sync in `build_webshop_assets.py` should remain visible as a risk. It is acceptable as an LT-local Docker bridge only if the required tests prove it after every rebuild/recreate.
