#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

class AdaptivePolicy:
    def __init__(self,path:str="ecosystem/runtime/cortex-active-policy.json"):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.registry=json.loads((HERE/"config"/"prompt_policies.json").read_text(encoding="utf-8"))

    def baseline(self):
        active=self.registry["active"]
        return next(x for x in self.registry["variants"] if x["id"]==active)

    def active(self):
        if self.path.exists():
            try:return json.loads(self.path.read_text(encoding="utf-8"))["policy"]
            except Exception:pass
        return self.baseline()

    def promote(self,candidate:dict[str,Any],evidence:dict[str,Any]):
        history=[]
        if self.path.exists():
            try:history=json.loads(self.path.read_text(encoding="utf-8")).get("history",[])
            except Exception:pass
        current=self.active()
        history.append({"policy":current,"replaced_at":int(time.time())})
        keep=int(self.registry["promotion"].get("rollback_keep",5))
        state={
          "schema":"harum.cortex.active-policy.v1",
          "policy":candidate,
          "evidence":evidence,
          "promoted_at":int(time.time()),
          "history":history[-keep:]
        }
        tmp=self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.path)
        return state

    def rollback(self):
        if not self.path.exists():return None
        state=json.loads(self.path.read_text(encoding="utf-8"))
        history=state.get("history",[])
        if not history:return None
        previous=history.pop()["policy"]
        new={
          "schema":state.get("schema"),
          "policy":previous,
          "evidence":{"reason":"rollback"},
          "promoted_at":int(time.time()),
          "history":history
        }
        self.path.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding="utf-8")
        return new
