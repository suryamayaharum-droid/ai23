#!/usr/bin/env python3
from __future__ import annotations
import json,re,math
from collections import Counter
from typing import Any

STOP={"a","o","e","de","da","do","em","um","uma","para","com","que","the","and","of","to","in","is"}

def tokens(text:str)->set[str]:
    return {
      t for t in re.findall(r"[\wÀ-ÿ]+",text.lower())
      if len(t)>2 and t not in STOP
    }

def similarity(a:str,b:str)->float:
    x,y=tokens(a),tokens(b)
    if not x or not y:return 0.0
    return len(x&y)/len(x|y)

def quorum(proposals:list[dict[str,Any]],threshold:float=0.18)->dict[str,Any]:
    valid=[p for p in proposals if p.get("text")]
    if len(valid)<2:
        return {"status":"INSUFFICIENT_BRAINS","pairs":[],"quorum":False}
    pairs=[]
    adjacency={p["brain"]:set() for p in valid}
    for i,a in enumerate(valid):
        for b in valid[i+1:]:
            s=similarity(a["text"],b["text"])
            agree=s>=threshold
            pairs.append({"a":a["brain"],"b":b["brain"],"similarity":round(s,4),"agree":agree})
            if agree:
                adjacency[a["brain"]].add(b["brain"])
                adjacency[b["brain"]].add(a["brain"])
    ranked=sorted(adjacency.items(),key=lambda x:(-len(x[1]),x[0]))
    strongest=ranked[0] if ranked else (None,set())
    needed=max(1,(len(valid)-1)//2)
    has=len(strongest[1])>=needed
    return {
      "status":"QUORUM" if has else "DISAGREEMENT",
      "quorum":has,
      "anchor_brain":strongest[0],
      "support":sorted(strongest[1]),
      "pairs":pairs,
      "threshold":threshold
    }

if __name__=="__main__":
    import sys
    data=json.load(sys.stdin)
    print(json.dumps(quorum(data),ensure_ascii=False,indent=2))
