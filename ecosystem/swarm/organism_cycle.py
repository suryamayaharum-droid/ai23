#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, time
from pathlib import Path

from capability_mesh import best_team
from harum_swarm import SwarmCity
from holographic_state import HolographicState
from holographic_state_v2 import build_organism_hologram, cell_hologram
from homeostasis import Homeostasis
from synapse_bus_v2 import SynapseBusV2

HERE=Path(__file__).resolve().parent

def mission_plans():
    data=json.loads((HERE/"config"/"missions.json").read_text(encoding="utf-8"))
    out=[]
    for m in data["missions"]:
        if m["status"] not in {"active","ready"}:
            continue
        team=best_team(m["capabilities"])
        out.append({
            "id":m["id"],
            "objective":m["objective"],
            "status":m["status"],
            "team":team["team"],
            "gaps":team["gaps"],
            "complete":team["complete"]
        })
    return out

def pulse(db_path: str, output: str|None=None) -> dict:
    city=SwarmCity(db_path)
    seeded=city.seed_agents()
    holo_state=HolographicState(city.db)
    syn=SynapseBusV2(city.db)
    syn.seed()

    hologram=build_organism_hologram()
    plans=mission_plans()

    holo_state.publish("mayor","organism.hologram",{
        "digest":hologram["organism_digest"],
        "districts":hologram["macro_city"]["district_count"],
        "swarms":hologram["macro_city"]["swarm_count"],
        "declared_agent_roles":hologram["macro_city"]["declared_agent_roles"],
        "micro_cells":hologram["micro_cells"]["count"],
        "resources":[r["id"] for r in hologram["resources"]]
    })
    holo_state.publish("dispatcher","organism.mission_plans",plans)

    routed=city.route_ready()
    health=Homeostasis(city.db).inspect()
    holo_state.publish("health_guard","organism.health",health)

    pulse_event=syn.publish(
        topic="health.pulse",
        source="health_guard",
        payload={
            "health":health["status"],
            "tasks":health["task_counts"],
            "missions":len(plans),
            "routed":routed
        },
        organism_digest=hologram["organism_digest"]
    )
    syn.publish(
        topic="organism.pulse",
        source="mayor",
        payload={
            "districts":hologram["macro_city"]["district_count"],
            "swarms":hologram["macro_city"]["swarm_count"],
            "micro_cells":hologram["micro_cells"]["count"]
        },
        organism_digest=hologram["organism_digest"],
        correlation_id=pulse_event["correlation_id"]
    )

    cells={
        a.id:cell_hologram(a.id,hologram)
        for a in city.agents()
    }
    report={
        "schema":"harum.organism.pulse.v1",
        "timestamp":int(time.time()),
        "organism_digest":hologram["organism_digest"],
        "vector_clock":holo_state.vector_clock(),
        "city":city.status(),
        "macro":{
            "districts":hologram["macro_city"]["district_count"],
            "swarms":hologram["macro_city"]["swarm_count"],
            "declared_agent_roles":hologram["macro_city"]["declared_agent_roles"]
        },
        "micro_cells":seeded,
        "resource_count":len(hologram["resources"]),
        "mission_plans":plans,
        "health":health,
        "synapses":syn.stats(),
        "pulse_event":pulse_event,
        "cell_holograms":cells
    }
    if output:
        path=Path(output)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_organism.db")
    ap.add_argument("--output",default="runtime/organism-pulse.json")
    args=ap.parse_args()
    print(json.dumps(pulse(args.db,args.output),ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
