#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
DEFAULT_AGENTS=HERE/"config"/"agents.json"

def load_agents(path=DEFAULT_AGENTS):
    data=json.loads(Path(path).read_text(encoding="utf-8"))
    out=[]
    for district in data["districts"]:
        for a in district["agents"]:
            out.append({
                "id":a["id"],
                "district":district["id"],
                "role":a["role"],
                "priority":int(a["priority"]),
                "capabilities":set(a["capabilities"])
            })
    return out

def best_team(required, agents=None):
    agents=agents or load_agents()
    uncovered=set(required)
    team=[]
    used=set()
    while uncovered:
        ranked=[]
        for a in agents:
            if a["id"] in used:
                continue
            cover=uncovered & a["capabilities"]
            if cover:
                ranked.append((len(cover),a["priority"],-len(a["capabilities"]),a))
        if not ranked:
            break
        ranked.sort(key=lambda x:(-x[0],-x[1],x[2],x[3]["id"]))
        chosen=ranked[0][3]
        cover=uncovered & chosen["capabilities"]
        team.append({
            "agent":chosen["id"],
            "district":chosen["district"],
            "role":chosen["role"],
            "covers":sorted(cover)
        })
        used.add(chosen["id"])
        uncovered-=cover
    return {"team":team,"gaps":sorted(uncovered),"complete":not uncovered}

def synergy_map(agents=None):
    agents=agents or load_agents()
    links=[]
    for i,a in enumerate(agents):
        for b in agents[i+1:]:
            shared=a["capabilities"] & b["capabilities"]
            complementary=(a["capabilities"] | b["capabilities"])
            if shared or len(complementary)>=6:
                links.append({
                    "a":a["id"],"b":b["id"],
                    "shared":sorted(shared),
                    "combined_capabilities":len(complementary)
                })
    links.sort(key=lambda x:(-x["combined_capabilities"],x["a"],x["b"]))
    return links

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--requires",nargs="*",default=["story","canon","scene_graph","truth","publish_gate"])
    ap.add_argument("--synergy",action="store_true")
    args=ap.parse_args()
    if args.synergy:
        print(json.dumps(synergy_map(),ensure_ascii=False,indent=2))
    else:
        print(json.dumps(best_team(args.requires),ensure_ascii=False,indent=2))
