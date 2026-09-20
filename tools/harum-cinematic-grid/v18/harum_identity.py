#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, hashlib, json, os, time
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

def b64(b): return base64.urlsafe_b64encode(b).decode().rstrip("=")
def ub64(s): return base64.urlsafe_b64decode(s + "="*((4-len(s)%4)%4))
def canonical(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def gen(out,node):
    priv=Ed25519PrivateKey.generate(); pub=priv.public_key()
    privb=priv.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())
    pubb=pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    peer_id=hashlib.sha256(pubb).hexdigest()
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({"node":node,"peer_id":peer_id,"private_key":b64(privb),"public_key":b64(pubb)},indent=2))
    os.chmod(p,0o600)
    return {"node":node,"peer_id":peer_id,"public_key":b64(pubb)}

def load(path): return json.loads(Path(path).read_text())

def sign(identity_path,payload):
    i=load(identity_path); priv=Ed25519PrivateKey.from_private_bytes(ub64(i["private_key"]))
    body={"issuer":i["peer_id"],"public_key":i["public_key"],"ts":time.time(),"payload":payload}
    return {**body,"signature":b64(priv.sign(canonical(body)))}

def verify(signed):
    body={k:signed[k] for k in ("issuer","public_key","ts","payload")}
    pubraw=ub64(signed["public_key"])
    if hashlib.sha256(pubraw).hexdigest()!=signed["issuer"]: return {"valid":False,"reason":"peer_id_mismatch"}
    try:
        Ed25519PublicKey.from_public_bytes(pubraw).verify(ub64(signed["signature"]),canonical(body))
        return {"valid":True,"issuer":signed["issuer"]}
    except Exception:
        return {"valid":False,"reason":"bad_signature"}
