#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,sqlite3
from pathlib import Path
from typing import Any

class ToolError(RuntimeError): pass

class ToolKernel:
    def __init__(self,root:str="."):
        self.root=Path(root).resolve()
        self.tools={
          "list_files":self.list_files,
          "read_text":self.read_text,
          "find_text":self.find_text,
          "hash_file":self.hash_file,
          "json_get":self.json_get,
          "sqlite_read":self.sqlite_read
        }

    def _safe(self,relative:str)->Path:
        p=(self.root/relative).resolve()
        try:
            p.relative_to(self.root)
        except ValueError:
            raise ToolError("path escapes allowed root")
        return p

    def describe(self)->dict[str,Any]:
        return {
          "list_files":{"args":{"path":"str","limit":"int<=200"}},
          "read_text":{"args":{"path":"str","max_chars":"int<=20000"}},
          "find_text":{"args":{"path":"str","pattern":"str","limit":"int<=50"}},
          "hash_file":{"args":{"path":"str"}},
          "json_get":{"args":{"path":"str","keys":"list[str]"}},
          "sqlite_read":{"args":{"path":"str","sql":"SELECT/WITH only","limit":"int<=100"}}
        }

    def call(self,name:str,args:dict[str,Any])->Any:
        if name not in self.tools:
            raise ToolError(f"tool not allowed: {name}")
        return self.tools[name](**args)

    def list_files(self,path:str=".",limit:int=100):
        limit=max(1,min(int(limit),200))
        p=self._safe(path)
        if not p.exists(): return []
        if p.is_file(): return [str(p.relative_to(self.root))]
        out=[]
        for x in p.rglob("*"):
            if x.is_file():
                out.append(str(x.relative_to(self.root)))
                if len(out)>=limit: break
        return out

    def read_text(self,path:str,max_chars:int=12000):
        max_chars=max(1,min(int(max_chars),20000))
        p=self._safe(path)
        if not p.is_file(): raise ToolError("file not found")
        if p.stat().st_size>2_000_000: raise ToolError("file too large for text tool")
        return p.read_text(encoding="utf-8",errors="replace")[:max_chars]

    def find_text(self,path:str,pattern:str,limit:int=20):
        limit=max(1,min(int(limit),50))
        p=self._safe(path)
        rx=re.compile(pattern,re.I)
        files=[p] if p.is_file() else [x for x in p.rglob("*") if x.is_file()]
        hits=[]
        for f in files[:1000]:
            if f.stat().st_size>1_000_000: continue
            try: lines=f.read_text(encoding="utf-8",errors="ignore").splitlines()
            except Exception: continue
            for i,line in enumerate(lines,1):
                if rx.search(line):
                    hits.append({"path":str(f.relative_to(self.root)),"line":i,"text":line[:500]})
                    if len(hits)>=limit:return hits
        return hits

    def hash_file(self,path:str):
        p=self._safe(path)
        h=hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):
                h.update(chunk)
        return {"sha256":h.hexdigest(),"bytes":p.stat().st_size}

    def json_get(self,path:str,keys:list[str]):
        obj=json.loads(self.read_text(path,20000))
        for k in keys:
            if isinstance(obj,list): obj=obj[int(k)]
            else: obj=obj[k]
        return obj

    def sqlite_read(self,path:str,sql:str,limit:int=100):
        if not re.match(r"^\s*(select|with)\b",sql,re.I):
            raise ToolError("read-only SELECT/WITH statements only")
        if ";" in sql.strip().rstrip(";"):
            raise ToolError("one statement only")
        p=self._safe(path)
        uri=f"file:{p}?mode=ro"
        con=sqlite3.connect(uri,uri=True)
        con.row_factory=sqlite3.Row
        try:
            rows=con.execute(sql).fetchmany(max(1,min(int(limit),100)))
            return [dict(r) for r in rows]
        finally:
            con.close()

if __name__=="__main__":
    print(json.dumps(ToolKernel().describe(),ensure_ascii=False,indent=2))
