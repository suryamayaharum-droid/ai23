#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,urllib.request
from pathlib import Path
from harum_lessons import search,put

HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/"DECISION_SCHEMA.json").read_text())
ALLOWED={"verify_hash","verify_signature","read_memory","append_memory","request_research","request_human_review"}

def validate(obj):
    if not isinstance(obj,dict) or set(obj)!={"actions","risks","confidence"}: raise ValueError("top_level_shape")
    acts=obj["actions"]
    if not isinstance(acts,list) or not 1<=len(acts)<=3: raise ValueError("actions")
    for a in acts:
        if not isinstance(a,dict) or set(a)!={"tool","reason"}: raise ValueError("action_shape")
        if a["tool"] not in ALLOWED or not isinstance(a["reason"],str) or len(a["reason"])>120: raise ValueError("action")
    if not isinstance(obj["risks"],list) or len(obj["risks"])>3: raise ValueError("risks")
    if not all(isinstance(x,str) and len(x)<=120 for x in obj["risks"]): raise ValueError("risk_item")
    c=obj["confidence"]
    if not isinstance(c,(int,float)) or not 0<=c<=1: raise ValueError("confidence")
    return True

def ask(base_url,task,lessons=None,max_tokens=512):
    examples=""
    for x in lessons or []:
        examples+="\nVALIDATED EXAMPLE:\nTASK: "+x["task"]+"\nPROPOSAL: "+json.dumps(x["decision"],ensure_ascii=False)+"\n"
    system=("You are a small local Harum advisory planning brain. Output only valid JSON matching the supplied grammar. "
            "Choose only allowlisted tools. A hash proves content integrity, not authorship. "
            "A digital signature verifies authorship/authenticity. If irreversible human approval is required, "
            "choose request_human_review. You do not decide execution authority."+examples)
    payload={"model":"local","messages":[{"role":"system","content":system},{"role":"user","content":task}],
             "temperature":0,"max_tokens":max_tokens,"reasoning_effort":"none",
             "chat_template_kwargs":{"enable_thinking":False},"json_schema":SCHEMA}
    req=urllib.request.Request(base_url.rstrip("/")+"/v1/chat/completions",
      data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    started=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as r:data=json.loads(r.read())
    msg=data["choices"][0]["message"]
    raw=(msg.get("content") or msg.get("reasoning_content") or "").strip()
    try:
        proposal=json.loads(raw);validate(proposal)
    except Exception as e:
        raise ValueError(f"{e}; raw={raw[:500]!r}") from e
    return {"proposal":proposal,"elapsed_seconds":round(time.perf_counter()-started,3)}

def judge(proposal,expected_tool=None,high_risk=False):
    try: validate(proposal)
    except Exception as e:return {"passed":False,"score":0.0,"reason":"invalid_schema:"+str(e)}
    tools={a["tool"] for a in proposal["actions"]}
    if expected_tool and expected_tool not in tools:return {"passed":False,"score":0.4,"reason":"expected_tool_missing","tools":sorted(tools)}
    if high_risk and "request_human_review" not in tools:return {"passed":False,"score":0.5,"reason":"high_risk_without_human_review","tools":sorted(tools)}
    return {"passed":True,"score":1.0,"reason":"deterministic_gates_passed","tools":sorted(tools)}

def route(task,fast_url,deep_url,expected_tool=None,high_risk=False,force_deep=False):
    lessons=search(task,3);fast=None;fast_error=None
    try:
        fast=ask(fast_url,task,lessons);fj=judge(fast["proposal"],expected_tool,high_risk)
    except Exception as e:
        fj={"passed":False,"score":0.0,"reason":"fast_exception"};fast_error=repr(e)
    if not force_deep and fj["passed"]:
        put(task,fast["proposal"],expected_tool,"fast",fj["score"])
        return {"selected":"fast","escalated":False,"proposal":fast["proposal"],"fast":fast,"fast_judge":fj,"lessons_used":len(lessons)}
    deep=ask(deep_url,task,lessons);dj=judge(deep["proposal"],expected_tool,high_risk)
    if dj["passed"]:
        put(task,deep["proposal"],expected_tool,"deep",dj["score"])
        return {"selected":"deep","escalated":True,"proposal":deep["proposal"],"fast":fast,"fast_judge":fj,"fast_error":fast_error,
                "deep":deep,"deep_judge":dj,"lessons_used":len(lessons)}
    return {"selected":"none","escalated":True,"proposal":None,"fast":fast,"fast_judge":fj,"fast_error":fast_error,
            "deep":deep,"deep_judge":dj,"lessons_used":len(lessons)}

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("task");ap.add_argument("--fast-url",default="http://127.0.0.1:8080")
    ap.add_argument("--deep-url",default="http://127.0.0.1:8081");ap.add_argument("--expected-tool")
    ap.add_argument("--high-risk",action="store_true");ap.add_argument("--force-deep",action="store_true")
    a=ap.parse_args();print(json.dumps(route(a.task,a.fast_url,a.deep_url,a.expected_tool,a.high_risk,a.force_deep),ensure_ascii=False,indent=2))
