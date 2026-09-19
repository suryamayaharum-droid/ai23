#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from organism_cycle_v4 import run as run_v4
from digital_twin_v2 import build_twin
from cortex_bridge import status as cortex_status
from capability_graph_v2 import plan as capability_plan

def run(db:str,output:str):
    result=run_v4(db,output)
    twin=build_twin()
    cortex=cortex_status()

    critical_plan=capability_plan([
      "coordinate","checkpoint","inventory","local_reasoning","critic"
    ])

    result["schema"]="harum.organism.cycle.v5"
    result["timestamp_v5"]=int(time.time())
    result["digital_twin_v2"]={
      "digest":twin["digest"],
      "capability_count":twin["capability_count_v2"],
      "cortex_state":cortex["state"]
    }
    result["cortex"]=cortex
    result["critical_capability_plan"]=critical_plan

    Path("runtime").mkdir(parents=True,exist_ok=True)
    Path("runtime/digital-twin-v2.json").write_text(
      json.dumps(twin,ensure_ascii=False,indent=2),encoding="utf-8")
    Path("runtime/cortex-status.json").write_text(
      json.dumps(cortex,ensure_ascii=False,indent=2),encoding="utf-8")
    Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_organism.db")
    ap.add_argument("--output",default="runtime/organism-v5.json")
    args=ap.parse_args()
    print(json.dumps(run(args.db,args.output),ensure_ascii=False,indent=2))
