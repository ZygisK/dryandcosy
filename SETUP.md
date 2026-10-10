# Dry & Cosy launch kit

## 1. You do these (about 30 minutes)
1. **Buy domains:** dryandcosy.com (+ dryandcosy.co.uk optional) on Cloudflare Registrar.
2. **Pinterest business account:** create one at business.pinterest.com.
   - Username: `dryandcosyhome` (`dryandcosy` is taken by a dormant account)
   - Display name: `Dry & Cosy | Damp, Condensation & Drying Clothes Indoors`
   - Bio: `Stop the damp. Dry your washing. Keep your home cosy. Fixes for UK & Irish homes: condensation, black mould, drying clothes indoors & cold rooms.`
   - Country: United Kingdom (or Ireland). Language: English (UK).
3. **Instagram:** reserve `dryandcosy`, or `dryandcosyhome` if it's taken. Don't post yet.
4. **Bank of America compliance:** submit the outside business activity request.
5. **Amazon.co.uk Associates:** **don't apply yet.** Apply in week 3, once 10+ posts are live (the 180-day / 3-sales clock starts at sign-up).

## 2. Pinterest boards (create these 10, exact names)
| Board | Board description |
| --- | --- |
| Drying Clothes Indoors | How to dry clothes indoors without damp: airers, routines and small-space ideas for UK homes. |
| Heated Airers & Clothes Airers | The best heated airers and clothes airers for flats and small houses, with running costs. |
| Dehumidifiers for Damp Homes | Compressor vs desiccant dehumidifiers, laundry mode and which size you need. |
| Condensation & Damp Fixes | Stop condensation on windows and walls with cheap, practical fixes. |
| Black Mould Prevention | Black mould on walls, ceilings and window frames: causes, cleaning and prevention. |
| Small Laundry Space Ideas | Laundry ideas for tiny flats, cupboards and rentals with no utility room. |
| Keep Your House Warm | Cheap ways to keep a cold house warm: draughts, insulation and heat-saving tips. |
| Draught Proofing Ideas | Draught excluders, door seals and window fixes that keep heat in. |
| Renter-Friendly Home Fixes | No-drill, no-damage fixes for damp, cold and storage in rented homes. |
| Cosy Winter Home | Warm, cosy home ideas for winter on a budget. |

## 3. Deploy the site (Vercel)
1. Code lives in a private GitHub repo called `dryandcosy`.
2. Vercel: Add New, then Project, then Import the repo. `vercel.json` sets the build for you.
3. Vercel: Settings, then Domains, add `dryandcosy.com` and follow the DNS steps at your registrar.
4. Pinterest: Settings, then Claimed accounts, claim the website (add the meta tag or DNS record it gives you).

## 4. Daily machine (what runs)
- `content/posts/*.md` then `python3 build.py` then the site
- `pins.yaml` then `python3 make_pins.py` then `dist/pins/*.png` + `pins_bulk.csv`
- Next build step: a GitHub Action that, every morning, drafts pin variants with the Claude API, renders them, deploys, and schedules them (via Pinterest's API or a scheduler).

## 5. Your weekly job
Products live in `products.yaml`. For each one, add:
- `asin:` the product code (it's in the Amazon URL after /dp/). Until then the button links to an Amazon search.
- `take:` your one-line honest opinion

Guides place a product with `[[product id="heated-airer-tiered"]]`. `python3 build.py` reports how many products still need an ASIN or a take.

## 6. Content plan (next 10 posts, highest value first)
1. Heated airer vs dehumidifier: which is cheaper to run? (high order value)
2. Best dehumidifier for a cold house (desiccant)
3. How to stop black mould on bedroom walls
4. Drying clothes in a small flat with no space
5. Condensation in the bedroom overnight: causes and fixes
6. Clothes airers for small spaces (tiered, wall-mounted, over-door)
7. How to keep a cold house warm without the heating on all day
8. Draught proofing a rented home without damaging anything
9. Bathroom mould: stop it coming back
10. Dehumidifier running costs explained (UK/IE)
