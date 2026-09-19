#!/usr/bin/env python3
"""Mix voice/music/foley/room and normalize final program loudness with FFmpeg."""
from __future__ import annotations
import argparse, shutil, subprocess

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("-o","--output",default="HARUM_AUDIO_MASTER.mp4")
    ap.add_argument("--voice"); ap.add_argument("--music"); ap.add_argument("--foley")
    ap.add_argument("--target",type=float,default=-16.0); ap.add_argument("--true-peak",type=float,default=-1.5)
    a=ap.parse_args()
    if shutil.which("ffmpeg") is None: raise SystemExit("ffmpeg not found")
    cmd=["ffmpeg","-y","-i",a.video]; streams=[]; filters=[]; idx=1
    if a.voice:
        cmd += ["-i",a.voice]; filters.append(f"[{idx}:a]highpass=f=70,lowpass=f=15000,volume=1.0[voice]"); streams.append("[voice]"); idx+=1
    if a.music:
        cmd += ["-i",a.music]; filters.append(f"[{idx}:a]volume=0.12[music]"); streams.append("[music]"); idx+=1
    if a.foley:
        cmd += ["-i",a.foley]; filters.append(f"[{idx}:a]volume=0.45[foley]"); streams.append("[foley]"); idx+=1
    if not streams: raise SystemExit("provide --voice, --music and/or --foley")
    filters.append("".join(streams)+f"amix=inputs={len(streams)}:normalize=0:dropout_transition=0,loudnorm=I={a.target}:LRA=11:TP={a.true_peak}[master]")
    cmd += ["-filter_complex",";".join(filters),"-map","0:v","-map","[master]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-shortest","-movflags","+faststart",a.output]
    subprocess.run(cmd,check=True); print(a.output)
if __name__=="__main__": main()
