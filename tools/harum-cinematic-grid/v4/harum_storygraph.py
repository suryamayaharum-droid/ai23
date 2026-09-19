#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def validate(data):
    opened={}; errors=[]
    for idx,scene in enumerate(data["scenes"]):
        sid=scene["id"]
        for loop in scene.get("opens",[]):
            if loop in opened:
                errors.append(f"{sid}: loop '{loop}' re-opened before payoff")
            opened[loop]=idx
        for loop in scene.get("pays",[]):
            if loop not in opened:
                errors.append(f"{sid}: payoff without open loop '{loop}'")
            else:
                age=idx-opened.pop(loop)
                if age>2:
                    errors.append(f"{sid}: payoff '{loop}' took {age} scenes; Noir target is 1–3 chapters")
    return {"open_remaining":opened,"errors":errors,"ok":not errors}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("story")
    a=ap.parse_args()
    data=json.loads(Path(a.story).read_text(encoding="utf-8"))
    print(json.dumps(validate(data),ensure_ascii=False,indent=2))
