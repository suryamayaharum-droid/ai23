#!/usr/bin/env python3
from __future__ import annotations
import json,time
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
CONFIG=ROOT/"ecosystem"/"browser-fabric"/"config"/"resource.json"
RUNTIME=ROOT/"ecosystem"/"runtime"

def _load(path:Path,default=None):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except Exception:return default

def status()->dict[str,Any]:
    cfg=_load(CONFIG,{})
    proof=_load(RUNTIME/"browser-fabric-proof.json")
    fresh=False
    if proof:
        ts=int(proof.get("timestamp",0))
        fresh=int(time.time())-ts<=180
    live=bool(
      proof and fresh and
      proof.get("browser_open") is True and
      proof.get("basic_runtime_ok") is True
    )
    return {
      "schema":"harum.browser-fabric.status.v1",
      "installed":bool(cfg),
      "state":"ACTIVE" if live else "STAGED",
      "live":live,
      "fresh_heartbeat":fresh,
      "proof":proof,
      "capabilities":cfg.get("capabilities",[]),
      "cost_policy":cfg.get("cost_policy"),
      "constraint":"browser compute exists only while an eligible browser/runtime is active"
    }

if __name__=="__main__":
    print(json.dumps(status(),ensure_ascii=False,indent=2))
