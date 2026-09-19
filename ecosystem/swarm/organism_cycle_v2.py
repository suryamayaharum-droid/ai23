#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from organism_cycle import pulse as base_pulse
from durable_journal import DurableJournal
from reconciler import reconcile
from redundancy_audit import audit as redundancy_audit
from resource_broker import compose
from evolution_loop import propose

def run(db:str,output:str):
    journal=DurableJournal("runtime/journal")
    start=journal.append("organism.cycle.started",{"version":"v2"},source="cycle_v2")

    pulse=base_pulse(db,None)
    recon=reconcile(pulse)
    redundancy=redundancy_audit()
    resources=compose(["python","git_history","shared_state","checkpoint"])
    proposals=propose({"health":pulse.get("health",{})})

    result={
      "schema":"harum.organism.cycle.v2",
      "timestamp":int(time.time()),
      "cycle_event":start["id"],
      "pulse":pulse,
      "reconciliation":recon,
      "redundancy":redundancy,
      "resource_fabric":resources,
      "evolution":{"proposals":proposals}
    }
    journal.append("organism.cycle.completed",{
      "cycle_event":start["id"],
      "health":pulse.get("health",{}).get("status"),
      "redundancy_score":redundancy["score"],
      "resource_fabric_complete":resources["complete"],
      "proposal_count":len(proposals)
    },source="cycle_v2")
    journal.materialize()

    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_organism.db")
    ap.add_argument("--output",default="runtime/organism-v2.json")
    args=ap.parse_args()
    print(json.dumps(run(args.db,args.output),ensure_ascii=False,indent=2))
