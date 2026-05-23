#!/usr/bin/env python3
"""Verify the Frappe Cloud app-root mirror contains required source files.

This verifier is intentionally read-only. Real mode clones the app-root mirror
into a temporary directory, compares required files against the local
`apps/locally_twisted` source tree, and deletes the clone before exit.
Self-test mode is offline and safe for `npm run test:release-prevention`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_APP_SOURCE_ROOT = ROOT / "apps" / "locally_twisted"
DEFAULT_APP_MIRROR = "https://github.com/CBaen/Locally-Twisted-Frappe-App.git"
DEFAULT_REQUIRED_FILES = (
    "locally_twisted/staging_owner_review_preflight.py",
    "locally_twisted/staging_owner_review_bootstrap.py",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run offline contract checks.")
    parser.add_argument("--mirror-url", default=DEFAULT_APP_MIRROR)
    parser.add_argument("--mirror-ref", default="main")
    parser.add_argument("--source-root", type=Path, default=DEFAULT_APP_SOURCE_ROOT)
    parser.add_argument(
        "--required-file",
        action="append",
        dest="required_files",
        help="App-root-relative path required in both source and mirror. Can be repeated.",
    )
    parser.add_argument("--output", type=Path, help="Write freshness result JSON to this path.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        if args.self_test:
            result = run_self_test()
        else:
            required_files = tuple(args.required_files or DEFAULT_REQUIRED_FILES)
            result = run_real_check(args.mirror_url, args.mirror_ref, args.source_root, required_files)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                result["output"] = str(args.output)
    except Exception as exc:
        result = {"ok": False, "failures": [f"{type(exc).__name__}: {exc}"]}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[FRAPPE CLOUD APP MIRROR FRESHNESS] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in result.get("failures", []):
            print(f"  - {failure}")
        if result.get("output"):
            print(f"  output: {result['output']}")
    return 0 if result["ok"] else 1


def run_real_check(
    mirror_url: str,
    mirror_ref: str,
    source_root: Path,
    required_files: tuple[str, ...],
) -> dict[str, Any]:
    source_root = source_root.resolve()
    if not source_root.exists():
        raise RuntimeError(f"source app root is missing: {source_root}")
    source_commit = git_output(["git", "rev-parse", "HEAD"], ROOT)
    ensure_required_files_are_clean(required_files)
    normalized_required_files = tuple(normalize_required_file(path) for path in required_files)
    mirror_hash = resolve_mirror_ref(mirror_url, mirror_ref)

    with tempfile.TemporaryDirectory(prefix="lt-app-mirror-") as tmp:
        mirror_root = Path(tmp) / "mirror"
        git_output(
            ["git", "clone", "--depth", "1", "--branch", mirror_ref, "--quiet", mirror_url, str(mirror_root)],
            ROOT,
            timeout=120,
        )
        check = check_required_files(source_root, mirror_root, normalized_required_files)

    return {
        "ok": not check["failures"],
        "failures": check["failures"],
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "source_commit": source_commit,
        "mirror_url": mirror_url,
        "mirror_ref": mirror_ref,
        "mirror_hash": mirror_hash,
        "required_files": check["files"],
        "provider_mutation_executed": False,
    }


def check_required_files(
    source_root: Path,
    mirror_root: Path,
    required_files: tuple[str, ...],
) -> dict[str, Any]:
    failures: list[str] = []
    rows: list[dict[str, Any]] = []
    for rel in required_files:
        source_path = source_root / rel
        mirror_path = mirror_root / rel
        row: dict[str, Any] = {
            "path": rel,
            "source_exists": source_path.exists(),
            "mirror_exists": mirror_path.exists(),
        }
        if not source_path.exists():
            failures.append(f"source required file is missing: {rel}")
        if not mirror_path.exists():
            failures.append(f"app mirror required file is missing: {rel}")
        if source_path.exists() and mirror_path.exists():
            source_sha = sha256_file(source_path)
            mirror_sha = sha256_file(mirror_path)
            row["source_sha256"] = source_sha
            row["mirror_sha256"] = mirror_sha
            row["matches"] = source_sha == mirror_sha
            if source_sha != mirror_sha:
                failures.append(f"app mirror required file differs from source: {rel}")
        else:
            row["matches"] = False
        rows.append(row)
    return {"failures": failures, "files": rows}


def normalize_required_file(rel_path: str) -> str:
    path = Path(rel_path)
    if path.is_absolute():
        raise RuntimeError(f"required file must be app-root-relative, not absolute: {rel_path}")
    parts = path.as_posix().split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise RuntimeError(f"required file must stay within the app root: {rel_path}")
    return path.as_posix()


def ensure_required_files_are_clean(required_files: tuple[str, ...]) -> None:
    app_relative_paths = [f"apps/locally_twisted/{normalize_required_file(path)}" for path in required_files]
    status = git_output(["git", "status", "--porcelain=v1", "--", *app_relative_paths], ROOT)
    if status:
        raise RuntimeError(
            "required source files must be clean before mirror freshness proof; git status: "
            + status.replace("\n", "; ")
        )


def run_self_test() -> dict[str, Any]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="lt-app-mirror-selftest-") as tmp:
        base = Path(tmp)
        source_root = base / "source"
        mirror_root = base / "mirror"
        rel = "locally_twisted/staging_owner_review_preflight.py"
        write_text(source_root / rel, "def preflight():\n    return True\n")
        write_text(mirror_root / rel, "def preflight():\n    return True\n")
        if check_required_files(source_root, mirror_root, (rel,))["failures"]:
            failures.append("matching source and mirror file did not pass")

        shutil.rmtree(mirror_root)
        mirror_root.mkdir(parents=True)
        if not check_required_files(source_root, mirror_root, (rel,))["failures"]:
            failures.append("missing mirror file did not fail")

        write_text(mirror_root / rel, "def preflight():\n    return False\n")
        if not check_required_files(source_root, mirror_root, (rel,))["failures"]:
            failures.append("different mirror file did not fail")

        shutil.rmtree(source_root)
        source_root.mkdir(parents=True)
        if not check_required_files(source_root, mirror_root, (rel,))["failures"]:
            failures.append("missing source file did not fail")
        for unsafe in ("../secret.txt", "/tmp/secret.txt", "locally_twisted/../secret.txt"):
            try:
                normalize_required_file(unsafe)
                failures.append(f"unsafe required path did not fail: {unsafe}")
            except RuntimeError:
                pass
    return {"ok": not failures, "failures": failures}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_mirror_ref(mirror_url: str, mirror_ref: str) -> str:
    ref_name = mirror_ref if mirror_ref.startswith("refs/") else f"refs/heads/{mirror_ref}"
    output = git_output(["git", "ls-remote", mirror_url, ref_name], ROOT, timeout=30)
    if not output:
        output = git_output(["git", "ls-remote", mirror_url, "HEAD"], ROOT, timeout=30)
    head = output.split()[0] if output else ""
    if len(head) != 40:
        raise RuntimeError(f"could not resolve app mirror ref {mirror_ref!r} from {mirror_url!r}")
    return head.lower()


def git_output(command: list[str], cwd: Path, timeout: int = 30) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise RuntimeError(message)
    return result.stdout.strip()


if __name__ == "__main__":
    sys.exit(main())
