#!/usr/bin/env python3
"""Save the latest built-in Codex image generation from session logs.

Codex's built-in image generation path is OAuth/session backed and does not
need OPENAI_API_KEY. On Wardenclyffe, generated image bytes may appear in the
session JSONL as an image_generation_call.result base64 payload instead of as a
normal file under CODEX_HOME/generated_images. This helper extracts that payload
into a project file so generated assets can be reviewed, finished, and archived.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImageHit:
	session_path: Path
	line_no: int
	event_timestamp: str
	call_id: str
	prompt: str
	image_bytes: bytes
	extension: str

	@property
	def sha256(self) -> str:
		return hashlib.sha256(self.image_bytes).hexdigest()


def detect_extension(image_bytes: bytes) -> str | None:
	if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
		return "png"
	if image_bytes.startswith(b"\xff\xd8\xff"):
		return "jpg"
	if len(image_bytes) >= 12 and image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
		return "webp"
	return None


def decode_image_result(raw: str) -> tuple[bytes, str] | None:
	value = raw.strip()
	if not value:
		return None
	if "," in value and value.startswith("data:image/"):
		value = value.split(",", 1)[1]
	try:
		image_bytes = base64.b64decode(value, validate=True)
	except Exception:
		return None
	extension = detect_extension(image_bytes)
	if not extension:
		return None
	return image_bytes, extension


def session_paths(codex_home: Path, explicit_session: Path | None, since_minutes: int | None) -> list[Path]:
	if explicit_session:
		return [explicit_session]

	root = codex_home / "sessions"
	if not root.exists():
		return []

	now = None
	if since_minutes is not None:
		import time

		now = time.time()

	paths: list[Path] = []
	for path in root.rglob("*.jsonl"):
		try:
			stat = path.stat()
		except OSError:
			continue
		if now is not None and now - stat.st_mtime > since_minutes * 60:
			continue
		paths.append(path)
	return sorted(paths, key=lambda p: p.stat().st_mtime)


def iter_image_hits(paths: list[Path]) -> list[ImageHit]:
	hits: list[ImageHit] = []
	for path in paths:
		try:
			lines = path.read_text(errors="replace").splitlines()
		except OSError:
			continue
		for line_no, line in enumerate(lines, 1):
			try:
				event = json.loads(line)
			except Exception:
				continue
			payload = event.get("payload")
			if not isinstance(payload, dict):
				continue
			if payload.get("type") != "image_generation_call":
				continue
			result = payload.get("result")
			if not isinstance(result, str):
				continue
			decoded = decode_image_result(result)
			if decoded is None:
				continue
			image_bytes, extension = decoded
			hits.append(
				ImageHit(
					session_path=path,
					line_no=line_no,
					event_timestamp=str(event.get("timestamp") or ""),
					call_id=str(payload.get("id") or ""),
					prompt=str(payload.get("revised_prompt") or ""),
					image_bytes=image_bytes,
					extension=extension,
				)
			)
	return hits


def default_out_path(hit: ImageHit, out_dir: Path) -> Path:
	return out_dir / f"codex-image-{hit.sha256[:12]}.{hit.extension}"


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Extract the latest OAuth-backed Codex image generation to a normal image file."
	)
	parser.add_argument(
		"--out",
		type=Path,
		help="Output image path. Defaults to output/imagegen/codex-image-<hash>.<ext>.",
	)
	parser.add_argument("--out-dir", type=Path, default=Path("output/imagegen"))
	parser.add_argument("--session", type=Path, help="Specific Codex session JSONL file to scan.")
	parser.add_argument("--codex-home", type=Path, default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
	parser.add_argument("--since-minutes", type=int, default=1440)
	parser.add_argument("--all", action="store_true", help="Scan all session files instead of the recent window.")
	parser.add_argument("--list", action="store_true", help="List matching image generations without writing a file.")
	parser.add_argument("--force", action="store_true", help="Overwrite the output path if it already exists.")
	args = parser.parse_args()

	since_minutes = None if args.all else args.since_minutes
	paths = session_paths(args.codex_home.expanduser(), args.session, since_minutes)
	hits = iter_image_hits(paths)
	if not hits:
		print("No built-in Codex image_generation_call result found.", file=sys.stderr)
		return 2

	if args.list:
		for index, hit in enumerate(hits[-20:], 1):
			rel_session: Path | str = hit.session_path
			try:
				rel_session = hit.session_path.relative_to(args.codex_home.expanduser())
			except ValueError:
				pass
			prompt = " ".join(hit.prompt.split())
			if len(prompt) > 100:
				prompt = prompt[:97] + "..."
			print(
				f"{index:02d} timestamp={hit.event_timestamp or 'unknown'} "
				f"line={hit.line_no} ext={hit.extension} bytes={len(hit.image_bytes)} "
				f"sha256={hit.sha256[:16]} session={rel_session} prompt={prompt}"
			)
		return 0

	hit = hits[-1]
	out_path = args.out.expanduser() if args.out else default_out_path(hit, args.out_dir.expanduser())
	out_path.parent.mkdir(parents=True, exist_ok=True)
	if out_path.exists() and not args.force:
		print(f"Refusing to overwrite existing file: {out_path}", file=sys.stderr)
		print("Use --force or choose a different --out path.", file=sys.stderr)
		return 3
	out_path.write_bytes(hit.image_bytes)
	print(f"saved={out_path}")
	print(f"bytes={len(hit.image_bytes)}")
	print(f"sha256={hit.sha256}")
	print(f"source_session={hit.session_path}")
	print(f"source_line={hit.line_no}")
	if hit.prompt:
		prompt = " ".join(hit.prompt.split())
		print(f"prompt={prompt[:240]}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
