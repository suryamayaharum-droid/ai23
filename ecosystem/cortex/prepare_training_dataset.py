#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path

def verified_examples(paths:list[str]):
    seen=set()
    for path in paths:
        p=Path(path)
        if not p.exists(): continue
        for line in p.read_text(encoding="utf-8",errors="ignore").splitlines():
            if not line.strip(): continue
            try:r=json.loads(line)
            except Exception:continue
            if r.get("verdict")!="accepted":continue
            ins=r.get("instruction","").strip()
            resp=r.get("response","").strip()
            if not ins or not resp:continue
            key=hashlib.sha256((ins+"\n"+resp).encode()).hexdigest()
            if key in seen:continue
            seen.add(key)
            yield {"instruction":ins,"output":resp,"id":key}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",action="append",default=["runtime/cortex-experience.jsonl"])
    ap.add_argument("--output",default="runtime/cortex-training.jsonl")
    args=ap.parse_args()
    examples=list(verified_examples(args.input))
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in examples)+("\n" if examples else ""),encoding="utf-8")
    print(json.dumps({"examples":len(examples),"output":str(out)},indent=2))
