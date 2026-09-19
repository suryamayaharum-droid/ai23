#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,urllib.request
from pathlib import Path

SERVER="http://127.0.0.1:8080/v1/chat/completions"
PROMPTS={
"router":"Route locally first. Prefer offline zero-paid auditable tools.",
"planner":"Build a dependency-aware executable DAG and state resource assumptions.",
"critic":"Challenge unsupported claims, hidden paid dependencies, license/security regressions and missing tests.",
"coder":"Propose minimal robust code and deterministic tests.",
"researcher":"Separate verified facts, assumptions and unknowns.",
"sentinel":"Independently challenge consensus and brittle assumptions.",
"synthesizer":"Merge only supported proposals into the smallest executable plan and preserve hard gates."
}
def call(role,task,url=SERVER):
    payload={"model":"local","messages":[{"role":"system","content":PROMPTS[role]},{"role":"user","content":task}],"temperature":0.15 if role in {"critic","sentinel"} else 0.25,"max_tokens":500}
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=300) as r:return json.loads(r.read())["choices"][0]["message"]["content"]
def council(task):
    proposals={}
    for role in ["router","planner","coder","researcher","critic","sentinel"]:
        try: proposals[role]=call(role,task)
        except Exception as e: proposals[role]={"error":type(e).__name__,"detail":str(e)[:200]}
    packed="\n\n".join(f"### {k}\n{v}" for k,v in proposals.items())
    final=call("synthesizer",f"Original task: {task}\nCouncil:\n{packed}")
    return {"task":task,"proposals":proposals,"final":final,"ts":time.time()}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("task");a=ap.parse_args()
    print(json.dumps(council(a.task),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
