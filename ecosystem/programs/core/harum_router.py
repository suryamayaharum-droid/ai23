#!/usr/bin/env python3
"""
HARUM Compute + Model Router
Escolhe uma rota técnica conservadora com base em tarefa, VRAM e destino de publicação.
Não baixa pesos nem executa modelos; produz um plano auditável.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, re

def detect_vram_gb():
    if shutil.which("nvidia-smi") is None:
        return 0.0
    try:
        out=subprocess.check_output(
            ["nvidia-smi","--query-gpu=memory.total","--format=csv,noheader,nounits"],
            text=True, stderr=subprocess.DEVNULL
        )
        vals=[float(x.strip())/1024 for x in out.splitlines() if x.strip()]
        return max(vals) if vals else 0.0
    except Exception:
        return 0.0

def route(task, vram, global_publish=True):
    # Global-publishing license gate:
    # MiniMax H3 Community License currently restricts use/display outside its Applicable Territory.
    # A globally accessible YouTube/Instagram output can therefore cross excluded territories.
    h3_allowed = not global_publish

    if task in {"edit","compile","grade","audio","subtitles","still_motion"}:
        return {"engine":"FFmpeg CPU","reason":"deterministic, zero GPU, preserves approved identity"}

    if task in {"portrait_motion","microexpression"}:
        if vram >= 6:
            return {"engine":"LivePortrait","reason":"purpose-built portrait animation; identity-first"}
        return {"engine":"FFmpeg CPU","reason":"safe fallback; no face regeneration"}

    if task == "lipsync":
        if vram >= 8:
            return {"engine":"MuseTalk 1.5","reason":"audio-driven lip sync; existing video remains the base"}
        return {"engine":"FFmpeg + still/voice","reason":"avoid identity-damaging generation on insufficient GPU"}

    if task in {"i2v","atelier_motion","object_motion"}:
        if vram >= 24:
            return {"engine":"HunyuanVideo-1.5 / Wan2.2 / LTX-2","reason":"quality tier; choose by license and shot"}
        if vram >= 12:
            return {"engine":"Wan2.2 5B / HunyuanVideo-1.5 offload","reason":"balanced consumer-GPU tier"}
        if vram >= 6:
            return {"engine":"WanGP + low-VRAM model","reason":"quantization/offload route"}
        return {"engine":"FFmpeg CPU","reason":"generate motion from approved still; wait for free GPU for diffusion"}

    if task in {"multi_reference","character_reference","audio_guided"}:
        if vram >= 24:
            return {"engine":"SkyReels V3","reason":"multi-subject reference/audio/video conditioning"}
        return {"engine":"split into smaller shots","reason":"reference-heavy generation should be sent to a free high-VRAM runtime"}

    if task == "native_audio_video":
        candidates=["LTX-2"]
        if h3_allowed:
            candidates.append("MiniMax H3")
        return {
            "engine":" / ".join(candidates),
            "reason":"native synchronized audiovisual generation; H3 excluded from global-public route by license gate"
        }

    if task == "interpolate":
        return {"engine":"RIFE","reason":"frame interpolation after generation"}
    if task == "upscale":
        return {"engine":"Real-ESRGAN","reason":"post-process only after narrative/QC approval"}

    return {"engine":"FFmpeg CPU","reason":"unknown task -> deterministic safe route"}

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--task", default="i2v",
                    choices=["edit","compile","grade","audio","subtitles","still_motion",
                             "portrait_motion","microexpression","lipsync","i2v",
                             "atelier_motion","object_motion","multi_reference",
                             "character_reference","audio_guided","native_audio_video",
                             "interpolate","upscale"])
    ap.add_argument("--vram", type=float, default=None,
                    help="VRAM GB; omitted = detect with nvidia-smi")
    ap.add_argument("--private-output", action="store_true",
                    help="Output will not be globally published; relaxes only the H3 territory gate. Review license anyway.")
    a=ap.parse_args()
    vram=detect_vram_gb() if a.vram is None else a.vram
    result={
        "task":a.task,
        "detected_vram_gb":round(vram,2),
        "global_publish":not a.private_output,
        **route(a.task,vram,global_publish=not a.private_output)
    }
    print(json.dumps(result,ensure_ascii=False,indent=2))
