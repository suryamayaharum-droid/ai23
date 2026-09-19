#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,platform,socket,time
from pathlib import Path
from typing import Any

def make_manifest(*,endpoint:str,models:list[str],capabilities:list[str],
                  ram_gb:float,health:str="online",load:float=0.0,
                  verified_local_inference:bool=False,
                  eval_score:float|None=None,
                  latency_ms:float|None=None)->dict[str,Any]:
    body={
      "schema":"harum.brain-node.v1",
      "node_id":"brain:"+socket.gethostname(),
      "host_arch":platform.machine(),
      "endpoint":endpoint,
      "models":sorted(models),
      "capabilities":sorted(set(capabilities)),
      "ram_gb":round(float(ram_gb),2),
      "health":health,
      "load":max(0.0,float(load)),
      "verified_local_inference":bool(verified_local_inference),
      "eval_score":eval_score,
      "latency_ms":latency_ms,
      "last_heartbeat":int(time.time())
    }
    raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    body["digest"]=hashlib.sha256(raw.encode()).hexdigest()
    return body

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--endpoint",default="http://127.0.0.1:8899/v1")
    ap.add_argument("--ram",type=float,default=8)
    ap.add_argument("--verified",action="store_true")
    ap.add_argument("--output",default="runtime/brain-node.json")
    args=ap.parse_args()
    m=make_manifest(
      endpoint=args.endpoint,
      models=["harum-cortex:auto","harum-cortex:council"],
      capabilities=["local_reasoning","planner","critic","tool_agent"],
      ram_gb=args.ram,
      verified_local_inference=args.verified
    )
    p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(m,ensure_ascii=False,indent=2))
