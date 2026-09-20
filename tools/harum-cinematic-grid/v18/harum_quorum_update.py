#!/usr/bin/env python3
from __future__ import annotations
import json,time,hashlib
from harum_identity import sign,verify

def manifest(version,target_sha,expires_in=3600):
    return {"type":"harum.update.manifest.v1","version":int(version),"target_sha256":target_sha,
            "expires":time.time()+expires_in,"rollback_ref":"git:previous",
            "tests":["compile","unit","integration"],"created":time.time()}

def approve(identity,m):
    mh=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return sign(identity,{"type":"harum.update.approval.v1","manifest_sha256":mh,"version":m["version"]})

def verify_quorum(m,approvals,allowed,threshold,current_version):
    if m["version"]<=current_version:return {"accepted":False,"reason":"rollback_or_same_version"}
    if time.time()>m["expires"]:return {"accepted":False,"reason":"expired_manifest"}
    mh=hashlib.sha256(json.dumps(m,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    good=set()
    for a in approvals:
        v=verify(a)
        if not v.get("valid"):continue
        p=a.get("payload",{})
        if v["issuer"] in allowed and p.get("manifest_sha256")==mh and p.get("version")==m["version"]:
            good.add(v["issuer"])
    return {"accepted":len(good)>=threshold,"valid_signers":sorted(good),"count":len(good),"threshold":threshold}
