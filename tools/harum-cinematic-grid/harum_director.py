#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
from harum_router import route, detect_vram_gb

DEFAULT_PATTERN=[
    ("anchor","still_motion",2.5),
    ("presence","portrait_motion",3.0),
    ("gesture","i2v",3.5),
    ("transformation","i2v",4.0),
    ("residue","still_motion",2.5),
]

def build(title,premise,vram,global_publish):
    shots=[]
    for i,(role,task,dur) in enumerate(DEFAULT_PATTERN,1):
        r=route(task,vram,global_publish)
        shots.append({"id":f"{i:02d}-{role}","narrative_role":role,
          "task":task,"duration":dur,"engine":r["engine"],
          "router_reason":r["reason"],"status":"planned",
          "input_asset":None,"prompt":None,"output":None,
          "gate":["face","hair","palette","movement","truth"] if role!="anchor" else ["palette","truth"]})
    return {"scene":title,"premise":premise,
      "estimated_duration":sum(s["duration"] for s in shots),
      "vram_gb":vram,"global_publish":global_publish,"shots":shots}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--title",required=True)
    ap.add_argument("--premise",required=True)
    ap.add_argument("--vram",type=float,default=None)
    ap.add_argument("--private-output",action="store_true")
    ap.add_argument("--out",default="scene_plan.json")
    a=ap.parse_args()
    vram=detect_vram_gb() if a.vram is None else a.vram
    Path(a.out).write_text(json.dumps(build(a.title,a.premise,vram,not a.private_output),
      ensure_ascii=False,indent=2),encoding="utf-8")
    print(a.out)
