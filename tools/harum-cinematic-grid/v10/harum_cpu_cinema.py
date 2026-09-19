#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, time, os
from pathlib import Path
import cv2, numpy as np

def cover(img,w,h):
    ih,iw=img.shape[:2]; s=max(w/iw,h/ih); nw,nh=int(iw*s+0.5),int(ih*s+0.5)
    x=cv2.resize(img,(nw,nh),interpolation=cv2.INTER_LANCZOS4)
    x0=(nw-w)//2; y0=(nh-h)//2
    return x[y0:y0+h,x0:x0+w].copy()

def face_center(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    cascade=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    faces=cascade.detectMultiScale(gray,1.1,4,minSize=(50,50))
    if len(faces):
        x,y,w,h=max(faces,key=lambda z:z[2]*z[3]); return (x+w/2,y+h/2,w,h)
    H,W=img.shape[:2]; return (W/2,H*0.42,W*0.35,H*0.35)

def mask_subject(img):
    H,W=img.shape[:2]; cx,cy,fw,fh=face_center(img)
    mask=np.zeros((H,W),np.uint8)
    center=(int(cx),int(min(H-1,cy+fh*0.7)))
    axes=(int(max(fw*1.15,W*.20)),int(max(fh*2.0,H*.32)))
    cv2.ellipse(mask,center,axes,0,0,360,255,-1)
    mask=cv2.GaussianBlur(mask,(0,0),sigmaX=max(10,W*0.025),sigmaY=max(10,H*0.025))
    return mask.astype(np.float32)/255.0

def warp(img,dx,dy,scale,angle=0):
    H,W=img.shape[:2]
    M=cv2.getRotationMatrix2D((W/2,H/2),angle,scale); M[:,2]+=np.array([dx,dy])
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)

def render(image,out,duration=3.0,fps=24,w=540,h=960,preset='breath',seed=23):
    cv2.setNumThreads(max(1,(os.cpu_count() or 2)//2))
    src=cv2.imread(str(image),cv2.IMREAD_COLOR)
    if src is None: raise SystemExit('image not found')
    base=cover(src,w,h)
    m=mask_subject(base)
    hard=(m>0.55).astype(np.uint8)*255
    bg=cv2.inpaint(base,hard,5,cv2.INPAINT_TELEA)
    frames=int(duration*fps)
    writer=cv2.VideoWriter(str(out),cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h))
    if not writer.isOpened(): raise SystemExit('VideoWriter failed')
    rng=np.random.default_rng(seed)
    dust=np.zeros((h,w),np.float32)
    for _ in range(max(30,int(w*h/12000))):
        x=int(rng.integers(0,w)); y=int(rng.integers(0,h)); dust[y,x]=rng.uniform(.15,.6)
    dust=cv2.GaussianBlur(dust,(0,0),1.0)
    for i in range(frames):
        t=i/max(1,frames-1); e=.5-.5*math.cos(math.pi*t)
        if preset=='left': dx=-6*e; dy=2*math.sin(t*math.pi); z=1+.018*e
        elif preset=='right': dx=6*e; dy=-2*math.sin(t*math.pi); z=1+.018*e
        elif preset=='push': dx=0; dy=-3*e; z=1+.030*e
        elif preset=='pull': dx=0; dy=3*e; z=1.03-.025*e
        else: dx=2*math.sin(t*math.pi*2); dy=-2*e; z=1+.014*math.sin(t*math.pi)
        b=warp(bg,-dx*.50,-dy*.50,1+(z-1)*.35)
        f=warp(base,dx,dy,z)
        mm=warp((m*255).astype(np.uint8),dx,dy,z).astype(np.float32)/255.0
        mm3=mm[...,None]
        frame=(f*mm3+b*(1-mm3)).astype(np.uint8)
        sigma=1.2+1.2*abs(math.sin(math.pi*t))
        soft=cv2.GaussianBlur(frame,(0,0),sigmaX=sigma)
        focus=np.clip(mm3*1.15,0,1)
        frame=(frame*focus+soft*(1-focus)).astype(np.uint8)
        yy,xx=np.mgrid[0:h,0:w]
        light=np.exp(-((xx-w*.18)**2/(2*(w*.50)**2)+(yy-h*.28)**2/(2*(h*.45)**2)))
        gain=(1+0.045*light*(.7+.3*math.sin(t*math.pi*2)))[...,None]
        frame=np.clip(frame.astype(np.float32)*gain,0,255).astype(np.uint8)
        noise=rng.normal(0,1.25,frame.shape[:2]).astype(np.float32)[...,None]
        frame=np.clip(frame.astype(np.float32)+noise+dust[...,None]*3.0,0,255).astype(np.uint8)
        writer.write(frame)
    writer.release(); return str(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('image'); ap.add_argument('--out',default='cpu_shot.mp4'); ap.add_argument('--duration',type=float,default=3); ap.add_argument('--fps',type=int,default=24); ap.add_argument('--preset',choices=['breath','left','right','push','pull'],default='breath')
    a=ap.parse_args(); t=time.perf_counter(); p=render(Path(a.image),Path(a.out),a.duration,a.fps,preset=a.preset); print(json.dumps({'output':p,'seconds':round(time.perf_counter()-t,3)},indent=2))
if __name__=='__main__':main()
