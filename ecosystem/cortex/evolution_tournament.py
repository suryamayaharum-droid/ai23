#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from brain_router import registry
from llama_brain import LlamaCppBrain
from evaluate_cortex import evaluate
from adaptive_policy import AdaptivePolicy

HERE=Path(__file__).resolve().parent

def run_variant(brain,variant,suite):
    answers={}; timings={}
    for case in suite["cases"]:
        start=time.perf_counter()
        out=brain.infer(
          variant["system"],case["task"],
          max_tokens=int(variant["max_tokens"]),
          temperature=float(variant["temperature"]),
          seed=123
        )
        timings[case["id"]]=time.perf_counter()-start
        answers[case["id"]]=out["text"]
    score=evaluate(answers)
    by_id={x["id"]:x for x in score["details"]}
    return {
      "policy":variant,
      "score":score["score"],
      "details":score["details"],
      "mean_seconds":sum(timings.values())/max(len(timings),1),
      "invariants":{
        "honesty":bool(by_id.get("honesty",{}).get("score")),
        "secret_guard":bool(by_id.get("secret_guard",{}).get("score"))
      }
    }

def tournament(brain_id:str,output:str,auto_promote:bool=False):
    cfg=registry()
    model=next(b for b in cfg["brains"] if b["id"]==brain_id)
    brain=LlamaCppBrain(model)
    suite=json.loads((HERE/"config"/"eval_suite.json").read_text(encoding="utf-8"))
    store=AdaptivePolicy()
    pcfg=store.registry

    results=[run_variant(brain,v,suite) for v in pcfg["variants"]]
    results.sort(key=lambda x:(-x["score"],x["mean_seconds"],x["policy"]["id"]))
    baseline=next(x for x in results if x["policy"]["id"]==pcfg["active"])
    best=results[0]
    rules=pcfg["promotion"]
    score_gain=best["score"]-baseline["score"]
    latency_ok=best["mean_seconds"] <= baseline["mean_seconds"]*float(rules["max_latency_regression_ratio"])
    invariants_ok=all(best["invariants"].values())
    promotable=(
      best["policy"]["id"]!=baseline["policy"]["id"] and
      score_gain>=float(rules["min_score_delta"]) and
      latency_ok and invariants_ok
    )
    state={
      "schema":"harum.cortex.tournament.v1",
      "brain":brain_id,
      "baseline":baseline,
      "best":best,
      "score_gain":score_gain,
      "latency_ok":latency_ok,
      "invariants_ok":invariants_ok,
      "promotable":promotable,
      "results":results
    }
    if auto_promote and promotable:
        state["promotion"]=store.promote(best["policy"],{
          "brain":brain_id,"score_gain":score_gain,
          "baseline_score":baseline["score"],"new_score":best["score"]
        })
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    return state

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--brain",default="smollm3_3b_scout")
    ap.add_argument("--output",default="runtime/cortex-tournament.json")
    ap.add_argument("--auto-promote",action="store_true")
    args=ap.parse_args()
    print(json.dumps(tournament(args.brain,args.output,args.auto_promote),ensure_ascii=False,indent=2))
