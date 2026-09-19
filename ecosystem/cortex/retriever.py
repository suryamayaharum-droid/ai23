#!/usr/bin/env python3
from __future__ import annotations
import json,math,os,re,urllib.request
from pathlib import Path
from typing import Any

STOP={"a","o","e","de","da","do","em","um","uma","para","com","que","the","and","of","to","in","is"}

def lex_tokens(s:str):
    return [t for t in re.findall(r"[\wÀ-ÿ]+",s.lower()) if len(t)>2 and t not in STOP]

def lexical_score(q:str,d:str):
    qv={};dv={}
    for t in lex_tokens(q):qv[t]=qv.get(t,0)+1
    for t in lex_tokens(d):dv[t]=dv.get(t,0)+1
    dot=sum(v*dv.get(k,0) for k,v in qv.items())
    nq=math.sqrt(sum(v*v for v in qv.values()));nd=math.sqrt(sum(v*v for v in dv.values()))
    return dot/(nq*nd) if nq and nd else 0.0

def cosine(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    na=math.sqrt(sum(x*x for x in a));nb=math.sqrt(sum(y*y for y in b))
    return dot/(na*nb) if na and nb else 0.0

class Retriever:
    def __init__(self,index_path:str="runtime/harum-knowledge.jsonl",embedding_url:str|None=None):
        self.path=Path(index_path)
        self.embedding_url=embedding_url or os.getenv("HARUM_EMBEDDING_URL")
        self.rows=[
          json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()
        ] if self.path.exists() else []

    def _embed(self,texts:list[str]):
        if not self.embedding_url:return None
        req=urllib.request.Request(
          self.embedding_url.rstrip("/")+"/v1/embeddings",
          data=json.dumps({"input":texts,"model":"local-embedding","encoding_format":"float"}).encode(),
          method="POST",
          headers={"Content-Type":"application/json"}
        )
        with urllib.request.urlopen(req,timeout=90) as r:
            data=json.loads(r.read().decode())
        return [x["embedding"] for x in sorted(data["data"],key=lambda x:x["index"])]

    def search(self,query:str,k:int=6):
        k=max(1,min(int(k),20))
        if not self.rows:return []
        if self.embedding_url:
            try:
                texts=[query]+[r["text"] for r in self.rows]
                vecs=self._embed(texts)
                q=vecs[0]
                ranked=[(cosine(q,v),row) for v,row in zip(vecs[1:],self.rows)]
            except Exception:
                ranked=[(lexical_score(query,r["text"]),r) for r in self.rows]
        else:
            ranked=[(lexical_score(query,r["text"]),r) for r in self.rows]
        ranked.sort(key=lambda x:-x[0])
        return [{"score":round(s,5),**r} for s,r in ranked[:k] if s>0]

    def context(self,query:str,k:int=6,max_chars:int=10000):
        hits=self.search(query,k)
        parts=[];used=0
        for h in hits:
            block=f"[SOURCE {h['source']}#{h['start']}-{h['end']}]\n{h['text']}"
            if used+len(block)>max_chars:break
            parts.append(block);used+=len(block)
        return "\n\n".join(parts),hits
