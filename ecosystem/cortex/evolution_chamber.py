#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from typing import Any

class CortexEvolution:
    """Bounded self-improvement: prompts/routes may evolve; production weights do not self-modify.

    Candidate changes enter a chamber, run against regression cases, and can only
    be promoted if they improve score while preserving invariants.
    """
    def __init__(self,root:str="runtime/cortex-evolution"):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        self.candidates=self.root/"candidates.jsonl"
        self.promotions=self.root/"promotions.jsonl"

    def propose(self,kind:str,patch:dict[str,Any],reason:str,metrics:dict[str,Any]|None=None):
        body={
          "kind":kind,"patch":patch,"reason":reason,"metrics":metrics or {},
          "created_at":int(time.time()),"status":"PROPOSED",
          "gates":["regression","license","resource_budget","rollback","no_secret_dependency"]
        }
        body["id"]=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()[:16]
        with self.candidates.open("a",encoding="utf-8") as f:
            f.write(json.dumps(body,ensure_ascii=False)+"\n")
        return body

    def promote(self,candidate:dict[str,Any],before:float,after:float,
                invariants_ok:bool)->dict[str,Any]:
        allowed=invariants_ok and after>before
        result={
          "candidate_id":candidate["id"],
          "before":before,"after":after,
          "invariants_ok":invariants_ok,
          "status":"PROMOTED" if allowed else "REJECTED",
          "timestamp":int(time.time())
        }
        with self.promotions.open("a",encoding="utf-8") as f:
            f.write(json.dumps(result,ensure_ascii=False)+"\n")
        return result
