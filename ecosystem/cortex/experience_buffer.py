#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path

def make_example(task:str,answer:str,verdict:str,source:str="cortex"):
    if verdict not in {"accepted","rejected"}:
        raise ValueError("verdict")
    return {
      "id":hashlib.sha256((task+"\n"+answer).encode()).hexdigest(),
      "instruction":task,
      "response":answer,
      "verdict":verdict,
      "source":source
    }

def append_verified(path:str,example:dict):
    if example["verdict"]!="accepted":
        return False
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f:
        f.write(json.dumps(example,ensure_ascii=False)+"\n")
    return True
