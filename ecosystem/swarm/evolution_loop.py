#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

RULES={
 "dead_letters":{"threshold":1,"proposal":"inspect failing tasks and improve fallback or validation"},
 "waiting_external":{"threshold":5,"proposal":"add provider-independent fallback or batch external actions"},
 "queue_pressure":{"threshold":20,"proposal":"increase bounded shard parallelism only after capacity check"},
 "missing_capability":{"threshold":1,"proposal":"extend capability registry before adding a permanent agent"},
}

def proposal_id(p:dict[str,Any])->str:
    return hashlib.sha256(json.dumps(p,sort_keys=True).encode()).hexdigest()[:16]

def propose(telemetry:dict[str,Any])->list[dict[str,Any]]:
    out=[]
    signals=telemetry.get("health",{}).get("signals",[])
    for s in signals:
        kind=s.get("type")
        if kind=="dead_letters":
            rule=RULES["dead_letters"]
            out.append({"kind":kind,"reason":s,"action":rule["proposal"]})
        elif kind=="external_bottleneck":
            rule=RULES["waiting_external"]
            out.append({"kind":kind,"reason":s,"action":rule["proposal"]})
        elif kind=="queue_pressure":
            rule=RULES["queue_pressure"]
            out.append({"kind":kind,"reason":s,"action":rule["proposal"]})
    for p in out:
        p["id"]=proposal_id(p)
        p["status"]="PROPOSED"
        p["created_at"]=int(time.time())
        p["promotion_gate"]=[
            "static_validation",
            "regression_tests",
            "no_new_secret_dependency",
            "no_quota_bypass",
            "rollback_path"
        ]
    return out

def main():
    pulse=Path("runtime/organism-pulse.json")
    data=json.loads(pulse.read_text()) if pulse.exists() else {"health":{"signals":[]}}
    out={"schema":"harum.evolution.proposals.v1","proposals":propose(data)}
    target=Path("runtime/evolution-proposals.json")
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
