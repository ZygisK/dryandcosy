import json, sys, yaml
B={"Drying Clothes Indoors":"1150669842234840914","Heated Airers & Clothes Airers":"1150669842234840915","Dehumidifiers for Damp Homes":"1150669842234840916","Condensation & Damp Fixes":"1150669842234840917","Black Mould Prevention":"1150669842234840918","Small Laundry Space Ideas":"1150669842234840919","Keep Your House Warm":"1150669842234840920","Draught Proofing Ideas":"1150669842234840921","Cosy Winter Home":"1150669842234840924"}
p=next(x for x in yaml.safe_load(open("pins.yaml")) if x["slug"]==sys.argv[1])
o={"board_id":B[p["board"]],"image_url":f"https://dryandcosy.com/pins/v2/{p['slug']}.jpg","link":("https://dryandcosy.com"+p["url"]) if p.get("url") else "","title":p["title"][:100],"description":p["description"][:500],"alt_text":p.get("alt",p["title"])[:500],"method":"scraped","scrape_metric":{"source":"www_url_scrape"}}
if not p.get("url"):
    o.pop("link"); o["method"]="uploaded"; o.pop("scrape_metric")
print("const options="+json.dumps(o)+";")
