#!/usr/bin/env python3
"""
HARUM Edit Engine
Monta microvídeos com cuts ou transições xfade e cria um master de som ambiente.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

def sh(cmd, quiet=False):
    p=subprocess.run(cmd,stdout=subprocess.PIPE if quiet else None,
                     stderr=subprocess.PIPE if quiet else None,text=True)
    if p.returncode:
        if quiet: print(p.stderr[-7000:],file=sys.stderr)
        raise SystemExit(p.returncode)
    return p

def duration(path):
    p=sh(["ffprobe","-v","error","-show_entries","format=duration",
          "-of","default=nw=1:nk=1",str(path)],quiet=True)
    return float(p.stdout.strip())

def xfade(inputs, out, transition=0.16, effect="fade", fps=30, crf=18, preset="veryfast"):
    if len(inputs)<2:
        shutil.copy2(inputs[0],out); return duration(inputs[0])
    durs=[duration(x) for x in inputs]
    cmd=["ffmpeg","-y"]
    for x in inputs: cmd += ["-i",str(x)]

    filters=[]
    for i in range(len(inputs)):
        filters.append(f"[{i}:v]setpts=PTS-STARTPTS,fps={fps},format=yuv420p[v{i}]")

    current="v0"
    elapsed=durs[0]
    for i in range(1,len(inputs)):
        offset=max(0.0,elapsed-transition)
        outlabel=f"x{i}"
        filters.append(
            f"[{current}][v{i}]xfade=transition={effect}:duration={transition}:offset={offset:.6f}[{outlabel}]"
        )
        current=outlabel
        elapsed += durs[i]-transition

    cmd += ["-filter_complex",";".join(filters),"-map",f"[{current}]",
            "-c:v","libx264","-crf",str(crf),"-preset",preset,
            "-pix_fmt","yuv420p","-movflags","+faststart","-an",str(out)]
    sh(cmd,quiet=True)
    return elapsed

def ambience(video, out, dur, level=0.018):
    # Quiet room tone: pink noise + a lower brown-noise bed.
    filt=(
      f"anoisesrc=color=pink:amplitude={level}:duration={dur}:sample_rate=48000,"
      "lowpass=f=4200,highpass=f=55[a];"
      f"anoisesrc=color=brown:amplitude={level*0.35}:duration={dur}:sample_rate=48000,"
      "lowpass=f=280,highpass=f=32[b];"
      "[a][b]amix=inputs=2:normalize=0,"
      "afade=t=in:st=0:d=1.2,"
      f"afade=t=out:st={max(0,dur-1.2):.3f}:d=1.2[aout]"
    )
    sh(["ffmpeg","-y","-i",str(video),"-filter_complex",filt,
        "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","160k",
        "-shortest","-movflags","+faststart",str(out)],quiet=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("inputs",nargs="+")
    ap.add_argument("-o","--output",default="HARUM_MASTER.mp4")
    ap.add_argument("--transition",type=float,default=0.16)
    ap.add_argument("--effect",default="fade",
                    choices=["fade","dissolve","smoothleft","smoothright","fadeblack","fadewhite"])
    ap.add_argument("--fps",type=int,default=30)
    ap.add_argument("--no-ambience",action="store_true")
    a=ap.parse_args()
    inputs=[Path(x).resolve() for x in a.inputs]
    visual=Path(a.output).with_suffix(".visual.mp4").resolve()
    final=Path(a.output).resolve()
    dur=xfade(inputs,visual,a.transition,a.effect,a.fps)
    if a.no_ambience:
        visual.replace(final)
    else:
        ambience(visual,final,dur)
        visual.unlink(missing_ok=True)
    print(json.dumps({"output":str(final),"duration":dur,
                      "shots":len(inputs),"transition":a.transition,
                      "effect":a.effect},indent=2))

if __name__=="__main__":
    main()