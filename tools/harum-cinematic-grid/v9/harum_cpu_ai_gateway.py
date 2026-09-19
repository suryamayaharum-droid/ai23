#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, json, shutil, subprocess, urllib.request
from pathlib import Path

def health(url):
    try:
        with urllib.request.urlopen(url,timeout=1.5) as r:
            return {"online":True,"status":r.status}
    except Exception as e:
        return {"online":False,"error":type(e).__name__}

def post_json(url,payload,timeout=3600):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.loads(r.read())

def ovms_image(prompt,out,base="http://127.0.0.1:8000/v3",model="OpenVINO/stable-diffusion-v1-5-int8-ov",steps=20):
    data=post_json(base+"/images/generations",{"model":model,"prompt":prompt,"num_inference_steps":steps,"size":"512x512"})
    Path(out).write_bytes(base64.b64decode(data["data"][0]["b64_json"])); return out

def ovms_tts(text,out,base="http://127.0.0.1:8000/v3",model="Kokoro-82M-int8-ov",voice="af_alloy"):
    req=urllib.request.Request(base+"/audio/speech",data=json.dumps({"model":model,"voice":voice,"input":text}).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=3600) as r:Path(out).write_bytes(r.read())
    return out

def llama_chat(text,base="http://127.0.0.1:8080/v1"):
    return post_json(base+"/chat/completions",{"model":"local","messages":[{"role":"user","content":text}],"temperature":0.2})

def espeak(text,out):
    exe=shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe: raise RuntimeError("eSpeak not installed")
    subprocess.run([exe,"-v","pt-br","-s","145","-w",out,text],check=True); return out

def status():
    return {
      "ovms":health("http://127.0.0.1:8000/v3/models"),
      "llama_cpp":health("http://127.0.0.1:8080/health"),
      "espeak":bool(shutil.which("espeak-ng") or shutil.which("espeak")),
      "whisper_cpp":bool(shutil.which("whisper-cli"))
    }

def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("status")
    i=sp.add_parser("image"); i.add_argument("prompt"); i.add_argument("--out",default="cpu_image.png")
    t=sp.add_parser("tts"); t.add_argument("text"); t.add_argument("--out",default="cpu_voice.wav"); t.add_argument("--fallback-espeak",action="store_true")
    l=sp.add_parser("chat"); l.add_argument("text")
    a=ap.parse_args()
    if a.cmd=="status":res=status()
    elif a.cmd=="image":res={"output":ovms_image(a.prompt,a.out)}
    elif a.cmd=="tts":
        try:res={"output":ovms_tts(a.text,a.out),"engine":"OpenVINO/Kokoro"}
        except Exception:
            if not a.fallback_espeak:raise
            res={"output":espeak(a.text,a.out),"engine":"eSpeak fallback"}
    else:res=llama_chat(a.text)
    print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
