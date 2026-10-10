"""Render photo-led Pinterest pins (1000x1500 JPG) from pins.yaml with headless Chromium.

Runs in GitHub Actions (.github/workflows/pins.yml), which has internet access for
Google Fonts and Unsplash. Browser typesetting gives proper kerning and the exact
look of the website. Output: static/pins/v2/<slug>.jpg + static/pins/index.html
(a preview sheet). Existing images are kept unless --force is passed.
"""
import html
import sys
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "static" / "pins" / "v2"
FORCE = "--force" in sys.argv

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;1,6..96,400&family=Hanken+Grotesk:wght@500&display=block" rel="stylesheet">
<style>
html,body{{margin:0;width:1000px;height:1500px}}
.pin{{width:1000px;height:1500px;position:relative;overflow:hidden;font-family:'Hanken Grotesk',sans-serif}}
.pin img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.pin::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,22,19,0) 38%,rgba(18,22,19,.72) 100%)}}
.cap{{position:absolute;left:68px;right:68px;bottom:68px;z-index:1;color:#fff}}
.cap h1{{font:400 {size}px/1.04 'Bodoni Moda',serif;margin:0;letter-spacing:-.01em;text-wrap:balance}}
.cap h1 em{{font-style:italic}}
.cap p{{margin:32px 0 0;font-size:28px;letter-spacing:.06em;opacity:.9}}
</style></head><body><div class="pin">
<img src="https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&h=1500&q=90">
<div class="cap"><h1>{head}{tail}</h1><p>dryandcosy.com</p></div></div></body></html>"""

def page_html(p):
    head = html.escape(p["head"])
    tail = f" <em>{html.escape(p['tail'])}</em>" if p.get("tail") else ""
    words = len((p["head"] + " " + (p.get("tail") or "")).split())
    size = 100 if words <= 6 else 90 if words <= 8 else 80
    return TEMPLATE.format(photo=p["photo"], head=head, tail=tail, size=size)

def main():
    pins = yaml.safe_load((ROOT / "pins.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1500})
        for p in pins:
            out = OUT / f"{p['slug']}.jpg"
            if out.exists() and not FORCE:
                continue
            page.set_content(page_html(p), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            page.screenshot(path=str(out), type="jpeg", quality=88)
            made += 1
            print("rendered", out.name)
        browser.close()
    cards = "".join(
        f'<figure><img src="v2/{p["slug"]}.jpg" alt=""><figcaption><b>{html.escape(p["board"])}</b><br>'
        f'{html.escape(p["title"])}<br><small>{html.escape(p["url"])} [{html.escape(p.get("status", "draft"))}]</small></figcaption></figure>'
        for p in pins if (OUT / f"{p['slug']}.jpg").exists())
    (OUT.parent / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Pin preview</title>'
        '<style>body{font:14px system-ui;margin:24px;background:#eeebe4}div{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px}'
        'img{width:100%;display:block}figure{margin:0}figcaption{margin-top:6px;color:#333}</style>'
        f'<h1>Pin preview</h1><div>{cards}</div>')
    print(f"rendered {made} new pins")

if __name__ == "__main__":
    main()
