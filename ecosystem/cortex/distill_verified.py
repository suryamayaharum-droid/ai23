#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
from typing import Any

from quorum import quorum

def build_example(task:str,proposals:list[dict[str,Any]],synthesis:str,
                  verifier:dict[str,Any]|None=None)->dict[str,Any]:
    q=quorum(proposals)
    verified=bool(verifier and verifier.get("ok"))
    accepted=q.get("quorum") and verified
    body={
      "instruction":task,
      "response":synthesis,
      "quorum":q,
      "verifier":verifier,
      "verdict":"accepted" if accepted else "rejected",
      "source":"cortex-distillation"
    }
    body["id"]=hashlib.sha256((task+"\n"+synthesis).encode()).hexdigest()
    return body

def append(path:str,item:dict[str,Any])->bool:
    if item.get("verdict")!="accepted":return False
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f:
        f.write(json.dumps(item,ensure_ascii=False)+"\n")
    return True
