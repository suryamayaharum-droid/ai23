#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,hashlib
from pathlib import Path

from evolution_chamber import CortexEvolution
from local_memory import LocalMemory

def extract_signals(runtime:Path):
    signals=[]
    for name in ["organism-v3-latest.json","organism-v2-latest.json","fabric-latest.json"]:
        p=runtime/name
        if p.exists():
            try:
                data=json.loads(p.read_text(encoding="utf-8"))
                signals.append({"source":name,"data":data})
            except Exception:
                pass
    return signals

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--runtime",default="ecosystem/runtime")
    args=ap.parse_args()
    signals=extract_signals(Path(args.runtime))
    evo=CortexEvolution()
    mem=LocalMemory()
    proposals=[]
    if not signals:
        proposals.append(evo.propose(
          "observability",
          {"action":"increase_runtime_snapshot_coverage"},
          "No organism runtime snapshot was available to the dream cycle."
        ))
    else:
        digest=hashlib.sha256(json.dumps(signals,sort_keys=True).encode()).hexdigest()
        mem.add(f"organism runtime digest {digest}",{"type":"dream-signal"})
        proposals.append(evo.propose(
          "context",
          {"runtime_digest":digest,"action":"benchmark_current_brain_pack"},
          "Fresh organism telemetry is available; compare current local brains before altering routing."
        ))
    print(json.dumps({"schema":"harum.cortex.dream.v1","signals":len(signals),"proposals":proposals},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
