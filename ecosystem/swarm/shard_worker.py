#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

def bucket(key:str,count:int)->int:
    return int(hashlib.sha256(key.encode()).hexdigest(),16)%count

def tasks():
    return [
      {"id":"dna-audit","kind":"audit","scope":"ecosystem/swarm"},
      {"id":"manifest-audit","kind":"audit","scope":"ecosystem/integration"},
      {"id":"archive-index","kind":"inventory","scope":"assets/harum-noir"},
      {"id":"program-index","kind":"inventory","scope":"ecosystem/programs"},
      {"id":"product-index","kind":"inventory","scope":"ecosystem/products-pdf"},
      {"id":"docs-index","kind":"inventory","scope":"ecosystem/docs"},
      {"id":"mission-plan","kind":"control","scope":"ecosystem/swarm/config/missions.json"},
      {"id":"resource-plan","kind":"control","scope":"ecosystem/swarm/config/resource_profiles.json"}
    ]

def inspect_task(task:dict,root:Path)->dict:
    p=root/task["scope"]
    if p.is_dir():
        files=[x for x in p.rglob("*") if x.is_file()]
        return {"id":task["id"],"kind":task["kind"],"files":len(files),
                "bytes":sum(x.stat().st_size for x in files)}
    if p.is_file():
        return {"id":task["id"],"kind":task["kind"],"files":1,"bytes":p.stat().st_size}
    return {"id":task["id"],"kind":task["kind"],"status":"missing"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--shard",type=int,required=True)
    ap.add_argument("--count",type=int,default=4)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    root=Path(".")
    assigned=[t for t in tasks() if bucket(t["id"],args.count)==args.shard]
    report={"shard":args.shard,"count":args.count,
            "tasks":[inspect_task(t,root) for t in assigned]}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
