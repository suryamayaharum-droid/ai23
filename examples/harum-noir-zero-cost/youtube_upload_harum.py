#!/usr/bin/env python3
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES=["https://www.googleapis.com/auth/youtube.upload"]

def upload(video, meta_path, client_secret="client_secret.json"):
    meta=json.load(open(meta_path, encoding="utf-8"))
    creds=InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES).run_local_server(port=0)
    yt=build("youtube","v3",credentials=creds)
    body={
      "snippet":{"title":meta["title"],"description":meta["description"],"tags":meta.get("tags",[]),"categoryId":meta.get("categoryId","26")},
      "status":{"privacyStatus":meta.get("privacyStatus","private"),"selfDeclaredMadeForKids":False}
    }
    req=yt.videos().insert(part="snippet,status",body=body,media_body=MediaFileUpload(video,chunksize=-1,resumable=True))
    response=None
    while response is None:
        status,response=req.next_chunk()
        if status: print(f"{int(status.progress()*100)}%")
    print("Video ID:",response["id"])
    return response
