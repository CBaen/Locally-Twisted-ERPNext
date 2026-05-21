#!/usr/bin/env python3
"""Build Webshop assets safely, then verify manifest assets through nginx."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
BACKEND_CONTAINER = "locally-twisted-erpnext-v15-backend-1"
FRONTEND_CONTAINER = "locally-twisted-erpnext-v15-frontend-1"
BASE_URL = "http://localhost:8081"
ASSETS_JSON = "/home/frappe/frappe-bench/sites/assets/assets.json"
IMAGE_TAG = "locally-twisted-erpnext:v15"
COMPOSE_FILE = ROOT / "Locally-Twisted-Backend" / "frappe_docker" / "pwd.yml"
COMPOSE_PROJECT = "locally-twisted-erpnext-v15"


def run(cmd: list[str], *, cwd: Path = ROOT, capture: bool = False) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        check=True,
        capture_output=capture,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--durable-rebuild",
        action="store_true",
        help="Rebuild locally-twisted-erpnext:v15 and recreate the stack so bundles survive container recreate.",
    )
    mode.add_argument(
        "--runtime-only",
        action="store_true",
        help="Emergency local repair only. Rebuilds frontend-container assets in the writable layer.",
    )
    return parser.parse_args()


def manifest_asset_path(key: str) -> str:
    code = (
        "import json;"
        f"print(json.load(open({ASSETS_JSON!r}))[{key!r}])"
    )
    result = run(
        ["docker", "exec", BACKEND_CONTAINER, "python", "-c", code],
        capture=True,
    )
    return result.stdout.strip()


def content_type_matches(content_type: str, expected: str) -> bool:
    content_type = content_type.lower()
    if expected == "css":
        return "text/css" in content_type
    if expected == "javascript":
        return "javascript" in content_type or "ecmascript" in content_type
    return True


def verify_asset(path: str, expected: str) -> None:
    url = BASE_URL.rstrip("/") + path
    request = Request(url, method="HEAD", headers={"User-Agent": "LT Webshop asset build verifier"})
    with urlopen(request, timeout=20) as response:
        content_type = response.headers.get("Content-Type", "")
        if response.status != 200 or not content_type_matches(content_type, expected):
            raise RuntimeError(f"{url} returned HTTP {response.status} with {content_type!r}")
    print(f"  PASS {url} returned {expected}", flush=True)


def sync_manifest_to_baked_webshop_assets() -> None:
    print("\n=== Align shared assets manifest to baked Webshop files ===", flush=True)
    script = r"""
import glob
import json
from pathlib import Path

bench = Path("/home/frappe/frappe-bench")
assets = bench / "sites" / "assets"
webshop_public = bench / "apps" / "webshop" / "webshop" / "public"

def one(pattern):
    matches = [Path(path) for path in glob.glob(str(pattern))]
    matches = [path for path in matches if not path.name.endswith(".map")]
    if not matches:
        raise SystemExit(f"missing Webshop asset for {pattern}")
    matches.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return matches[0]

css = one(webshop_public / "dist" / "css" / "webshop-web.bundle.*.css")
rtl_css = one(webshop_public / "dist" / "css-rtl" / "webshop-web.bundle.*.css")
js = one(webshop_public / "dist" / "js" / "web.bundle.*.js")

assets_json_path = assets / "assets.json"
assets_rtl_json_path = assets / "assets-rtl.json"

assets_json = json.loads(assets_json_path.read_text())
assets_rtl_json = json.loads(assets_rtl_json_path.read_text())

def public_asset_path(path):
    return "/assets/webshop/" + str(path.relative_to(webshop_public)).replace("\\", "/")

assets_json["webshop-web.bundle.css"] = public_asset_path(css)
assets_json["web.bundle.js"] = public_asset_path(js)
assets_rtl_json["rtl_webshop-web.bundle.css"] = public_asset_path(rtl_css)

assets_json_path.write_text(json.dumps(assets_json, indent=1, sort_keys=True) + "\n")
assets_rtl_json_path.write_text(json.dumps(assets_rtl_json, indent=1, sort_keys=True) + "\n")

print(assets_json["webshop-web.bundle.css"])
print(assets_json["web.bundle.js"])
print(assets_rtl_json["rtl_webshop-web.bundle.css"])
"""
    run(["docker", "exec", BACKEND_CONTAINER, "python", "-c", script])


def durable_rebuild() -> None:
    print("\n=== Rebuild durable custom ERPNext image ===", flush=True)
    run(["docker", "build", "-f", "docker/Dockerfile", "-t", IMAGE_TAG, "."])

    print("\n=== Recreate stack from rebuilt image ===", flush=True)
    run(
        [
            "docker",
            "compose",
            "-p",
            COMPOSE_PROJECT,
            "-f",
            str(COMPOSE_FILE),
            "up",
            "-d",
            "--force-recreate",
        ]
    )
    sync_manifest_to_baked_webshop_assets()


def runtime_only_build() -> None:
    print(
        "\n=== Runtime-only Webshop asset repair ===\n"
        "WARNING: this writes bundles into the running frontend container only. "
        "A frontend recreate can remove them; use --durable-rebuild for launch proof.",
        flush=True,
    )
    print("\n=== Build Webshop assets in frontend/static-serving container ===", flush=True)
    run(
        [
            "docker",
            "exec",
            FRONTEND_CONTAINER,
            "sh",
            "-c",
            "cd /home/frappe/frappe-bench && bench build --app webshop --production",
        ]
    )


def verify_manifest_assets() -> None:
    print("\n=== Verify manifest paths are served by nginx ===", flush=True)
    checks = (
        ("webshop-web.bundle.css", "css"),
        ("web.bundle.js", "javascript"),
    )
    for key, expected in checks:
        verify_asset(manifest_asset_path(key), expected)


def main() -> int:
    args = parse_args()
    if args.durable_rebuild:
        durable_rebuild()
    elif args.runtime_only:
        runtime_only_build()

    print("\n=== Clear Frappe website and asset path caches ===", flush=True)
    run([sys.executable, str(ROOT / "scripts" / "dev" / "clear_website_cache.py")])

    verify_manifest_assets()
    print("\nDone. Webshop bundle manifest and served public assets are aligned.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
