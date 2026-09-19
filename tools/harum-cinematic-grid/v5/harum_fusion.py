#!/usr/bin/env python3
import argparse, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ENG={e["id"]:e for e in json.loads((HERE/"engine_catalog.json").read_text())["engines"]}
PROV={p["id"]:p for p in json.loads((HERE/"provider_catalog.json").read_text())["providers"]}

PREFERRED={
 "storyboard":["flux2_klein_4b","qwen_image_edit_2511"],
 "image_generate":["flux2_klein_4b","qwen_image_edit_2511"],
 "image_edit":["qwen_image_edit_2511","flux2_klein_4b"],
 "video_i2v":["wan22","hunyuan15","ltx2","skyreels_v3"],
 "video_t2v":["wan22","hunyuan15","ltx2"],
 "music":["ace_step_15"],
 "mask":["sam2"],
 "edit":["ffmpeg"]
}
CAP={
 "storyboard":"storyboard_frame","image_generate":"text_to_image","image_edit":"image_edit",
 "video_i2v":"image_to_video","video_t2v":"text_to_video","music":"music","mask":"segmentation","edit":"edit"
}
PROVIDER_ENGINES={
 "local_cpu":{"ffmpeg"},
 "kaggle_t4x2":{"flux2_klein_4b","qwen_image_edit_2511","wan22","lightx2v","ace_step_15","sam2"},
 "hf_zerogpu":{"flux2_klein_4b","qwen_image_edit_2511","wan22","ace_step_15","sam2"},
 "colab_free":{"flux2_klein_4b","qwen_image_edit_2511","wan22","lightx2v","ace_step_15","sam2"},
 "github_actions_public":{"ffmpeg"}
}

def route(task, public_commercial=True, allow_review=False, provider=None):
    pids=[provider] if provider else list(PROV)
    for eid in PREFERRED[task]:
        e=ENG[eid]
        if CAP[task] not in e["capabilities"]: continue
        if public_commercial and not e["auto_public_commercial"] and not allow_review: continue
        for pid in pids:
            p=PROV[pid]
            if eid not in PROVIDER_ENGINES.get(pid,set()): continue
            if p["cost_extra_usd"]!=0: continue
            vr=p["vram_per_gpu_gb"]
            if e["vram_gb"] and vr and e["vram_gb"]>vr: continue
            return {"task":task,"engine":eid,"provider":pid,"license":e["license"],"cost_extra_usd":0}
    if task in {"video_i2v","edit"}:
        return {"task":task,"engine":"ffmpeg","provider":"local_cpu","fallback":True,"cost_extra_usd":0}
    return {"task":task,"blocked":True,"reason":"No zero-cost route passes the current license/provider gates."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("task",choices=sorted(PREFERRED))
    ap.add_argument("--provider",choices=sorted(PROV))
    ap.add_argument("--private",action="store_true")
    ap.add_argument("--allow-review",action="store_true")
    a=ap.parse_args()
    print(json.dumps(route(a.task,not a.private,a.allow_review,a.provider),indent=2))
if __name__=="__main__": main()
