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
- 3 pins/day (cut from 6 on 20 Oct). Keep a BUFFER of at least 3 days of pins built AND scheduled (user, 21 Oct). Schedule each pin as its own send_later (no chains), so one failed run never stops the rest.
- ONE URL PER PIN (found 20 Oct): Pinterest displays the landing page's og:title/description, not our pin title. Every new pin needs its own landing page (a real guide with products) whose page title matches the pin title. Max 2 pins per URL ever. Never point new pins at /shop/* or the older guides that already have 4+ pins.
- Vary posting times every day (user, 20 Oct): never reuse yesterday's slots. Pick one random time inside each window (Dublin): 08:00-10:30, 12:00-15:00, 17:30-21:00. Use odd minutes (not :00/:05/:10 etc). Gaps of at least 60 min. Also shuffle the topic order.

## 4. Report
- PushNotification with a 2-3 line summary: numbers vs yesterday, what changed, what's next.
- Commit everything (author ZygisK, trailers) and push.
- Schedule the next review with send_later at 20:45Z (21:45 Dublin; 21:45Z after clocks go back on 25 Oct).

## SEO rules (every new pin)
- Title starts with a real Pinterest search phrase from ops/keywords-*.md, 40-75 chars.
- Description 280-480 chars, 3-5 keyword variants in natural sentences, UK/Irish, ends with a save prompt. No hashtags.
- Alt text set (pins.yaml `alt`). Refresh keywords monthly via AdvancedTypeaheadResource; pivot to Christmas/New Year phrases from early Nov.

## Cadence and links (user, 27 Oct)
- 2 pins a day. Only 1 of the 2 carries a link to dryandcosy.com; the other is a pure aesthetic pin with NO link (set `url:` empty in pins.yaml). Alternate which slot gets the link.
- Styles to use: v4edit (editorial full photo) and v4grid (inspo grid), photos made with Higgsfield z_image, realistic, never stock.

## Pin style (user, 27 Oct)
- User rejected v3cover (bold boxes, 'no luxury'). Go back to the original clean, sleek beige editorial styles (checklist / trio / Bodoni). Do not use v3cover.
- ALL POSTING PAUSED by the user on 27 Oct. Do not post or schedule pins until the user says to resume.

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

## Winner (1 Nov)
- WORD pins win by far: Hygge 139 views / 8 saves, Hiraeth 61 / 2 saves, vs ~10 views for everything else. Second best: dark moody photo + serif headline (28 views).
- Batch 2 of 10 word pins scheduled 5-9 Nov (2/day, 1 linked, 1 no link). Long words auto-shrink (ws in make_pins.py).
- Next: more word pins (Irish/Scottish/Nordic cosy words), dark moody photos, centred or low text.

## Browser (user, 11 Nov)
- Always post from the user's 24/7 Windows PC Chrome: deviceId 4967f73a-3d1b-476e-96bd-341d524ee2b0 (connected via switch_browser, labelled "PC"; shows as "Browser 2" in lists). If tools say several browsers are connected, call select_browser with this deviceId. Never use the other Chrome (12885a49-..., its tab groups break) and never the Mac.

## Batch 3 (11 Nov): 5/day test, 12-14 Nov. 3 linked buyer-intent photo pins + 2 no-link (word/aesthetic) per day. Decision point 1 Dec: under 10k monthly impressions or under 30 outbound clicks -> stop or pivot (Etsy prints).
