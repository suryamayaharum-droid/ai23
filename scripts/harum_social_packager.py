import argparse,json,hashlib,re
from pathlib import Path

def clean(s): return re.sub(r"\s+"," ",s).strip()
def pack(platform,title,story,cta):
    base=clean(story)
    if platform=="instagram": return {"title":title,"caption":base+"\n\n"+cta,"format":"reel"}
    if platform=="threads": return {"text":clean(base[:420])+"\n\n"+cta,"format":"image_or_text"}
    if platform=="youtube": return {"title":clean(title)[:100],"description":base+"\n\n"+cta+"\n#HarumNoir #ArteHarum","format":"short"}
    if platform=="tiktok": return {"title":clean(base[:160])+" #HarumNoir #desenhoacarvao","format":"vertical_video","is_aigc":False}
    if platform=="pinterest": return {"title":clean(title)[:100],"description":clean(base+" "+cta)[:500],"format":"pin"}
    if platform=="facebook": return {"caption":base+"\n\n"+cta,"format":"reel"}
    raise ValueError(platform)
ap=argparse.ArgumentParser(); ap.add_argument("--asset",required=True); ap.add_argument("--code",required=True); ap.add_argument("--title",required=True); ap.add_argument("--story",required=True); ap.add_argument("--cta",default="Acompanhe o arquivo HARUM NOIR.")
a=ap.parse_args(); p=Path(a.asset)
if not p.is_file(): raise SystemExit("asset missing")
h=hashlib.sha256(p.read_bytes()).hexdigest()
out={"asset_code":a.code,"source_asset":str(p),"sha256":h,"platforms":{}}
for x in ["instagram","threads","youtube","tiktok","pinterest","facebook"]: out["platforms"][x]=pack(x,a.title,a.story,a.cta)
Path("distribution-pack.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(out,ensure_ascii=False))
