"""Render Pinterest pins (1000x1500 PNG) from pins.yaml and write a bulk-upload CSV.

Run: python3 make_pins.py
Output: static/pins/*.png (copied to the site by build.py) + pins_bulk.csv (Pinterest bulk create format).
Add AI background images by setting `image:` on a pin (file in pins/images/).
"""
import base64, csv, html, re
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
SITE = yaml.safe_load((ROOT / "site.yaml").read_text())
OUT = ROOT / "static" / "pins"  # build.py copies static/ into dist/
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=Figtree:wght@600;700&display=swap" rel="stylesheet">'

BASE_CSS = """
*{box-sizing:border-box;margin:0}
body{width:1000px;height:1500px;font-family:'Figtree',system-ui,sans-serif;color:#2b2d2a;overflow:hidden}
.pin{width:1000px;height:1500px;position:relative;background:#f6f6f2;display:flex;flex-direction:column}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.brand{position:absolute;bottom:44px;left:0;right:0;text-align:center;font-weight:800;letter-spacing:3px;font-size:26px;color:#3f5745}
.serif{font-family:'Manrope',system-ui,sans-serif;font-weight:800;letter-spacing:-.02em;line-height:1.08}
"""

def esc(s):
    return html.escape(str(s or ""))

def bg(pin):
    img = pin.get("image")
    if img:
        data = base64.b64encode((ROOT / "pins/images" / img).read_bytes()).decode()
        return f'<div class="bg" style="background-image:url(data:image/jpeg;base64,{data})"></div>'
    # default: soft sage pattern
    return '<div class="bg" style="background:radial-gradient(circle at 20% 15%,#e6ede2 0,transparent 45%),radial-gradient(circle at 85% 80%,#dfe7dc 0,transparent 40%),#f6f6f2"></div>'

def headline(p):
    return f"""{bg(p)}<div style="position:relative;margin:auto 60px;background:rgba(255,253,248,.94);border-radius:36px;padding:70px 60px 80px;text-align:center">
<div style="display:inline-block;background:#a7834c;color:#fff;font-weight:800;letter-spacing:3px;font-size:30px;padding:10px 26px;border-radius:999px">{esc(p.get('kicker'))}</div>
<h1 class="serif" style="font-size:104px;margin:40px 0 30px;color:#2b2d2a">{esc(p['title'])}</h1>
<div style="height:6px;width:120px;background:#7d977f;margin:0 auto 30px;border-radius:3px"></div>
<p style="font-size:42px;font-weight:600;color:#3f5745;line-height:1.3">{esc(p.get('sub'))}</p></div>"""

def problem_fix(p):
    return f"""{bg(p)}<div style="position:relative;display:flex;flex-direction:column;height:100%;padding:70px 60px 120px;gap:30px">
<div style="flex:1;background:#a7834c;color:#fff;border-radius:36px;padding:56px;display:flex;flex-direction:column;justify-content:center">
<div style="font-weight:800;letter-spacing:4px;font-size:32px;opacity:.9">THE PROBLEM</div>
<div class="serif" style="font-size:78px;margin-top:20px">{esc(p['problem'])}</div></div>
<div style="flex:1;background:#3f5745;color:#fff;border-radius:36px;padding:56px;display:flex;flex-direction:column;justify-content:center">
<div style="font-weight:800;letter-spacing:4px;font-size:32px;opacity:.9">THE FIX</div>
<div class="serif" style="font-size:78px;margin-top:20px">{esc(p['fix'])}</div></div></div>"""

def checklist(p):
    items = "".join(
        f'<li style="display:flex;gap:26px;align-items:center;font-size:46px;font-weight:600;padding:22px 0;border-bottom:2px solid #e2e5df">'
        f'<span style="flex:none;width:64px;height:64px;border-radius:50%;background:#7d977f;color:#fff;display:grid;place-items:center;font-weight:800;font-size:36px">{i}</span>{esc(t)}</li>'
        for i, t in enumerate(p["items"], 1))
    return f"""{bg(p)}<div style="position:relative;margin:auto 56px;background:rgba(255,253,248,.95);border-radius:36px;padding:64px 56px">
<h1 class="serif" style="font-size:88px;margin-bottom:30px">{esc(p['title'])}</h1>
<ol style="list-style:none;padding:0">{items}</ol></div>"""

LAYOUTS = {"headline": headline, "problem_fix": problem_fix, "checklist": checklist}

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]

def main():
    pins = yaml.safe_load((ROOT / "pins.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1500})
        for i, p in enumerate(pins, 1):
            body = LAYOUTS[p["layout"]](p)
            page.set_content(f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>{BASE_CSS}</style></head>"
                             f"<body><div class='pin'>{body}<div class='brand'>{SITE['name'].upper()} · DRYANDCOSY.COM</div></div></body></html>")
            page.wait_for_timeout(400)
            name = f"{i:03d}-{slugify(p['title'])}.png"
            page.screenshot(path=str(OUT / name))
            link = SITE["url"].rstrip("/") + p["url"]
            rows.append({"Title": p["title"][:100], "Media URL": f"{SITE['url']}/pins/{name}",
                         "Pinterest board": p["board"], "Thumbnail": "", "Description": p["description"][:500],
                         "Link": link, "Publish date": "", "Keywords": ""})
            print("rendered", name)
        browser.close()
    with open(ROOT / "pins_bulk.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} pins -> {OUT} and pins_bulk.csv")

if __name__ == "__main__":
    main()
