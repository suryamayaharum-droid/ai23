#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from capability_mesh import best_team
from harum_swarm import SwarmCity
from subagent_factory import SubagentFactory

HERE=Path(__file__).resolve().parent
MISSIONS=HERE/"config"/"missions.json"

def load_missions(path=MISSIONS):
    return json.loads(Path(path).read_text(encoding="utf-8"))["missions"]

def plan_missions():
    plans=[]
    for m in load_missions():
        if m["status"] not in {"active","ready"}:
            continue
        plan=best_team(m["capabilities"])
        plans.append({
            "mission":m["id"],
            "status":m["status"],
            "objective":m["objective"],
            "team":plan["team"],
            "gaps":plan["gaps"],
            "complete":plan["complete"]
        })
    return plans

def tick(db_path: str):
    city=SwarmCity(db_path)
    city.seed_agents()
    factory=SubagentFactory(city)
    reaped=factory.reap_expired()
    routed=city.route_ready()
    plans=plan_missions()
    return {
        "city":city.status(),
        "routed_this_tick":routed,
        "expired_subagents_reaped":reaped,
        "mission_plans":plans
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--db",default="runtime/harum_swarm.db")
    ap.add_argument("--loop",action="store_true")
    ap.add_argument("--interval",type=int,default=30)
    args=ap.parse_args()
    if not args.loop:
        print(json.dumps(tick(args.db),ensure_ascii=False,indent=2))
        return
    while True:
        print(json.dumps(tick(args.db),ensure_ascii=False))
        time.sleep(max(args.interval,5))

if __name__=="__main__":
    main()
