#!/usr/bin/env python3
"""Stateful scene orchestrator: identifies ready/missing shots and compiles when possible."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

def exists(scene_path,p):
    if not p: return False
    q=Path(p); q=q if q.is_absolute() else scene_path.parent/q
    return q.exists()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("scene")
    ap.add_argument("--compile",action="store_true")
    ap.add_argument("--output",default="HARUM_MASTER.mp4")
    a=ap.parse_args(); scene_path=Path(a.scene).resolve()
    data=json.loads(scene_path.read_text(encoding="utf-8"))
    ready=[]; pending=[]
    for shot in data.get("shots",[]):
        out=shot.get("output")
        if exists(scene_path,out): ready.append(shot)
        else: pending.append({
          "id":shot.get("id"),"engine":shot.get("engine"),"task":shot.get("task"),
          "input":shot.get("input_asset") or shot.get("src"),
          "prompt":shot.get("prompt"),"gate":shot.get("gate")})
    state={"scene":data.get("scene") or data.get("project"),
           "ready":len(ready),"pending":pending,"total":len(data.get("shots",[]))}
    Path("render_state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(state,ensure_ascii=False,indent=2))
    if a.compile:
        if pending: raise SystemExit("cannot compile: pending shots remain")
        inputs=[]
        for s in ready:
            p=Path(s["output"]); p=p if p.is_absolute() else scene_path.parent/p; inputs.append(str(p))
        editor=Path(__file__).with_name("harum_edit.py")
        subprocess.run([sys.executable,str(editor),*inputs,"-o",a.output],check=True)

if __name__=="__main__": main()
