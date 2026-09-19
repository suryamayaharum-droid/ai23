#!/usr/bin/env python3
"""Queue API-exported ComfyUI workflows on a local/authorized ComfyUI server."""
from __future__ import annotations
import argparse, json, time, urllib.request, uuid
from pathlib import Path

def request_json(url,data=None):
    req=urllib.request.Request(url,data=None if data is None else json.dumps(data).encode("utf-8"),
                               headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=20) as r: return json.loads(r.read())

def patch(workflow,assignments):
    for item in assignments:
        lhs,value=item.split("=",1); node,input_name=lhs.split(".",1)
        if node not in workflow: raise KeyError(f"node {node} missing")
        try: parsed=json.loads(value)
        except Exception: parsed=value
        workflow[node].setdefault("inputs",{})[input_name]=parsed
    return workflow

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("workflow",help="ComfyUI workflow exported with File -> Export (API)")
    ap.add_argument("--server",default="127.0.0.1:8188")
    ap.add_argument("--set",action="append",default=[],metavar="NODE.INPUT=VALUE")
    ap.add_argument("--poll",type=float,default=1.5)
    a=ap.parse_args(); wf=json.loads(Path(a.workflow).read_text(encoding="utf-8")); patch(wf,a.set)
    client_id=str(uuid.uuid4())
    queued=request_json(f"http://{a.server}/prompt",{"prompt":wf,"client_id":client_id})
    pid=queued["prompt_id"]; print(json.dumps({"prompt_id":pid,"client_id":client_id},indent=2))
    while True:
        hist=request_json(f"http://{a.server}/history/{pid}")
        if pid in hist:
            Path(f"comfy_history_{pid}.json").write_text(json.dumps(hist[pid],indent=2),encoding="utf-8")
            print(f"done: {pid}"); break
        time.sleep(a.poll)

if __name__=="__main__": main()
