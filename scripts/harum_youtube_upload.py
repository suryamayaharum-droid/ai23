import json, os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

required=["YOUTUBE_CLIENT_ID","YOUTUBE_CLIENT_SECRET","YOUTUBE_REFRESH_TOKEN","MEDIA_PATH","TITLE","DESCRIPTION","PRIVACY"]
missing=[k for k in required if not os.getenv(k)]
if missing:
    raise SystemExit("Missing required secrets/inputs: "+", ".join(missing))

media=Path(os.environ["MEDIA_PATH"])
qc=media.with_suffix(".qc.json")
if not media.is_file() or not qc.is_file():
    raise SystemExit("Media or QC receipt missing")

creds=Credentials(
    token=None,
    refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["YOUTUBE_CLIENT_ID"],
    client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)
youtube=build("youtube","v3",credentials=creds,cache_discovery=False)
body={
 "snippet":{"title":os.environ["TITLE"][:100],"description":os.environ["DESCRIPTION"][:5000],"categoryId":"22"},
 "status":{"privacyStatus":os.environ["PRIVACY"],"selfDeclaredMadeForKids":os.getenv("MADE_FOR_KIDS","false").lower()=="true"}
}
request=youtube.videos().insert(
 part="snippet,status",
 body=body,
 media_body=MediaFileUpload(str(media),mimetype="video/mp4",resumable=True),
 notifySubscribers=False,
)
response=None
while response is None:
    status,response=request.next_chunk()
video_id=response["id"]
receipt={
 "platform":"youtube",
 "video_id":video_id,
 "permalink":f"https://www.youtube.com/watch?v={video_id}",
 "source_asset":str(media),
 "title":body["snippet"]["title"],
 "privacy":body["status"]["privacyStatus"],
}
Path("youtube-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(receipt,ensure_ascii=False))
