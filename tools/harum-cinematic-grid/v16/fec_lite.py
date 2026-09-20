#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path
def encode(path,outdir,parts=8):
    b=Path(path).read_bytes();n=max(1,math.ceil(len(b)/parts));chunks=[b[i*n:(i+1)*n] for i in range(parts)]
    chunks += [b""]*(parts-len(chunks));mx=max(map(len,chunks));chunks=[x+b"\0"*(mx-len(x)) for x in chunks]
    parity=bytearray(mx)
    for ch in chunks:
        for i,v in enumerate(ch): parity[i]^=v
    o=Path(outdir);o.mkdir(parents=True,exist_ok=True)
    for i,ch in enumerate(chunks):(o/f"chunk_{i:03d}.bin").write_bytes(ch)
    (o/"parity.bin").write_bytes(bytes(parity));man={"original_size":len(b),"parts":parts,"chunk_size":mx}
    (o/"manifest.json").write_text(json.dumps(man,indent=2));return man
def recover(outdir,missing,dest):
    o=Path(outdir);m=json.loads((o/"manifest.json").read_text());data=bytearray((o/"parity.bin").read_bytes())
    for i in range(m["parts"]):
        if i==missing:continue
        ch=(o/f"chunk_{i:03d}.bin").read_bytes()
        for j,v in enumerate(ch):data[j]^=v
    (o/f"chunk_{missing:03d}.bin").write_bytes(bytes(data))
    allb=b"".join((o/f"chunk_{i:03d}.bin").read_bytes() for i in range(m["parts"]))[:m["original_size"]]
    Path(dest).write_bytes(allb);return {"recovered":missing,"bytes":len(allb)}
if __name__=="__main__":
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    e=sp.add_parser("encode");e.add_argument("path");e.add_argument("outdir");e.add_argument("--parts",type=int,default=8)
    r=sp.add_parser("recover");r.add_argument("outdir");r.add_argument("missing",type=int);r.add_argument("dest")
    a=ap.parse_args();print(json.dumps(encode(a.path,a.outdir,a.parts) if a.cmd=="encode" else recover(a.outdir,a.missing,a.dest),indent=2))
