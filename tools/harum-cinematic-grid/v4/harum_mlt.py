#!/usr/bin/env python3
from __future__ import annotations
import argparse, shutil, subprocess
from pathlib import Path
from xml.sax.saxutils import escape

def make_xml(clips,out_xml):
    lines=['<mlt LC_NUMERIC="C" title="Harum">','  <profile width="1080" height="1920" progressive="1" frame_rate_num="30" frame_rate_den="1"/>']
    for i,c in enumerate(clips):
        lines += [f'  <producer id="p{i}">',f'    <property name="resource">{escape(str(Path(c).resolve()))}</property>','  </producer>']
    lines.append('  <playlist id="playlist0">')
    for i,_ in enumerate(clips): lines.append(f'    <entry producer="p{i}"/>')
    lines += ['  </playlist>','  <tractor id="tractor0">','    <track producer="playlist0"/>','  </tractor>','</mlt>']
    Path(out_xml).write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("clips",nargs="+"); ap.add_argument("--xml",default="harum_timeline.mlt")
    ap.add_argument("--render"); a=ap.parse_args(); make_xml(a.clips,a.xml)
    if a.render:
        if not shutil.which("melt"): raise SystemExit("melt/MLT não instalado")
        subprocess.run(["melt",a.xml,"-consumer",f"avformat:{a.render}","vcodec=libx264","acodec=aac"],check=True)
    print(a.xml)
