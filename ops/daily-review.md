# Daily growth review (runs every evening, ~21:45 Dublin)

Owner: Claude, on Zygimantas's standing instruction (14 Oct 2026): "take over, do daily scans, see what's working, change what isn't, more impressions, more sales".

Goal ladder: 1k impressions/month -> 10k/month -> steady outbound clicks -> Amazon sales.

## 1. Pull data (PC Chrome, Pinterest tab)
- Overview: open https://analytics.pinterest.com/ in a new tab, wait, get_page_text.
  Record: impressions, engagements, outbound clicks, saves (30d), plus the Top Pins list.
  Also switch the URL param aggregation=last7d and record the 7d totals.
- Profile: UserResource/get (username dryandcosyhome) for follower_count and pin_count.
- Save as ops/stats/YYYY-MM-DD.md (totals + per-pin table). Compare with the previous file(s).
- Vercel and Amazon Associates are not logged in on the PC. Never sign in. Note "n/a" and ask the user for a screenshot once a week (Monday).

## 2. Diagnose (write 3-6 bullets in the stats file)
- Which pins gained most impressions since last review, and their format (photo+headline / text / product / word / mood).
- Topic winners vs losers (drying washing, condensation, mould, heating, cosy mood).
- Saves and outbound clicks: which pin earned them.
- Anything broken: a pin image 404, a site page 404 (WebFetch dryandcosy.com and the top linked URLs), Amazon links missing the tag.

## 3. Act (do it, don't just report)
- Double down: for each winning pin, create 2-3 fresh variations (new Unsplash photo, new headline angle, same keyword, same URL). Add to pins.yaml as approved, render via the pins workflow, check the jpg visually, then slot them into the posting chain in place of weaker queued pins.
- Cut: stop queuing formats that sit under ~10 impressions after 3 days while photo+headline pins of the same age are higher.
- Site: if a pin topic wins and the landing page is thin, improve that page (more picks, clearer top pick, comparison table). If a topic has no product coverage, add products (real ASINs with the dryandcosy-21 tag).
- Engagement: save 6 relevant, high-save pins from other accounts onto our matching boards (BaseSearchResource search, RepinResource/create). No promoted pins, no competitors' affiliate spam, never our own pins.
- Keep tomorrow's posting chain full (6-8 pins/day). If the queue has fewer than 2 days of approved pins, build more.

## 4. Report
- PushNotification with a 2-3 line summary: numbers vs yesterday, what changed, what's next.
- Commit everything (author ZygisK, trailers) and push.
- Schedule the next review with send_later at 20:45Z (21:45 Dublin; 21:45Z after clocks go back on 25 Oct).

## Hard rules
- Real photos only (Unsplash), no AI-looking images, no product cut-outs pasted onto scenes.
- No em dashes on the site or pins.
- Never sign in, never enter passwords, never delete pins (the user deletes).
- Never post to Reddit/Facebook as the user; draft only.
- If Chrome on the PC is unreachable, notify the user and still do the offline parts.

## Helpers
- ops/pinjs.py <slug>  -> options JSON for PinResource/create
- ops/markposted.py <slug> -> flips status to posted
- Post: fetch('/resource/PinResource/create/') with X-CSRFToken, source_url "/pin-creation-tool/".
- Repin: fetch('/resource/RepinResource/create/') data {options:{board_id,pin_id,description:"",link:"",title:"",is_buyable_pin:false,carousel_slot_index:0}}, source_url "/pin/<id>/".
- Search: GET /resource/BaseSearchResource/get/ options {query, scope:'pins', page_size:25}, header X-Pinterest-Pws-Handler 'www/search/[scope].js'.
