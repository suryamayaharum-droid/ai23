#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,time
from pathlib import Path

from evolution_chamber import CortexEvolution
from local_memory import LocalMemory

def load_json(p:Path):
    if not p.exists():return None
    try:return json.loads(p.read_text(encoding="utf-8"))
    except Exception:return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runtime",default="ecosystem/runtime")
    ap.add_argument("--output",default="runtime/cortex-dream-v2.json")
    args=ap.parse_args()

    rt=Path(args.runtime)
    organism=load_json(rt/"organism-v3-latest.json") or load_json(rt/"organism-v2-latest.json")
    council=load_json(rt/"cortex-council-latest.json")
    smoke=load_json(rt/"cortex-local-smoke-latest.json")
    knowledge=load_json(rt/"harum-knowledge.manifest.json")
    evo=CortexEvolution()
    mem=LocalMemory()
    proposals=[]

    if not smoke or not smoke.get("proof_token_present"):
        proposals.append(evo.propose(
          "runtime_validation",
          {"action":"prove_local_quantized_inference","tier":"B"},
          "No persisted proof of local GGUF inference exists yet."
        ))

    if council:
        top=council.get("preferred_general_brain")
        members=council.get("members",[])
        if top and members:
            score=float(members[0].get("score",0))
            proposals.append(evo.propose(
              "routing",
              {"preferred_general_brain":top},
              f"Council benchmark currently ranks {top} first.",
              {"score":score}
            ))
    else:
        proposals.append(evo.propose(
          "benchmark",
          {"action":"run_distributed_cortex_council"},
          "No persisted multi-brain council benchmark exists yet."
        ))

    if organism:
        health=organism.get("pulse",organism).get("health",{})
        if health.get("status") not in {None,"healthy"}:
            proposals.append(evo.propose(
              "resilience",
              {"action":"review_organism_health","signals":health.get("signals",[])},
              "Organism telemetry reports degraded health."
            ))

    if knowledge:
        mem.add(
          f"knowledge pack {knowledge.get('index_sha256')} chunks {knowledge.get('chunks')}",
          {"type":"knowledge-manifest","files":knowledge.get("files")}
        )

    state={
      "schema":"harum.cortex.dream.v2",
      "timestamp":int(time.time()),
      "inputs":{
        "organism":bool(organism),
        "council":bool(council),
        "smoke":bool(smoke),
        "knowledge":bool(knowledge)
      },
      "proposals":proposals
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
