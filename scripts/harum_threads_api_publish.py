import json,os,time,urllib.parse,urllib.request
from pathlib import Path
token=os.environ["THREADS_ACCESS_TOKEN"]
host=os.getenv("THREADS_API_HOST","https://graph.threads.net")
text=os.environ.get("TEXT","")
media_type=os.getenv("MEDIA_TYPE","TEXT").upper()
data={"media_type":media_type,"text":text,"access_token":token}
if media_type=="IMAGE": data["image_url"]=os.environ["IMAGE_URL"]
if media_type=="VIDEO": data["video_url"]=os.environ["VIDEO_URL"]
body=urllib.parse.urlencode(data).encode()
req=urllib.request.Request(host+"/me/threads",data=body,method="POST")
with urllib.request.urlopen(req,timeout=60) as r: c=json.load(r)
cid=c["id"]
time.sleep(2)
body=urllib.parse.urlencode({"creation_id":cid,"access_token":token}).encode()
req=urllib.request.Request(host+"/me/threads_publish",data=body,method="POST")
with urllib.request.urlopen(req,timeout=60) as r: p=json.load(r)
receipt={"platform":"threads","route":"threads_api","media_id":p["id"],"container_id":cid,"status":"published"}
Path("threads-direct-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n"); print(json.dumps(receipt))
