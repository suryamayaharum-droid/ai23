#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math,re
from pathlib import Path
from typing import Any

class LocalMemory:
    """Dependency-free fallback memory.

    Uses lexical cosine TF vectors by default so memory works with zero model
    dependencies. An embedding adapter can replace score() later without
    changing callers.
    """
    def __init__(self,path:str="runtime/cortex-memory.jsonl"):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)

    def add(self,text:str,metadata:dict[str,Any]|None=None)->str:
        rid=hashlib.sha256(text.encode()).hexdigest()
        rec={"id":rid,"text":text,"metadata":metadata or {}}
        existing={r["id"] for r in self.records()}
        if rid not in existing:
            with self.path.open("a",encoding="utf-8") as f:
                f.write(json.dumps(rec,ensure_ascii=False)+"\n")
        return rid

    def records(self):
        if not self.path.exists(): return []
        return [json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()]

    def _vec(self,s:str):
        v={}
        for t in re.findall(r"[\wÀ-ÿ]+",s.lower()):
            v[t]=v.get(t,0)+1
        return v

    def score(self,a:str,b:str)->float:
        x,y=self._vec(a),self._vec(b)
        dot=sum(v*y.get(k,0) for k,v in x.items())
        nx=math.sqrt(sum(v*v for v in x.values()))
        ny=math.sqrt(sum(v*v for v in y.values()))
        return dot/(nx*ny) if nx and ny else 0.0

    def search(self,query:str,k:int=5):
        ranked=[(self.score(query,r["text"]),r) for r in self.records()]
        ranked.sort(key=lambda x:-x[0])
        return [{"score":round(s,4),**r} for s,r in ranked[:k] if s>0]
