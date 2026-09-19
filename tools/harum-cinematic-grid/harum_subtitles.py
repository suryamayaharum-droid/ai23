#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, shutil
from pathlib import Path

def tc(sec):
    ms=int(round(sec*1000)); h=ms//3600000; ms%=3600000
    m=ms//60000; ms%=60000; s=ms//1000; ms%=1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def write_srt(lines,out):
    chunks=[]
    for i,x in enumerate(lines,1):
        chunks.append(f"{i}\n{tc(float(x['start']))} --> {tc(float(x['end']))}\n{x['text'].strip()}\n")
    Path(out).write_text("\n".join(chunks),encoding="utf-8")

def burn(video,srt,out):
    if shutil.which("ffmpeg") is None: raise SystemExit("ffmpeg not found")
    style="FontName=DejaVu Serif,FontSize=17,PrimaryColour=&H00F4F0E8,OutlineColour=&H80000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=115,Alignment=2"
    sub=str(Path(srt).resolve()).replace("\\","/").replace(":","\\:")
    subprocess.run(["ffmpeg","-y","-i",video,"-vf",f"subtitles='{sub}':force_style='{style}'",
                    "-c:v","libx264","-crf","18","-preset","medium","-c:a","copy",out],check=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("timeline_json")
    ap.add_argument("--srt",default="captions.srt"); ap.add_argument("--video"); ap.add_argument("--burn-output")
    a=ap.parse_args(); data=json.loads(Path(a.timeline_json).read_text(encoding="utf-8"))
    write_srt(data["captions"],a.srt)
    if a.video and a.burn_output: burn(a.video,a.srt,a.burn_output)
    print(a.srt)
if __name__=="__main__": main()
