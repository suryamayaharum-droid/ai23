#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path

from digital_twin_v2 import build_twin as build_v2
from capability_graph_v3 import build as cap_v3
from browser_bridge import status as browser_status

def build_twin():
    base=build_v2()
    browser=browser_status()
    caps=cap_v3()
    body={
      **base,
      "schema":"harum.digital-twin.v3",
      "timestamp_v3":int(time.time()),
      "capabilities_v3":caps,
      "capability_count_v3":len(caps),
      "browser_fabric":browser
    }
    body.pop("digest",None)
    raw=json.dumps(body,ensure_ascii=False,sort_keys=True,separators=(",",":"))
    body["digest"]=hashlib.sha256(raw.encode()).hexdigest()
    return body

if __name__=="__main__":
    t=build_twin()
    p=Path("runtime/digital-twin-v3.json");p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"digest":t["digest"],"browser":t["browser_fabric"]["state"]},indent=2))
