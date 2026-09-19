#!/usr/bin/env python3
from __future__ import annotations
import json, os, platform, re, shutil
from pathlib import Path

def mem_gb():
    try:
        t=Path("/proc/meminfo").read_text()
        return round(int(re.search(r"MemTotal:\s+(\d+)",t).group(1))/1024/1024,2)
    except Exception:
        return None

def cpu_flags():
    try:
        text=Path("/proc/cpuinfo").read_text().lower()
        m=re.search(r"(?:flags|features)\s*:\s*(.+)",text)
        return set(m.group(1).split()) if m else set()
    except Exception:
        return set()

def module(name):
    try:
        __import__(name); return True
    except Exception:
        return False

def profile():
    cpus=os.cpu_count() or 1; mem=mem_gb(); flags=cpu_flags()
    parallel_jobs=max(1,min(4,cpus//2 or 1))
    threads_per_job=max(1,cpus//parallel_jobs)
    return {
      "platform":platform.platform(),
      "cpu_count":cpus,"memory_gb":mem,
      "simd":{"avx2":"avx2" in flags,"avx512":any(x.startswith("avx512") for x in flags),"amx":any(x.startswith("amx") for x in flags),"neon":"asimd" in flags or "neon" in flags},
      "installed":{"ffmpeg":bool(shutil.which("ffmpeg")),"ffprobe":bool(shutil.which("ffprobe")),"blender":bool(shutil.which("blender")),
                   "llama_cpp":bool(shutil.which("llama-cli") or shutil.which("llama-server")),"whisper_cpp":bool(shutil.which("whisper-cli")),
                   "openvino":module("openvino"),"onnxruntime":module("onnxruntime"),"cv2":module("cv2"),"duckdb":module("duckdb")},
      "recommended":{
        "local_worker_processes":parallel_jobs,
        "threads_per_heavy_job":threads_per_job,
        "memory_budget_gb":round((mem or 1)*0.70,2),
        "ffmpeg_threads":cpus,
        "avoid_oversubscription":True,
        "llm_quantization":"Q4/Q5 GGUF when a local llama.cpp model is authorized and fits RAM",
        "image_cpu":"OpenVINO int8 image service on supported Intel/ARM; otherwise approved keyframes plus deterministic CPU animation",
        "video_cpu":"FFmpeg/OpenCV/Blender microshot compiler; diffusion video is optional"
      }
    }

if __name__=="__main__":
    print(json.dumps(profile(),ensure_ascii=False,indent=2))
