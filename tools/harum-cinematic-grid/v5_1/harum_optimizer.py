#!/usr/bin/env python3
import argparse,json

def plan(vram,gpus,task,provider):
    layers=[]
    if task=="video_t2v":
        if vram>=8:
            model="wan22"
            layers=["DiffSynth VRAM management","VAE tiling","TeaCache if benchmarked","SageAttention/FlashAttention if compatible"]
        elif vram>=3.6:
            model="cogvideox_2b"
            layers=["Diffusers","TorchAO INT8","VAE slicing/tiling"]
        else:
            model="storyboard_only"
    elif task=="video_i2v":
        model="wan22" if vram>=8 else "ffmpeg_motion"
        if model=="wan22": layers=["DiffSynth VRAM management","VAE tiling","TeaCache if benchmarked"]
    else:
        model="ffmpeg"
    if gpus>=2 and provider=="kaggle_t4x2" and model=="wan22":
        layers+=["xFuser when supported OR independent GPU0/GPU1 microshot lanes"]
    return {"task":task,"model":model,"layers":layers,"guard":"Benchmark before defaulting an accelerator; never trade FACE LOCK for speed."}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--task",required=True); p.add_argument("--vram",type=float,required=True); p.add_argument("--gpus",type=int,default=1); p.add_argument("--provider",default="local")
    a=p.parse_args(); print(json.dumps(plan(a.vram,a.gpus,a.task,a.provider),indent=2))
