#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,urllib.request

def chat(base_url,role,task,max_tokens=180,temperature=0.1):
    url=base_url.rstrip("/")+"/v1/chat/completions"
    system={
      "router":"You are a local routing brain. Choose the smallest local-first path. Be terse.",
      "planner":"You are a local planning brain. Return an executable dependency-aware plan. Be terse.",
      "critic":"You are a local critic. Find unsupported assumptions, hidden costs and missing tests. Be terse.",
      "coder":"You are a coding brain. Prefer minimal dependency-light changes with tests. Be terse.",
      "synthesizer":"You are a council synthesizer. Merge only supported ideas and preserve hard gates. Be terse."
    }.get(role,"You are a local Harum brain. Be terse and resource-honest.")
    payload={"model":"local","messages":[{"role":"system","content":system},{"role":"user","content":task}],"temperature":temperature,"max_tokens":max_tokens}
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    started=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as r:
        data=json.loads(r.read())
    text=data["choices"][0]["message"]["content"]
    return {"role":role,"text":text,"elapsed_seconds":round(time.perf_counter()-started,3)}

def council(base_url,task,roles=None):
    roles=roles or ["router","planner","critic"]
    proposals=[chat(base_url,r,task) for r in roles]
    packed="\n\n".join(f"## {x['role']}\n{x['text']}" for x in proposals)
    synth=chat(base_url,"synthesizer",f"MISSION:\n{task}\n\nPROPOSALS:\n{packed}\n\nReturn one compact executable decision.")
    return {"task":task,"proposals":proposals,"final":synth}

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("ask");a.add_argument("task");a.add_argument("--base-url",default="http://127.0.0.1:8080");a.add_argument("--role",default="planner")
    c=sp.add_parser("council");c.add_argument("task");c.add_argument("--base-url",default="http://127.0.0.1:8080")
    x=ap.parse_args()
    res=chat(x.base_url,x.role,x.task) if x.cmd=="ask" else council(x.base_url,x.task)
    print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
