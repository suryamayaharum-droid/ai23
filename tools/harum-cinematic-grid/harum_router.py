#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess

def detect_vram_gb():
    if shutil.which("nvidia-smi") is None: return 0.0
    try:
        out=subprocess.check_output(
            ["nvidia-smi","--query-gpu=memory.total","--format=csv,noheader,nounits"],
            text=True,stderr=subprocess.DEVNULL)
        vals=[float(x.strip())/1024 for x in out.splitlines() if x.strip()]
        return max(vals) if vals else 0.0
    except Exception:
        return 0.0

def route(task,vram,global_publish=True):
    if task in {"edit","compile","grade","audio","subtitles","still_motion"}:
        return {"engine":"FFmpeg CPU","license_gate":"green",
                "reason":"deterministic zero-GPU post-production; preserves approved identity"}
    if task=="depth_parallax":
        return {"engine":"Video Depth Anything Small + harum_parallax.py" if vram>=6 else "harum_parallax.py + supplied depth",
                "license_gate":"green",
                "reason":"Apache-2.0 small depth model plus deterministic pixel motion; no face redraw"}
    if task=="segmentation":
        return {"engine":"SAM 2","license_gate":"review_checkpoint",
                "reason":"temporal masks for selective edits and compositing"}
    if task in {"portrait_motion","microexpression"}:
        if vram>=6:
            return {"engine":"LivePortrait with compliant face detector","license_gate":"yellow",
                    "reason":"excellent portrait motion, but bundled InsightFace models are non-commercial research"}
        return {"engine":"FFmpeg/Depth Parallax","license_gate":"green",
                "reason":"identity-safe fallback without facial synthesis"}
    if task=="lipsync":
        if vram>=8:
            return {"engine":"MuseTalk 1.5","license_gate":"green-with-dependency-check",
                    "reason":"audio-driven lip sync; project states commercial model use is allowed"}
        return {"engine":"Still/portrait + subtitles/voice","license_gate":"green",
                "reason":"avoid low-quality face synthesis when GPU is insufficient"}
    if task in {"i2v","atelier_motion","object_motion"}:
        if global_publish:
            if vram>=16:
                return {"engine":"Wan2.2","license_gate":"green",
                        "reason":"Apache-2.0 public-channel default; choose TI2V/I2V/Animate by shot"}
            if vram>=8:
                return {"engine":"Wan2.2 5B via low-VRAM runtime","license_gate":"green",
                        "reason":"lower-VRAM public-channel route; use WanGP/LightX2V when compatible"}
            return {"engine":"FFmpeg/Depth Parallax","license_gate":"green",
                    "reason":"free deterministic fallback until GPU is available"}
        if vram>=24:
            return {"engine":"Wan2.2 / SkyReels V3 / LTX-2.x / HunyuanVideo-1.5",
                    "license_gate":"mixed-review",
                    "reason":"private R&D may compare models; each checkpoint still needs its own license review"}
        if vram>=8:
            return {"engine":"Wan2.2 5B / WanGP / LightX2V","license_gate":"green-or-review",
                    "reason":"quantization/offload route"}
        return {"engine":"FFmpeg/Depth Parallax","license_gate":"green",
                "reason":"CPU fallback"}
    if task in {"multi_reference","character_reference","audio_guided"}:
        if vram>=24:
            return {"engine":"SkyReels V3","license_gate":"yellow",
                    "reason":"multi-reference/audio/video conditioning; Skywork Community License review required"}
        return {"engine":"split scene into smaller shots + Wan2.2","license_gate":"green",
                "reason":"reduce reference complexity and keep public-route licensing simpler"}
    if task=="native_audio_video":
        return {"engine":"LTX-2.x","license_gate":"yellow",
                "reason":"strong native audio/video generation; current community license is version/revenue dependent"}
    if task=="tts":
        return {"engine":"Chatterbox Multilingual pt-BR","license_gate":"green-code/review-model",
                "reason":"MIT code, Portuguese/pt-BR support; use only authorized voice references"}
    if task=="foley":
        if vram>=8:
            return {"engine":"MMAudio","license_gate":"green-code/review-checkpoint",
                    "reason":"video/text conditioned synchronized audio; MIT code"}
        return {"engine":"Procedural FFmpeg ambience","license_gate":"green",
                "reason":"zero-GPU deterministic sound bed"}
    if task=="transcribe":
        return {"engine":"faster-whisper / whisper.cpp","license_gate":"green",
                "reason":"local subtitle/transcription path; choose speed vs footprint"}
    if task=="scene_detect":
        return {"engine":"PySceneDetect","license_gate":"green",
                "reason":"automatic cut/transition analysis for ingest and archive footage"}
    if task=="timeline":
        return {"engine":"OpenTimelineIO","license_gate":"green",
                "reason":"editorial interchange for NLEs and adapters"}
    if task=="interpolate":
        return {"engine":"RIFE / Video2X","license_gate":"green-tooling",
                "reason":"frame interpolation after visual QC"}
    if task=="upscale":
        return {"engine":"Real-ESRGAN / Video2X","license_gate":"green-tooling",
                "reason":"post-process only after narrative QC"}
    return {"engine":"FFmpeg CPU","license_gate":"green",
            "reason":"unknown task -> deterministic safe route"}

CHOICES=[
 "edit","compile","grade","audio","subtitles","still_motion","depth_parallax","segmentation",
 "portrait_motion","microexpression","lipsync","i2v","atelier_motion","object_motion",
 "multi_reference","character_reference","audio_guided","native_audio_video","tts","foley",
 "transcribe","scene_detect","timeline","interpolate","upscale"
]

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--task",default="i2v",choices=CHOICES)
    ap.add_argument("--vram",type=float,default=None)
    ap.add_argument("--private-output",action="store_true")
    a=ap.parse_args(); vram=detect_vram_gb() if a.vram is None else a.vram
    print(json.dumps({"task":a.task,"detected_vram_gb":round(vram,2),
      "global_publish":not a.private_output,
      **route(a.task,vram,global_publish=not a.private_output)},ensure_ascii=False,indent=2))
