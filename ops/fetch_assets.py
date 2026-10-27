"""Download AI photos listed in assets.yaml into static/img/<name>.jpg (runs in GitHub Actions)."""
import io, urllib.request
from pathlib import Path
import yaml
from PIL import Image
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "img"; OUT.mkdir(parents=True, exist_ok=True)
for name, url in (yaml.safe_load((ROOT / "assets.yaml").read_text()) or {}).items():
    out = OUT / f"{name}.jpg"
    if out.exists():
        continue
    data = urllib.request.urlopen(url, timeout=60).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((2000, 2000))
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    print("saved", out.name, im.size)
