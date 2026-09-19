#!/usr/bin/env python3
from __future__ import annotations
from typing import Any

DENY_KEYS={"password","token","cookie","api_key","secret","service_role_key"}

def contains_secret_shape(obj:Any)->bool:
    if isinstance(obj,dict):
        for k,v in obj.items():
            if str(k).lower() in DENY_KEYS:
                return True
            if contains_secret_shape(v):
                return True
    elif isinstance(obj,list):
        return any(contains_secret_shape(x) for x in obj)
    return False

def evaluate(action:dict[str,Any])->dict[str,Any]:
    reasons=[]
    allowed=True
    if contains_secret_shape(action):
        allowed=False; reasons.append("secret-like data blocked")
    if action.get("bypass_quota"):
        allowed=False; reasons.append("quota bypass forbidden")
    if action.get("publish_public") and not action.get("publication_gate"):
        allowed=False; reasons.append("public release requires publication gate")
    if action.get("commerce_claim") and not action.get("truth_gate"):
        allowed=False; reasons.append("commerce claim requires truth gate")
    if action.get("external_write") and not action.get("authorized_adapter"):
        allowed=False; reasons.append("external write requires authorized adapter")
    return {"allowed":allowed,"reasons":reasons or ["policy passed"]}
