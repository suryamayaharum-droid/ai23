#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from resource_broker import compose

HERE=Path(__file__).resolve().parent

def desired():
    return {
      "state":"healthy",
      "minimum_resources":["python","git_history","shared_state","checkpoint"],
      "minimum_active_missions":1,
      "max_dead_letters":0,
      "max_waiting_external":10
    }

def reconcile(pulse:dict)->dict:
    d=desired()
    tasks=pulse.get("city",{}).get("tasks",{})
    actual={
      "dead_letters":pulse.get("health",{}).get("dead_letters",0),
      "waiting_external":int(tasks.get("WAITING_EXTERNAL",0)),
      "mission_count":len(pulse.get("mission_plans",[]))
    }
    resource_plan=compose(d["minimum_resources"])
    actions=[]
    if actual["dead_letters"]>d["max_dead_letters"]:
        actions.append({"action":"inspect_dead_letters","safe_auto":True})
    if actual["waiting_external"]>d["max_waiting_external"]:
        actions.append({"action":"aggregate_external_queue","safe_auto":True})
    if actual["mission_count"]<d["minimum_active_missions"]:
        actions.append({"action":"refresh_mission_board","safe_auto":True})
    if not resource_plan["complete"]:
        actions.append({"action":"record_capability_gap","gaps":resource_plan["gaps"],"safe_auto":True})
    return {
      "schema":"harum.reconcile.v1",
      "desired":d,
      "actual":actual,
      "resource_plan":resource_plan,
      "actions":actions,
      "timestamp":int(time.time())
    }

if __name__=="__main__":
    p=Path("runtime/organism-pulse.json")
    pulse=json.loads(p.read_text()) if p.exists() else {}
    out=reconcile(pulse)
    q=Path("runtime/reconcile.json");q.parent.mkdir(parents=True,exist_ok=True)
    q.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))
