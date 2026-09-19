#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any

class CortexState:
    def __init__(self,path:str="runtime/cortex-state.json"):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.data=json.loads(self.path.read_text()) if self.path.exists() else {
          "version":"1.0","brain_stats":{},"skill_stats":{},"events":[]
        }

    def record_brain(self,brain:str,success:bool,latency:float|None=None):
        s=self.data["brain_stats"].setdefault(brain,{"runs":0,"successes":0,"latency_sum":0.0,"latency_n":0})
        s["runs"]+=1
        if success:s["successes"]+=1
        if latency is not None:
            s["latency_sum"]+=float(latency);s["latency_n"]+=1
        self._event("brain.run",{"brain":brain,"success":success,"latency":latency})
        self.save()

    def brain_score(self,brain:str):
        s=self.data["brain_stats"].get(brain,{})
        runs=s.get("runs",0)
        return {
          "reliability":s.get("successes",0)/runs if runs else 0.0,
          "mean_latency":s.get("latency_sum",0)/s.get("latency_n",1) if s.get("latency_n",0) else None,
          "runs":runs
        }

    def _event(self,topic,payload):
        self.data["events"].append({"ts":int(time.time()),"topic":topic,"payload":payload})
        self.data["events"]=self.data["events"][-500:]

    def save(self):
        tmp=self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.path)
