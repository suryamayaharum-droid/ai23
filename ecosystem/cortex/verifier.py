#!/usr/bin/env python3
from __future__ import annotations
import json,re
from typing import Any,Callable

class Verification:
    @staticmethod
    def exact(text:str,expected:list[str])->dict[str,Any]:
        n=re.sub(r"\s+"," ",text.strip()).casefold()
        ok=any(n==re.sub(r"\s+"," ",x.strip()).casefold() for x in expected)
        return {"ok":ok,"type":"exact"}

    @staticmethod
    def contains(text:str,required:list[str])->dict[str,Any]:
        low=text.casefold()
        missing=[x for x in required if x.casefold() not in low]
        return {"ok":not missing,"type":"contains","missing":missing}

    @staticmethod
    def json_shape(text:str,required_keys:list[str])->dict[str,Any]:
        try:d=json.loads(text)
        except Exception as exc:return {"ok":False,"type":"json_shape","error":str(exc)}
        if not isinstance(d,dict):
            return {"ok":False,"type":"json_shape","error":"root not object"}
        missing=[k for k in required_keys if k not in d]
        return {"ok":not missing,"type":"json_shape","missing":missing}

    @staticmethod
    def policy(action:dict[str,Any])->dict[str,Any]:
        forbidden={"password","token","cookie","api_key","secret","service_role_key"}
        def walk(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if str(k).casefold() in forbidden:return False
                    if not walk(v):return False
            if isinstance(x,list):
                return all(walk(y) for y in x)
            return True
        return {"ok":walk(action),"type":"secret_policy"}
