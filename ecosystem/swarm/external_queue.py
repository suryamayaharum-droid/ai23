#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,time
from pathlib import Path
from typing import Any

FORBIDDEN=re.compile(r"(password|token|cookie|api[_-]?key|secret)",re.I)

def sanitize(obj:Any,path:str="$")->Any:
    if isinstance(obj,dict):
        out={}
        for k,v in obj.items():
            if FORBIDDEN.search(str(k)):
                raise ValueError(f"secret-like field blocked at {path}.{k}")
            out[k]=sanitize(v,f"{path}.{k}")
        return out
    if isinstance(obj,list):
        return [sanitize(v,f"{path}[]") for v in obj]
    return obj

def idem(adapter:str,capability:str,intent:str,payload:dict)->str:
    raw=json.dumps([adapter,capability,intent,payload],sort_keys=True,separators=(",",":"))
    return hashlib.sha256(raw.encode()).hexdigest()

class ExternalQueue:
    def __init__(self,path:str="ecosystem/runtime/external-queue.json"):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if self.path.exists():
            self.data=json.loads(self.path.read_text(encoding="utf-8"))
        else:
            self.data={"version":"1.0","items":[]}

    def add(self,adapter:str,capability:str,intent:str,payload:dict)->dict:
        payload=sanitize(payload)
        key=idem(adapter,capability,intent,payload)
        for item in self.data["items"]:
            if item["idempotency_key"]==key and item["status"] in {"PENDING","CLAIMED","DONE"}:
                return item
        item={
            "id":key[:16],
            "adapter":adapter,
            "capability":capability,
            "intent":intent,
            "payload":payload,
            "idempotency_key":key,
            "created_at":int(time.time()),
            "status":"PENDING",
            "attempts":0,
            "result":None
        }
        self.data["items"].append(item)
        self.save()
        return item

    def save(self):
        self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")

    def pending(self):
        return [i for i in self.data["items"] if i["status"]=="PENDING"]

if __name__=="__main__":
    q=ExternalQueue()
    print(json.dumps({"pending":q.pending()},ensure_ascii=False,indent=2))
