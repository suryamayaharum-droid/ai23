#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="runtime/cortex-benchmarks")
    ap.add_argument("--output",default="runtime/cortex-council-latest.json")
    args=ap.parse_args()
    reports=[]
    for p in Path(args.input).rglob("*.json"):
        try:
            r=json.loads(p.read_text(encoding="utf-8"))
            if "brain" in r and "score" in r:
                reports.append(r)
        except Exception:
            pass
    reports.sort(key=lambda r:(-float(r.get("score",0)),float(r.get("mean_seconds",999999)),r["brain"]))
    result={
      "schema":"harum.cortex.council.benchmark.v1",
      "timestamp":int(time.time()),
      "members":reports,
      "ranking":[r["brain"] for r in reports],
      "preferred_general_brain":reports[0]["brain"] if reports else None,
      "promotion_ready":bool(reports) and float(reports[0].get("score",0))>=0.75,
      "rule":"advisory only; source routing changes still require regression-safe promotion"
    }
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
