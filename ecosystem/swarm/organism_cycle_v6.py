#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from organism_cycle_v5 import run as run_v5
from digital_twin_v3 import build_twin
from browser_bridge import status as browser_status
from capability_graph_v3 import plan as capability_plan

def run(db:str,output:str):
    result=run_v5(db,output)
    twin=build_twin()
    browser=browser_status()
    result["schema"]="harum.organism.cycle.v6"
    result["timestamp_v6"]=int(time.time())
    result["digital_twin_v3"]={
      "digest":twin["digest"],
      "capability_count":twin["capability_count_v3"],
      "browser_fabric_state":browser["state"]
    }
    result["browser_fabric"]=browser
    result["edge_capability_plan"]=capability_plan([
      "browser_compute","wasm_python","semantic_wasm","webgpu_llm","crdt_sync"
    ])
    Path("runtime").mkdir(parents=True,exist_ok=True)
    Path("runtime/digital-twin-v3.json").write_text(json.dumps(twin,ensure_ascii=False,indent=2),encoding="utf-8")
    Path("runtime/browser-fabric-status.json").write_text(json.dumps(browser,ensure_ascii=False,indent=2),encoding="utf-8")
    Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_organism.db")
    ap.add_argument("--output",default="runtime/organism-v6.json")
    a=ap.parse_args()
    print(json.dumps(run(a.db,a.output),ensure_ascii=False,indent=2))
