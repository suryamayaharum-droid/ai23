import os,json,urllib.request
from pathlib import Path
media=Path(os.environ["MEDIA_PATH"]); token=os.environ["TIKTOK_ACCESS_TOKEN"]; title=os.environ["TITLE"]
if not media.is_file(): raise SystemExit("media missing")
creator=urllib.request.Request("https://open.tiktokapis.com/v2/post/publish/creator_info/query/",data=b"{}",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"},method="POST")
with urllib.request.urlopen(creator) as r: info=json.load(r)
opts=info["data"]["privacy_level_options"]; privacy=os.getenv("PRIVACY","SELF_ONLY")
if privacy not in opts: raise SystemExit("privacy not authorized for creator")
size=media.stat().st_size
body={"post_info":{"title":title,"privacy_level":privacy,"disable_duet":False,"disable_comment":False,"disable_stitch":False},"source_info":{"source":"FILE_UPLOAD","video_size":size,"chunk_size":size,"total_chunk_count":1}}
req=urllib.request.Request("https://open.tiktokapis.com/v2/post/publish/video/init/",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+token,"Content-Type":"application/json; charset=UTF-8"},method="POST")
with urllib.request.urlopen(req) as r: init=json.load(r)
if init.get("error",{}).get("code")!="ok": raise SystemExit(json.dumps(init))
url=init["data"]["upload_url"]; data=media.read_bytes()
up=urllib.request.Request(url,data=data,headers={"Content-Type":"video/mp4","Content-Length":str(size),"Content-Range":f"bytes 0-{size-1}/{size}"},method="PUT")
with urllib.request.urlopen(up) as r: r.read()
receipt={"platform":"tiktok","publish_id":init["data"]["publish_id"],"source_asset":str(media),"status":"submitted"}
Path("tiktok-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps(receipt))
