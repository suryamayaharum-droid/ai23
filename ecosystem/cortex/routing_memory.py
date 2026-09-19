#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any

class RoutingMemory:
    def __init__(self,path:str="runtime/cortex-routing-memory.json"):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.data=json.loads(self.path.read_text()) if self.path.exists() else {"routes":{}}

    def record(self,task_class:str,brain:str,score:float,latency:float):
        key=f"{task_class}:{brain}"
        s=self.data["routes"].setdefault(key,{
          "task_class":task_class,"brain":brain,"n":0,"score_sum":0.0,"latency_sum":0.0
        })
        s["n"]+=1;s["score_sum"]+=float(score);s["latency_sum"]+=float(latency)
        self.save()

    def rank(self,task_class:str):
        rows=[]
        for s in self.data["routes"].values():
            if s["task_class"]!=task_class or not s["n"]:continue
            rows.append({
              "brain":s["brain"],
              "mean_score":s["score_sum"]/s["n"],
              "mean_latency":s["latency_sum"]/s["n"],
              "n":s["n"]
            })
        rows.sort(key=lambda x:(-x["mean_score"],x["mean_latency"],-x["n"]))
        return rows

    def save(self):
        tmp=self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.path)
