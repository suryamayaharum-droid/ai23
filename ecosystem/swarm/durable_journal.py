#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,time
from pathlib import Path
from typing import Any

def canon(x:Any)->str:
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

class DurableJournal:
    def __init__(self, root:str="runtime/journal"):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)
        self.log=self.root/"events.jsonl"
        self.snapshot=self.root/"snapshot.json"

    def append(self, topic:str, payload:dict[str,Any], *,
               source:str="organism", correlation_id:str|None=None)->dict[str,Any]:
        event={
            "ts":int(time.time()),
            "topic":topic,
            "source":source,
            "correlation_id":correlation_id,
            "payload":payload
        }
        event["id"]=hashlib.sha256(canon(event).encode()).hexdigest()
        with self.log.open("a",encoding="utf-8") as f:
            f.write(canon(event)+"\n")
            f.flush()
            os.fsync(f.fileno())
        return event

    def replay(self)->list[dict[str,Any]]:
        if not self.log.exists(): return []
        out=[]
        seen=set()
        for line in self.log.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            e=json.loads(line)
            if e["id"] in seen: continue
            seen.add(e["id"]); out.append(e)
        return out

    def materialize(self)->dict[str,Any]:
        state={"last_by_topic":{},"event_count":0}
        for e in self.replay():
            state["event_count"]+=1
            state["last_by_topic"][e["topic"]]=e
        tmp=self.snapshot.with_suffix(".tmp")
        tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.snapshot)
        return state

if __name__=="__main__":
    j=DurableJournal()
    print(json.dumps(j.materialize(),ensure_ascii=False,indent=2))
