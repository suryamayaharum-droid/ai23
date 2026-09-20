#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/"DECISION_SCHEMA.json").read_text())

def call(base_url,mission,max_tokens=512):
    payload={"model":"local","messages":[
      {"role":"system","content":"You are a small local planning brain. Output only the requested schema. Choose only allowlisted tools. Keep reasons short."},
      {"role":"user","content":mission}],
      "temperature":0,"max_tokens":max_tokens,
      "response_format":{"type":"json_schema","schema":SCHEMA}}
    req=urllib.request.Request(base_url.rstrip("/")+"/v1/chat/completions",
        data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    started=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as r:data=json.loads(r.read())
    msg=data["choices"][0]["message"]
    raw=(msg.get("content") or msg.get("reasoning_content") or "").strip()
    obj=json.loads(raw); validate(obj)
    return {"decision":obj,"elapsed_seconds":round(time.perf_counter()-started,3)}

def validate(obj):
    if obj.get("decision") not in {"accept","revise","reject"}: raise ValueError("bad decision")
    acts=obj.get("actions"); allowed={"verify_hash","verify_signature","read_memory","append_memory","request_research","request_human_review"}
    if not isinstance(acts,list) or not (1<=len(acts)<=3): raise ValueError("bad actions")
    for a in acts:
        if set(a)!={"tool","reason"} or a["tool"] not in allowed or not isinstance(a["reason"],str): raise ValueError("bad action")
    risks=obj.get("risks")
    if not isinstance(risks,list) or len(risks)>3 or not all(isinstance(x,str) for x in risks): raise ValueError("bad risks")
    c=obj.get("confidence")
    if not isinstance(c,(int,float)) or not (0<=c<=1): raise ValueError("bad confidence")
    return True

def reliable_call(base_url,mission):
    errors=[]
    for attempt,max_tokens in enumerate((512,768),1):
        try:
            out=call(base_url,mission,max_tokens);out["attempt"]=attempt;return out
        except Exception as e: errors.append(type(e).__name__+":"+str(e)[:240])
    raise RuntimeError("structured brain failed after retries: "+" | ".join(errors))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("mission");ap.add_argument("--base-url",default="http://127.0.0.1:8080")
    a=ap.parse_args();print(json.dumps(reliable_call(a.base_url,a.mission),ensure_ascii=False,indent=2))
