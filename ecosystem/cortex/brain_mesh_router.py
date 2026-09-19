#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any

def alive(node:dict[str,Any],ttl:int=180)->bool:
    return (
      node.get("health")=="online" and
      int(time.time())-int(node.get("last_heartbeat",0))<=ttl
    )

def select(nodes:list[dict[str,Any]],required:list[str],*,ttl:int=180,
           require_verified:bool=True,distinct:int=1)->dict[str,Any]:
    req=set(required)
    candidates=[]
    for n in nodes:
        if not alive(n,ttl):continue
        if require_verified and not n.get("verified_local_inference"):continue
        if not req.issubset(set(n.get("capabilities",[]))):continue
        score=float(n.get("eval_score") or 0)
        load=float(n.get("load") or 0)
        latency=float(n.get("latency_ms") or 1e9)
        ram=float(n.get("ram_gb") or 0)
        candidates.append((
          -score,load,latency,ram,n.get("node_id",""),n
        ))
    candidates.sort(key=lambda x:x[:5])
    chosen=[x[-1] for x in candidates[:max(1,distinct)]]
    return {
      "complete":len(chosen)>=max(1,distinct),
      "required":required,
      "chosen":chosen,
      "available_candidates":len(candidates)
    }

def load_registry(path:str="runtime/brain-nodes.json"):
    p=Path(path)
    if not p.exists():return []
    d=json.loads(p.read_text(encoding="utf-8"))
    return d.get("nodes",d if isinstance(d,list) else [])

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("capabilities",nargs="+")
    ap.add_argument("--registry",default="runtime/brain-nodes.json")
    ap.add_argument("--distinct",type=int,default=1)
    args=ap.parse_args()
    print(json.dumps(select(load_registry(args.registry),args.capabilities,distinct=args.distinct),
                     ensure_ascii=False,indent=2))
