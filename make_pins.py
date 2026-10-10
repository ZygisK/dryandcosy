"""Render photo-led Pinterest pins (1000x1500 JPG) from pins.yaml.

Runs during the Vercel build (which has internet access):
  - downloads the brand fonts (Bodoni Moda, Hanken Grotesk) from the Google Fonts GitHub repo
  - downloads each Unsplash photo at 1000x1500
  - draws a bottom fade, the headline (roman + italic tail) and the dryandcosy.com credit
Output: dist/pins/v2/<slug>.jpg and dist/pins/index.html (a preview sheet).
If a download fails the pin is skipped; the site build never fails because of pins.
Run after build.py:  python3 make_pins.py
"""
import html
import io
import sys
import urllib.request
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
OUT = ROOT / "dist" / "pins" / "v2"
CACHE = ROOT / ".cache"
W, H = 1000, 1500
MARGIN = 68
FONTS = {
    "roman": "https://raw.githubusercontent.com/google/fonts/main/ofl/bodonimoda/BodoniModa%5Bopsz%2Cwght%5D.ttf",
    "italic": "https://raw.githubusercontent.com/google/fonts/main/ofl/bodonimoda/BodoniModa-Italic%5Bopsz%2Cwght%5D.ttf",
    "sans": "https://raw.githubusercontent.com/google/fonts/main/ofl/hankengrotesk/HankenGrotesk%5Bwght%5D.ttf",
}

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "dryandcosy-build"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def font_file(key):
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"{key}.ttf"
    if not path.exists():
        path.write_bytes(fetch(FONTS[key]))
    return path

from PIL import features
ENGINE = ImageFont.Layout.RAQM if features.check("raqm") else ImageFont.Layout.BASIC
print("text layout engine:", "raqm (kerning on)" if ENGINE == ImageFont.Layout.RAQM else "basic (no kerning)")

def load_font(key, size, axes):
    f = ImageFont.truetype(str(font_file(key)), size, layout_engine=ENGINE)
    try:
        vals = []
        for a in f.get_variation_axes():
            n = (a["name"].decode() if isinstance(a["name"], bytes) else str(a["name"])).lower()
            key = "opsz" if "optic" in n or n == "opsz" else "wght" if "weight" in n or n == "wght" else n
            v = axes.get(key, a.get("default", 400))
            vals.append(max(a["minimum"], min(a["maximum"], v)))
        f.set_variation_by_axes(vals)
    except Exception as ex:
        print("variable font axes not set:", ex)
    return f

def wrap(draw, text, font, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textlength(test, font=font) <= width or not line:
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def render(pin, fonts):
    raw = fetch(f"https://images.unsplash.com/{pin['photo']}?auto=format&fit=crop&w={W}&h={H}&q=88&fm=jpg")
    img = Image.open(io.BytesIO(raw)).convert("RGB").resize((W, H))
    # bottom fade: transparent at 38% height, 72% ink at the bottom
    fade = Image.new("L", (1, H))
    start = int(H * 0.38)
    for y in range(H):
        fade.putpixel((0, y), 0 if y < start else int(184 * ((y - start) / (H - start)) ** 1.1))
    ink = Image.new("RGB", (W, H), (18, 22, 19))
    img = Image.composite(ink, img, fade.resize((W, H)))
    d = ImageDraw.Draw(img)
    width = W - 2 * MARGIN
    size = 100
    while True:
        roman, italic = fonts["roman"](size), fonts["italic"](size)
        lines = [(l, roman) for l in wrap(d, pin["head"], roman, width)]
        if pin.get("tail"):
            lines += [(l, italic) for l in wrap(d, pin["tail"], italic, width)]
        if len(lines) <= 4 or size <= 72:
            break
        size -= 6
    lh = int(size * 1.06)
    credit = fonts["sans"](28)
    y = H - MARGIN - 28 - 34 - lh * len(lines)
    for text, f in lines:
        d.text((MARGIN, y), text, font=f, fill=(255, 255, 255))
        y += lh
    x, cy = MARGIN, H - MARGIN - 28
    for ch in "dryandcosy.com":  # letter-spaced credit
        d.text((x, cy), ch, font=credit, fill=(236, 236, 232))
        x += d.textlength(ch, font=credit) + 1.7
    return img

def main():
    pins = yaml.safe_load((ROOT / "pins.yaml").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        fonts = {
            "roman": lambda s: load_font("roman", s, {"opsz": 36, "wght": 430}),
            "italic": lambda s: load_font("italic", s, {"opsz": 36, "wght": 430}),
            "sans": lambda s: load_font("sans", s, {"wght": 500}),
        }
        fonts["roman"](20)
    except Exception as ex:
        print("pins skipped, fonts unavailable:", ex)
        return
    done = []
    for p in pins:
        try:
            render(p, fonts).save(OUT / f"{p['slug']}.jpg", quality=88, optimize=True)
            done.append(p)
        except Exception as ex:
            print("pin skipped:", p["slug"], ex, file=sys.stderr)
    cards = "".join(
        f'<figure><img src="v2/{p["slug"]}.jpg" alt=""><figcaption><b>{html.escape(p["board"])}</b><br>{html.escape(p["title"])}<br><small>{html.escape(p["url"])}</small></figcaption></figure>'
        for p in done)
    (OUT.parent / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Pin preview</title>'
        '<style>body{font:14px system-ui;margin:24px;background:#eeebe4}div{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:20px}'
        'img{width:100%;display:block}figure{margin:0}figcaption{margin-top:6px;color:#333}</style>'
        f'<h1>Pin preview ({len(done)})</h1><div>{cards}</div>')
    print(f"rendered {len(done)}/{len(pins)} pins")

if __name__ == "__main__":
    main()
