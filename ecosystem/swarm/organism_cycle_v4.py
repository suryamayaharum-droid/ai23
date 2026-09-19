#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from organism_cycle_v3 import run as run_v3
from digital_twin import build_twin
from reflex_engine import reflexes

def run(db:str,output:str):
    result=run_v3(db,output)
    twin=build_twin()
    safe_reflexes=reflexes(result)

    result["schema"]="harum.organism.cycle.v4"
    result["timestamp_v4"]=int(time.time())
    result["digital_twin"]={
      "digest":twin["digest"],
      "knowledge_counts":twin["knowledge_counts"],
      "capability_count":twin["capability_count"]
    }
    result["reflexes"]=safe_reflexes

    twin_path=Path("runtime/digital-twin.json")
    twin_path.parent.mkdir(parents=True,exist_ok=True)
    twin_path.write_text(json.dumps(twin,ensure_ascii=False,indent=2),encoding="utf-8")

    p=Path(output)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_organism.db")
    ap.add_argument("--output",default="runtime/organism-v4.json")
    args=ap.parse_args()
    print(json.dumps(run(args.db,args.output),ensure_ascii=False,indent=2))
