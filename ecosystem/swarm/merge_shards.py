#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time,hashlib
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="runtime/shards")
    ap.add_argument("--output",default="runtime/fabric-latest.json")
    args=ap.parse_args()
    root=Path(args.input)
    reports=[]
    for p in sorted(root.rglob("*.json")):
        try:
            reports.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    merged={
        "schema":"harum.resource.fabric.v2",
        "timestamp":int(time.time()),
        "shards":reports,
        "task_count":sum(len(r.get("tasks",[])) for r in reports)
    }
    raw=json.dumps(merged,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    merged["digest"]=hashlib.sha256(raw.encode()).hexdigest()
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(merged,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(merged,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
