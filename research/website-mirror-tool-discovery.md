# Website Mirror Tool Discovery
# Job: mirror http://5.78.136.133/ (legacy_source/QWeb, JS-enhanced) for Frappe v15 port

---

## Top Recommendation: crawl4ai

**GitHub:** https://github.com/unclecode/crawl4ai (58k+ stars)
**Docs:** https://docs.crawl4ai.com/

**Why it wins for this job:**
- Uses Playwright under the hood — renders the full legacy_source/QWeb JS layer before capturing HTML, so carousels, lazy-loaded images, and client-side state are included.
- Built-in BFS deep crawler (`BFSDeepCrawlStrategy`) with `max_depth`, `max_pages`, domain-boundary locks — mirrors an entire site in one script, not page-by-page.
- Pure Python, Apache 2.0, no API key, no SaaS account. Installs cleanly into the existing Python 3.12 venv.
- Returns both raw HTML and markdown per page — raw HTML is the useful output for CMS porting (inspect structure, extract content blocks).
- Actively maintained v0.8.x; deep-crawl feature is documented and stable as of 2026-04-30.

**Install (Bash, Python 3.12 venv):**
```bash
pip install crawl4ai
crawl4ai-setup          # downloads Chromium automatically
crawl4ai-doctor         # verify install
```

**Run command (save all pages as HTML):**
```python
# mirror.py — drop in project root, run: python mirror.py
import asyncio, os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy

TARGET = "http://5.78.136.133/"
OUT_DIR = "./mirror-output"

async def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    strategy = BFSDeepCrawlStrategy(max_depth=4, include_external=False)
    config = CrawlerRunConfig(deep_crawl_strategy=strategy)
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        results = await crawler.arun(TARGET, config=config)
        for r in (results if isinstance(results, list) else [results]):
            slug = r.url.replace("http://", "").replace("/", "__").strip("_")
            with open(f"{OUT_DIR}/{slug}.html", "w", encoding="utf-8") as f:
                f.write(r.html or "")
            print(f"saved: {slug}")

asyncio.run(main())
```

**Known limitations:**
- Saves rendered HTML snapshots — does not download binary assets (images, fonts, CSS files) to disk. For a CMS port you want the HTML structure anyway; assets can be fetched separately via their URLs found in the HTML.
- Does not replay authenticated sessions by default; legacy_source's public shop is unauthenticated so this is not a blocker here.

---

## Backup Option 1: single-file-cli

**GitHub:** https://github.com/gildas-lormeau/single-file-cli (Node.js CLI, uses Chromium DevTools Protocol)

- Saves each page as one self-contained HTML file with all CSS, images, and fonts inlined as data URIs — most faithful visual snapshot possible.
- JS-rendered: yes, via headless Chromium.
- Limitation: one URL at a time; requires a separate shell loop to crawl a multi-page site. Not a site-walker, a page-saver. Best as a companion to crawl4ai: crawl4ai discovers all URLs, single-file-cli saves pixel-perfect snapshots.
- Install: `npm install -g single-file-cli` (requires Node.js).
- Run: `single-file http://5.78.136.133/shop ./shop.html`

## Backup Option 2: Browsertrix Crawler

**GitHub:** https://github.com/webrecorder/browsertrix-crawler

- Webrecorder project; high-fidelity browser-based archival crawler in a Docker container.
- Captures WARC archives (web archival format) — complete fidelity including JS state, video, behaviors.
- Limitation for this job: Docker-only, WARC output requires a WARC viewer (ReplayWeb.page) to browse — not a folder of .html files you can diff and port. Overpowered for a CMS migration reference.
- Install: `docker pull webrecorder/crawlee` then `docker run webrecorder/browsertrix-crawler ...`

---

## Ruled Out

| Tool | Reason |
|------|--------|
| **httrack** | Cannot execute JavaScript. Returns empty shells on legacy_source/QWeb pages. Confirmed by HTTrack's own forum and 2026 comparison sources. |
| **wget --mirror** | Same as httrack: static HTML fetcher only. legacy_source renders content via JavaScript; wget captures the unrendered skeleton. |
| **websnap** (uirip/websnap) | 1 GitHub star, effectively unmaintained, Node.js only. Interesting architecture (state-tree exploration) but too immature to rely on. |
| **Firecrawl** | Excellent tool; requires API key + SaaS account for hosted use (self-host possible but heavy setup). No advantage over crawl4ai for this job given the free/local requirement. |

---

## Claude-Skill Check

**No.** No github-hosted Claude skill exists for this job. Checked:
- `github.com/anthropics/skills` — document-focused skills only (PDF, DOCX, PPTX, XLSX). No site-mirror or web-archive skill.
- `github.com/travisvn/awesome-claude-skills` — no website mirroring entry.
- Searched for `clone-site`, `mirror-site`, `site-mirror`, `web-mirror`, `archive-site` in Claude skill registries — no results.

---

## Sources
- https://github.com/unclecode/crawl4ai
- https://docs.crawl4ai.com/core/deep-crawling/
- https://docs.crawl4ai.com/core/quickstart/
- https://docs.crawl4ai.com/core/installation/
- https://github.com/gildas-lormeau/single-file-cli
- https://github.com/webrecorder/browsertrix-crawler
- https://github.com/uirip/websnap
- https://forum.httrack.com/readmsg/26620/index.html (HTTrack JS limitation)
- https://github.com/anthropics/skills
- https://github.com/travisvn/awesome-claude-skills
