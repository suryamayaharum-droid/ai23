import json,os,time,urllib.parse,urllib.request
from pathlib import Path
token=os.environ["META_PAGE_ACCESS_TOKEN"]
user=os.environ["META_IG_USER_ID"]
version=os.getenv("META_GRAPH_VERSION","v24.0")
video=os.environ["VIDEO_URL"]; caption=os.environ.get("CAPTION","")
base=f"https://graph.facebook.com/{version}"
def post(url,data):
    body=urllib.parse.urlencode(data).encode()
    req=urllib.request.Request(url,data=body,method="POST")
    with urllib.request.urlopen(req,timeout=60) as r: return json.load(r)
def get(url,params):
    q=urllib.parse.urlencode(params)
    with urllib.request.urlopen(url+"?"+q,timeout=60) as r: return json.load(r)
c=post(f"{base}/{user}/media",{"media_type":"REELS","video_url":video,"caption":caption,"share_to_feed":"true","access_token":token})
cid=c["id"]
for _ in range(30):
    st=get(f"{base}/{cid}",{"fields":"status_code,status","access_token":token})
    if st.get("status_code")=="FINISHED": break
    if st.get("status_code") in {"ERROR","EXPIRED"}: raise SystemExit(json.dumps(st))
    time.sleep(10)
else: raise SystemExit("container not ready; mark indeterminate and reconcile before retry")
pub=post(f"{base}/{user}/media_publish",{"creation_id":cid,"access_token":token})
receipt={"platform":"instagram","route":"meta_api","media_id":pub["id"],"container_id":cid,"status":"published"}
Path("instagram-direct-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps(receipt))
