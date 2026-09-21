#!/usr/bin/env python3
import json,os,sys
from pathlib import Path

if len(sys.argv)!=2:
    raise SystemExit("usage: harum_queue_request.py <request.json>")
p=Path(sys.argv[1])
req=json.loads(p.read_text())
required=["platform","asset_code"]
missing=[k for k in required if not req.get(k)]
if missing:
    raise SystemExit("missing: "+",".join(missing))

allowed={"instagram","threads","youtube","tiktok","pinterest","facebook"}
if req["platform"] not in allowed:
    raise SystemExit("unsupported platform")

mapping={
 "PLATFORM":req["platform"],
 "ASSET_CODE":req["asset_code"],
 "MEDIA_PATH":req.get("media_path",""),
 "PUBLIC_VIDEO_URL":req.get("public_video_url",""),
 "PUBLIC_IMAGE_URL":req.get("public_image_url",""),
 "TITLE":req.get("title",""),
 "TEXT":req.get("text",""),
 "DESCRIPTION":req.get("description",""),
 "PRIVACY":req.get("privacy","private" if req["platform"]=="youtube" else "SELF_ONLY"),
 "IS_AIGC":"true" if req.get("is_aigc",True) else "false",
}
with open(os.environ["GITHUB_ENV"],"a") as f:
    for k,v in mapping.items():
        f.write(f"{k}={str(v).replace(chr(10),'%0A')}\n")
print(json.dumps({"request":str(p),"platform":req["platform"],"asset_code":req["asset_code"]}))
