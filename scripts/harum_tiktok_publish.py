import os,json,time,urllib.request
from pathlib import Path

media=Path(os.environ["MEDIA_PATH"])
token=os.environ["TIKTOK_ACCESS_TOKEN"]
title=os.environ["TITLE"]
if not media.is_file():
    raise SystemExit("media missing")

headers={"Authorization":"Bearer "+token,"Content-Type":"application/json; charset=UTF-8"}

def post_json(url,body):
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers=headers,method="POST")
    with urllib.request.urlopen(req,timeout=60) as r:
        return json.load(r)

info=post_json("https://open.tiktokapis.com/v2/post/publish/creator_info/query/",{})
if info.get("error",{}).get("code")!="ok":
    raise SystemExit(json.dumps(info))
opts=info["data"]["privacy_level_options"]
privacy=os.getenv("PRIVACY","SELF_ONLY")
if privacy not in opts:
    raise SystemExit("privacy not authorized for creator")

size=media.stat().st_size
post_info={
    "title":title,
    "privacy_level":privacy,
    "disable_duet":False,
    "disable_comment":False,
    "disable_stitch":False,
    "is_aigc":os.getenv("IS_AIGC","true").lower()=="true",
}
body={
    "post_info":post_info,
    "source_info":{
        "source":"FILE_UPLOAD",
        "video_size":size,
        "chunk_size":size,
        "total_chunk_count":1,
    },
}
init=post_json("https://open.tiktokapis.com/v2/post/publish/video/init/",body)
if init.get("error",{}).get("code")!="ok":
    raise SystemExit(json.dumps(init))

url=init["data"]["upload_url"]
data=media.read_bytes()
up=urllib.request.Request(
    url,data=data,
    headers={
        "Content-Type":"video/mp4",
        "Content-Length":str(size),
        "Content-Range":f"bytes 0-{size-1}/{size}",
    },
    method="PUT",
)
with urllib.request.urlopen(up,timeout=120) as r:
    r.read()

publish_id=init["data"]["publish_id"]
status_payload=None
for _ in range(12):
    time.sleep(5)
    status_payload=post_json("https://open.tiktokapis.com/v2/post/publish/status/fetch/",{"publish_id":publish_id})
    if status_payload.get("error",{}).get("code")!="ok":
        break
    state=status_payload.get("data",{}).get("status")
    if state in {"PUBLISH_COMPLETE","FAILED","SEND_TO_USER_INBOX"}:
        break

receipt={
    "platform":"tiktok",
    "publish_id":publish_id,
    "source_asset":str(media),
    "privacy":privacy,
    "is_aigc":post_info["is_aigc"],
    "status":"submitted",
    "status_readback":status_payload,
}
Path("tiktok-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(receipt,ensure_ascii=False))
