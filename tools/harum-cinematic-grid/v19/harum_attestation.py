#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, time, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"v18"))
from harum_identity import sign, verify

def stable(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()

def build_chain(identity_path, task_id, stages):
    prev = "0"*64
    chain = []
    for index,(stage,detail) in enumerate(stages):
        payload = {
            "type":"harum.attestation.v1",
            "task_id":task_id,
            "index":index,
            "stage":stage,
            "detail":detail,
            "prev":prev,
            "ts":time.time()
        }
        signed = sign(identity_path,payload)
        digest = hashlib.sha256(stable(signed)).hexdigest()
        chain.append(signed)
        prev = digest
    return chain

def verify_chain(chain, expected_task=None, expected_issuer=None):
    prev="0"*64
    for index,signed in enumerate(chain):
        v=verify(signed)
        if not v.get("valid"):
            return {"valid":False,"index":index,"reason":"bad_signature"}
        if expected_issuer and v["issuer"]!=expected_issuer:
            return {"valid":False,"index":index,"reason":"wrong_issuer"}
        p=signed.get("payload",{})
        if p.get("type")!="harum.attestation.v1":
            return {"valid":False,"index":index,"reason":"wrong_type"}
        if p.get("index")!=index:
            return {"valid":False,"index":index,"reason":"wrong_index"}
        if p.get("prev")!=prev:
            return {"valid":False,"index":index,"reason":"broken_chain"}
        if expected_task and p.get("task_id")!=expected_task:
            return {"valid":False,"index":index,"reason":"wrong_task"}
        prev=hashlib.sha256(stable(signed)).hexdigest()
    return {"valid":True,"steps":len(chain),"root":prev}
