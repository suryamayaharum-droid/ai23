#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

SWARM=Path(__file__).resolve().parent
ROOT=SWARM.parents[1]
CORTEX=ROOT/"ecosystem"/"cortex"
RUNTIME=ROOT/"ecosystem"/"runtime"

def load(path:Path,default=None):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception:return default

def status()->dict[str,Any]:
    models=load(CORTEX/"config"/"models.json",{"brains":[]})
    frontier=load(CORTEX/"config"/"frontier_models_v2.json",{"tracks":[]})
    skills=load(CORTEX/"config"/"skills.json",{"skills":[]})
    smoke=load(RUNTIME/"cortex-local-smoke-latest.json")
    council=load(RUNTIME/"cortex-council-latest.json")
    dream=load(RUNTIME/"cortex-dream-latest.json")
    knowledge=load(RUNTIME/"harum-knowledge.manifest.json")

    proven=bool(smoke and smoke.get("proof_token_present") and
                smoke.get("external_inference_api_used") is False)

    return {
      "schema":"harum.cortex.status.v1",
      "installed":True,
      "local_inference_proven":proven,
      "state":"ACTIVE" if proven else "STAGED",
      "core_brains":[b["id"] for b in models.get("brains",[])],
      "frontier_brains":[b["id"] for b in frontier.get("tracks",[])],
      "skills":[s["id"] for s in skills.get("skills",[])],
      "council":council,
      "smoke":smoke,
      "dream":dream,
      "knowledge":knowledge,
      "gateway":{
        "provider":"harum-cortex",
        "base_url":"http://127.0.0.1:8899/v1",
        "usable":proven
      },
      "fallback":"deterministic_swarm_runtime"
    }

def route(requested:list[str])->dict[str,Any]:
    s=status()
    cognitive={"local_reasoning","planner","critic","scout","synthesis","consensus","tool_agent"}
    wants=bool(cognitive & set(requested))
    if not wants:
        return {"route":"not-cognitive","status":s}
    if s["local_inference_proven"]:
        return {"route":"harum-cortex","provider":s["gateway"],"status":s}
    return {
      "route":"deterministic-fallback",
      "reason":"local quantized inference has not yet produced a persisted proof",
      "status":s
    }

if __name__=="__main__":
    print(json.dumps(status(),ensure_ascii=False,indent=2))
