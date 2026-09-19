#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,time
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

def norm(s:str)->str:
    return re.sub(r"\s+"," ",s.strip()).upper()

def score_case(case:dict[str,Any],text:str)->tuple[float,list[str]]:
    n=norm(text); checks=[]; ok=True
    if case.get("must_match"):
        hit=any(norm(x) in n for x in case["must_match"])
        checks.append(f"must_match={hit}"); ok &= hit
    if case.get("must_contain_any"):
        low=text.lower()
        hit=any(x.lower() in low for x in case["must_contain_any"])
        checks.append(f"contains_any={hit}"); ok &= hit
    words=re.findall(r"\b[\wÀ-ÿ-]+\b",text)
    if "min_words" in case:
        hit=len(words)>=case["min_words"]; checks.append(f"min_words={hit}"); ok &= hit
    if "max_words" in case:
        hit=len(words)<=case["max_words"]; checks.append(f"max_words={hit}"); ok &= hit
    return (float(case.get("weight",1)) if ok else 0.0),checks

def evaluate(responses:dict[str,str],suite_path:Path|None=None):
    suite=json.loads((suite_path or HERE/"config"/"eval_suite.json").read_text(encoding="utf-8"))
    total=sum(float(c.get("weight",1)) for c in suite["cases"])
    got=0.0; details=[]
    for c in suite["cases"]:
        text=responses.get(c["id"],"")
        s,checks=score_case(c,text);got+=s
        details.append({"id":c["id"],"score":s,"weight":c.get("weight",1),"checks":checks,"response":text})
    return {"score":round(got/total,4) if total else 0.0,"earned":got,"total":total,"details":details}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("responses_json")
    args=ap.parse_args()
    responses=json.loads(Path(args.responses_json).read_text(encoding="utf-8"))
    print(json.dumps(evaluate(responses),ensure_ascii=False,indent=2))
