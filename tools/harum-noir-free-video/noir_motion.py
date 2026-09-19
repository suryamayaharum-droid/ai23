#!/usr/bin/env python3
import argparse, shutil, subprocess
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument("--image",required=True)
p.add_argument("--output",default="harum_noir_short.mp4")
p.add_argument("--audio")
p.add_argument("--duration",type=float,default=8.0)
p.add_argument("--fps",type=int,default=30)
a=p.parse_args()
if shutil.which("ffmpeg") is None:
    raise SystemExit("FFmpeg não encontrado.")
frames=max(1,int(a.duration*a.fps))
vf=("scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,"
    f"zoompan=z='min(zoom+0.00045,1.055)':x='iw/2-(iw/zoom/2)+sin(on/22)*3':"
    f"y='ih/2-(ih/zoom/2)+cos(on/29)*2':d={frames}:s=1080x1920:fps={a.fps},"
    "eq=contrast=1.035:brightness=-0.02:saturation=0.82,"
    "vignette=PI/5,noise=alls=2.2:allf=t,"
    f"fade=t=in:st=0:d=0.35,fade=t=out:st={max(0,a.duration-0.45):.2f}:d=0.45")
cmd=["ffmpeg","-y","-loop","1","-i",str(Path(a.image).resolve())]
if a.audio: cmd+=["-i",str(Path(a.audio).resolve())]
cmd+=["-vf",vf,"-t",str(a.duration),"-r",str(a.fps),"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p"]
cmd += ["-c:a","aac","-b:a","192k","-shortest"] if a.audio else ["-an"]
cmd += [str(Path(a.output).resolve())]
subprocess.run(cmd,check=True)
print(a.output)
