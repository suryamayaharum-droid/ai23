#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/"DECISION_SCHEMA.json").read_text())
ALLOWED={"verify_hash","verify_signature","read_memory","append_memory","request_research","request_human_review"}

def deterministic_decision(obj):
    confidence=float(obj["confidence"])
    tools=[a["tool"] for a in obj["actions"]]
    if confidence < 0.20:
        return "reject"
    if confidence < 0.55 or any(t in {"request_research","request_human_review"} for t in tools):
        return "revise"
    return "accept"

def call(base_url,mission,max_tokens=512):
    payload={
      "model":"local",
      "messages":[
        {"role":"system","content":"You are a small local advisory planning brain. Output only valid JSON matching the supplied grammar. Choose only allowlisted tools. Keep reasons short. You do not decide execution authority."},
        {"role":"user","content":mission}
      ],
      "temperature":0,
      "max_tokens":max_tokens,
      "reasoning_effort":"none",
      "chat_template_kwargs":{"enable_thinking":False},
      "json_schema":SCHEMA
    }
    req=urllib.request.Request(base_url.rstrip("/")+"/v1/chat/completions",
        data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    started=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as r:
        data=json.loads(r.read())
    msg=data["choices"][0]["message"]
    raw=(msg.get("content") or "").strip()
    if not raw:
        raw=(msg.get("reasoning_content") or "").strip()
    try:
        obj=json.loads(raw)
        validate(obj)
    except Exception as e:
        raise ValueError(f"{e}; raw={raw[:500]!r}") from e
    return {
      "decision":deterministic_decision(obj),
      "proposal":obj,
      "structured_valid":True,
      "fallback":False,
      "elapsed_seconds":round(time.perf_counter()-started,3)
    }

def validate(obj):
    if not isinstance(obj,dict) or set(obj)!={"actions","risks","confidence"}:
        raise ValueError("bad top-level shape")
    acts=obj["actions"]
    if not isinstance(acts,list) or not (1<=len(acts)<=3):
        raise ValueError("bad actions")
    for a in acts:
        if not isinstance(a,dict) or set(a)!={"tool","reason"}:
            raise ValueError("bad action shape")
        if a["tool"] not in ALLOWED or not isinstance(a["reason"],str) or len(a["reason"])>120:
            raise ValueError("bad action")
    risks=obj["risks"]
    if not isinstance(risks,list) or len(risks)>3 or not all(isinstance(x,str) and len(x)<=120 for x in risks):
        raise ValueError("bad risks")
    c=obj["confidence"]
    if not isinstance(c,(int,float)) or not (0<=c<=1):
        raise ValueError("bad confidence")
    return True

def reliable_call(base_url,mission):
    errors=[]
    for attempt,max_tokens in enumerate((512,768),1):
        try:
            out=call(base_url,mission,max_tokens)
            out["attempt"]=attempt
            return out
        except Exception as e:
            errors.append(type(e).__name__+":"+str(e)[:700])
    fallback={
      "actions":[{"tool":"request_human_review","reason":"Local structured model output unavailable"}],
      "risks":["structured_generation_failed"],
      "confidence":0.0
    }
    return {
      "decision":"reject",
      "proposal":fallback,
      "structured_valid":False,
      "fallback":True,
      "attempt":2,
      "errors":errors
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("mission")
    ap.add_argument("--base-url",default="http://127.0.0.1:8080")
    a=ap.parse_args()
    print(json.dumps(reliable_call(a.base_url,a.mission),ensure_ascii=False,indent=2))
