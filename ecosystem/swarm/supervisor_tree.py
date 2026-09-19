#!/usr/bin/env python3
from __future__ import annotations
import json,time
from dataclasses import dataclass,field
from typing import Callable,Any

@dataclass
class Child:
    name:str
    start:Callable[[],Any]
    max_restarts:int=3
    window_seconds:int=60
    restarts:list[int]=field(default_factory=list)

class Supervisor:
    def __init__(self,strategy:str="one_for_one"):
        if strategy not in {"one_for_one","one_for_all","rest_for_one"}:
            raise ValueError(strategy)
        self.strategy=strategy
        self.children:list[Child]=[]

    def add(self,child:Child):
        self.children.append(child)

    def _allowed(self,c:Child)->bool:
        now=int(time.time())
        c.restarts=[t for t in c.restarts if now-t<=c.window_seconds]
        return len(c.restarts)<c.max_restarts

    def run_child(self,index:int)->dict:
        c=self.children[index]
        if not self._allowed(c):
            return {"child":c.name,"status":"CIRCUIT_OPEN"}
        try:
            result=c.start()
            return {"child":c.name,"status":"OK","result":result}
        except Exception as exc:
            c.restarts.append(int(time.time()))
            affected=[index]
            if self.strategy=="one_for_all":
                affected=list(range(len(self.children)))
            elif self.strategy=="rest_for_one":
                affected=list(range(index,len(self.children)))
            return {
                "child":c.name,
                "status":"FAILED",
                "error":f"{type(exc).__name__}: {exc}",
                "restart_candidates":[self.children[i].name for i in affected
                                      if self._allowed(self.children[i])]
            }
