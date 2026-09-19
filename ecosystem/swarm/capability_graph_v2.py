#!/usr/bin/env python3
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

SWARM=Path(__file__).resolve().parent
ROOT=SWARM.parents[1]
CORTEX=ROOT/"ecosystem"/"cortex"

def cortex_proven()->bool:
    p=ROOT/"ecosystem"/"runtime"/"cortex-local-smoke-latest.json"
    if not p.exists():
        return False
    try:
        d=json.loads(p.read_text(encoding="utf-8"))
        return bool(d.get("proof_token_present")) and d.get("external_inference_api_used") is False
    except Exception:
        return False

def build():
    providers=defaultdict(list)

    agents=json.loads((SWARM/"config"/"agents.json").read_text(encoding="utf-8"))
    resources=json.loads((SWARM/"config"/"resource_profiles.json").read_text(encoding="utf-8"))
    overlay=json.loads((CORTEX/"config"/"resource_overlay.json").read_text(encoding="utf-8"))

    for d in agents["districts"]:
        for a in d["agents"]:
            for c in a["capabilities"]:
                providers[c].append({
                  "kind":"agent","id":a["id"],"district":d["id"],
                  "priority":a["priority"],"available":True
                })

    for r in resources["resources"]:
        for c in r.get("capabilities",[]):
            providers[c].append({
              "kind":"resource","id":r["id"],"status":r["status"],
              "available":r["status"] in {"active","active_when_session_runs","available_not_bound"}
            })

    proof=cortex_proven()
    for r in overlay["resources"]:
        for c in r.get("capabilities",[]):
            providers[c].append({
              "kind":"cortex","id":r["id"],
              "status":"active" if proof else r["status"],
              "available":proof,
              "proof_required":not proof
            })

    return {k:sorted(v,key=lambda x:(not x.get("available",False),x["kind"],x["id"]))
            for k,v in sorted(providers.items())}

def plan(required:list[str]):
    graph=build()
    routes=[];gaps=[];pending=[]
    for cap in required:
        opts=graph.get(cap,[])
        live=[x for x in opts if x.get("available")]
        if live:
            routes.append({"capability":cap,"primary":live[0],"alternates":live[1:]})
        elif opts:
            pending.append({"capability":cap,"candidates":opts})
        else:
            gaps.append(cap)
    return {
      "complete":not gaps and not pending,
      "routes":routes,
      "pending_proof":pending,
      "gaps":gaps
    }

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("capabilities",nargs="*")
    args=ap.parse_args()
    print(json.dumps(plan(args.capabilities),ensure_ascii=False,indent=2))
