#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

CHUNK=32*1024*1024
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def ingest(path,vault,chunk_size=CHUNK):
    p=Path(path);v=Path(vault);objects=v/"objects";objects.mkdir(parents=True,exist_ok=True);chunks=[]
    with open(p,"rb") as f:
        index=0
        while True:
            b=f.read(chunk_size)
            if not b:break
            d=hashlib.sha256(b).hexdigest();dst=objects/d[:2]/d;dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists():dst.write_bytes(b)
            chunks.append({"index":index,"sha256":d,"bytes":len(b)});index+=1
    manifest={"format":"harum.model.vault.v1","name":p.name,"bytes":p.stat().st_size,"sha256":sha(p),"chunk_size":chunk_size,"chunks":chunks}
    (v/(manifest["sha256"]+".manifest.json")).write_text(json.dumps(manifest,indent=2));return manifest

def materialize(manifest_path,vault,out):
    m=json.loads(Path(manifest_path).read_text());v=Path(vault);o=Path(out)
    with open(o,"wb") as w:
        for ch in m["chunks"]:
            p=v/"objects"/ch["sha256"][:2]/ch["sha256"];b=p.read_bytes()
            if hashlib.sha256(b).hexdigest()!=ch["sha256"]:raise ValueError("corrupt chunk")
            w.write(b)
    if o.stat().st_size!=m["bytes"] or sha(o)!=m["sha256"]:raise ValueError("materialized model mismatch")
    return {"ok":True,"sha256":m["sha256"],"bytes":m["bytes"],"chunks":len(m["chunks"])}

if __name__=="__main__":
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    i=sp.add_parser("ingest");i.add_argument("path");i.add_argument("vault");i.add_argument("--chunk-size",type=int,default=CHUNK)
    m=sp.add_parser("materialize");m.add_argument("manifest");m.add_argument("vault");m.add_argument("out")
    a=ap.parse_args();res=ingest(a.path,a.vault,a.chunk_size) if a.cmd=="ingest" else materialize(a.manifest,a.vault,a.out)
    print(json.dumps(res,indent=2))
