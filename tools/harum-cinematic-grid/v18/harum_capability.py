#!/usr/bin/env python3
from __future__ import annotations
import time
from harum_identity import sign,verify

def issue(identity,subject,actions,resource,ttl=3600):
    payload={"type":"harum.capability.v1","subject":subject,"actions":sorted(set(actions)),"resource":resource,"expires":time.time()+ttl}
    return sign(identity,payload)

def check(token,subject,action,resource):
    v=verify(token)
    if not v.get("valid"): return {"allowed":False,"reason":"invalid_signature"}
    p=token["payload"]
    if p.get("type")!="harum.capability.v1": return {"allowed":False,"reason":"wrong_type"}
    if time.time()>p["expires"]: return {"allowed":False,"reason":"expired"}
    if p["subject"]!=subject: return {"allowed":False,"reason":"wrong_subject"}
    if action not in p["actions"]: return {"allowed":False,"reason":"action_not_granted"}
    if not (resource==p["resource"] or resource.startswith(p["resource"].rstrip("/")+"/")):
        return {"allowed":False,"reason":"resource_out_of_scope"}
    return {"allowed":True,"issuer":token["issuer"],"expires":p["expires"]}
