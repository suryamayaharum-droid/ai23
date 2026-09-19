#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time,traceback
from pathlib import Path
from typing import Any,Callable
from durable_journal import DurableJournal

class CircuitBreaker:
    def __init__(self, failures:int=3, cooldown:int=900):
        self.failures=failures; self.cooldown=cooldown
        self.state:dict[str,dict[str,Any]]={}

    def allow(self,key:str)->bool:
        s=self.state.get(key)
        if not s: return True
        if s["count"]<self.failures: return True
        if int(time.time())-s["last"]>=self.cooldown:
            self.state[key]={"count":0,"last":0}; return True
        return False

    def fail(self,key:str)->None:
        s=self.state.setdefault(key,{"count":0,"last":0})
        s["count"]+=1; s["last"]=int(time.time())

    def success(self,key:str)->None:
        self.state[key]={"count":0,"last":0}

class ResilientExecutor:
    def __init__(self,journal:DurableJournal|None=None):
        self.journal=journal or DurableJournal()
        self.breaker=CircuitBreaker()
        self.done_file=self.journal.root/"completed.json"
        self.done=json.loads(self.done_file.read_text()) if self.done_file.exists() else {}

    def _key(self,name:str,payload:dict[str,Any])->str:
        raw=json.dumps({"name":name,"payload":payload},sort_keys=True,separators=(",",":"))
        return hashlib.sha256(raw.encode()).hexdigest()

    def run(self,name:str,payload:dict[str,Any],fn:Callable[[dict[str,Any]],Any],
            *,resource:str="local",retries:int=2)->dict[str,Any]:
        key=self._key(name,payload)
        if key in self.done:
            return {"status":"CACHED","key":key,"output":self.done[key]}
        if not self.breaker.allow(resource):
            self.journal.append("executor.circuit_open",{"task":name,"resource":resource})
            return {"status":"WAITING_RESOURCE","key":key,"resource":resource}

        self.journal.append("executor.started",{"task":name,"key":key,"resource":resource})
        last_error=None
        for attempt in range(1,retries+2):
            try:
                output=fn(payload)
                self.done[key]=output
                self.done_file.write_text(json.dumps(self.done,ensure_ascii=False,indent=2),encoding="utf-8")
                self.breaker.success(resource)
                self.journal.append("executor.completed",{"task":name,"key":key,"attempt":attempt})
                return {"status":"COMPLETED","key":key,"output":output}
            except Exception as exc:
                last_error=f"{type(exc).__name__}: {exc}"
                self.breaker.fail(resource)
                self.journal.append("executor.failed",{
                    "task":name,"key":key,"attempt":attempt,"error":last_error
                })
                if attempt<=retries:
                    time.sleep(min(2**(attempt-1),8))
        return {"status":"FAILED","key":key,"error":last_error}
