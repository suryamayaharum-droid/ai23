#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,secrets,shutil,time,zipfile
from pathlib import Path

def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def sha_bytes(b): return hashlib.sha256(b).hexdigest()

class Store:
    def __init__(self,root,node):
        self.root=Path(root); self.node=node
        for d in ("bundles","objects","receipts"): (self.root/d).mkdir(parents=True,exist_ok=True)

    def create(self,topic,payload,priority=50,ttl_hours=720):
        now=time.time()
        core={"origin":self.node,"created":now,"expires":now+ttl_hours*3600,"topic":topic,"priority":priority,"payload":payload,"nonce":secrets.token_hex(8)}
        bid=hashlib.sha256(stable(core).encode()).hexdigest()
        bundle={**core,"bundle_id":bid,"path":[],"hops":0}
        (self.root/"bundles"/f"{bid}.json").write_text(json.dumps(bundle,ensure_ascii=False,indent=2),encoding="utf-8")
        return bundle

    def export_capsule(self,bids,out):
        with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
            man={"format":"harum.capsule.v1","from":self.node,"created":time.time(),"bundles":list(bids)}
            for bid in bids:
                p=self.root/"bundles"/f"{bid}.json"; z.write(p,f"bundles/{bid}.json")
            man["manifest_sha256"]=sha_bytes(stable({k:v for k,v in man.items() if k!="manifest_sha256"}).encode())
            z.writestr("manifest.json",json.dumps(man,ensure_ascii=False,indent=2))
        return str(out)

    def import_capsule(self,capsule):
        accepted=[]
        with zipfile.ZipFile(capsule) as z:
            man=json.loads(z.read("manifest.json"))
            expected=sha_bytes(stable({k:v for k,v in man.items() if k!="manifest_sha256"}).encode())
            if expected!=man.get("manifest_sha256"): raise ValueError("manifest integrity failure")
            for bid in man["bundles"]:
                b=json.loads(z.read(f"bundles/{bid}.json"))
                if b["bundle_id"]!=bid or b["expires"]<time.time(): continue
                dst=self.root/"bundles"/f"{bid}.json"
                if not dst.exists():
                    b["path"]=b.get("path",[])+[self.node];b["hops"]=int(b.get("hops",0))+1
                    dst.write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding="utf-8");accepted.append(bid)
        return accepted
