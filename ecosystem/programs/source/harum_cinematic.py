#!/usr/bin/env python3
"""
HARUM CINEMATIC GRID
Compila microvídeos e imagens em cenas verticais maiores usando FFmpeg.

- Sem assinatura.
- Não gera identidade nova: preserva os frames/vídeos que você aprovar.
- Aceita stills e vídeos.
- Cria movimentos de câmera em stills.
- Normaliza tudo para 9:16 / CFR.
- Faz cortes ou dips curtos para preto.
- Adiciona ambiente procedural e/ou voz/música.
- Executa QC com ffprobe.
"""

from __future__ import annotations
import argparse, json, shutil, subprocess, sys
from pathlib import Path

def sh(cmd, quiet=False):
    p = subprocess.run(cmd, stdout=subprocess.PIPE if quiet else None,
                       stderr=subprocess.PIPE if quiet else None, text=True)
    if p.returncode:
        if quiet:
            print(p.stderr[-6000:], file=sys.stderr)
        raise SystemExit(p.returncode)
    return p

def require(bin_name):
    if shutil.which(bin_name) is None:
        raise SystemExit(f"{bin_name} não encontrado no PATH")

def probe(path):
    p = sh(["ffprobe","-v","error","-show_entries",
            "format=duration,size:stream=codec_name,width,height,r_frame_rate",
            "-of","json",str(path)], quiet=True)
    return json.loads(p.stdout)

def motion_expr(preset, frames, z0=1.0, z1=1.06):
    step=(z1-z0)/max(frames,1)
    z=f"min(max(zoom,{z0})+{step:.9f},{z1})"
    xy={
      "push": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
      "pull": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
      "drift_left": ("iw/2-(iw/zoom/2)-45", "ih/2-(ih/zoom/2)"),
      "drift_right": ("iw/2-(iw/zoom/2)+45", "ih/2-(ih/zoom/2)"),
      "drift_up": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)-80"),
      "drift_down": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)+80"),
      "macro_bottom": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)+140"),
      "macro_top": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)-140"),
      "static": ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)")
    }.get(preset, ("iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"))
    if preset == "pull":
        step=(z0-z1)/max(frames,1)
        z=f"max(min(zoom,{z0})-{step:.9f},{z1})"
    if preset == "static":
        z="1.0"
    return z, xy[0], xy[1]

def make_image_shot(src, out, shot, cfg):
    fps=cfg["fps"]; w=cfg["width"]; h=cfg["height"]
    dur=float(shot["duration"]); frames=max(1,int(round(dur*fps)))
    motion=shot.get("motion","push")
    z0=float(shot.get("zoom_start",1.0))
    z1=float(shot.get("zoom_end",1.06))
    z,x,y=motion_expr(motion,frames,z0,z1)
    fade=float(shot.get("fade",0.18))
    grade=cfg.get("grade",{})
    contrast=grade.get("contrast",1.04)
    brightness=grade.get("brightness",-0.02)
    saturation=grade.get("saturation",0.82)
    vf=(
      f"scale={w+140}:{h+220}:force_original_aspect_ratio=increase,"
      f"crop={w+140}:{h+220},"
      f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps},"
      f"eq=contrast={contrast}:brightness={brightness}:saturation={saturation},"
      f"vignette=PI/5,"
      f"fade=t=in:st=0:d={fade},fade=t=out:st={max(0,dur-fade):.3f}:d={fade},"
      "format=yuv420p"
    )
    sh(["ffmpeg","-y","-loop","1","-i",str(src),"-vf",vf,"-t",str(dur),
        "-r",str(fps),"-c:v","libx264","-preset",cfg.get("preset","medium"),
        "-crf",str(cfg.get("crf",19)),"-an",str(out)], quiet=True)

def make_video_shot(src, out, shot, cfg):
    fps=cfg["fps"]; w=cfg["width"]; h=cfg["height"]
    start=float(shot.get("start",0))
    dur=float(shot.get("duration",4))
    fade=float(shot.get("fade",0.16))
    grade=cfg.get("grade",{})
    vf=(
      f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
      f"fps={fps},"
      f"eq=contrast={grade.get('contrast',1.04)}:"
      f"brightness={grade.get('brightness',-0.02)}:"
      f"saturation={grade.get('saturation',0.82)},"
      f"fade=t=in:st=0:d={fade},fade=t=out:st={max(0,dur-fade):.3f}:d={fade},"
      "format=yuv420p"
    )
    sh(["ffmpeg","-y","-ss",str(start),"-i",str(src),"-t",str(dur),"-vf",vf,
        "-r",str(fps),"-c:v","libx264","-preset",cfg.get("preset","medium"),
        "-crf",str(cfg.get("crf",19)),"-an",str(out)], quiet=True)

def add_master_audio(visual, output, duration, audio):
    voice=audio.get("voice")
    music=audio.get("music")
    room=audio.get("room_tone",True)
    inputs=["-i",str(visual)]
    filters=[]
    mix_labels=[]
    idx=1

    if voice:
        inputs += ["-i",voice]
        filters.append(f"[{idx}:a]volume={audio.get('voice_volume',1.0)}[voice]")
        mix_labels.append("[voice]"); idx+=1
    if music:
        inputs += ["-i",music]
        filters.append(f"[{idx}:a]volume={audio.get('music_volume',0.12)}[music]")
        mix_labels.append("[music]"); idx+=1

    if room:
        filters.append(
          f"anoisesrc=color=pink:amplitude={audio.get('room_level',0.02)}:"
          f"duration={duration}:sample_rate=48000,"
          f"lowpass=f=3800,afade=t=in:st=0:d=1.0,"
          f"afade=t=out:st={max(0,duration-1.0):.3f}:d=1.0[room]"
        )
        mix_labels.append("[room]")

    if not mix_labels:
        shutil.copy2(visual,output); return

    if len(mix_labels)==1:
        filters.append(f"{mix_labels[0]}anull[aout]")
    else:
        filters.append("".join(mix_labels)+f"amix=inputs={len(mix_labels)}:"
                       "normalize=0:dropout_transition=0[aout]")
    sh(["ffmpeg","-y",*inputs,"-filter_complex",";".join(filters),
        "-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","160k",
        "-shortest",str(output)], quiet=True)

def render(project_path):
    require("ffmpeg"); require("ffprobe")
    p=Path(project_path).resolve()
    project=json.loads(p.read_text(encoding="utf-8"))
    work=(p.parent/project.get("workdir",".harum_render")).resolve()
    work.mkdir(parents=True,exist_ok=True)
    cfg=project.get("output",{})
    cfg.setdefault("width",1080); cfg.setdefault("height",1920)
    cfg.setdefault("fps",30); cfg.setdefault("crf",19); cfg.setdefault("preset","medium")
    cfg.setdefault("grade",{"contrast":1.04,"brightness":-0.02,"saturation":0.82})

    prepared=[]
    total=0.0
    for i,shot in enumerate(project["shots"],1):
        src=(p.parent/shot["src"]).resolve()
        if not src.exists(): raise SystemExit(f"Arquivo ausente: {src}")
        out=work/f"{i:03d}_{shot.get('id','shot')}.mp4"
        if shot.get("type","image")=="image":
            make_image_shot(src,out,shot,cfg)
        else:
            make_video_shot(src,out,shot,cfg)
        prepared.append(out); total+=float(shot["duration"])

    concat=work/"concat.txt"
    concat.write_text("".join(f"file '{x.as_posix()}'\n" for x in prepared),encoding="utf-8")
    visual=work/"visual_master.mp4"
    sh(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),
        "-c","copy",str(visual)], quiet=True)

    output=(p.parent/project.get("render","HARUM_SCENE.mp4")).resolve()
    add_master_audio(visual,output,total,project.get("audio",{}))
    q=probe(output)
    qc={
      "project":project.get("project"),
      "render":str(output),
      "expected":{"width":cfg["width"],"height":cfg["height"],"fps":cfg["fps"]},
      "probe":q
    }
    (work/"qc.json").write_text(json.dumps(qc,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(qc,ensure_ascii=False,indent=2))
    return output

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("project",help="JSON do projeto")
    args=ap.parse_args()
    render(args.project)