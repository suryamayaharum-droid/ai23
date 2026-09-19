#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path

from digital_twin import build_twin as build_v1
from capability_graph_v2 import build as capabilities_v2
from cortex_bridge import status as cortex_status

def build_twin():
    base=build_v1()
    cortex=cortex_status()
    caps=capabilities_v2()
    body={
      **base,
      "schema":"harum.digital-twin.v2",
      "timestamp_v2":int(time.time()),
      "capabilities_v2":caps,
      "capability_count_v2":len(caps),
      "cortex":cortex
    }
    body.pop("digest",None)
    raw=json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    body["digest"]=hashlib.sha256(raw.encode()).hexdigest()
    return body

if __name__=="__main__":
    twin=build_twin()
    p=Path("runtime/digital-twin-v2.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(twin,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({
      "digest":twin["digest"],
      "capability_count_v2":twin["capability_count_v2"],
      "cortex_state":twin["cortex"]["state"]
    },ensure_ascii=False,indent=2))
