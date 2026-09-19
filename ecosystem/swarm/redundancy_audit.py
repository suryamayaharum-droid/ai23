#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

HERE=Path(__file__).resolve().parent

CRITICAL={
  "state":["shared_state","transactions","event_store","git_history"],
  "compute":["python","parallel_cpu"],
  "archive":["git_history","manifests"],
  "coordination":["shared_state","queue","event_store"],
  "publication_control":["publish_gate","human_review"],
  "recovery":["checkpoint","event_store","git_history"]
}

def load_capability_routes():
    routes=defaultdict(set)
    rp=json.loads((HERE/"config"/"resource_profiles.json").read_text(encoding="utf-8"))
    for r in rp["resources"]:
        if r["status"]=="candidate_not_configured":
            continue
        for cap in r.get("capabilities",[]):
            routes[cap].add(r["id"])
    agents=json.loads((HERE/"config"/"agents.json").read_text(encoding="utf-8"))
    for d in agents["districts"]:
        for a in d["agents"]:
            for cap in a["capabilities"]:
                routes[cap].add("agent:"+a["id"])
    return routes

def audit():
    routes=load_capability_routes()
    findings=[]
    for domain,caps in CRITICAL.items():
        domain_routes=set()
        cap_detail={}
        for cap in caps:
            rs=sorted(routes.get(cap,set()))
            cap_detail[cap]=rs
            domain_routes.update(rs)
        findings.append({
          "domain":domain,
          "routes":sorted(domain_routes),
          "route_count":len(domain_routes),
          "capabilities":cap_detail,
          "status":"REDUNDANT" if len(domain_routes)>=2 else "SINGLE_POINT"
        })
    score=sum(1 for f in findings if f["status"]=="REDUNDANT")/len(findings)
    return {"schema":"harum.redundancy.audit.v1","score":round(score,3),"findings":findings}

if __name__=="__main__":
    print(json.dumps(audit(),ensure_ascii=False,indent=2))
