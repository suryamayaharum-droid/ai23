#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, json, re, tempfile, os

def has_vmaf():
    p=subprocess.run(["ffmpeg","-hide_banner","-filters"],capture_output=True,text=True)
    return "libvmaf" in (p.stdout+p.stderr)

def run_metric(ref,test):
    if has_vmaf():
        with tempfile.NamedTemporaryFile(suffix=".json",delete=False) as tf: log=tf.name
        subprocess.run(["ffmpeg","-i",test,"-i",ref,"-lavfi",f"libvmaf=log_fmt=json:log_path={log}","-f","null","-"],capture_output=True,text=True)
        try:
            data=json.load(open(log,"r"))
            return {"metric":"VMAF","mean":data.get("pooled_metrics",{}).get("vmaf",{}).get("mean")}
        finally:
            try: os.unlink(log)
            except OSError: pass
    p=subprocess.run(["ffmpeg","-i",test,"-i",ref,"-lavfi","[0:v][1:v]ssim;[0:v][1:v]psnr","-f","null","-"],capture_output=True,text=True)
    ssim=re.findall(r"All:([0-9.]+)",p.stderr); psnr=re.findall(r"average:([0-9.]+)",p.stderr)
    return {"metric":"SSIM/PSNR","ssim":float(ssim[-1]) if ssim else None,"psnr":float(psnr[-1]) if psnr else None}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("reference"); ap.add_argument("test")
    a=ap.parse_args(); print(json.dumps(run_metric(a.reference,a.test),indent=2))
