"""SEO titles and descriptions for every pin, written against real Pinterest UK
search suggestions (AdvancedTypeaheadResource, pulled 18 Oct 2026, see
ops/keywords-2026-10-18.md). Rules:
- Title opens with the exact phrase people type (front-loaded), 40-75 chars.
- Description 300-480 chars, 3-5 keyword variants woven into real sentences,
  UK/Irish framing, one soft call to action. No hashtags, no em dashes.
Run: python3 ops/seo_meta.py  (rewrites title/description/alt in pins.yaml)
"""
import re, sys
from pathlib import Path

M = {
"free-fixes-drying-indoors": ("Drying clothes indoors hacks: 5 free fixes that stop damp",
 "Drying clothes indoors in winter without the damp? These 5 free drying clothes indoors hacks work in any UK or Irish home: spin twice, crack a window, space the load, close the door and keep the heating low and steady. Simple laundry hacks for small spaces with no tumble dryer. Save this for the next rainy washing day."),
"dry-clothes-faster-winter": ("Drying clothes indoors winter: how to dry them faster",
 "How to dry clothes faster indoors in winter, even on a wet week. Air drying clothes indoors tips that actually work: an extra spin, a clothes drying rack by a warm wall, a fan or dehumidifier in the same room and smart spacing. Drying clothes indoors ideas for UK and Irish homes with no garden and no tumble dryer."),
"small-flat-no-dryer": ("Drying clothes indoors small spaces: ideas for a flat with no dryer",
 "Drying clothes indoors in small spaces with no tumble dryer? Clever clothes airer ideas for small flats: wall mounted airers, over the door rails, ceiling pulley airers and folding racks that store flat. Small laundry room ideas and laundry room small space ideas for renters in the UK and Ireland. Save for your flat."),
"windows-wet-every-morning": ("Condensation on windows: why they are wet every morning",
 "Condensation on windows every morning? It is not your windows, it is the air. Here is why it happens in UK and Irish homes and the condensation windows tips that stop it: open trickle vents, wipe with a window vac, dry washing in one room and run a small dehumidifier. Stop condensation on windows before it turns to mould."),
"stop-condensation-before-mould": ("Stop condensation on windows before it turns to black mould",
 "Stop condensation on windows before it becomes black mould around the frames and on the walls. Easy condensation windows tips for winter: ventilate after showers and cooking, wipe glass each morning, keep furniture off cold walls and use a dehumidifier in damp rooms. A simple routine for UK and Irish homes. Save this for winter."),
"warm-without-heating-all-day": ("How to stay warm in winter without the heating on all day",
 "How to stay warm in winter without running the heating all day. Cosy, cheap ideas: a heated throw blanket on the sofa, an electric blanket in bed, draught excluders on doors and heating only the room you sit in. Stay warm and cosy while the energy bills stay low, for UK and Irish homes. Save for cold evenings."),
"cosy-evenings-for-less": ("Cosy winter home ideas: cosy evenings in for less",
 "Cosy winter home ideas that cost less to run. Warm lamp light, a heavy throw, a hot water bottle and one warm room make a cosy winter living room without heating the whole house. Cosy home ideas and winter home vibes for long dark evenings in the UK and Ireland. Save this for your cosy winter aesthetic board."),
"keep-the-heat-you-pay-for": ("Draught proofing home: keep the heat you pay for",
 "Draught proofing your home is the cheapest way to stay warm in winter. Draught excluder ideas for doors, self adhesive window seals, letterbox brushes and chimney balloons keep the heat in. Simple draught proofing for UK and Irish homes, most of it renter friendly. Save this winter home checklist before the cold sets in."),
"heat-only-rooms-you-use": ("Energy saving tips: heat only the rooms you use",
 "Energy saving tips for winter: smart radiator valves let you heat only the rooms you actually use. Set the bedroom warm at night, the living room warm in the evening and leave spare rooms cool. An easy energy saving house upgrade for UK and Irish homes that cuts heating bills without feeling cold. Save for later."),
"which-dehumidifier": ("Best dehumidifier for drying clothes: compressor or desiccant?",
 "Compressor or desiccant dehumidifier, which is best for your home? Desiccant suits cold rooms and drying clothes indoors in winter, compressor suits warmer rooms and big damp problems. A simple guide to choosing a dehumidifier for your bedroom, bathroom or laundry space in the UK and Ireland. Save this before you buy."),
"dry-mould-free-bathroom": ("Mould free bathroom: how to keep a bathroom dry",
 "How to keep a bathroom dry and mould free all winter. Run the extractor fan for 20 minutes, squeegee the tiles, leave the door open after showers and use a small dehumidifier for bathroom damp. How to clean mould in a bathroom and stop black mould coming back, for UK and Irish homes. Save this bathroom routine."),
"wet-washing-dry-walls": ("Drying clothes indoors without damp walls",
 "Drying clothes indoors puts litres of water into the air, and it ends up on your walls and windows. How to dry washing indoors without damp walls: one room, door closed, window open a crack and a dehumidifier or heated clothes airer doing the work. Drying clothes indoors winter tips for UK and Irish homes. Save this."),
"rainy-day-cosy-home": ("Rainy day aesthetic: a cosy home on a wet afternoon",
 "Rainy day aesthetic for a cosy home: rain on the window, a lamp on, a blanket and a warm drink. Cosy home inspiration and autumn home aesthetic ideas for slow wet days in the UK and Ireland. Make your home a calm, warm place to be when the weather turns. Save to your cosy winter home board."),
"sheets-dry-no-damp-smell": ("Drying bedding indoors without a damp smell",
 "How to dry sheets, duvet covers and bedding indoors without that damp smell. Fold sheets over a clothes airer in a W shape, turn them halfway, keep air moving and finish on a heated clothes airer. Drying clothes indoors ideas for big loads in small spaces, for UK and Irish homes with no tumble dryer. Save for wash day."),
"unused-fireplace-draught": ("Draught proofing: stop draughts from an unused fireplace",
 "An unused fireplace can pull warm air straight up the chimney. Draught proofing the easy way: a chimney balloon or a fireplace draught excluder blocks the cold air and saves on heating. Draught excluder ideas for period homes and cosy winter living rooms in the UK and Ireland. Save this draught proofing home tip."),
"9-ways-dry-clothes-indoors": ("9 drying clothes indoors ideas, no tumble dryer needed",
 "9 ways to dry clothes indoors without a tumble dryer. Drying clothes indoors ideas and hacks for winter: heated clothes airers, dehumidifiers, wall mounted airers, extra spins, smart spacing and the best room to dry washing in. Laundry hacks for small spaces in UK and Irish homes. Save this list for rainy wash days."),
"7-ways-stop-window-condensation": ("7 ways to stop condensation on windows",
 "7 ways to stop condensation on windows for good. Condensation windows tips that work in UK and Irish homes: trickle vents open, a window vac each morning, lids on pans, extractor fans on, washing dried in one room, a bedroom dehumidifier and steady low heat. Stop condensation on windows before mould starts. Save this."),
"windows-look-like-this": ("Condensation on windows every morning? Do this",
 "Do your windows look like this every morning? Condensation on windows means too much moisture indoors. Quick condensation windows tips: wipe it off, open the trickle vents, ventilate after showers and run a dehumidifier overnight in the bedroom. Stop condensation on windows in winter in UK and Irish homes. Save for later."),
"5-signs-need-dehumidifier": ("5 signs your home needs a dehumidifier",
 "5 signs your home needs a dehumidifier: wet windows every morning, a musty smell, washing that takes days to dry, black spots on walls and a bathroom that never dries out. Which dehumidifier for bathroom, bedroom or drying clothes indoors in winter, for UK and Irish homes. Save this before damp sets in."),
"black-mould-coming-back": ("Black mould removal: why it keeps coming back",
 "Black mould keeps coming back because the moisture never leaves. Black mould removal that lasts: clean it properly, then fix the cause with ventilation, a dehumidifier and less condensation on windows. How to clean mould on walls, window frames and in the bathroom for UK and Irish homes. Save this mould removal guide."),
"6-cheap-ways-stay-warm": ("6 cheap ways to stay warm in winter without heating the whole house",
 "6 cheap ways to stay warm in winter without heating the whole house. A heated throw blanket, an electric blanket, a hot water bottle, draught excluders, thermal curtains and one warm room. Stay warm and cosy and save on energy bills, with costs per hour for UK and Irish homes. Save this for the cold months."),
"bosch-dry-1000-hero": ("Best dehumidifier for bedroom: quiet, compact Bosch Dry 1000",
 "Looking for the best dehumidifier for a bedroom? The Bosch Dry 1000 is quiet enough to sleep next to, compact and looks good in the room. It stops condensation on windows overnight and helps with drying clothes indoors. A dehumidifier aesthetic people actually want on show, for UK and Irish homes. Save this pick."),
"bosch-10-litres-a-day": ("Quiet dehumidifier for bedroom and drying clothes: Bosch Dry 1000",
 "Bosch Dry 1000 dehumidifier pulls about 10 litres a day while staying whisper quiet. A great quiet dehumidifier for bedroom condensation and drying clothes indoors in winter. Compact, simple and easy to empty, for flats and family homes in the UK and Ireland. Save this if your windows are wet every morning."),
"3-dehumidifiers-worth-buying": ("Best dehumidifier UK: 3 worth buying this winter",
 "The 3 best dehumidifiers for UK homes this winter: a quiet dehumidifier for the bedroom, a desiccant for cold rooms and drying clothes indoors, and a bigger one for serious damp. Simple picks with what each is best for, for UK and Irish homes. Stop condensation and black mould. Save this before you buy."),
"word-coorie": ("Coorie meaning: the Scottish art of a cosy winter home",
 "Coorie is the Scottish word for getting cosy, close and warm. Like hygge, it is about blankets, warm light, good food and slow evenings. Cosy winter home ideas and cosy home aesthetic inspiration for the UK and Ireland. Bring a little coorie into your winter living room. Save this word for your cosy winter aesthetic board."),
"word-hygge": ("Hygge meaning: hygge winter home ideas",
 "Hygge is the Danish feeling of cosiness and contentment. Hygge winter home ideas: soft lamp light, candles, a heavy throw, warm drinks and time with people you love. Hygge decor and hygge aesthetic home inspiration for long dark evenings in the UK and Ireland. Save this for your cosy winter home board."),
"word-cwtch": ("Cwtch meaning: the Welsh word for a cosy cuddle",
 "Cwtch is the Welsh word for a cosy cuddle and a safe, warm place. Cosy home ideas inspired by cwtch: a snug corner, a soft throw, a hot water bottle and a warm room on a cold night. Cosy winter vibes and cosy home aesthetic inspiration from the UK and Ireland. Save this word for your cosy board."),
"word-hiraeth": ("Hiraeth meaning: the Welsh word for longing for home",
 "Hiraeth is the Welsh word for a deep longing for home. A beautiful word for anyone who loves a cosy home, autumn home aesthetic and the feeling of coming in from the cold. Cosy home inspiration and cosy winter vibes from Wales, the UK and Ireland. Save this word for your cosy home aesthetic board."),
"mood-stove-knit-blanket": ("Cosy winter living room: stove lit, blanket on",
 "Cosy winter living room inspiration: the stove lit, a chunky knit blanket and nowhere to be. Cosy winter decor and cosy home aesthetic ideas for slow evenings in the UK and Ireland. A warm room you actually want to sit in, without heating the whole house. Save to your cosy winter home board."),
"mood-sofa-heavy-throw": ("Cosy winter aesthetic: heavy throw season",
 "Heavy throw season has officially started. Cosy winter aesthetic inspiration for the sofa: a big soft throw, warm lamp light and a slow evening in. Cosy winter decor and cosy living room ideas that keep you warm for less, for UK and Irish homes. Save this to your cosy winter home board."),
"mood-reading-corner-throw": ("Cosy home ideas: a reading corner with a soft throw",
 "Cosy home ideas for a reading corner: a comfy chair, a soft throw, a warm lamp and a good book. Cosy home aesthetic and hygge home inspiration for autumn and winter in the UK and Ireland. A small corner that makes the whole house feel warmer. Save to your cosy home inspiration board."),
"mood-washing-by-window": ("Drying clothes indoors aesthetic: washing by the window",
 "Drying clothes indoors aesthetic: washing day, a clothes airer by a bright window. Clothes airer ideas and hang drying clothes indoors inspiration for small spaces with no tumble dryer. Simple, calm laundry room ideas for UK and Irish homes. Save this to your small laundry space ideas board."),
"mood-warm-lamp-bedroom": ("Cosy winter bedroom: a warm bed on a cold night",
 "Cosy winter bedroom inspiration: a warm lamp, layered bedding and an electric blanket on a cold night. Winter bedroom ideas cosy enough to make dark evenings feel good, without the heating on all night. Cosy bedroom aesthetic for UK and Irish homes. Save to your winter bedroom aesthetic board."),
"mood-bright-dry-bedroom": ("Winter bedroom ideas: a bedroom that stays fresh and dry",
 "Winter bedroom ideas for a room that stays fresh, bright and dry. No condensation on the windows, no musty smell, no damp corners. A quiet bedroom dehumidifier and good airflow keep it that way. Cosy bedroom aesthetic and damp free living for UK and Irish homes. Save this to your winter bedroom board."),
"mood-front-door-coats": ("Draught excluder ideas: coats on the hooks, cold kept out",
 "Coats on the hooks, cold kept outside. Draught excluder ideas for the front door: a door draught excluder, a letterbox brush and self adhesive seals keep the hallway warm. Cosy winter home and draught proofing home ideas for UK and Irish houses. Save this to your draught proofing ideas board."),
"cost-per-hour-stay-warm": ("Stay warm in winter for less: what it costs per hour",
 "What it really costs per hour to stay warm in winter. A heated throw blanket costs pennies an hour, an electric blanket even less, while a plug in heater costs far more. Energy saving tips to stay warm and cosy for less, with real UK running costs. Save this before you switch the heating on."),
"checklist-winter-proof-weekend": ("Winter home checklist: winter-proof your home in a weekend",
 "A winter home checklist to winter-proof your home in one weekend. Draught proofing, bleeding radiators, sealing windows, a door draught excluder, a dehumidifier for damp rooms and a heated airer for washing. Simple jobs that keep UK and Irish homes warm and dry all winter. Save this checklist for the weekend."),
"renter-draught-fixes": ("Draught proofing for renters: no drilling, deposit safe",
 "Renter friendly draught proofing that keeps your deposit safe. Draught excluder ideas with no drilling: self adhesive window seals, removable door draught excluders, letterbox brushes, thermal curtains and a chimney balloon. Draught proofing home ideas for renters in the UK and Ireland. Save this before winter."),
"blanket-throw-bottle-costs": ("Electric blanket vs heated throw vs hot water bottle: costs",
 "Electric blanket, heated throw blanket or hot water bottle, which is cheapest to stay warm? An electric blanket costs about 2p an hour, a heated throw about 3p and a hot water bottle about 5p a fill, compared with over 50p an hour for a plug in heater. Energy saving tips to stay warm in winter. Save this."),
"mould-free-bathroom-routine": ("Mould free bathroom routine: five minutes a week",
 "The mould free bathroom routine that takes five minutes a week. Squeegee the tiles, run the extractor fan, wipe the window, wash the bath mat and spray the sealant lines. How to clean mould in a bathroom and stop black mould coming back, for UK and Irish homes. Save this bathroom cleaning routine."),
"washing-smells-damp": ("Why your washing smells damp when drying clothes indoors",
 "Why does washing smell damp when you dry clothes indoors? It dries too slowly. Air drying clothes indoors tips to fix it: an extra spin, space between items, a warm room with airflow and a dehumidifier or heated clothes airer. Drying clothes indoors hacks for winter in UK and Irish homes. Save for wash day."),
"baby-clothes-drying": ("Drying baby clothes indoors without damp or mould",
 "How to dry baby clothes indoors safely, without damp or mould in the nursery. Use a heated clothes airer in a separate room, keep the door closed, ventilate and run a dehumidifier. Drying clothes indoors ideas for new parents in UK and Irish homes with lots of small loads. Save this for wash day."),
"drying-indoors-do-this-first": ("Drying clothes indoors? Do this first to stop the damp",
 "Drying clothes indoors? Do this first: pick one room, close the door, open the window a crack and give the load an extra spin. Simple drying clothes indoors hacks that stop damp walls and condensation on windows. Drying clothes indoors winter tips for UK and Irish homes. Save this for your next rainy wash day."),
"washing-dry-in-a-day": ("Drying clothes indoors: dry in a day, not three",
 "How to get washing dry in a day indoors, not three. Drying clothes indoors hacks: an extra spin, a clothes drying rack near warmth, items spaced out and a dehumidifier in the room. Air drying clothes indoors tips for winter, for UK and Irish homes with no tumble dryer. Save this for wash day."),
"no-dryer-no-damp": ("Drying clothes indoors with no tumble dryer and no damp",
 "Dry clothes indoors with no tumble dryer and no damp. Heated clothes airers, dehumidifiers and smart drying clothes indoors ideas for winter that keep walls and windows dry. Laundry hacks for small spaces and flats in the UK and Ireland. Save this drying clothes indoors guide for rainy weeks."),
"where-to-dry-washing-small-home": ("Drying clothes indoors small spaces: the best place to dry",
 "Where is the best place to dry washing indoors in a small home? Not the bedroom. Drying clothes indoors in small spaces works best in one warm room with a door you can close and a window you can open. Clothes airer ideas and small laundry room ideas for UK and Irish flats. Save this for your small space."),
"towels-still-damp": ("How to dry towels indoors: still damp the next day?",
 "Towels still damp the next day? How to dry towels indoors fast: an extra spin, hang them folded over two rails, turn them halfway and finish on a heated clothes airer. Drying clothes indoors winter hacks for thick loads in UK and Irish homes with no tumble dryer. Save this for towel wash day."),
"cosy-nights-for-less": ("Cosy winter home: cosy nights in for less",
 "Cosy nights in for less this winter. Cosy winter home ideas: lamp light instead of big lights, a heavy throw, a hot water bottle, warm socks and one warm room. Stay warm and cosy without high energy bills, for UK and Irish homes. Cosy winter vibes for long dark evenings. Save to your cosy winter board."),
"rainy-day-dry-washing": ("Rainy day? Drying clothes indoors without the damp",
 "Rainy day and a full basket? Drying clothes indoors without the damp: an extra spin, one room with the door closed, a window open a crack and a dehumidifier or heated airer. Drying clothes indoors winter tips and hacks for UK and Irish homes with no garden or dryer. Save this for rainy days."),
"photo-stove-rain-outside": ("Cosy winter aesthetic: stove on, rain outside",
 "Stove on, rain outside, nowhere to be. Cosy winter aesthetic and rainy day aesthetic inspiration for a warm living room. Cosy winter home decor ideas for slow wet evenings in the UK and Ireland. Make one room warm and stay cosy for less. Save to your cosy winter home board."),
"wet-windows-not-the-windows": ("Condensation on windows? It is not the windows",
 "Wet windows every morning? It is not the windows, it is moisture in the air from breathing, showers, cooking and drying washing. Condensation windows tips that fix the cause: ventilate, wipe, dry clothes in one room and run a bedroom dehumidifier. Stop condensation on windows in UK and Irish homes. Save this."),
"airer-full-again": ("Clothes airer full again? Drying clothes indoors faster",
 "Clothes airer full again? How to dry a load faster indoors: an extra spin, a heated clothes airer, space between items and a dehumidifier in the room. Clothes airer ideas and drying clothes indoors hacks for busy households in UK and Irish homes. Save this for your next wash day."),
"photo-slow-sunday-plants": ("Cosy home aesthetic: a slow Sunday at home",
 "A slow Sunday at home. Cosy home aesthetic inspiration with plants, soft light and a sofa by the window. Autumn home aesthetic and slow living ideas for cosy weekends in the UK and Ireland. Make your home a calm, warm place to be. Save to your cosy home inspiration board."),
"ultimate-guide-dry-warm-home": ("Winter home checklist: the ultimate guide to a dry, warm home",
 "The ultimate winter home checklist for a dry, warm home. Drying clothes indoors without damp, how to stop condensation on windows, black mould removal, draught proofing your home and staying warm for less. Everything UK and Irish homes need for winter, with the products that actually work. Save this guide."),
"heated-airers-worth-buying": ("Heated clothes airer: 3 best for drying clothes indoors",
 "Which heated clothes airer should you buy? The best heated airer with a cover for fast drying, the best for small spaces and flats, and the best winged airer for sheets and towels. Dry washing indoors in winter for pennies an hour, for UK and Irish homes. Save this before you buy a heated airer."),
"condensation-guide-save-this": ("How to stop condensation on windows: a simple checklist",
 "How to stop condensation on windows for good, a simple checklist. Condensation windows tips for UK and Irish homes: open trickle vents, a window vac each morning, extractor fans on, dry washing in one room and a quiet bedroom dehumidifier. Stop condensation on windows before black mould starts. Save this checklist."),
"stay-warm-for-less-trio": ("How to stay warm in winter without heating the whole house",
 "How to stay warm in winter without heating the whole house. Three cheap ways: a heated throw blanket for the sofa, an electric blanket for bed and an oil radiator for one room. Stay warm and cosy with energy saving tips and real running costs for UK and Irish homes. Save this for the cold months."),
"black-mould-checklist": ("Black mould removal: a simple checklist to get rid of it for good",
 "How to get rid of black mould for good, a simple black mould removal checklist. How to clean mould in the bathroom, on window frames and on walls, then stop it coming back with ventilation, sealant and a dehumidifier. For UK and Irish homes. Save this mould removal checklist."),
}

def main():
    p = Path("pins.yaml"); s = p.read_text()
    import yaml
    slugs = [x["slug"] for x in yaml.safe_load(s)]
    missing = [x for x in slugs if x not in M]
    if missing: sys.exit(f"missing: {missing}")
    for slug,(t,d) in M.items():
        assert len(t) <= 100 and len(d) <= 500 and "—" not in t + d, slug
        q = lambda v: '"' + v.replace('\\','\\\\').replace('"','\\"') + '"'
        block = re.search(rf"- slug: {re.escape(slug)}\n((?:  .*\n?)*)", s)
        if not block: sys.exit("no block " + slug)
        b = block.group(0)
        nb = re.sub(r"\n  title: .*(?:\n    .*)*", "\n  title: " + q(t), b)
        nb = re.sub(r"\n  description: .*(?:\n    .*)*", "\n  description: " + q(d), nb)
        nb = re.sub(r"\n  alt: .*", "", nb)
        nb = nb.rstrip("\n") + "\n  alt: " + q(t + ". " + d.split(". ")[0] + ".") + "\n"
        s = s.replace(b, nb, 1)
    yaml.safe_load(s)
    p.write_text(s)
    print("updated", len(M))

if __name__ == "__main__":
    main()
