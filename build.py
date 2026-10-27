"""Static site builder for Dry & Cosy.

Inputs:
  site.yaml              site settings (Amazon tag, hero photos, featured products)
  products.yaml          categories + product catalogue
  content/posts/*.md     guides (YAML front matter + Markdown)
  content/pages/*.md     about, disclosure, privacy, contact
In a guide, place a catalogue product with:  [[product id="heated-airer-tiered"]]
Run: python3 build.py   ->   dist/
"""
import html, re, shutil, sys
from datetime import date
from pathlib import Path
from urllib.parse import quote, quote_plus

import markdown
import yaml

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SITE = yaml.safe_load((ROOT / "site.yaml").read_text())
CAT = yaml.safe_load((ROOT / "products.yaml").read_text())
CATS = {c["id"]: c for c in CAT["categories"]}
PRODUCTS = {p["id"]: p for p in CAT["products"]}
DISCLOSURE_LINE = "As an Amazon Associate I earn from qualifying purchases."
e = html.escape

def photo(pid, w=1600, alt="", cls="", eager=False):
    if str(pid).startswith("/"):
        load = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<img src="{pid}" alt="{e(alt)}" {load} decoding="async"{f" class={cls}" if cls else ""}>'
    src = f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w={w}&q=80"
    srcset = ", ".join(f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w={x}&q=80 {x}w" for x in (640, 1080, 1600, 2400) if x <= w * 1.5)
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{src}" srcset="{srcset}" sizes="(max-width:900px) 100vw, 60vw" alt="{e(alt)}" {load} decoding="async"{f" class={cls}" if cls else ""}>'

def read(path):
    raw = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta, body = (yaml.safe_load(m.group(1)), m.group(2)) if m else ({}, raw)
    meta.setdefault("slug", path.stem)
    return meta, body

def amazon_url(p):
    base, tag = f"https://{SITE['amazon_domain']}", SITE.get("amazon_tag") or ""
    if p.get("asin"):
        return f"{base}/dp/{p['asin']}" + (f"?tag={tag}" if tag else "")
    return f"{base}/s?k={quote_plus(p['search'])}" + (f"&tag={tag}" if tag else "")

def label(p):
    return "View on Amazon" if p.get("asin") else "See options on Amazon"

def pimg(p, size=500):
    """Product photo from Amazon's image CDN (same URLs the Product Advertising API returns)."""
    if not (p.get("img") and SITE.get("product_images", True)):
        return ""
    return (f'<img src="https://m.media-amazon.com/images/I/{quote(p["img"])}._AC_SL{size}_.jpg" '
            f'alt="{e(p.get("title") or p["name"])}" loading="lazy" decoding="async">')

def title(p):
    return p.get("title") or p["name"]

def row(p, show_cat=False):
    cat = f'<span class="cat">{e(CATS[p["cat"]]["name"])}</span>' if show_cat else ""
    take = f'<span class="take">{e(p["take"])}</span>' if p.get("take") else ""
    thumb = f'<span class="thumb">{pimg(p, 200)}</span>' if p.get("img") else '<span class="thumb empty"></span>'
    return (f'<a class="row has-thumb" href="{amazon_url(p)}" rel="sponsored nofollow noopener" target="_blank">{thumb}'
            f'<span class="name">{cat}{e(title(p))}{take}</span><span class="for">Best for {e(p["best"].lower())}</span>'
            f'<span class="go">{label(p)}</span></a>')

def card(p, show_cat=False):
    cat = f'<span class="cat">{e(CATS[p["cat"]]["name"])}</span>' if show_cat else f'<span class="cat">Best for {e(p["best"].lower())}</span>'
    take = f'<p class="take">{e(p["take"])}</p>' if p.get("take") else ""
    return (f'<a class="card" href="{amazon_url(p)}" rel="sponsored nofollow noopener" target="_blank">'
            f'<div class="pimg">{pimg(p)}</div>{cat}<h3>{e(title(p))}</h3>{take}<span class="go">{label(p)}</span></a>')

def product_block(items, show_cat=False):
    """Picked products (with a photo) as a card grid; the rest as a typographic list beneath."""
    picked, rest = [p for p in items if p.get("img")], [p for p in items if not p.get("img")]
    out = f'<div class="cards">{"".join(card(p, show_cat) for p in picked)}</div>' if picked else ""
    if rest:
        out += (f'<h3 class="more-head">More to browse</h3>' if picked else "") + f'<div class="index">{"".join(row(p, show_cat) for p in rest)}</div>'
    return out

def inline_product(m):
    attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
    p = dict(PRODUCTS.get(attrs.get("id"), {}))
    if not p:
        raise SystemExit(f"Unknown product id in guide: {attrs.get('id')}")
    p.update({k: v for k, v in attrs.items() if k != "id"})
    take = f'<p class="take">{e(p["take"])}</p>' if p.get("take") else ""
    img = f'<a class="pimg" href="{amazon_url(p)}" rel="sponsored nofollow noopener" target="_blank">{pimg(p, 300)}</a>' if p.get("img") else ""
    return (f'<div class="pick{" with-img" if img else ""}">{img}<div><span class="for">Best for {e(p["best"].lower())}</span><h4>{e(title(p))}</h4>{take}</div>'
            f'<a class="btn line" href="{amazon_url(p)}" rel="sponsored nofollow noopener" target="_blank">{label(p)}</a></div>')

def render_md(body):
    body = re.sub(r"\[\[product (.*?)\]\]", inline_product, body)
    out = markdown.markdown(body, extensions=["tables", "attr_list", "md_in_html"])
    return out.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")

HEADER_JS = """<script>
(function(){var h=document.querySelector('.site-head');if(!h||!document.body.classList.contains('home'))return;
function f(){h.classList.toggle('solid',window.scrollY>window.innerHeight*0.6)}f();addEventListener('scroll',f,{passive:true})})();
</script>"""

def layout(title, desc, content, path="", body_class="", og=None):
    canonical = SITE["url"].rstrip("/") + "/" + path
    foot_cats = "".join(f'<li><a href="/shop/{c["id"]}/">{e(c["name"])}</a></li>' for c in CAT["categories"])
    og_src = (SITE["url"].rstrip("/") + og) if og and str(og).startswith("/") else f"https://images.unsplash.com/{og}?auto=format&fit=crop&w=1200&q=80"
    og_img = f'<meta property="og:image" content="{og_src}">' if og else ""
    return f"""<!doctype html><html lang="en-GB"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="p:domain_verify" content="{SITE.get('pinterest_verify','')}"/>
<meta property="og:type" content="website"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}"><meta property="og:site_name" content="Dry &amp; Cosy">{og_img}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Jost:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<script defer src="/_vercel/insights/script.js"></script></head><body class="{body_class}">
<header class="site-head"><div class="wrap head-row">
<a class="logo" href="/">Dry &amp; <em>Cosy</em></a>
<nav class="nav"><a href="/shop/">Shop</a><a href="/guides/">Guides</a><a class="hide-sm" href="/about/">About</a></nav>
</div></header>
<main>{content}</main>
<footer><div class="wrap foot">
<div><a class="logo" href="/">Dry &amp; <em>Cosy</em></a><p style="margin-top:18px;max-width:28em">{e(SITE['tagline'])}</p></div>
<div><h4>Shop</h4><ul>{foot_cats}</ul></div>
<div><h4>Dry &amp; Cosy</h4><ul><li><a href="/guides/">Guides</a></li><li><a href="/about/">About</a></li><li><a href="/contact/">Contact</a></li><li><a href="/affiliate-disclosure/">Affiliate disclosure</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="{SITE['pinterest']}">Pinterest</a></li></ul></div>
<div class="legal">© {date.today().year} Dry &amp; Cosy, Ireland. {DISCLOSURE_LINE} Product links are paid links. Photography from Unsplash.</div>
</div></footer>{HEADER_JS}</body></html>"""

def write(rel, text):
    out = DIST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)

def entry(m):
    img = photo(m["image"], 1080, m["title"]) if m.get("image") else ""
    return (f'<a class="entry" href="/{m["slug"]}/"><div class="ph">{img}</div>'
            f'<h3>{e(m["title"])}</h3><p>{e(m.get("description",""))}</p></a>')

def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    for f in (ROOT / "static").glob("*"):
        (shutil.copytree if f.is_dir() else shutil.copy)(f, DIST / f.name)
    by_cat = {c["id"]: [p for p in CAT["products"] if p["cat"] == c["id"]] for c in CAT["categories"]}

    # guides
    posts = []
    for p in sorted((ROOT / "content/posts").glob("*.md")):
        meta, body = read(p)
        if meta.get("draft") and "--drafts" not in sys.argv:
            continue
        posts.append(meta)
        paras = body.strip().split("\n\n", 1)
        lede, rest = paras[0], (paras[1] if len(paras) > 1 else "")
        hero = f'<div class="article-hero">{photo(meta["image"], 2400, meta["title"], eager=True)}</div>' if meta.get("image") else ""
        art = f"""{hero}<div class="wrap narrow"><article class="article">
<p class="crumbs"><a href="/">Home</a> / <a href="/guides/">Guides</a> / {e(meta.get('category','Guide'))}</p>
<h1>{e(meta['title'])}</h1><p class="lede">{e(lede)}</p>
<p class="meta">Updated {e(str(meta.get('updated','')))}. Contains paid links. {DISCLOSURE_LINE}</p>
{render_md(rest)}</article></div>"""
        write(f"{meta['slug']}/index.html", layout(f"{meta['title']} | Dry & Cosy", meta.get("description", ""), art, meta["slug"] + "/", og=meta.get("image")))
    posts.sort(key=lambda m: str(m.get("date", "")), reverse=True)

    # pages
    for p in sorted((ROOT / "content/pages").glob("*.md")):
        meta, body = read(p)
        page = f'<div class="wrap narrow"><article class="article"><h1>{e(meta["title"])}</h1>{render_md(body)}</article></div>'
        write(f"{meta['slug']}/index.html", layout(f"{meta['title']} | Dry & Cosy", meta.get("description", ""), page, meta["slug"] + "/"))

    # category pages
    for c in CAT["categories"]:
        related = [m for m in posts if c["id"] in (m.get("cats") or [])]
        rel = (f'<section class="section band"><div class="wrap"><div class="head"><h2>Read before you buy</h2></div>'
               f'<div class="journal">{"".join(entry(m) for m in related[:2])}</div></div></section>') if related else ""
        content = f"""<section class="banner">{photo(c['image'], 2400, c['name'], eager=True)}<div class="wrap">
<p class="crumbs"><a href="/">Home</a> / <a href="/shop/">Shop</a></p><h1>{e(c['name'])}</h1><p>{e(c['blurb'])}</p></div></section>
<section class="section"><div class="wrap">{product_block(by_cat[c['id']])}
<p class="paid">{len(by_cat[c['id']])} products. Paid links.</p></div></section>{rel}"""
        write(f"shop/{c['id']}/index.html", layout(f"{c['name']} | Dry & Cosy", c["blurb"], content, f"shop/{c['id']}/", og=c.get("image")))

    rooms = "".join(
        f'<a class="room" href="/shop/{c["id"]}/"><div class="ph">{photo(c["image"], 1080, c["name"])}</div>'
        f'<h3>{e(c["name"])}</h3><p>{e(c["blurb"])}</p><span class="n">{len(by_cat[c["id"]])} products</span></a>'
        for c in CAT["categories"])

    shop = f"""<section class="plainhead"><div class="wrap"><p class="crumbs"><a href="/">Home</a></p><h1>The shop</h1>
<p>{len(CAT['products'])} products for damp, cold and slow-drying washing, chosen for UK and Irish homes.</p></div></section>
<div class="rail-wrap"><div class="rail">{rooms}</div></div>
<section class="section band"><div class="wrap"><div class="head"><h2>Everything, A to Z</h2></div>
<div class="index">{''.join(row(p, True) for p in sorted(CAT['products'], key=lambda p: p['name'].lower()))}</div></div></section>"""
    write("shop/index.html", layout("Shop | Dry & Cosy", "Products for a dry, warm home.", shop, "shop/"))

    guides = f"""<section class="plainhead"><div class="wrap"><p class="crumbs"><a href="/">Home</a></p><h1>Guides</h1>
<p>What causes the problem, the free fixes, and what to buy if those are not enough.</p></div></section>
<section class="section" style="padding-top:20px"><div class="wrap"><div class="journal">{''.join(entry(m) for m in posts)}</div></div></section>"""
    write("guides/index.html", layout("Guides | Dry & Cosy", "Guides to damp, condensation, drying clothes and heating.", guides, "guides/"))

    # home
    featured = [PRODUCTS[i] for i in SITE.get("featured", []) if i in PRODUCTS][:8]
    lead = posts[-1] if posts else None
    lead = next((m for m in posts if m["slug"] == "dry-clothes-indoors-without-damp"), lead)
    home = f"""<section class="hero">{photo(SITE['hero_image'], 2400, 'A linen cupboard with folded towels in soft daylight', eager=True)}
<div class="hero-copy"><div class="wrap"><h1>A calm, clean, <em>cosy</em> home.</h1>
<p>Quiet, considered guides and a few beautiful things for a home that stays dry, warm and fresh. Chosen for UK and Irish homes.</p>
<div class="actions"><a class="btn light" href="/shop/">Explore the shop</a></div></div></div></section>

<section class="statement"><div class="wrap"><p>A calm home is mostly small rituals: dry air, fresh linen, warm light.</p>
<p class="sub">We start with what causes the problem and the free fixes. Then we point you to the few products that genuinely help, from linen care and natural cleaning to airers, dehumidifiers and throws.</p></div></section>

<section><div class="wrap head"><div><h2>Shop by room and problem</h2><p>{len(CAT['products'])} products across {len(CAT['categories'])} collections.</p></div><a class="textlink" href="/shop/">View the full shop</a></div>
<div class="rail-wrap"><div class="rail">{rooms}</div></div></section>

<section class="band"><div class="wrap feature"><div class="ph">{photo(SITE['feature_image'], 1600, 'Linen drying by a sunlit window')}</div>
<div><h2>Drying washing indoors, without the damp</h2><p>A single load can release around two litres of water into your home. Here is how to dry it quickly and keep that moisture off your walls and windows.</p>
<div class="actions"><a class="btn dark" href="/{lead['slug']}/">Read the guide</a></div></div></div></section>

<section class="section"><div class="wrap"><div class="head"><div><h2>The winter edit</h2><p>What homes reach for first when the heating goes on.</p></div><a class="textlink" href="/shop/">All products</a></div>
<div class="cards">{''.join(card(p, True) for p in featured)}</div><p class="paid">Paid links.</p></div></section>

<section class="section band"><div class="wrap"><div class="head"><h2>From the guides</h2><a class="textlink" href="/guides/">All guides</a></div>
<div class="journal">{''.join(entry(m) for m in posts[:2])}</div></div></section>

<div class="wrap trust"><div><h3>Chosen, not listed</h3><p>We pick products for what they do for the problem, and leave out the rest.</p></div>
<div><h3>Written for our homes</h3><p>Advice for Irish and UK weather, older housing and today's energy prices.</p></div>
<div><h3>Clear about links</h3><p>Product links are paid links. The price you pay stays the same.</p></div></div>"""
    write("index.html", layout("Dry & Cosy | For a dry, warm home", SITE["tagline"], home, body_class="home", og=SITE["hero_image"]))

    urls = ["", "shop/", "guides/"] + [f"shop/{c['id']}/" for c in CAT["categories"]] + [m["slug"] + "/" for m in posts]
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          + "".join(f"<url><loc>{SITE['url']}/{u}</loc></url>" for u in urls) + "</urlset>")
    print(f"Built {len(posts)} guides, {len(CAT['products'])} products in {len(CAT['categories'])} categories -> {DIST}")
    print(f"Still to do: {sum(1 for p in CAT['products'] if not p.get('asin'))} products without an ASIN, "
          f"{sum(1 for p in CAT['products'] if not p.get('take'))} without your take.")

if __name__ == "__main__":
    build()
