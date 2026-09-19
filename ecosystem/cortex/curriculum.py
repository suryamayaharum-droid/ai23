#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from typing import Any

class Curriculum:
    """Creates candidate training/eval lessons from verifiable failures.

    It never assigns truth from model preference. A lesson enters VERIFIED only
    if a deterministic verifier or an externally validated correction supplies
    the expected result.
    """
    def __init__(self,path:str="runtime/cortex-curriculum.jsonl"):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)

    def propose(self,task:str,response:str,reason:str,verifier:dict[str,Any]|None=None):
        item={
          "task":task,
          "failed_response":response,
          "reason":reason,
          "verifier":verifier,
          "status":"VERIFIED_CHALLENGE" if verifier and verifier.get("ok") is False else "CANDIDATE",
          "created_at":int(time.time())
        }
        item["id"]=hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()[:16]
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(item,ensure_ascii=False)+"\n")
        return item

    def verified(self):
        if not self.path.exists():return []
        out=[]
        for line in self.path.read_text(encoding="utf-8").splitlines():
            r=json.loads(line)
            if r.get("status")=="VERIFIED_CHALLENGE":out.append(r)
        return out
