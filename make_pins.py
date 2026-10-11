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
.cap h1{{font:400 {size}px/1.04 'Bodoni Moda',serif;margin:0;letter-spacing:-.01em;text-wrap:balance;font-variation-settings:'opsz' 28}}
.cap h1 em{{font-style:italic}}
.cap p{{margin:32px 0 0;font-size:28px;letter-spacing:.06em;opacity:.9}}
</style></head><body><div class="pin">
<img src="https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&h=1500&q=90">
<div class="cap"><h1>{head}{tail}</h1><p>dryandcosy.com</p></div></div></body></html>"""

# "bold" style: the format that dominates Pinterest search for these topics.
# Big heavy headline in a linen band on top, the photo of the actual problem below.
BOLD = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;800;900&display=block" rel="stylesheet">
<style>
html,body{{margin:0;width:1000px;height:1500px}}
.pin{{width:1000px;height:1500px;display:flex;flex-direction:column;background:#eeebe4;font-family:'Hanken Grotesk',sans-serif}}
.top{{padding:70px 64px 50px;text-align:center}}
.top .n{{display:block;font:900 230px/0.9 'Hanken Grotesk';color:#2f3f35;letter-spacing:-.04em}}
.top h1{{font:800 {size}px/1.02 'Hanken Grotesk';color:#1c211e;margin:10px 0 0;letter-spacing:-.025em;text-wrap:balance;text-transform:uppercase}}
.top p{{font:500 34px/1.3 'Hanken Grotesk';color:#59605a;margin:22px 0 0;text-wrap:balance}}
.ph{{flex:1;position:relative;overflow:hidden}}
.ph img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.ph span{{position:absolute;left:0;right:0;bottom:0;padding:22px;text-align:center;color:#fff;font:600 28px 'Hanken Grotesk';letter-spacing:.06em;background:linear-gradient(transparent,rgba(18,22,19,.6))}}
</style></head><body><div class="pin">
<div class="top">{num}<h1>{head}</h1>{sub}</div>
<div class="ph"><img src="https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&h=1000&q=90"><span>dryandcosy.com</span></div>
</div></body></html>"""

# Product-led templates (product photo from Amazon's CDN, blended onto the paper tone)
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;1,6..96,400&family=Hanken+Grotesk:wght@500;600&display=block" rel="stylesheet">'
BASE_CSS = """html,body{margin:0;width:1000px;height:1500px}
.pin{width:1000px;height:1500px;position:relative;overflow:hidden;background:#eeebe4;color:#1c211e;font-family:'Hanken Grotesk',sans-serif}
.k{font:600 23px/1 'Hanken Grotesk';letter-spacing:.2em;text-transform:uppercase;color:#9c7a45}
h1{font:400 var(--hs)/1.05 'Bodoni Moda',serif;margin:0;letter-spacing:-.01em;text-wrap:balance;font-variation-settings:'opsz' 28}
h1 em{font-style:italic}
.url{font:500 22px/1 'Hanken Grotesk';letter-spacing:.16em;text-transform:uppercase;color:#59605a}
.stage{background:#f7f5f0;display:grid;place-items:center;overflow:hidden}
.stage img{mix-blend-mode:multiply;object-fit:contain}"""

PRODUCT = """<!doctype html><html><head><meta charset="utf-8">{fonts}<style>{base}
.pin{{display:flex;flex-direction:column;align-items:center;text-align:center;padding:84px 70px 64px;box-sizing:border-box}}
h1{{margin-top:26px}}
.stage{{width:860px;flex:1;margin:44px 0 0}}
.stage img{{width:78%;height:88%}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);width:860px;border-top:1px solid #1c211e;margin-top:0}}
.stats div{{padding:24px 10px 0;border-left:1px solid #d9d5cc}} .stats div:first-child{{border-left:0}}
.stats b{{display:block;font:400 54px/1 'Bodoni Moda';font-variation-settings:'opsz' 28}}
.stats span{{display:block;font:500 21px/1.3 'Hanken Grotesk';color:#59605a;margin-top:10px}}
.sub{{font:500 27px/1.35 'Hanken Grotesk';color:#59605a;margin:30px 0 26px}}
</style></head><body><div class="pin" style="--hs:{size}px">
<div class="k">{kicker}</div><h1>{head}</h1>
<div class="stage"><img src="{img}"></div>{stats}
<p class="sub">{sub}</p><div class="url">dryandcosy.com</div></div></body></html>"""

SCENE = """<!doctype html><html><head><meta charset="utf-8">{fonts}<style>{base}
.ph{{position:absolute;left:0;top:0;width:1000px;height:960px;object-fit:cover}}
.panel{{position:absolute;left:0;right:0;bottom:0;height:540px;padding:58px 0 0 70px;box-sizing:border-box}}
.panel .txt{{width:500px}}
.panel h1{{margin-top:22px}}
.panel .url{{position:absolute;left:70px;bottom:62px}}
.card{{position:absolute;right:60px;top:735px;width:320px}}
.card .stage{{width:320px;height:420px;box-shadow:0 30px 60px -30px rgba(28,33,30,.35)}}
.card .stage img{{width:80%;height:86%}}
.card p{{font:500 20px/1.3 'Hanken Grotesk';color:#59605a;margin:16px 0 0;text-align:center;letter-spacing:.04em}}
</style></head><body><div class="pin" style="--hs:{size}px">
<img class="ph" src="https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&h=960&q=90">
<div class="panel"><div class="txt"><div class="k">{kicker}</div><h1>{head}</h1></div><div class="url">dryandcosy.com</div></div>
<div class="card"><div class="stage"><img src="{img}"></div><p>{caption}</p></div></div></body></html>"""

TRIO = """<!doctype html><html><head><meta charset="utf-8">{fonts}<style>{base}
.pin{{display:flex;flex-direction:column;align-items:center;text-align:center;padding:90px 50px 64px;box-sizing:border-box}}
h1{{margin-top:26px}}
.cols{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;width:900px;flex:1;margin-top:60px;border-top:1px solid #1c211e;padding-top:40px}}
.cols .stage{{height:600px}} .cols .stage img{{width:84%;height:84%}}
.n{{font:600 21px/1 'Hanken Grotesk';letter-spacing:.18em;color:#9c7a45;margin-top:28px}}
.cols h2{{font:400 40px/1.12 'Bodoni Moda';margin:12px 0 0;font-variation-settings:'opsz' 28}}
.cols p{{font:500 23px/1.35 'Hanken Grotesk';color:#59605a;margin:10px 0 0}}
</style></head><body><div class="pin" style="--hs:{size}px">
<div class="k">{kicker}</div><h1>{head}</h1><div class="cols">{cols}</div><div class="url">dryandcosy.com</div></div></body></html>"""

WORD = """<!doctype html><html><head><meta charset="utf-8">{fonts}<style>{base}
.ph{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.pin::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(14,17,15,.18) 0%,rgba(14,17,15,.42) 55%,rgba(14,17,15,.55) 100%)}}
.w{{position:absolute;left:84px;right:84px;top:50%;transform:translateY(-50%);z-index:1;color:#fff;text-shadow:0 2px 28px rgba(0,0,0,.45)}}
.low .w{{top:auto;bottom:170px;transform:none}}
.low::after{{background:linear-gradient(180deg,rgba(14,17,15,.05) 0%,rgba(14,17,15,.15) 35%,rgba(14,17,15,.82) 78%,rgba(14,17,15,.9) 100%)}}
.w h1{{font:400 168px/1 'Bodoni Moda',serif;letter-spacing:-.015em;font-variation-settings:'opsz' 96}}
.w .m{{font:italic 400 36px/1.3 'Bodoni Moda',serif;margin-top:18px;opacity:.92}}
.w p{{font:500 36px/1.45 'Hanken Grotesk';margin:34px 0 0;max-width:760px;opacity:.95}}
.u{{position:absolute;left:0;right:0;bottom:64px;text-align:center;z-index:1;font:500 21px/1 'Hanken Grotesk';letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.8)}}
</style></head><body><div class="pin {pos}">
<img class="ph" src="https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&h=1500&q=90">
<div class="w"><h1>{word}</h1><div class="m">{meta}</div><p>{definition}</p></div><div class="u">dryandcosy.com</div></div></body></html>"""

COSTS = """<!doctype html><html><head><meta charset="utf-8">{fonts}<style>{base}
.pin{{padding:84px 72px 60px;box-sizing:border-box;display:flex;flex-direction:column}}
h1{{text-align:center;margin-top:22px}} .k{{text-align:center}}
.lede{{text-align:center;font:500 27px/1.4 'Hanken Grotesk';color:#59605a;margin:22px 40px 0}}
.rows{{margin-top:48px;border-top:2px solid #1c211e;flex:1}}
.r{{display:grid;grid-template-columns:1fr auto;align-items:baseline;padding:var(--rp) 4px;border-bottom:1px solid #cfcabf}}
.r b{{font:400 38px/1.2 'Bodoni Moda';font-variation-settings:'opsz' 28}}
.r small{{display:block;font:500 21px/1.3 'Hanken Grotesk';color:#7a7f78;margin-top:4px}}
.r span{{font:400 56px/1 'Bodoni Moda';font-variation-settings:'opsz' 28}}
.r.win span{{color:#2f3f35}} .r.win b::after{{content:"  \\2713";color:#9c7a45;font-size:30px}}
.r.lose span{{color:#9a4a34}}
.foot{{display:flex;justify-content:space-between;align-items:flex-end;margin-top:26px}}
.foot p{{font:500 19px/1.35 'Hanken Grotesk';color:#7a7f78;max-width:560px;margin:0}}
</style></head><body><div class="pin" style="--hs:{size}px;--rp:{rp}px">
<div class="k">{kicker}</div><h1>{head}</h1><p class="lede">{lede}</p>
<div class="rows">{rows}</div>
<div class="foot"><p>{note}</p><div class="url">dryandcosy.com</div></div></div></body></html>"""

CHECK = """<!doctype html><html><head><meta charset="utf-8">{fonts}<style>{base}
.top{{height:320px;position:relative;overflow:hidden}} .top img{{width:100%;height:100%;object-fit:cover}}
.body{{padding:46px 76px 0}}
h1{{margin-top:18px}}
ul{{list-style:none;padding:0;margin:30px 0 0}}
li{{display:grid;grid-template-columns:44px 1fr;gap:20px;align-items:start;padding:var(--lp) 0;border-bottom:1px solid #d9d5cc;font:500 var(--lf)/1.3 'Hanken Grotesk'}}
li i{{width:30px;height:30px;border:2px solid #2f3f35;margin-top:3px;display:block}}
li em{{font-style:normal;color:#7a7f78;font-size:calc(var(--lf) * .78);display:block;margin-top:2px}}
.url{{position:absolute;left:76px;bottom:44px}}
</style></head><body><div class="pin" style="--hs:{size}px;--lp:{lp}px;--lf:{lf}px">
<div class="top"><img src="https://images.unsplash.com/{photo}?auto=format&fit=crop&w=1000&h=320&q=90"></div>
<div class="body"><div class="k">{kicker}</div><h1>{head}</h1><ul>{items}</ul></div><div class="url">dryandcosy.com</div></div></body></html>"""

CATALOGUE = {x["id"]: x for x in yaml.safe_load((ROOT / "products.yaml").read_text())["products"]}

def pimg(pid):
    from urllib.parse import quote
    return f"https://m.media-amazon.com/images/I/{quote(CATALOGUE[pid]['img'])}._AC_SL1500_.jpg"

def fmt_head(p):
    head = html.escape(p["head"])
    return head + (f" <em>{html.escape(p['tail'])}</em>" if p.get("tail") else "")

def page_html(p):
    st = p.get("style")
    words = len((p["head"] + " " + (p.get("tail") or "")).split())
    if st == "costs":
        rows = "".join(f'<div class="r {c}"><div><b>{html.escape(n)}</b><small>{html.escape(w)}</small></div><span>{html.escape(v)}</span></div>'
                       for n, w, v, c in p["rows"])
        return COSTS.format(fonts=FONTS, base=BASE_CSS, size=80, kicker=html.escape(p.get("kicker", "")), head=fmt_head(p),
                            lede=html.escape(p.get("lede", "")), rows=rows, note=html.escape(p.get("note", "")),
                            rp=22 if len(p["rows"]) >= 7 else 34 if len(p["rows"]) >= 5 else 52)
    if st == "checklist":
        items = "".join(f'<li><i></i><div>{html.escape(a)}<em>{html.escape(b)}</em></div></li>' for a, b in p["items"])
        return CHECK.format(fonts=FONTS, base=BASE_CSS, size=72, kicker=html.escape(p.get("kicker", "")), head=fmt_head(p),
                            photo=p["photo"], items=items,
                             lp=13 if len(p["items"]) >= 8 else 21 if len(p["items"]) >= 7 else 27, lf=28 if len(p["items"]) >= 8 else 31)
    if st == "photo":
        return (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;width:1000px;height:1500px}}'
                f'img{{width:1000px;height:1500px;object-fit:cover;display:block}}</style></head><body>'
                f'<img src="https://images.unsplash.com/{p["photo"]}?auto=format&fit=crop&w=1000&h=1500&q=92"></body></html>')
    if st == "word":
        return WORD.format(fonts=FONTS, base=BASE_CSS, pos=p.get("pos", ""), photo=p["photo"], word=html.escape(p["head"]),
                           meta=html.escape(p.get("meta", "")), definition=html.escape(p.get("definition", "")))
    if st == "product":
        stats = "".join(f"<div><b>{html.escape(str(a))}</b><span>{html.escape(b)}</span></div>" for a, b in (p.get("stats") or []))
        return PRODUCT.format(fonts=FONTS, base=BASE_CSS, size=86 if words <= 7 else 74, kicker=html.escape(p.get("kicker", "")),
                              head=fmt_head(p), img=pimg(p["product"]), stats=f'<div class="stats">{stats}</div>' if stats else "",
                              sub=html.escape(p.get("sub", "")))
    if st == "scene":
        return SCENE.format(fonts=FONTS, base=BASE_CSS, size=86 if words <= 4 else 72 if words <= 6 else 64, kicker=html.escape(p.get("kicker", "")),
                            head=fmt_head(p), photo=p["photo"], img=pimg(p["product"]), caption=html.escape(p.get("caption", "")))
    if st == "trio":
        cols = "".join(f'<div><div class="stage"><img src="{pimg(pid)}"></div><div class="n">0{i+1}</div><h2>{html.escape(name)}</h2><p>{html.escape(why)}</p></div>'
                       for i, (pid, name, why) in enumerate(p["items"]))
        return TRIO.format(fonts=FONTS, base=BASE_CSS, size=80 if words <= 7 else 70, kicker=html.escape(p.get("kicker", "")), head=fmt_head(p), cols=cols)
    if st == "bold":
        num = f'<span class="n">{html.escape(str(p["num"]))}</span>' if p.get("num") else ""
        sub = f"<p>{html.escape(p['tail'])}</p>" if p.get("tail") else ""
        words = len(p["head"].split())
        size = 92 if words <= 5 else 80 if words <= 7 else 68
        return BOLD.format(photo=p["photo"], num=num, head=html.escape(p["head"]), sub=sub, size=size)
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
