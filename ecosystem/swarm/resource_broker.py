#!/usr/bin/env python3
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

@dataclass
class Resource:
    id:str
    type:str
    status:str
    capabilities:set[str]
    persistent:Any
    raw:dict[str,Any]

def load_resources(path:Path|None=None)->list[Resource]:
    data=json.loads((path or HERE/"config"/"resource_profiles.json").read_text(encoding="utf-8"))
    return [
        Resource(
            id=r["id"],type=r["type"],status=r["status"],
            capabilities=set(r.get("capabilities",[])),
            persistent=r.get("persistent",False),raw=r
        ) for r in data["resources"]
    ]

def choose(required:list[str], *, require_persistent:bool=False,
           allow_candidate:bool=False)->dict[str,Any]:
    req=set(required)
    ranked=[]
    for r in load_resources():
        if r.status=="candidate_not_configured" and not allow_candidate:
            continue
        if r.status not in {"active","active_when_session_runs","available_not_bound","candidate_not_configured"}:
            continue
        if require_persistent and not r.persistent:
            continue
        cover=req & r.capabilities
        if not cover:
            continue
        missing=req-r.capabilities
        status_penalty={
            "active":0,
            "active_when_session_runs":1,
            "available_not_bound":2,
            "candidate_not_configured":3
        }.get(r.status,9)
        ranked.append((len(missing),status_penalty,-len(cover),r.id,r,missing))
    if not ranked:
        return {"complete":False,"resource":None,"missing":sorted(req)}
    ranked.sort(key=lambda x:(x[0],x[1],x[2],x[3]))
    _,_,_,_,r,missing=ranked[0]
    return {
        "complete":not missing,
        "resource":r.id,
        "type":r.type,
        "status":r.status,
        "covered":sorted(req-missing),
        "missing":sorted(missing),
        "constraints":r.raw.get("constraints",[])
    }

def compose(required:list[str], *, max_resources:int=4)->dict[str,Any]:
    uncovered=set(required)
    pool=load_resources()
    picked=[]
    while uncovered and len(picked)<max_resources:
        candidates=[]
        for r in pool:
            if r.id in {p["resource"] for p in picked}:
                continue
            if r.status not in {"active","active_when_session_runs","available_not_bound"}:
                continue
            cover=uncovered & r.capabilities
            if cover:
                penalty={"active":0,"active_when_session_runs":1,"available_not_bound":2}.get(r.status,9)
                candidates.append((len(cover),-penalty,r.id,r,cover))
        if not candidates: break
        candidates.sort(key=lambda x:(-x[0],-x[1],x[2]))
        _,_,_,r,cover=candidates[0]
        picked.append({"resource":r.id,"covers":sorted(cover),"status":r.status})
        uncovered-=cover
    return {"complete":not uncovered,"fabric":picked,"gaps":sorted(uncovered)}

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("capabilities",nargs="+")
    ap.add_argument("--compose",action="store_true")
    args=ap.parse_args()
    result=compose(args.capabilities) if args.compose else choose(args.capabilities)
    print(json.dumps(result,ensure_ascii=False,indent=2))
