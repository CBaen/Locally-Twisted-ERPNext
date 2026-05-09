"""Build static HTML previews from contestant Jinja templates + Python controllers."""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTEST_DIR = BASE
GALLERY_DIR = os.path.join(BASE, "render-gallery")

PAGES = ["civic-community", "corporate-events", "private-celebrations", "schools-campuses"]
PAGE_FILES = {
    "civic-community": "civic_community",
    "corporate-events": "corporate_events",
    "private-celebrations": "private_celebrations",
    "schools-campuses": "schools_campuses",
}
CONCEPTS = {
    1: "Audience Authority",
    2: "The Right Room",
    3: "Made For You (anxiety-first)",
    4: "One System, Four Buyers",
    5: "Proof-First Buyer Suite",
    6: "Buyer-Scoped Authority",
    7: "The Proof is in the Place",
    8: "Made For You (named-promise)",
}
SCORES = {1: 26.00, 2: 26.00, 3: 24.29, 4: 24.57, 5: 26.00, 6: 24.71, 7: 26.71, 8: 24.29}
RANKS = {7: "1st", 1: "2nd (tie)", 2: "2nd (tie)", 5: "2nd (tie)", 6: "5th", 4: "6th", 3: "7th", 8: "8th"}

LT_CSS = """
:root {
  --lt-navy:#0E2240;--lt-slate:#2F3A4A;--lt-slate-blue:#2C3E5D;
  --lt-crimson:#B31B34;--lt-brass:#B89A5B;--lt-warm-white:#FAF7F2;
  --lt-white:#FFFFFF;--lt-near-white:#FBFBFB;--lt-near-black:#0A0A0B;
  --lt-soft-gray:#595A5C;--lt-stone:#E7E5E1;--lt-sandstone:#D9C7B3;
  --lt-sand:#D9C7B3;--lt-berry:#6B2D5E;--lt-ink:#0A0A0B;
  --lt-font-heading:'Cormorant Garamond',Georgia,serif;
  --lt-font-display:'Cinzel',Georgia,serif;
  --lt-font-body:'Lato',system-ui,sans-serif;
  --lt-font-accent:'Cormorant Garamond',Georgia,serif;
}
*{box-sizing:border-box;}
body{margin:0;padding:0;font-family:var(--lt-font-body);background:var(--lt-warm-white);}
img{max-width:100%;height:auto;}
a{color:inherit;}
"""

NAVBAR = """<nav style="background:var(--lt-navy);padding:12px 24px;display:flex;align-items:center;justify-content:space-between;">
  <span style="font-family:var(--lt-font-heading);color:var(--lt-warm-white);font-size:1.3rem;font-weight:700;">Locally Twisted</span>
  <span style="color:var(--lt-brass);font-size:0.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;">Preview Harness</span>
</nav>"""

FOOTER = """<footer style="background:var(--lt-near-black);padding:32px 24px;text-align:center;color:rgba(250,247,242,.5);font-size:.8rem;">
  Locally Twisted &middot; West Jordan, UT &middot; (801) 285-0860 &middot; hi@locallytwisted.com
</footer>"""


def extract_ctx(py_path):
    with open(py_path, "r", encoding="utf-8") as f:
        source = f.read()
    mock = {"frappe": type("F", (), {"_": lambda s, x: x, "throw": lambda s, x: None})(), "__name__": "__main__"}
    try:
        exec(compile(source, py_path, "exec"), mock)
    except Exception as e:
        print(f"  exec warn: {e}")
    ctx = {k.lower(): v for k, v in mock.items() if k.isupper() and isinstance(v, (list, dict))}
    if "get_context" in mock:
        class P(dict):
            __setattr__ = dict.__setitem__
            __getattr__ = lambda s, k: s.get(k, "")
        p = P()
        try:
            mock["get_context"](p)
            ctx.update(p)
        except Exception as e:
            print(f"  ctx warn: {e}")
    return ctx


def render(html, ctx):
    from jinja2 import Environment, BaseLoader, Undefined
    class SU(Undefined):
        def _fail_with_undefined_error(self, *a, **k): return ""
        __str__ = lambda s: ""
        __iter__ = lambda s: iter([])
        __len__ = lambda s: 0
        __bool__ = lambda s: False
    html = re.sub(r"\{%-?\s*extends[^%]*-?%\}", "", html)
    html = re.sub(r"\{%-?\s*block\s+\w+\s*-?%\}", "", html)
    html = re.sub(r"\{%-?\s*endblock\s*-?%\}", "", html)
    env = Environment(loader=BaseLoader(), undefined=SU, autoescape=False)
    try:
        return env.from_string(html).render(**ctx)
    except Exception as e:
        print(f"  jinja warn: {e}")
        html = re.sub(r"\{#.*?#\}", "", html, flags=re.DOTALL)
        html = re.sub(r"\{%.*?%\}", "", html, flags=re.DOTALL)
        html = re.sub(r"\{\{.*?\}\}", "", html, flags=re.DOTALL)
        return html


def fix_paths(html):
    html = re.sub(r"url\(['\"]?/assets/locally_twisted/images/[^'\")\s]+['\"]?\)",
                  "url('https://placehold.co/800x600/2F3A4A/B89A5B?text=LT+Photo')", html)
    html = re.sub(r'src=["\']?/assets/locally_twisted/icons/[^"\'>\s]+["\']?',
                  'src="https://placehold.co/44x44/B89A5B/FAF7F2?text=ico"', html)
    html = re.sub(r'src=["\']?/assets/locally_twisted/[^"\'>\s]+["\']?',
                  'src="https://placehold.co/400x300/E7E5E1/595A5C?text=Asset"', html)
    return html


def wrap(content, c, page, ctx):
    concept = CONCEPTS[c]
    score = SCORES[c]
    rank = RANKS[c]
    label = page.replace("-", " ").title()
    fonts = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Cinzel:wght@400;600;700&family=Lato:ital,wght@0,300;0,400;0,700;1,400&display=swap"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>C{c}: {concept} - {label}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>
{LT_CSS}
.preview-bar{{background:var(--lt-near-black);color:var(--lt-brass);font-family:var(--lt-font-body);font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 16px;text-align:center;border-bottom:1px solid rgba(184,154,91,.3);}}
</style>
</head>
<body>
<div class="preview-bar">C{c} &middot; {concept} &middot; {label} &middot; Score {score}/30 &middot; Rank {rank} &middot; Static preview harness</div>
{NAVBAR}
{content}
{FOOTER}
</body>
</html>"""


def build_all():
    errors = []
    for c in range(1, 9):
        c_dir = os.path.join(CONTEST_DIR, f"contestant-{c}")
        out_dir = os.path.join(GALLERY_DIR, "preview", f"contestant-{c}")
        os.makedirs(out_dir, exist_ok=True)
        for page in PAGES:
            pf = PAGE_FILES[page]
            html_path = os.path.join(c_dir, page, f"{pf}.html")
            py_path = os.path.join(c_dir, page, f"{pf}.py")
            print(f"C{c}/{page}...", end=" ")
            if not os.path.exists(html_path):
                print("MISSING")
                errors.append(f"C{c}/{page}: html missing")
                continue
            ctx = extract_ctx(py_path) if os.path.exists(py_path) else {}
            with open(html_path, "r", encoding="utf-8") as f:
                raw = f.read()
            rendered = render(raw, ctx)
            rendered = fix_paths(rendered)
            final = wrap(rendered, c, page, ctx)
            out = os.path.join(out_dir, f"{page}.html")
            with open(out, "w", encoding="utf-8") as f:
                f.write(final)
            print("OK")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  {e}")
    print("\nDone.")


if __name__ == "__main__":
    build_all()
