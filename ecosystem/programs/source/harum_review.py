#!/usr/bin/env python3
"""Create review frames/contact sheet for human or VLM QC."""
from __future__ import annotations
import argparse, subprocess, shutil
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out",default="review.jpg"); ap.add_argument("--frames",type=int,default=9)
    a=ap.parse_args()
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None: raise SystemExit("ffmpeg/ffprobe required")
    d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",a.video],text=True).strip())
    fps=a.frames/max(d,0.1); cols=3; rows=(a.frames+cols-1)//cols
    subprocess.run(["ffmpeg","-y","-i",a.video,"-vf",f"fps={fps:.8f},scale=320:-1,tile={cols}x{rows}:padding=6:margin=6","-frames:v","1",a.out],check=True)
    print(a.out)
if __name__=="__main__": main()