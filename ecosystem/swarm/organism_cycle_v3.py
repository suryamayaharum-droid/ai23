#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from organism_cycle_v2 import run as run_v2
from hybrid_state import HybridState

def run(db:str,output:str):
    result=run_v2(db,output)
    hybrid=HybridState()
    digest=result.get("pulse",{}).get("organism_digest")
    sync=hybrid.heartbeat(
      "organism.root",
      layer="control-plane",
      district="governo",
      capabilities=[
        "coordinate","event_store","checkpoint","reconcile",
        "resource_route","capability_mesh"
      ],
      health=result.get("pulse",{}).get("health",{}).get("status","unknown"),
      load=0,
      hologram_digest=digest,
      vector_clock=result.get("pulse",{}).get("vector_clock",{}),
      state={
        "cycle":"v3",
        "redundancy_score":result.get("redundancy",{}).get("score"),
        "resource_fabric_complete":result.get("resource_fabric",{}).get("complete"),
        "backend_mode":hybrid.mode
      }
    )
    result["hybrid_backend"]=sync
    result["schema"]="harum.organism.cycle.v3"
    result["timestamp_v3"]=int(time.time())
    p=Path(output)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_organism.db")
    ap.add_argument("--output",default="runtime/organism-v3.json")
    args=ap.parse_args()
    print(json.dumps(run(args.db,args.output),ensure_ascii=False,indent=2))
