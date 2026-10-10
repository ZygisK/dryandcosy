"""Make a flat, self-contained preview of dist/ for sharing as a claude.ai artifact.
Run after build.py and make_pins.py: python3 preview.py -> preview/
"""
import re, shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST, OUT = ROOT / "dist", ROOT / "preview"
css = (DIST / "style.css").read_text()

def flat(path):  # "/shop/laundry/" -> "shop-laundry.html"
    path = path.strip("/")
    return (path.replace("/", "-") or "home") + ".html"

def rewrite(page):
    page = page.replace('<link rel="stylesheet" href="/style.css">', f"<style>{css}</style>")
    def fix(m):
        url = m.group(1)
        path, _, anchor = url.partition("#")
        return f'href="{flat(path)}{"#" + anchor if anchor else ""}"'
    page = re.sub(r'href="(/[^"]*)"', fix, page)
    return page.replace('<a href="guides.html">Guides</a>', '<a href="guides.html">Guides</a><a href="pins.html">Pins</a>', 1)

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
names = []
for f in DIST.rglob("index.html"):
    rel = "/" + str(f.relative_to(DIST).parent).replace(".", "")
    name = flat(rel)
    (OUT / name).write_text(rewrite(f.read_text()))
    names.append(name)

shutil.copytree(DIST / "pins", OUT / "pins")
imgs = sorted(p.name for p in (OUT / "pins").glob("*.png"))
grid = "".join(f'<a href="pins/{n}" target="_blank"><img src="pins/{n}" alt="Pinterest pin" loading="lazy" style="border-radius:8px;border:1px solid var(--line)"></a>' for n in imgs)
home = (OUT / "home.html").read_text()
head, rest = home.split("<main>", 1)
tail = rest.split("</main>", 1)[1]
(OUT / "pins.html").write_text(head + f"""<main><section class="pagehead"><div class="wrap"><h1>Pinterest pins</h1>
<p>Generated automatically from pins.yaml at 1000×1500. Each pin links to a guide.</p></div></section>
<div class="wrap"><section class="section"><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px">{grid}</div></section></div></main>""" + tail)
names.append("pins.html")

main = re.sub(r"<!doctype html><html[^>]*><head>|</head><body>|</body></html>", "", home)
main = re.sub(r"<title>.*?</title>", "<title>Dry &amp; Cosy Preview</title>", main, count=1)
(OUT / "index.html").write_text(main)
print(sorted(names))
