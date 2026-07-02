"""Fail if the retired source-system label returns to repo paths or text."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = "".join(chr(code) for code in (111, 100, 111, 111))
SKIP_PARTS = {
    ".git",
    "node_modules",
    "__pycache__",
}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".svg",
    ".toml",
    ".txt",
    ".yml",
}


def repo_files() -> list[Path]:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        rel = Path(raw.decode("utf-8", errors="ignore"))
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        full = ROOT / rel
        if full.is_file():
            paths.append(rel)
    return paths


def text_contains_forbidden(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    data = (ROOT / path).read_bytes()
    if FORBIDDEN.encode("ascii") not in data.lower():
        return False
    text = data.decode("utf-8", errors="ignore").lower()
    return FORBIDDEN in text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    bad_paths: list[str] = []
    bad_text: list[str] = []

    for rel in repo_files():
        rel_text = rel.as_posix().lower()
        if FORBIDDEN in rel_text:
            bad_paths.append(rel.as_posix())
        if text_contains_forbidden(rel):
            bad_text.append(rel.as_posix())

    if bad_paths or bad_text:
        print("FAIL: forbidden retired-source label found.")
        if bad_paths:
            print("Paths:")
            for path in bad_paths[:50]:
                print(f"  - {path}")
        if bad_text:
            print("Text:")
            for path in bad_text[:50]:
                print(f"  - {path}")
        return 1

    print("PASS: forbidden retired-source label absent from repo paths and text.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
