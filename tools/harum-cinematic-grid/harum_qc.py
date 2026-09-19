#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess, shutil
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

def require(name):
    if shutil.which(name) is None: raise SystemExit(f"{name} not found")

def probe(path):
    p=run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)])
    if p.returncode: raise SystemExit(p.stderr)
    return json.loads(p.stdout)

def detect(path,expr):
    return run(["ffmpeg","-hide_banner","-nostats","-i",str(path),"-vf",expr,"-an","-f","null","-"]).stderr

def detect_audio(path,expr):
    return run(["ffmpeg","-hide_banner","-nostats","-i",str(path),"-af",expr,"-vn","-f","null","-"]).stderr

def loudness(path):
    p=run(["ffmpeg","-hide_banner","-nostats","-i",str(path),"-af",
           "loudnorm=I=-16:LRA=11:TP=-1.5:print_format=json","-f","null","-"])
    m=re.findall(r'\{\s*"input_i".*?\}',p.stderr,flags=re.S)
    if not m: return None
    try: return json.loads(m[-1])
    except Exception: return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input"); ap.add_argument("--out")
    ap.add_argument("--target-width",type=int,default=1080)
    ap.add_argument("--target-height",type=int,default=1920)
    ap.add_argument("--target-fps",type=float,default=30)
    a=ap.parse_args(); require("ffmpeg"); require("ffprobe")
    path=Path(a.input).resolve(); meta=probe(path)
    video=next((s for s in meta.get("streams",[]) if s.get("codec_type")=="video"),None)
    audio=next((s for s in meta.get("streams",[]) if s.get("codec_type")=="audio"),None)
    if not video: raise SystemExit("no video stream")
    def fps(v):
        n,d=(v.get("avg_frame_rate") or "0/1").split("/")
        return float(n)/float(d) if float(d) else 0.0
    black=detect(path,"blackdetect=d=0.35:pix_th=0.10")
    freeze=detect(path,"freezedetect=n=-55dB:d=1.5")
    silence=detect_audio(path,"silencedetect=n=-45dB:d=1.2") if audio else ""
    report={
      "file":str(path),
      "duration":float(meta.get("format",{}).get("duration",0) or 0),
      "size_bytes":int(meta.get("format",{}).get("size",0) or 0),
      "video":{"codec":video.get("codec_name"),"width":video.get("width"),
               "height":video.get("height"),"fps":fps(video)},
      "audio":None if not audio else {"codec":audio.get("codec_name"),
               "sample_rate":audio.get("sample_rate"),"channels":audio.get("channels")},
      "detections":{
        "black_start":re.findall(r"black_start:([0-9.]+)",black),
        "freeze_start":re.findall(r"freeze_start: ([0-9.]+)",freeze),
        "silence_start":re.findall(r"silence_start: ([0-9.]+)",silence)
      },
      "loudness":loudness(path) if audio else None
    }
    report["checks"]={
      "resolution_ok":video.get("width")==a.target_width and video.get("height")==a.target_height,
      "fps_ok":abs(fps(video)-a.target_fps)<0.05,
      "codec_ok":video.get("codec_name") in {"h264","hevc","av1","vp9"},
      "has_audio":bool(audio),"nonempty":report["size_bytes"]>1024,
      "duration_ok":report["duration"]>0.25
    }
    report["pass"]=all(v for k,v in report["checks"].items() if k!="has_audio")
    out=Path(a.out) if a.out else path.with_suffix(".qc.json")
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
