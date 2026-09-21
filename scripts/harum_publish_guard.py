#!/usr/bin/env python3
import argparse,json,time
from pathlib import Path

ROOT=Path("state/distribution")
ROOT.mkdir(parents=True,exist_ok=True)
DB=ROOT/"publish_guard.json"

def load():
    if DB.exists():
        return json.loads(DB.read_text())
    return {"version":1,"keys":{}}

def save(db):
    DB.write_text(json.dumps(db,ensure_ascii=False,indent=2)+"\n")

p=argparse.ArgumentParser()
p.add_argument("action",choices=["check","start","success","indeterminate","fail"])
p.add_argument("--platform",required=True)
p.add_argument("--asset",required=True)
p.add_argument("--external-id")
p.add_argument("--permalink")
a=p.parse_args()
key=f"{a.platform}:{a.asset}"
db=load(); rec=db["keys"].get(key)
if a.action=="check":
    if not rec:
        print(json.dumps({"allowed":True,"reason":"new"})); raise SystemExit(0)
    if rec["status"] in ("success","indeterminate","started"):
        print(json.dumps({"allowed":False,"reason":rec["status"],"record":rec})); raise SystemExit(3)
    print(json.dumps({"allowed":True,"reason":"previous_failed","record":rec})); raise SystemExit(0)
now=int(time.time())
record={"platform":a.platform,"asset":a.asset,"status":a.action,"updated_at_unix":now}
if a.external_id: record["external_id"]=a.external_id
if a.permalink: record["permalink"]=a.permalink
db["keys"][key]=record; save(db); print(json.dumps(record))
