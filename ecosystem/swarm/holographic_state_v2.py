#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from holographic_state import digest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def _load(name: str) -> Any:
    return json.loads((HERE/"config"/name).read_text(encoding="utf-8"))

def resource_census(root: Path=ROOT) -> dict[str,Any]:
    skip={".git","runtime","__pycache__",".pytest_cache"}
    by_ext={}
    total_files=0
    total_bytes=0
    top=[]
    for p in root.rglob("*"):
        if not p.is_file() or any(part in skip for part in p.parts):
            continue
        try:
            size=p.stat().st_size
        except OSError:
            continue
        total_files+=1
        total_bytes+=size
        ext=(p.suffix.lower() or "<none>")
        by_ext[ext]=by_ext.get(ext,0)+1
        if len(top)<20:
            top.append((size,str(p.relative_to(root))))
        else:
            smallest=min(range(len(top)),key=lambda i:top[i][0])
            if size>top[smallest][0]:
                top[smallest]=(size,str(p.relative_to(root)))
    top=sorted(top,reverse=True)
    return {
        "files":total_files,
        "bytes":total_bytes,
        "by_extension":dict(sorted(by_ext.items())),
        "largest":[{"path":p,"bytes":s} for s,p in top]
    }

def build_organism_hologram() -> dict[str,Any]:
    micro=_load("agents.json")
    macro=_load("city_v8_airtable_snapshot.json")
    plugins=_load("plugin_fabric.json")
    missions=_load("missions.json")
    cells=[]
    for district in micro["districts"]:
        for a in district["agents"]:
            cells.append({
                "id":a["id"],
                "district":district["id"],
                "role":a["role"],
                "priority":a["priority"],
                "capabilities":sorted(a["capabilities"])
            })
    body={
        "schema":"harum.organism.hologram.v2",
        "principle":"every cell carries a digest and routable model of the whole organism",
        "macro_city":{
            "districts":macro["districts"],
            "swarms":macro["swarms"],
            "district_count":len(macro["districts"]),
            "swarm_count":len(macro["swarms"]),
            "declared_agent_roles":sum(int(s.get("agents") or 0) for s in macro["swarms"])
        },
        "micro_cells":{
            "count":len(cells),
            "cells":sorted(cells,key=lambda x:x["id"])
        },
        "missions":missions["missions"],
        "resources":plugins["resources"],
        "repository_census":resource_census(),
        "invariants":[
            "no_secrets_in_bus",
            "capabilities_must_be_declared",
            "bounded_hops_and_retries",
            "publication_requires_gates",
            "external_actions_require_authorized_connector_or_runtime",
            "preserve_provenance_and_versions"
        ]
    }
    body["organism_digest"]=digest(body)
    return body

def cell_hologram(cell_id: str, global_hologram: dict[str,Any]) -> dict[str,Any]:
    local=None
    for c in global_hologram["micro_cells"]["cells"]:
        if c["id"]==cell_id:
            local=c;break
    if local is None:
        raise KeyError(cell_id)
    return {
        "schema":"harum.cell.hologram.v1",
        "cell":local,
        "organism_digest":global_hologram["organism_digest"],
        "macro_summary":{
            "districts":global_hologram["macro_city"]["district_count"],
            "swarms":global_hologram["macro_city"]["swarm_count"],
            "declared_agent_roles":global_hologram["macro_city"]["declared_agent_roles"]
        },
        "resources":[r["id"] for r in global_hologram["resources"]],
        "active_missions":[m["id"] for m in global_hologram["missions"] if m["status"] in {"active","ready"}]
    }
