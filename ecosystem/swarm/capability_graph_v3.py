#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

SWARM=Path(__file__).resolve().parent
ROOT=SWARM.parents[1]

from capability_graph_v2 import build as build_v2
from browser_bridge import status as browser_status

def build():
    graph=defaultdict(list)
    for cap,providers in build_v2().items():
        graph[cap].extend(providers)

    browser=browser_status()
    cfg=json.loads((ROOT/"ecosystem"/"browser-fabric"/"config"/"resource.json").read_text(encoding="utf-8"))
    for cap in cfg.get("capabilities",[]):
        graph[cap].append({
          "kind":"browser-fabric",
          "id":cfg["id"],
          "status":browser["state"],
          "available":browser["live"],
          "proof_required":not browser["live"],
          "constraint":browser["constraint"]
        })

    return {
      k:sorted(v,key=lambda x:(not x.get("available",False),x.get("kind",""),x.get("id","")))
      for k,v in sorted(graph.items())
    }

def plan(required:list[str]):
    graph=build();routes=[];pending=[];gaps=[]
    for cap in required:
        opts=graph.get(cap,[])
        live=[x for x in opts if x.get("available")]
        if live:
            routes.append({"capability":cap,"primary":live[0],"alternates":live[1:]})
        elif opts:
            pending.append({"capability":cap,"candidates":opts})
        else:gaps.append(cap)
    return {"complete":not gaps and not pending,"routes":routes,"pending_proof":pending,"gaps":gaps}

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument("capabilities",nargs="*")
    a=ap.parse_args();print(json.dumps(plan(a.capabilities),ensure_ascii=False,indent=2))
