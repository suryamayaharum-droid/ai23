#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

from brain_router import registry
from llama_brain import LlamaCppBrain
from evaluate_cortex import evaluate

HERE=Path(__file__).resolve().parent

def run(brain_id:str,output:str):
    cfg=registry()
    model=next(b for b in cfg["brains"] if b["id"]==brain_id)
    suite=json.loads((HERE/"config"/"eval_suite.json").read_text(encoding="utf-8"))
    answers={}
    timings={}
    brain=LlamaCppBrain(model)
    for case in suite["cases"]:
        start=time.perf_counter()
        r=brain.infer(
          "Follow the user's requested output format exactly. Do not provide hidden reasoning.",
          case["task"],max_tokens=96,temperature=0.0,seed=123
        )
        timings[case["id"]]=round(time.perf_counter()-start,3)
        answers[case["id"]]=r["text"]
    result=evaluate(answers)
    result.update({
      "brain":brain_id,
      "repo":model["repo"],
      "quant":model["quant"],
      "timings_seconds":timings,
      "mean_seconds":round(sum(timings.values())/max(len(timings),1),3)
    })
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--brain",default="smollm3_3b_scout")
    ap.add_argument("--output",default="runtime/cortex-benchmark.json")
    args=ap.parse_args()
    print(json.dumps(run(args.brain,args.output),ensure_ascii=False,indent=2))
