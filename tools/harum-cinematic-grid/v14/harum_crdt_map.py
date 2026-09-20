#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path

def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

class OpMap:
    def __init__(self,node,path):
        self.node=node;self.path=Path(path)
        self.data=json.loads(self.path.read_text()) if self.path.exists() else {"node":node,"clock":0,"ops":{}}
    def put(self,key,value):
        self.data["clock"]+=1
        op={"node":self.node,"clock":self.data["clock"],"key":key,"value":value,"deleted":False,"ts":time.time()}
        op["id"]=hashlib.sha256(stable(op).encode()).hexdigest();self.data["ops"][op["id"]]=op;self.save();return op
    def merge(self,other):
        o=json.loads(Path(other).read_text());self.data["ops"].update(o["ops"]);self.data["clock"]=max(self.data["clock"],o.get("clock",0));self.save()
    def state(self):
        latest={}
        for op in self.data["ops"].values():
            rank=(op["clock"],op["node"],op["id"])
            if op["key"] not in latest or rank>latest[op["key"]][0]: latest[op["key"]]=(rank,op)
        return {k:v[1]["value"] for k,v in latest.items() if not v[1]["deleted"]}
    def save(self): self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2))
