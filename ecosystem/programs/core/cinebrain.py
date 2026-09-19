#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, hashlib, os, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE/"registries"/"model_registry.json"

TASK_PRIORITY = {
    "still_motion":["ffmpeg_motion"],
    "edit":["ffmpeg_motion"],
    "compile":["ffmpeg_motion"],
    "grade":["opencolorio","ffmpeg_motion"],
    "portrait_motion":["liveportrait","ffmpeg_motion"],
    "microexpression":["liveportrait","ffmpeg_motion"],
    "lipsync":["musetalk15"],
    "i2v":["wan22","hunyuan15","ltx2","framepack"],
    "long_video":["framepack","ltx2"],
    "multi_reference":["skyreelsv3","ltx2"],
    "native_audio_video":["ltx2"],
    "depth":["video_depth_anything"],
    "segmentation":["sam2"],
    "tracking":["cotracker3"],
    "interpolate":["rife"],
    "upscale":["realesrgan"],
    "transcript":["whisperx"],
    "continuity_qc":["dinov2"],
    "quality_metric":["vmaf"],
}

def load_registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))

def detect_vram():
    if not shutil.which("nvidia-smi"): return 0.0
    try:
        out=subprocess.check_output(["nvidia-smi","--query-gpu=memory.total","--format=csv,noheader,nounits"],text=True)
        vals=[float(x.strip())/1024 for x in out.splitlines() if x.strip()]
        return max(vals) if vals else 0.0
    except Exception:
        return 0.0

def doctor():
    bins=["python","ffmpeg","ffprobe","git","nvidia-smi"]
    result={"binaries":{b:shutil.which(b) for b in bins},"vram_gb":round(detect_vram(),2)}
    optional={}
    for pkg in ["PIL","numpy","cv2","torch","opentimelineio","prefect","scenedetect"]:
        try:
            __import__(pkg); optional[pkg]=True
        except Exception: optional[pkg]=False
    result["optional_python"]=optional
    result["registry_engines"]=len(load_registry()["engines"])
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

def choose_engine(task, vram, global_publish=True, allow_review=False):
    reg=load_registry()
    by_id={e["id"]:e for e in reg["engines"]}
    candidates=TASK_PRIORITY.get(task,["ffmpeg_motion"])
    rejected=[]
    for eid in candidates:
        e=by_id[eid]
        if e["min_vram_gb"] > vram:
            rejected.append({"engine":eid,"reason":"vram"}); continue
        if global_publish and not e["approved_for_global_output"] and not allow_review:
            rejected.append({"engine":eid,"reason":"license_review"}); continue
        return {"engine":eid,"name":e["name"],"rejected":rejected}
    # Deterministic fallback if generation model is blocked.
    fb=by_id["ffmpeg_motion"]
    return {"engine":"ffmpeg_motion","name":fb["name"],"fallback":True,"rejected":rejected}

def make_scene(scene_id,title,premise,target_duration,vram,global_publish,allow_review=False):
    # NOIR LOOP translated to film beats.
    template=[
        ("anchor","still_motion",0.16),
        ("presence","portrait_motion",0.17),
        ("gesture","i2v",0.20),
        ("detail","depth",0.12),
        ("transformation","i2v",0.20),
        ("residue","still_motion",0.15),
    ]
    shots=[]
    for i,(role,task,frac) in enumerate(template,1):
        dur=max(1.5,round(target_duration*frac,2))
        r=choose_engine(task,vram,global_publish,allow_review)
        shots.append({
            "shot_id":f"{scene_id}-s{i:02d}",
            "role":role,"task":task,"duration":dur,
            "engine":r["engine"],"engine_name":r["name"],
            "status":"planned","input_assets":[],"prompt":None,
            "seed":None,"output":None,"router":r
        })
    return {
        "scene_id":scene_id,"title":title,"premise":premise,
        "target_duration":target_duration,
        "global_publish":global_publish,
        "continuity_memory":{
            "identity_source":"HARUM_NOIR_FACE_LOCK_CLEAN_v1.png",
            "hair":"chin-length black bob",
            "wardrobe":"matte black / graphite + subtle aged gold",
            "palette":["#0B0B0B","#242424","#EEE8DC","#B58A3A","#3A171B"],
            "camera_language":"restrained editorial realism; 35–50mm; negative space",
            "truth_gate":"fictional editorial voice; no fabricated real-world biography"
        },
        "shots":shots
    }

def cmd_plan(a):
    vram=detect_vram() if a.vram is None else a.vram
    scene=make_scene(a.scene_id,a.title,a.premise,a.duration,vram,not a.private_output,a.allow_review)
    out=Path(a.out)
    out.write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding="utf-8")
    print(out)

def cmd_graph(a):
    p=json.loads(Path(a.plan).read_text(encoding="utf-8"))
    lines=["flowchart LR"]
    for i,s in enumerate(p["shots"]):
        safe=s["role"].replace("-","_")
        lines.append(f'  S{i}["{s["shot_id"]}<br/>{s["role"]}<br/>{s["engine"]}"]')
        if i: lines.append(f"  S{i-1} --> S{i}")
    Path(a.out).write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(a.out)

def cmd_jobs(a):
    plan=json.loads(Path(a.plan).read_text(encoding="utf-8"))
    outdir=Path(a.outdir); outdir.mkdir(parents=True,exist_ok=True)
    provider_rules={
      "local_cpu":{"tasks":{"still_motion","edit","compile","grade","audio","subtitles","qc","depth"}},
      "local_gpu":{"tasks":{"portrait_motion","microexpression","lipsync","i2v","multi_reference","native_audio_video","depth","segmentation","tracking","interpolate","upscale"}},
      "colab_free":{"tasks":{"portrait_motion","microexpression","lipsync","i2v","depth","segmentation","tracking","interpolate","upscale"}},
      "kaggle":{"tasks":{"portrait_motion","microexpression","lipsync","i2v","depth","segmentation","tracking","interpolate","upscale"}},
      "hf_zerogpu":{"tasks":{"portrait_motion","microexpression","lipsync","i2v","depth","segmentation","tracking","interpolate","upscale"}},
    }
    buckets={k:[] for k in provider_rules}
    for shot in plan["shots"]:
        task=shot["task"]
        # CPU gets deterministic tasks. GPU job goes to selected provider if requested.
        if task in provider_rules["local_cpu"]["tasks"]:
            buckets["local_cpu"].append(shot)
        else:
            provider=a.gpu_provider
            buckets[provider].append(shot)
    index={}
    for provider,shots in buckets.items():
        if not shots: continue
        fp=outdir/f"{provider}.json"
        payload={
          "provider":provider,
          "policy":"manual/authorized runtime only; do not bypass quotas",
          "scene_id":plan["scene_id"],"shots":shots
        }
        fp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
        index[provider]=str(fp)
    (outdir/"index.json").write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(index,ensure_ascii=False,indent=2))

def main():
    ap=argparse.ArgumentParser(prog="cinebrain")
    sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("doctor")
    p=sp.add_parser("plan")
    p.add_argument("--scene-id",required=True); p.add_argument("--title",required=True)
    p.add_argument("--premise",required=True); p.add_argument("--duration",type=float,default=24)
    p.add_argument("--vram",type=float); p.add_argument("--private-output",action="store_true")
    p.add_argument("--allow-review",action="store_true",help="Allow models whose license still needs review.")
    p.add_argument("--out",default="scene.json")
    g=sp.add_parser("graph"); g.add_argument("plan"); g.add_argument("--out",default="scene.mmd")
    j=sp.add_parser("jobs"); j.add_argument("plan"); j.add_argument("--outdir",default="jobs")
    j.add_argument("--gpu-provider",choices=["local_gpu","colab_free","kaggle","hf_zerogpu"],default="kaggle")
    a=ap.parse_args()
    if a.cmd=="doctor": doctor()
    elif a.cmd=="plan": cmd_plan(a)
    elif a.cmd=="graph": cmd_graph(a)
    elif a.cmd=="jobs": cmd_jobs(a)

if __name__=="__main__":
    main()
