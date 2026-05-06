#!/usr/bin/env python3
"""Stage approved category images and sync them to Item Group.image.

Default behavior is safe: generate or dry-run only. Use --apply only after the
selection file has explicit Jeff/GL approval flags.

Run:
  python scripts/setup/sync_category_media.py --write-template
  python scripts/setup/sync_category_media.py --selection output/category-media-selection.template.json
  python scripts/setup/sync_category_media.py --selection output/category-media-selection.approved.json --apply
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
STAGE = "/tmp/lt-category-media"
DEFAULT_CANDIDATES = ROOT / "output" / "category-media-candidates.json"
DEFAULT_TEMPLATE = ROOT / "output" / "category-media-selection.template.json"
STAGED_SELECTION = "category-media-selection.json"


class CategoryMediaFail(Exception):
    pass


def run(cmd: list[str], *, timeout: int = 120) -> str:
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise CategoryMediaFail(
            "Command failed:\n"
            + " ".join(cmd)
            + f"\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout


def write_template(candidates_path: Path, template_path: Path) -> None:
    if not candidates_path.exists():
        raise CategoryMediaFail(
            f"Missing candidates report: {candidates_path}. "
            "Run python scripts/verify/category_media_candidates.py first."
        )

    report = json.loads(candidates_path.read_text(encoding="utf-8"))
    selections: dict[str, dict[str, object]] = {}
    for category, data in (report.get("categories") or {}).items():
        candidate = data.get("top_candidate")
        if not candidate:
            selections[category] = {
                "approved": False,
                "source_path": "",
                "review_label": "",
                "review_note": "No candidate found; choose manually before approval.",
            }
            continue
        selections[category] = {
            "approved": False,
            "source_path": candidate["path"],
            "review_label": candidate.get("product_name") or candidate.get("portfolio_title") or candidate["path"],
            "candidate_kind": candidate["kind"],
            "candidate_score": candidate["score"],
            "review_note": "Set approved to true only after Jeff/GL approves this category image.",
        }

    payload = {
        "schema_version": 1,
        "generated_from": _rel(candidates_path),
        "approval_required": True,
        "instructions": "Set approved=true only for category images Jeff/GL approved. Keep source_path exact.",
        "selections": selections,
    }
    template_path.parent.mkdir(parents=True, exist_ok=True)
    template_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[category-media-sync] wrote {template_path.relative_to(ROOT)}")


def stage_selection(selection_path: Path, *, apply: bool) -> None:
    if not selection_path.exists():
        raise CategoryMediaFail(f"Missing selection file: {selection_path}")
    payload = json.loads(selection_path.read_text(encoding="utf-8"))
    selections = payload.get("selections") or {}
    if not selections:
        raise CategoryMediaFail(f"Selection file has no selections: {selection_path}")

    run(["docker", "exec", CONTAINER, "bash", "-lc", f"rm -rf {STAGE} && mkdir -p {STAGE}/images"])
    run(["docker", "cp", str(selection_path), f"{CONTAINER}:{STAGE}/{STAGED_SELECTION}"])

    copied: set[Path] = set()
    for category, selection in selections.items():
        approved = bool(selection.get("approved"))
        source_path = str(selection.get("source_path") or "")
        if apply and not approved:
            continue
        if not source_path:
            raise CategoryMediaFail(f"{category} has no source_path")
        source = (ROOT / source_path).resolve()
        if not source.exists():
            raise CategoryMediaFail(f"{category} source_path does not exist: {source_path}")
        if not source.is_relative_to(ROOT):
            raise CategoryMediaFail(f"{category} source_path is outside repo: {source_path}")
        if source in copied:
            continue
        run(["docker", "cp", str(source), f"{CONTAINER}:{STAGE}/images/{source.name}"])
        copied.add(source)


def bench_execute(*, dry_run: bool) -> Any:
    out = run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            "locally_twisted.seed.sync_category_media.execute",
            "--kwargs",
            repr({"data_dir": STAGE, "selection_file": STAGED_SELECTION, "dry_run": dry_run}),
        ],
        timeout=300,
    )
    try:
        parsed = json.loads(out.strip())
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        return parsed
    except json.JSONDecodeError as exc:
        raise CategoryMediaFail(f"sync_category_media returned non-JSON output:\n{out}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selection", default=str(DEFAULT_TEMPLATE), help="Approved selection JSON path")
    parser.add_argument("--write-template", action="store_true", help="Write a selection template from candidates JSON")
    parser.add_argument("--candidates", default=str(DEFAULT_CANDIDATES), help="Candidates JSON for --write-template")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="Selection template path for --write-template")
    parser.add_argument("--apply", action="store_true", help="Apply approved selections; otherwise dry-run only")
    parser.add_argument("--report", help="Write sync summary JSON to this path")
    args = parser.parse_args()

    try:
        if args.write_template:
            write_template(_rooted(args.candidates), _rooted(args.template))
            return 0
        if not shutil.which("docker"):
            raise CategoryMediaFail("Docker CLI was not found on PATH.")
        stage_selection(_rooted(args.selection), apply=args.apply)
        summary = bench_execute(dry_run=not args.apply)
    except CategoryMediaFail as exc:
        print(f"[category-media-sync] FAIL: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(summary, indent=2)
    if args.report:
        report_path = _rooted(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"[category-media-sync] wrote {report_path.relative_to(ROOT)}")
    print(rendered)
    if not summary.get("ok"):
        return 1
    return 0


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


if __name__ == "__main__":
    sys.exit(main())
