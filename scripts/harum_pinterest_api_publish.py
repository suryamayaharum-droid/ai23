import json,os,urllib.request
from pathlib import Path
token=os.environ["PINTEREST_ACCESS_TOKEN"]
board=os.environ["PINTEREST_BOARD_ID"]
image=os.environ["IMAGE_URL"]
body={
 "board_id":board,
 "title":os.environ.get("TITLE","")[:100],
 "description":os.environ.get("DESCRIPTION","")[:500],
 "media_source":{"source_type":"image_url","url":image}
}
if os.getenv("LINK_URL"): body["link"]=os.environ["LINK_URL"]
req=urllib.request.Request("https://api.pinterest.com/v5/pins",data=json.dumps(body).encode(),method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
with urllib.request.urlopen(req,timeout=60) as r: p=json.load(r)
receipt={"platform":"pinterest","route":"pinterest_api","pin_id":p["id"],"status":"published"}
Path("pinterest-direct-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps(receipt))
