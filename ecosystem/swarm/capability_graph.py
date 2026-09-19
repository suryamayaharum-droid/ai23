#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict, deque

HERE=Path(__file__).resolve().parent

def build():
    agents=json.loads((HERE/"config"/"agents.json").read_text(encoding="utf-8"))
    resources=json.loads((HERE/"config"/"resource_profiles.json").read_text(encoding="utf-8"))
    providers=defaultdict(list)
    for d in agents["districts"]:
        for a in d["agents"]:
            for c in a["capabilities"]:
                providers[c].append({"kind":"agent","id":a["id"],"district":d["id"],"priority":a["priority"]})
    for r in resources["resources"]:
        for c in r.get("capabilities",[]):
            providers[c].append({"kind":"resource","id":r["id"],"status":r["status"]})
    return {k:sorted(v,key=lambda x:(x["kind"],x["id"])) for k,v in sorted(providers.items())}

def plan(required:list[str])->dict:
    graph=build()
    selected=[]
    gaps=[]
    for c in required:
        opts=graph.get(c,[])
        if not opts:
            gaps.append(c); continue
        selected.append({"capability":c,"primary":opts[0],"alternates":opts[1:]})
    return {"complete":not gaps,"routes":selected,"gaps":gaps}

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("capabilities",nargs="*")
    args=ap.parse_args()
    print(json.dumps(plan(args.capabilities),ensure_ascii=False,indent=2))
