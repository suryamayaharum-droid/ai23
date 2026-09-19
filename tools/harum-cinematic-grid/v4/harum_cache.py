#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path

def sha256_file(path,chunk=1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def cache_put(src,cache_dir,namespace="media"):
    src=Path(src); cache=Path(cache_dir)/namespace
    cache.mkdir(parents=True,exist_ok=True)
    digest=sha256_file(src); dst=cache/digest[:2]/digest
    dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists(): shutil.copy2(src,dst)
    dst.with_suffix(".json").write_text(json.dumps({"sha256":digest,"original":str(src),"size":src.stat().st_size},indent=2),encoding="utf-8")
    return digest,dst

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("file"); ap.add_argument("--cache",default=".harum_cache")
    ap.add_argument("--namespace",default="media")
    a=ap.parse_args()
    d,p=cache_put(a.file,a.cache,a.namespace)
    print(json.dumps({"sha256":d,"cached":str(p)},indent=2))
