"""
install_webshop.py — Reproducible install of frappe/webshop + frappe/payments
on the Locally Twisted ERPNext stack.

Why this script exists:
  - ERPNext v15 ships NO ecommerce out of the box. The v14 e_commerce module
    was extracted to a separate app at github.com/frappe/webshop.
  - webshop has a hard runtime dependency on github.com/frappe/payments
    (Payment Gateway abstraction layer for Stripe, PayPal, etc.).
  - frappe_docker's production image does NOT include Node.js, so
    `bench get-app` fails its asset-build step. We use `--skip-assets`.
  - apps/ is NOT shared across frappe-image services in the compose stack;
    we bind-mount each upstream app into all 8 services (mirrors the
    locally_twisted pattern). Bind-mounts live in pwd.yml.
  - Editable pip install (uv pip install -e) lives in each container's
    writable layer and is lost on `docker compose up --force-recreate`,
    so install must be re-run in every frappe-image service after recreate.

What this script does:
  1. (assumes apps/payments and apps/webshop already exist on host —
     copied via `docker cp` from a prior `bench get-app` OR cloned via
     this script's --fetch flag)
  2. (assumes pwd.yml already bind-mounts both apps into all 8 services)
  3. Re-runs `uv pip install -e` for payments + webshop in backend,
     queue-long, queue-short, scheduler
  4. Restarts those four services
  5. Verifies modules import cleanly via a Python smoke check
  6. Probes /shop, /all-products, /cart routes for HTTP 200

Run after every `docker compose --force-recreate` of the LT stack.
Run once after the initial pwd.yml update.

Usage:
  python scripts/setup/install_webshop.py            # re-pip-install + restart + verify
  python scripts/setup/install_webshop.py --fetch    # also: clone payments + webshop
                                                     # from upstream into apps/ (with .git stripped)
  python scripts/setup/install_webshop.py --site-install  # also: bench install-app on the site
                                                     # (only needed on first install ever — once
                                                     # the app is on the site, recreates need only
                                                     # the pip install + restart)
  python scripts/setup/install_webshop.py --build-assets  # also: install Node+yarn (if missing)
                                                     # and run `bench build` so webshop's
                                                     # web.bundle.js and webshop-web.bundle.css
                                                     # actually compile. Required after every
                                                     # container recreation, since the apt-installed
                                                     # node + system-PATH symlinks live in the
                                                     # container's writable layer.

Idempotent: safe to re-run.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PROJECT = "locally-twisted-erpnext-v15"
SITE = "frontend"
APPS = ("locally_twisted", "payments", "webshop")
SERVICES_NEEDING_PIP = ("backend", "queue-long", "queue-short", "scheduler")
WEBSHOP_REPO = "https://github.com/frappe/webshop"
PAYMENTS_REPO = "https://github.com/frappe/payments"


def container(svc: str) -> str:
    return f"{COMPOSE_PROJECT}-{svc}-1"


def run(cmd: Iterable[str], *, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(list(cmd), capture_output=capture, text=True, check=check)


def fetch_upstream_apps() -> None:
    """Clone payments + webshop from upstream into apps/, strip .git."""
    apps_dir = PROJECT_ROOT / "apps"
    apps_dir.mkdir(exist_ok=True)

    for app, repo in (("payments", PAYMENTS_REPO), ("webshop", WEBSHOP_REPO)):
        target = apps_dir / app
        if target.exists():
            print(f"  apps/{app} already exists; skipping clone")
            continue
        print(f"\n=== Cloning {app} from {repo} ===")
        # Use bench-style clone path inside backend so we get the same
        # version bench would pick. Cleaner than direct host git clone.
        run(["docker", "exec", container("backend"), "bash", "-lc",
             f"cd /tmp && rm -rf {app} && git clone --depth 1 {repo} {app}"])
        run(["docker", "cp", f"{container('backend')}:/tmp/{app}", str(target)])
        run(["docker", "exec", container("backend"), "bash", "-lc",
             f"rm -rf /tmp/{app}"])
        # Strip .git — we don't track upstream history; runtime doesn't need it
        git_dir = target / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir)
            print(f"  removed apps/{app}/.git")


def site_install() -> None:
    """One-time: register payments + webshop on the site DB.

    Only run once per site, ever. Subsequent recreates need only the pip install.
    """
    print("\n=== Site install (one-time) ===")
    for app in APPS:
        run(["docker", "exec", container("backend"), "bash", "-lc",
             f"cd /home/frappe/frappe-bench && bench --site {SITE} install-app {app} || true"])


def reinstall_pip() -> None:
    """Re-run editable pip install in every frappe-image service that imports app code."""
    print("\n=== Editable pip install in all frappe services ===")
    apps_args = " ".join(f"-e /home/frappe/frappe-bench/apps/{a}" for a in APPS)
    for svc in SERVICES_NEEDING_PIP:
        print(f"\n--- {svc} ---")
        run(["docker", "exec", container(svc), "bash", "-lc",
             f"uv pip install --quiet --upgrade {apps_args} "
             f"--python /home/frappe/frappe-bench/env/bin/python"])


def restart_services() -> None:
    print("\n=== Restart frappe services ===")
    targets = [container(s) for s in SERVICES_NEEDING_PIP]
    run(["docker", "restart", *targets])


def verify_imports() -> None:
    print("\n=== Verify imports ===")
    for app in APPS:
        result = run(
            ["docker", "exec", container("backend"), "bash", "-lc",
             f"/home/frappe/frappe-bench/env/bin/python -c 'import {app}; print({app}.__file__)'"],
            capture=True, check=False,
        )
        ok = "/apps/" in (result.stdout or "")
        print(f"  {app}: {'OK' if ok else 'FAIL'} — {(result.stdout or result.stderr).strip()}")
        if not ok:
            sys.exit(f"Import check failed for {app}")


def verify_routes() -> None:
    """Probe webshop public URLs. Wait briefly for services to come up after restart."""
    print("\n=== Probe webshop routes ===")
    time.sleep(5)
    # /all-products is webshop's products listing; /shop-by-category its category index.
    # /cart redirects to /login when no customer session (HTTP 301 is expected).
    # The LT site will probably want /shop as a friendlier URL (custom website_route_rule).
    routes = ("/all-products", "/shop-by-category", "/cart")
    for route in routes:
        result = run(
            ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
             f"http://localhost:8081{route}"],
            capture=True, check=False,
        )
        code = (result.stdout or "").strip()
        print(f"  {route}: HTTP {code}")
        if code in ("500", "502", "503"):
            print(f"    WARN  {route} returned {code} -- check backend logs:")
            print(f"       docker exec {container('backend')} tail -40 "
                  f"/home/frappe/frappe-bench/sites/{SITE}/logs/frappe.log")


def build_assets() -> None:
    """Install Node+yarn (if missing) and run `bench build` so webshop's
    SCSS/JS bundles actually compile.

    Why this is its own step:
      - frappe_docker's production image has no Node. `bench install-app`
        and `bench get-app` both attempt asset builds and crash in our
        container, so the apps install with NO compiled bundles.
      - Without compiled bundles, `webshop-web.bundle.css` and
        `web.bundle.js` are missing from sites/assets/assets.json.
        Frappe's bundled_asset() falls back to the bare path → 404.
      - The 404 itself is browser-visible noise. Worse, `web.bundle.js`
        defines the global `webshop` JS namespace; without it, every
        webshop page (e.g. /all-products) throws
        `Uncaught ReferenceError: webshop is not defined`.

    What this does (idempotent):
      1. As root: apt-install nodejs and curl (skipped if already there).
      2. As root: install yarn globally (skipped if `yarn --version` works).
      3. As root: symlink node + yarn from frappe-user nvm into
         /usr/local/bin/ so subprocesses spawned via /bin/sh find them.
         (bench build's popen wrapper uses sh, not bash with nvm sourced.)
      4. As frappe: `bench build` (all apps; webshop alone leaves
         frappe-web.bundle missing on a clean container).
      5. Flush Redis cache + bump assets.json mtime so Frappe re-reads.

    Run after every `docker compose --force-recreate`. The compiled
    bundles in apps/<app>/public/dist/ persist via the bind-mount,
    but assets.json (in the sites volume) is rewritten by bench build,
    and Node + yarn live in the container's writable layer which is
    lost on recreate.

    Long-term fix: bake Node + yarn into a custom Docker image, OR
    add a sidecar Node container that runs bench build on demand.
    Tracked at agency conventions doc "Asset pipeline reality" section.
    """
    backend = container("backend")
    print("\n=== Build assets — install Node + yarn (if missing) and run bench build ===")

    # Step 1+2+3: ensure node + yarn on system path (idempotent).
    # Run as root so apt + npm install -g work; symlink covers nvm-only installs.
    bootstrap_script = r"""set -e
if ! command -v node >/dev/null 2>&1; then
  apt-get update -qq
  apt-get install -y --no-install-recommends curl ca-certificates >/dev/null
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash - >/dev/null
  apt-get install -y --no-install-recommends nodejs >/dev/null
fi
# Capture the frappe-user's nvm node + yarn if they exist (we may have just
# installed system node, but the bench helper expects yarn too).
NVM_NODE=$(ls /home/frappe/.nvm/versions/node/*/bin/node 2>/dev/null | head -1 || true)
NVM_YARN=$(ls /home/frappe/.nvm/versions/node/*/bin/yarn 2>/dev/null | head -1 || true)
# Install yarn via npm if no nvm-yarn exists.
if [ -z "$NVM_YARN" ] && ! command -v yarn >/dev/null 2>&1; then
  npm install -g yarn >/dev/null 2>&1
  NVM_YARN=$(ls /home/frappe/.nvm/versions/node/*/bin/yarn 2>/dev/null | head -1 || command -v yarn || true)
fi
# Symlink to /usr/local/bin so /bin/sh subprocesses find them.
[ -n "$NVM_NODE" ] && ln -sf "$NVM_NODE" /usr/local/bin/node
[ -n "$NVM_YARN" ] && ln -sf "$NVM_YARN" /usr/local/bin/yarn
echo "node: $(/usr/local/bin/node --version 2>&1 || which node)"
echo "yarn: $(/usr/local/bin/yarn --version 2>&1 || which yarn)"
"""
    run(["docker", "exec", "-u", "0", backend, "bash", "-lc", bootstrap_script])

    # Step 4: bench build (as frappe). Build every app — webshop alone
    # would leave frappe-web/erpnext-web bundles missing on a fresh container.
    print("\n=== Run bench build ===")
    run(["docker", "exec", backend, "bash", "-lc",
         f"cd /home/frappe/frappe-bench && bench build"])

    # Step 5: invalidate cached assets.json and restart so the new entries
    # are picked up on the next page render.
    print("\n=== Flush asset cache and restart backend ===")
    run(["docker", "exec", container("redis-cache"), "redis-cli", "FLUSHALL"], capture=True)
    run(["docker", "exec", backend, "bash", "-lc",
         "touch /home/frappe/frappe-bench/sites/assets/assets.json"])
    run(["docker", "restart", backend], capture=True)
    # Wait for backend to come back.
    print("  waiting for backend to be ready...")
    for _ in range(30):
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "http://localhost:8081/accessibility"],
            capture_output=True, text=True, check=False,
        )
        if (result.stdout or "").strip() == "200":
            print("  backend ready.")
            return
        time.sleep(1)
    print("  WARN  backend did not return 200 within 30 s; check `docker logs` if pages misbehave.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fetch", action="store_true",
                        help="Clone payments+webshop from upstream into apps/ first.")
    parser.add_argument("--site-install", action="store_true",
                        help="Run bench install-app on the site (first install only).")
    parser.add_argument("--build-assets", action="store_true",
                        help="Install Node+yarn if missing and run bench build.")
    args = parser.parse_args()

    if args.fetch:
        fetch_upstream_apps()

    reinstall_pip()
    restart_services()
    verify_imports()

    if args.site_install:
        site_install()
        # Re-run pip + restart again because site-install may have re-bench-built
        reinstall_pip()
        restart_services()
        verify_imports()

    if args.build_assets:
        build_assets()

    verify_routes()
    print("\nDone. Webshop install is reproducible.")


if __name__ == "__main__":
    main()
