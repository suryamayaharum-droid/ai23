#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, socket, time, urllib.request
from pathlib import Path

TOKEN=os.environ.get("HARUM_MESH_TOKEN","")

def call(url:str,method:str="GET",payload=None):
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(url,data=data,method=method)
    if TOKEN:
        req.add_header("Authorization","Bearer "+TOKEN)
    if data:
        req.add_header("Content-Type","application/json")
    with urllib.request.urlopen(req,timeout=30) as r:
        if r.status==204: return None
        return json.loads(r.read().decode())

def execute(task):
    required=set(task.get("required",[]))
    allowed={"hash","inventory","qc","checkpoint","json","python","shell"}
    if not required.issubset(allowed):
        return {"status":"UNSUPPORTED","missing":sorted(required-allowed)}
    payload=task.get("payload",{})
    op=payload.get("op","echo")
    if op=="hash_file":
        p=Path(payload["path"])
        h=hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):
                h.update(chunk)
        return {"status":"OK","sha256":h.hexdigest(),"bytes":p.stat().st_size}
    if op=="inventory":
        p=Path(payload.get("path","."))
        files=[x for x in p.rglob("*") if x.is_file()]
        return {"status":"OK","files":len(files),"bytes":sum(x.stat().st_size for x in files)}
    return {"status":"OK","echo":payload}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--gateway",default="http://127.0.0.1:8765")
    ap.add_argument("--once",action="store_true")
    ap.add_argument("--sleep",type=int,default=5)
    args=ap.parse_args()
    if not TOKEN:
        raise SystemExit("HARUM_MESH_TOKEN must be set")
    wid=socket.gethostname()
    while True:
        try:
            task=call(args.gateway+"/pull")
            if task:
                out=execute(task)
                call(args.gateway+"/complete","POST",{"id":task["id"],"worker":wid,"output":out})
            elif args.once:
                return
        except Exception as exc:
            if args.once:
                raise
        time.sleep(max(args.sleep,1))

if __name__=="__main__":
    main()
