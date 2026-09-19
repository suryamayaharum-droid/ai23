#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,socket,time
from pathlib import Path

from hybrid_state import HybridState

CAPABILITIES=[
  "python","hash","inventory","qc","checkpoint","json",
  "event_replay","manifest","dedupe"
]

def execute(task:dict):
    payload=task.get("payload",{})
    op=payload.get("op","noop")
    if op=="noop":
        return {"status":"OK"}
    if op=="inventory":
        p=Path(payload.get("path","."))
        files=[x for x in p.rglob("*") if x.is_file()]
        return {"status":"OK","files":len(files),"bytes":sum(x.stat().st_size for x in files)}
    return {"status":"UNSUPPORTED","op":op}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--node-id",default=None)
    ap.add_argument("--once",action="store_true")
    ap.add_argument("--sleep",type=int,default=10)
    args=ap.parse_args()

    node=args.node_id or "worker:"+socket.gethostname()
    state=HybridState()
    state.heartbeat(
      node,
      layer="portable-worker",
      district="infraestrutura",
      capabilities=CAPABILITIES,
      health="online",
      load=0,
      hologram_digest=None,
      vector_clock={node:1},
      state={"backend_mode":state.mode}
    )
    print(json.dumps({"node":node,"backend_mode":state.mode,"capabilities":CAPABILITIES}))

    if args.once:
        return

    while True:
        state.heartbeat(
          node,
          layer="portable-worker",
          district="infraestrutura",
          capabilities=CAPABILITIES,
          health="online",
          load=0,
          hologram_digest=None,
          vector_clock={},
          state={"backend_mode":state.mode}
        )
        time.sleep(max(args.sleep,5))

if __name__=="__main__":
    main()
