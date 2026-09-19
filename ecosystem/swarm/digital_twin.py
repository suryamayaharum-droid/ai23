#!/usr/bin/env python3
from __future__ import annotations
import json,time,hashlib
from pathlib import Path
from knowledge_graph import KnowledgeGraph, seed_from_configs
from capability_graph import build as capability_build

def build_twin()->dict:
    g=KnowledgeGraph()
    counts=seed_from_configs(g)
    graph=g.export()
    cap=capability_build()
    body={
      "schema":"harum.digital-twin.v1",
      "timestamp":int(time.time()),
      "knowledge_counts":counts,
      "capability_count":len(cap),
      "capabilities":cap,
      "knowledge_graph":graph
    }
    raw=json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    body["digest"]=hashlib.sha256(raw.encode()).hexdigest()
    return body

if __name__=="__main__":
    twin=build_twin()
    p=Path("runtime/digital-twin.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(twin,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({
      "digest":twin["digest"],
      "knowledge_counts":twin["knowledge_counts"],
      "capability_count":twin["capability_count"]
    },ensure_ascii=False,indent=2))
