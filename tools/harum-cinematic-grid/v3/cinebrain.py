#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,shutil,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
REG=HERE/"model_registry.json"
PRIORITY={
 "still_motion":["ffmpeg_motion"],
 "portrait_motion":["framepack","ffmpeg_motion"],
 "i2v":["wan22","hunyuan15","ltx2","framepack"],
 "multi_reference":["skyreelsv3","ltx2"],
 "depth":["video_depth_anything"],
 "segmentation":["sam2"],
 "tracking":["cotracker3"],
 "continuity_qc":["dinov2"],
 "quality_metric":["vmaf"]
}

def vram():
    if not shutil.which("nvidia-smi"): return 0.0
    try:
        s=subprocess.check_output(["nvidia-smi","--query-gpu=memory.total","--format=csv,noheader,nounits"],text=True)
        return max(float(x)/1024 for x in s.split())
    except Exception: return 0.0

def registry():
    return json.loads(REG.read_text())

def choose(task,gb,allow_review=False):
    by={e["id"]:e for e in registry()["engines"]}
    rejected=[]
    for eid in PRIORITY.get(task,["ffmpeg_motion"]):
        e=by[eid]
        if e["min_vram_gb"]>gb:
            rejected.append([eid,"vram"]); continue
        if e["license_gate"].startswith("review") and not allow_review:
            rejected.append([eid,"license"]); continue
        return {"engine":eid,"rejected":rejected}
    return {"engine":"ffmpeg_motion","fallback":True,"rejected":rejected}

def plan(scene_id,title,premise,duration,gb,allow_review):
    template=[("anchor","still_motion",.16),("presence","portrait_motion",.17),
              ("gesture","i2v",.20),("detail","depth",.12),
              ("transformation","i2v",.20),("residue","still_motion",.15)]
    shots=[]
    for i,(role,task,f) in enumerate(template,1):
        shots.append({"shot_id":f"{scene_id}-s{i:02d}","role":role,"task":task,
                      "duration":round(max(1.5,duration*f),2),
                      **choose(task,gb,allow_review),"status":"planned"})
    return {"scene_id":scene_id,"title":title,"premise":premise,
            "target_duration":duration,"vram_gb":gb,"shots":shots}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scene-id",required=True); ap.add_argument("--title",required=True)
    ap.add_argument("--premise",required=True); ap.add_argument("--duration",type=float,default=24)
    ap.add_argument("--vram",type=float); ap.add_argument("--allow-review",action="store_true")
    ap.add_argument("--out",default="scene.json")
    a=ap.parse_args()
    p=plan(a.scene_id,a.title,a.premise,a.duration,vram() if a.vram is None else a.vram,a.allow_review)
    Path(a.out).write_text(json.dumps(p,ensure_ascii=False,indent=2))
    print(a.out)
