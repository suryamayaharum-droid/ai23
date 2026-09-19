#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

DETERMINISTIC_HINTS={
  "hash","sha","inventory","count files","json","manifest","sqlite",
  "list files","find text","dedupe","validate schema"
}
HIGH_RISK_HINTS={
  "architecture","migration","production","security","license",
  "publish","commerce","database","delete","deploy","credential"
}
COMPLEX_HINTS={
  "plan","design","refactor","debug","investigate","compare","reason",
  "strategy","integrate","coordinate"
}

def _contains(text:str,terms:set[str])->bool:
    t=text.lower()
    return any(x in t for x in terms)

def route(task:str, *,
          local_proven:bool,
          confidence:float|None=None,
          disagreement:bool=False,
          tool_failed:bool=False,
          ram_gb:float=8.0)->dict[str,Any]:
    if _contains(task,DETERMINISTIC_HINTS):
        tier="T0";reason="deterministic capability detected"
    elif not local_proven:
        tier="T0";reason="local LLM inference not yet proven; deterministic fallback"
    elif disagreement or (confidence is not None and confidence<0.55) or tool_failed:
        tier="T3";reason="uncertainty/disagreement requires council"
    elif _contains(task,HIGH_RISK_HINTS):
        tier="T3";reason="high cost of error"
    elif _contains(task,COMPLEX_HINTS):
        tier="T2";reason="multi-step cognition"
    else:
        tier="T1";reason="single local brain sufficient"

    if tier=="T3" and ram_gb>=12 and _contains(task,{"large","deep","difficult","complex"}):
        tier="T4";reason="deep route available within RAM budget"

    budget=json.loads((HERE/"config"/"cognitive_budget.json").read_text(encoding="utf-8"))
    spec=next(x for x in budget["tiers"] if x["id"]==tier)
    return {"tier":tier,"reason":reason,"spec":spec}

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--proven",action="store_true")
    ap.add_argument("--ram",type=float,default=8)
    args=ap.parse_args()
    print(json.dumps(route(args.task,local_proven=args.proven,ram_gb=args.ram),ensure_ascii=False,indent=2))
