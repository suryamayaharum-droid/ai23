#!/usr/bin/env python3
from __future__ import annotations
import argparse,base64,hashlib,json,time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
def b64(b):return base64.urlsafe_b64encode(b).decode().rstrip("=")
def ub64(s):return base64.urlsafe_b64decode(s+"="*((4-len(s)%4)%4))
def stable(x):return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def gen():
    p=Ed25519PrivateKey.generate();pub=p.public_key()
    pr=p.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())
    pu=pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    return {"private":b64(pr),"public":b64(pu),"peer_id":hashlib.sha256(pu).hexdigest()}
def sign(i,payload):
    body={"issuer":i["peer_id"],"public_key":i["public"],"payload":payload}
    sig=Ed25519PrivateKey.from_private_bytes(ub64(i["private"])).sign(stable(body));return {**body,"signature":b64(sig)}
def verify(x):
    body={k:x[k] for k in ("issuer","public_key","payload")};pub=ub64(x["public_key"])
    if hashlib.sha256(pub).hexdigest()!=x["issuer"]:return False
    try:Ed25519PublicKey.from_public_bytes(pub).verify(ub64(x["signature"]),stable(body));return True
    except Exception:return False
def sender(outdir):
    o=Path(outdir);o.mkdir(parents=True,exist_ok=True);i=gen()
    payload={"type":"harum.dtn.task.v1","task_id":hashlib.sha256(b"cross-runner-v21").hexdigest(),"kind":"sha256_text","text":"HARUM v21 cross-runner store-carry-forward","created":time.time()}
    (o/"signed_task.json").write_text(json.dumps(sign(i,payload),indent=2));return {"task_id":payload["task_id"],"sender":i["peer_id"]}
def receiver(indir,outdir):
    i=Path(indir);o=Path(outdir);o.mkdir(parents=True,exist_ok=True);signed=json.loads((i/"signed_task.json").read_text())
    if not verify(signed):raise ValueError("bad sender signature")
    p=signed["payload"]
    if p["kind"]!="sha256_text":raise ValueError("kind not allowlisted")
    result={"sha256":hashlib.sha256(p["text"].encode()).hexdigest(),"length":len(p["text"])}
    rid=gen();receipt=sign(rid,{"type":"harum.dtn.receipt.v1","task_id":p["task_id"],"result":result,"completed":time.time()})
    (o/"signed_receipt.json").write_text(json.dumps(receipt,indent=2));return {"task_id":p["task_id"],"receiver":rid["peer_id"],"result":result}
def final_verify(indir):
    r=json.loads((Path(indir)/"signed_receipt.json").read_text())
    if not verify(r):raise ValueError("bad receipt")
    return {"verified":True,"task_id":r["payload"]["task_id"],"receiver":r["issuer"]}
if __name__=="__main__":
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    s=sp.add_parser("sender");s.add_argument("outdir")
    r=sp.add_parser("receiver");r.add_argument("indir");r.add_argument("outdir")
    v=sp.add_parser("verify");v.add_argument("indir")
    a=ap.parse_args();x=sender(a.outdir) if a.cmd=="sender" else receiver(a.indir,a.outdir) if a.cmd=="receiver" else final_verify(a.indir)
    print(json.dumps(x,indent=2))
