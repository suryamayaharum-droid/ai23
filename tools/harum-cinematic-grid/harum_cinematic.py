#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

def sh(cmd, quiet=False):
    p=subprocess.run(cmd,stdout=subprocess.PIPE if quiet else None,
                     stderr=subprocess.PIPE if quiet else None,text=True)
    if p.returncode:
        if quiet: print(p.stderr[-6000:],file=sys.stderr)
        raise SystemExit(p.returncode)
    return p

def require(name):
    if shutil.which(name) is None: raise SystemExit(f"{name} not found")

def probe(path):
    p=sh(["ffprobe","-v","error","-show_entries",
          "format=duration,size:stream=codec_name,width,height,r_frame_rate",
          "-of","json",str(path)],quiet=True)
    return json.loads(p.stdout)

def motion(preset,frames,z0=1.0,z1=1.06):
    step=(z1-z0)/max(frames,1)
    z=f"min(max(zoom,{z0})+{step:.9f},{z1})"
    xy={
      "push":("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"),
      "drift_left":("iw/2-(iw/zoom/2)-45","ih/2-(ih/zoom/2)"),
      "drift_right":("iw/2-(iw/zoom/2)+45","ih/2-(ih/zoom/2)"),
      "drift_up":("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)-80"),
      "drift_down":("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)+80"),
      "macro_bottom":("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)+140"),
      "macro_top":("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)-140"),
      "static":("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)")
    }.get(preset,("iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"))
    if preset=="static": z="1.0"
    return z,*xy

def image_shot(src,out,shot,cfg):
    fps,w,h=cfg["fps"],cfg["width"],cfg["height"]
    dur=float(shot["duration"]); frames=max(1,int(round(dur*fps)))
    z,x,y=motion(shot.get("motion","push"),frames,
                 float(shot.get("zoom_start",1.0)),
                 float(shot.get("zoom_end",1.06)))
    fade=float(shot.get("fade",0.18)); g=cfg["grade"]
    vf=(f"scale={w+140}:{h+220}:force_original_aspect_ratio=increase,"
        f"crop={w+140}:{h+220},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps},"
        f"eq=contrast={g['contrast']}:brightness={g['brightness']}:saturation={g['saturation']},"
        f"vignette=PI/5,fade=t=in:st=0:d={fade},"
        f"fade=t=out:st={max(0,dur-fade):.3f}:d={fade},format=yuv420p")
    sh(["ffmpeg","-y","-loop","1","-i",str(src),"-vf",vf,"-t",str(dur),
        "-r",str(fps),"-c:v","libx264","-preset",cfg["preset"],
        "-crf",str(cfg["crf"]),"-an",str(out)],quiet=True)

def video_shot(src,out,shot,cfg):
    fps,w,h=cfg["fps"],cfg["width"],cfg["height"]
    dur=float(shot["duration"]); start=float(shot.get("start",0))
    fade=float(shot.get("fade",0.16)); g=cfg["grade"]
    vf=(f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},"
        f"eq=contrast={g['contrast']}:brightness={g['brightness']}:saturation={g['saturation']},"
        f"fade=t=in:st=0:d={fade},fade=t=out:st={max(0,dur-fade):.3f}:d={fade},format=yuv420p")
    sh(["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(dur),"-vf",vf,
        "-r",str(fps),"-c:v","libx264","-preset",cfg["preset"],
        "-crf",str(cfg["crf"]),"-an",str(out)],quiet=True)

def add_audio(visual,output,duration,audio):
    voice=audio.get("voice"); music=audio.get("music"); room=audio.get("room_tone",True)
    inputs=["-i",str(visual)]; filters=[]; labels=[]; idx=1
    if voice:
        inputs+=["-i",voice]; filters.append(f"[{idx}:a]volume={audio.get('voice_volume',1.0)}[voice]")
        labels.append("[voice]"); idx+=1
    if music:
        inputs+=["-i",music]; filters.append(f"[{idx}:a]volume={audio.get('music_volume',0.12)}[music]")
        labels.append("[music]"); idx+=1
    if room:
        filters.append(f"anoisesrc=color=pink:amplitude={audio.get('room_level',0.02)}:"
                       f"duration={duration}:sample_rate=48000,lowpass=f=3800,"
                       f"afade=t=in:st=0:d=1,afade=t=out:st={max(0,duration-1):.3f}:d=1[room]")
        labels.append("[room]")
    if not labels:
        shutil.copy2(visual,output); return
    if len(labels)==1: filters.append(f"{labels[0]}anull[aout]")
    else: filters.append("".join(labels)+f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0[aout]")
    sh(["ffmpeg","-y",*inputs,"-filter_complex",";".join(filters),
        "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","160k",
        "-shortest",str(output)],quiet=True)

def render(project_file):
    require("ffmpeg"); require("ffprobe")
    p=Path(project_file).resolve()
    project=json.loads(p.read_text(encoding="utf-8"))
    work=(p.parent/project.get("workdir",".harum_render")).resolve()
    work.mkdir(parents=True,exist_ok=True)
    cfg=project.get("output",{})
    cfg.setdefault("width",1080); cfg.setdefault("height",1920); cfg.setdefault("fps",30)
    cfg.setdefault("crf",19); cfg.setdefault("preset","medium")
    cfg.setdefault("grade",{"contrast":1.04,"brightness":-0.02,"saturation":0.82})
    prepared=[]; total=0.0
    for i,shot in enumerate(project["shots"],1):
        src=(p.parent/shot["src"]).resolve()
        if not src.exists(): raise SystemExit(f"missing asset: {src}")
        out=work/f"{i:03d}_{shot.get('id','shot')}.mp4"
        (image_shot if shot.get("type","image")=="image" else video_shot)(src,out,shot,cfg)
        prepared.append(out); total+=float(shot["duration"])
    concat=work/"concat.txt"
    concat.write_text("".join(f"file '{x.as_posix()}'\n" for x in prepared),encoding="utf-8")
    visual=work/"visual_master.mp4"
    sh(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(visual)],quiet=True)
    output=(p.parent/project.get("render","HARUM_SCENE.mp4")).resolve()
    add_audio(visual,output,total,project.get("audio",{}))
    qc={"project":project.get("project"),"render":str(output),"probe":probe(output)}
    (work/"qc.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(qc,ensure_ascii=False,indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("project")
    render(ap.parse_args().project)
