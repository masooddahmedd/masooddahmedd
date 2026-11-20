# Renders README.md with GitHub's own Markdown API and wraps it in GitHub's stylesheet, dark and
# light, at the width of the profile README column, so the preview matches what visitors see.
#
#   python tools/render_preview.py      # writes .preview/readme_dark.html and readme_light.html
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5.8.1/github-markdown-{}.css"

md = (ROOT / "README.md").read_text(encoding="utf-8")
req = urllib.request.Request(
    "https://api.github.com/markdown",
    data=json.dumps({"text": md, "mode": "gfm"}).encode(),
    headers={"Accept": "application/vnd.github+json", "Content-Type": "application/json"},
)
body = urllib.request.urlopen(req, timeout=30).read().decode().replace('src="assets/', 'src="../assets/')
(ROOT / ".preview").mkdir(exist_ok=True)
for theme, bg, border in (("dark", "#0d1117", "#30363d"), ("light", "#ffffff", "#d0d7de")):
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>profile preview ({theme})</title>
<link rel="stylesheet" href="{CSS.format(theme)}">
<style>body{{background:{bg};margin:0;padding:24px}}
.markdown-body{{box-sizing:border-box;max-width:880px;margin:0 auto;padding:24px;border:1px solid {border};border-radius:6px}}</style>
</head><body><article class="markdown-body">{body}</article></body></html>"""
    (ROOT / ".preview" / f"readme_{theme}.html").write_text(page, encoding="utf-8")
print("ok")
