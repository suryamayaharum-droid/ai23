#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from harum_living_circuit import request
from harum_identity import verify

def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

class CarrierFailover:
    def __init__(self,root):
        self.root=Path(root); self.out=self.root/"outbox"; self.receipts=self.root/"receipts"
        self.out.mkdir(parents=True,exist_ok=True); self.receipts.mkdir(parents=True,exist_ok=True)
    def spool(self,envelope,reason):
        bid=hashlib.sha256(stable(envelope)).hexdigest()
        p=self.out/f"{bid}.json"
        p.write_text(json.dumps({"id":bid,"envelope":envelope,"reason":reason,"spooled":time.time()},ensure_ascii=False,indent=2))
        return {"status":"spooled","id":bid,"path":str(p),"reason":reason}
    def dispatch(self,host,port,envelope):
        try:
            res=request(host,port,envelope)
            if res.get("ok") and verify(res.get("signed_receipt",{})).get("valid"):
                rid=res["signed_receipt"]["payload"]["task_id"]
                (self.receipts/f"{rid}.json").write_text(json.dumps(res,ensure_ascii=False,indent=2))
                return {"status":"delivered","response":res}
            return self.spool(envelope,"remote_rejected:"+res.get("error","unknown"))
        except Exception as e:
            return self.spool(envelope,type(e).__name__+":"+str(e))
    def flush(self,host,port):
        sent=[]; failed=[]
        for p in sorted(self.out.glob("*.json")):
            d=json.loads(p.read_text())
            try:
                res=request(host,port,d["envelope"])
                if res.get("ok") and verify(res.get("signed_receipt",{})).get("valid"):
                    rid=res["signed_receipt"]["payload"]["task_id"]
                    (self.receipts/f"{rid}.json").write_text(json.dumps(res,ensure_ascii=False,indent=2))
                    p.unlink(); sent.append({"id":d["id"],"task_id":rid,"replayed":res.get("replayed",False)})
                else: failed.append({"id":d["id"],"error":res.get("error")})
            except Exception as e: failed.append({"id":d["id"],"error":type(e).__name__})
        return {"sent":sent,"failed":failed,"remaining":len(list(self.out.glob("*.json")))}
