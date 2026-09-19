#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any
from policy_engine import evaluate

SAFE_REFLEXES={
  "dead_letters":"inspect_dead_letters",
  "external_bottleneck":"aggregate_external_queue",
  "queue_pressure":"increase_bounded_shards",
  "stale_cells":"mark_stale_and_request_heartbeat"
}

def reflexes(cycle:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    signals=cycle.get("pulse",{}).get("health",{}).get("signals",[])
    for s in signals:
        kind=s.get("type")
        action=SAFE_REFLEXES.get(kind)
        if not action:
            continue
        candidate={
          "action":action,
          "signal":s,
          "external_write":False,
          "publish_public":False,
          "commerce_claim":False,
          "bypass_quota":False
        }
        policy=evaluate(candidate)
        out.append({
          "reflex":action,
          "signal":s,
          "policy":policy,
          "status":"READY" if policy["allowed"] else "BLOCKED",
          "created_at":int(time.time())
        })
    return out

if __name__=="__main__":
    p=Path("runtime/organism-v3.json")
    cycle=json.loads(p.read_text()) if p.exists() else {}
    result={"reflexes":reflexes(cycle)}
    out=Path("runtime/reflexes.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
