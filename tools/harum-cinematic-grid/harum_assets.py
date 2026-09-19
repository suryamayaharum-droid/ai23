#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, mimetypes
from pathlib import Path

def sha256(path,chunk=1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--out",default="asset_registry.json")
    a=ap.parse_args(); root=Path(a.root).resolve(); items=[]
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name==a.out: continue
        items.append({"path":p.relative_to(root).as_posix(),"size":p.stat().st_size,
                      "sha256":sha256(p),"mime":mimetypes.guess_type(p.name)[0]})
    out=root/a.out
    out.write_text(json.dumps({"root":str(root),"assets":items},indent=2),encoding="utf-8")
    print(out)
if __name__=="__main__": main()
