"""Mirror http://5.78.136.133/ for the LT ERPNext rebuild.

Two passes:
  1. crawl4ai BFS walk — captures rendered HTML per route (post-legacy_source-JS DOM).
  2. Asset sweep — parses every captured HTML for <link href>, <script src>,
     <img src>, <source srcset>, and CSS url() refs; downloads each asset
     preserving original directory structure.

Output:
  _resources/retired-source-mirror/
    pages/<slugified-route>.html         rendered DOM per page
    assets/<original-path>/<file>        every linked asset
    manifest.json                         index of pages + assets + status

Failure mode: loud. If a request fails or a parse fails, we log and keep going,
but every failure is in manifest.json so it's visible in the report.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "_resources" / "retired-source-mirror"
PAGES_DIR = OUT / "pages"
ASSETS_DIR = OUT / "assets"
MANIFEST = OUT / "manifest.json"

START_URL = "http://5.78.136.133/"
TARGET_HOST = "5.78.136.133"
MAX_DEPTH = 4
MAX_PAGES = 200  # generous cap; LT has ~70 expected routes


def slug_for(url: str) -> str:
    """Turn a URL into a filesystem-safe slug for naming the page file."""
    p = urlparse(url)
    path = p.path.rstrip("/") or "/index"
    if path == "/":
        path = "/index"
    slug = path.replace("/", "_").strip("_") or "index"
    if p.query:
        q = re.sub(r"[^a-zA-Z0-9._-]", "_", p.query)[:60]
        slug = f"{slug}__q_{q}"
    return slug + ".html"


def asset_local_path(asset_url: str) -> Path | None:
    """Map an absolute asset URL to its local path under assets/.

    Same-host assets keep their original directory structure.
    External assets (Google Fonts CDN, etc.) go under _external/<host>/<path>.
    """
    p = urlparse(asset_url)
    if not p.netloc:
        return None
    if p.netloc == TARGET_HOST or p.netloc == f"{TARGET_HOST}:80":
        rel = p.path.lstrip("/")
    else:
        rel = f"_external/{p.netloc}{p.path}"
    if not rel or rel.endswith("/"):
        return None
    return ASSETS_DIR / rel


def extract_asset_urls(html: str, base_url: str) -> set[str]:
    """Pull every asset URL referenced from the page."""
    soup = BeautifulSoup(html, "lxml")
    urls: set[str] = set()
    for tag, attr in (
        ("link", "href"),
        ("script", "src"),
        ("img", "src"),
        ("source", "src"),
        ("video", "src"),
        ("audio", "src"),
        ("iframe", "src"),
    ):
        for el in soup.find_all(tag):
            v = el.get(attr)
            if v:
                urls.add(urljoin(base_url, v))
    # srcset (img, source)
    for el in soup.find_all(["img", "source"]):
        srcset = el.get("srcset")
        if srcset:
            for piece in srcset.split(","):
                u = piece.strip().split(" ")[0]
                if u:
                    urls.add(urljoin(base_url, u))
    # inline <style> url() refs
    for style in soup.find_all("style"):
        for m in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", style.get_text() or ""):
            urls.add(urljoin(base_url, m))
    return urls


def fetch_asset(url: str, dest: Path, session: requests.Session) -> tuple[str, str | None]:
    """Download one asset to dest. Returns (status, error)."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        r = session.get(url, timeout=20, stream=True)
        if r.status_code != 200:
            return ("error", f"HTTP {r.status_code}")
        with dest.open("wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return ("ok", None)
    except Exception as exc:
        return ("error", f"{type(exc).__name__}: {exc}")


def parse_css_for_assets(css_text: str, base_url: str) -> set[str]:
    """Find url(...) refs inside a CSS file body."""
    out: set[str] = set()
    for m in re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", css_text):
        if m.startswith("data:"):
            continue
        out.add(urljoin(base_url, m))
    return out


async def main() -> int:
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] crawl4ai BFS walk of {START_URL} (max_depth={MAX_DEPTH}, max_pages={MAX_PAGES})")

    browser_cfg = BrowserConfig(headless=True, verbose=False)
    run_cfg = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=MAX_DEPTH,
            include_external=False,
            max_pages=MAX_PAGES,
        ),
        verbose=False,
        page_timeout=30000,
    )

    pages: list[dict] = []
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        results = await crawler.arun(url=START_URL, config=run_cfg)
        if not isinstance(results, list):
            results = [results]
        for res in results:
            if not res.success:
                print(f"  FAIL  {res.url}  ({res.error_message})")
                pages.append({"url": res.url, "status": "error", "error": res.error_message})
                continue
            slug = slug_for(res.url)
            (PAGES_DIR / slug).write_text(res.html or "", encoding="utf-8")
            pages.append({"url": res.url, "status": "ok", "file": f"pages/{slug}", "bytes": len(res.html or "")})
            print(f"  OK    {res.url}  -> pages/{slug}  ({len(res.html or 0)} bytes)")

    print(f"\n[2/3] Extracting asset URLs from {sum(1 for p in pages if p['status']=='ok')} pages")
    asset_urls: set[str] = set()
    for entry in pages:
        if entry["status"] != "ok":
            continue
        try:
            html = (PAGES_DIR / Path(entry["file"]).name).read_text(encoding="utf-8")
        except Exception as exc:
            print(f"  parse-fail  {entry['url']}  {exc}")
            continue
        new = extract_asset_urls(html, entry["url"])
        asset_urls |= new
    print(f"  Found {len(asset_urls)} unique asset URLs")

    print(f"\n[3/3] Downloading assets to {ASSETS_DIR}")
    session = requests.Session()
    session.headers["User-Agent"] = "lt-mirror/1.0"
    asset_log: list[dict] = []
    css_assets: set[str] = set()
    for url in sorted(asset_urls):
        local = asset_local_path(url)
        if local is None:
            asset_log.append({"url": url, "status": "skip", "reason": "no-local-path"})
            continue
        if local.exists() and local.stat().st_size > 0:
            asset_log.append({"url": url, "status": "cached", "file": str(local.relative_to(OUT))})
            continue
        status, err = fetch_asset(url, local, session)
        entry = {"url": url, "status": status, "file": str(local.relative_to(OUT))}
        if err:
            entry["error"] = err
        asset_log.append(entry)
        if status == "ok" and local.suffix.lower() == ".css":
            try:
                css_assets |= parse_css_for_assets(local.read_text(encoding="utf-8", errors="ignore"), url)
            except Exception:
                pass

    # Second-wave: assets referenced from inside CSS files (background-image, fonts).
    new_from_css = css_assets - asset_urls
    if new_from_css:
        print(f"  Second wave: {len(new_from_css)} additional assets from CSS url() refs")
        for url in sorted(new_from_css):
            local = asset_local_path(url)
            if local is None:
                asset_log.append({"url": url, "status": "skip", "reason": "no-local-path", "from": "css"})
                continue
            if local.exists() and local.stat().st_size > 0:
                continue
            status, err = fetch_asset(url, local, session)
            entry = {"url": url, "status": status, "file": str(local.relative_to(OUT)), "from": "css"}
            if err:
                entry["error"] = err
            asset_log.append(entry)

    # Manifest
    summary = {
        "start_url": START_URL,
        "pages_crawled": len(pages),
        "pages_ok": sum(1 for p in pages if p["status"] == "ok"),
        "pages_error": sum(1 for p in pages if p["status"] == "error"),
        "assets_total": len(asset_log),
        "assets_ok": sum(1 for a in asset_log if a["status"] == "ok"),
        "assets_cached": sum(1 for a in asset_log if a["status"] == "cached"),
        "assets_error": sum(1 for a in asset_log if a["status"] == "error"),
        "assets_skip": sum(1 for a in asset_log if a["status"] == "skip"),
        "pages": pages,
        "assets": asset_log,
    }
    MANIFEST.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nManifest: {MANIFEST}")
    print(f"  pages: ok={summary['pages_ok']} error={summary['pages_error']}")
    print(f"  assets: ok={summary['assets_ok']} cached={summary['assets_cached']} error={summary['assets_error']} skip={summary['assets_skip']}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
