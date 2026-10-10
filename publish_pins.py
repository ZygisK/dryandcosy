"""Post the next approved pin to Pinterest via the API v5, then mark it posted in pins.yaml.

Run by .github/workflows/publish.yml a few times a day (one pin per run).
Needs repo secrets: PINTEREST_APP_ID, PINTEREST_APP_SECRET, PINTEREST_REFRESH_TOKEN.
If they are missing the script exits quietly, so the schedule is safe to leave on.
"""
import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
SITE = "https://dryandcosy.com"
API = "https://api.pinterest.com/v5"

def req(method, url, token=None, data=None, form=None, basic=None):
    headers = {}
    body = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if basic:
        headers["Authorization"] = "Basic " + base64.b64encode(basic.encode()).decode()
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    if form is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(form).encode()
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {url} -> {e.code}: {e.read().decode()[:400]}")

def access_token():
    app_id, secret, refresh = (os.environ.get(k) for k in ("PINTEREST_APP_ID", "PINTEREST_APP_SECRET", "PINTEREST_REFRESH_TOKEN"))
    if not (app_id and secret and refresh):
        print("Pinterest secrets not set yet; nothing to do.")
        sys.exit(0)
    out = req("POST", f"{API}/oauth/token", basic=f"{app_id}:{secret}",
              form={"grant_type": "refresh_token", "refresh_token": refresh})
    return out["access_token"]

def boards(token):
    found, bookmark = {}, None
    while True:
        url = f"{API}/boards?page_size=100" + (f"&bookmark={bookmark}" if bookmark else "")
        page = req("GET", url, token=token)
        for b in page.get("items", []):
            found[b["name"]] = b["id"]
        bookmark = page.get("bookmark")
        if not bookmark:
            return found

def main():
    path = ROOT / "pins.yaml"
    raw = path.read_text()
    pins = yaml.safe_load(raw)
    nxt = next((p for p in pins if p.get("status") == "approved"), None)
    if not nxt:
        print("No approved pins waiting.")
        return
    token = access_token()
    board_id = boards(token).get(nxt["board"])
    if not board_id:
        sys.exit(f"Board not found on Pinterest: {nxt['board']}")
    pin = req("POST", f"{API}/pins", token=token, data={
        "board_id": board_id,
        "title": nxt["title"][:100],
        "description": nxt["description"][:500],
        "link": SITE + nxt["url"],
        "alt_text": nxt["title"][:500],
        "media_source": {"source_type": "image_url", "url": f"{SITE}/pins/v2/{nxt['slug']}.jpg"},
    })
    print("posted", nxt["slug"], "->", pin.get("id"))
    # mark this pin as posted without reformatting the rest of the file
    block = re.compile(rf"(- slug: {re.escape(nxt['slug'])}\n(?:  .*\n)*?  status: )approved")
    path.write_text(block.sub(r"\1posted", raw, count=1))

if __name__ == "__main__":
    main()
