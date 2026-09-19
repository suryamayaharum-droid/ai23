#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, time
from pathlib import Path

class CAS:
    def __init__(self, root):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
        (self.root/'objects').mkdir(exist_ok=True); (self.root/'manifests').mkdir(exist_ok=True)
    def sha(self,path):
        h=hashlib.sha256()
        with open(path,'rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        return h.hexdigest()
    def put(self,path,meta=None):
        path=Path(path); d=self.sha(path); obj=self.root/'objects'/d[:2]/d
        obj.parent.mkdir(parents=True,exist_ok=True)
        if not obj.exists(): shutil.copy2(path,obj)
        man={'sha256':d,'source':str(path),'size':path.stat().st_size,'stored':str(obj),'created':time.time(),'meta':meta or {}}
        (self.root/'manifests'/f'{d}.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
        return man
    def materialize(self,dest,digest):
        obj=self.root/'objects'/digest[:2]/digest
        if not obj.exists(): raise FileNotFoundError(digest)
        dest=Path(dest); dest.parent.mkdir(parents=True,exist_ok=True)
        try: os.link(obj,dest)
        except Exception: shutil.copy2(obj,dest)
        return str(dest)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.harum_cas'); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('put'); p.add_argument('file')
    m=sp.add_parser('materialize'); m.add_argument('sha256'); m.add_argument('dest')
    a=ap.parse_args(); cas=CAS(a.root)
    print(json.dumps(cas.put(a.file) if a.cmd=='put' else {'path':cas.materialize(a.dest,a.sha256)},indent=2))
if __name__=='__main__':main()
