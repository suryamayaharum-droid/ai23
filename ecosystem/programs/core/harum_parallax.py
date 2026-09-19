#!/usr/bin/env python3
"""2.5D cinematic parallax from an approved image + depth map. No generative face redraw."""
from __future__ import annotations
import argparse, math, shutil, subprocess, tempfile
from pathlib import Path
import cv2, numpy as np

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("image"); ap.add_argument("depth")
    ap.add_argument("-o","--output",default="HARUM_PARALLAX.mp4")
    ap.add_argument("--duration",type=float,default=5.0)
    ap.add_argument("--fps",type=int,default=30)
    ap.add_argument("--strength",type=float,default=18.0,help="max pixel displacement")
    ap.add_argument("--zoom",type=float,default=1.035)
    a=ap.parse_args()
    if shutil.which("ffmpeg") is None: raise SystemExit("ffmpeg not found")
    img=cv2.imread(a.image,cv2.IMREAD_COLOR); dep=cv2.imread(a.depth,cv2.IMREAD_GRAYSCALE)
    if img is None or dep is None: raise SystemExit("image/depth unreadable")
    h,w=img.shape[:2]; dep=cv2.resize(dep,(w,h),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255.0
    # Near pixels move more; blur depth to reduce tearing around fine edges.
    dep=cv2.GaussianBlur(dep,(0,0),sigmaX=4.0)
    xx,yy=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
    n=max(1,int(a.duration*a.fps))
    tmp=Path(tempfile.mkstemp(suffix=".mp4")[1])
    writer=cv2.VideoWriter(str(tmp),cv2.VideoWriter_fourcc(*"mp4v"),a.fps,(w,h))
    if not writer.isOpened(): raise SystemExit("VideoWriter failed")
    for i in range(n):
        t=i/max(n-1,1); ease=0.5-0.5*math.cos(math.pi*t)
        dx=(ease-0.5)*2*a.strength; dy=math.sin(t*math.pi)*a.strength*0.22
        shift=(dep-0.5)
        mapx=xx - dx*shift; mapy=yy - dy*shift
        frame=cv2.remap(img,mapx,mapy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT101)
        if a.zoom!=1.0:
            z=1+(a.zoom-1)*ease; nw,nh=int(w*z),int(h*z)
            big=cv2.resize(frame,(nw,nh),interpolation=cv2.INTER_CUBIC)
            x=(nw-w)//2; y=(nh-h)//2; frame=big[y:y+h,x:x+w]
        writer.write(frame)
    writer.release()
    subprocess.run(["ffmpeg","-y","-i",str(tmp),"-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-movflags","+faststart","-an",a.output],check=True)
    tmp.unlink(missing_ok=True); print(a.output)
if __name__=="__main__": main()
