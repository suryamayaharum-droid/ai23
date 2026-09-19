#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,re
from pathlib import Path

TEXT_EXT={".md",".txt",".json",".py",".yml",".yaml",".csv",".toml",".sql"}
SKIP_PARTS={".git","runtime","__pycache__",".pytest_cache","node_modules"}
SKIP_NAMES={".env",".env.local","secrets.json","credentials.json"}

def chunks(text:str,size:int=1400,overlap:int=180):
    text=re.sub(r"\r\n?","\n",text)
    start=0
    while start<len(text):
        end=min(len(text),start+size)
        piece=text[start:end].strip()
        if piece:yield start,end,piece
        if end>=len(text):break
        start=max(start+1,end-overlap)

def build(root:Path,include:list[str],out:Path):
    rows=[]
    for rel in include:
        base=(root/rel)
        if not base.exists():continue
        files=[base] if base.is_file() else list(base.rglob("*"))
        for p in files:
            if not p.is_file() or p.suffix.lower() not in TEXT_EXT:continue
            if p.name in SKIP_NAMES or any(x in SKIP_PARTS for x in p.parts):continue
            if p.stat().st_size>2_000_000:continue
            try:text=p.read_text(encoding="utf-8",errors="ignore")
            except Exception:continue
            source=str(p.relative_to(root))
            file_sha=hashlib.sha256(text.encode()).hexdigest()
            for start,end,piece in chunks(text):
                cid=hashlib.sha256(f"{source}:{start}:{end}:{file_sha}".encode()).hexdigest()
                rows.append({
                  "id":cid,
                  "source":source,
                  "file_sha256":file_sha,
                  "start":start,
                  "end":end,
                  "text":piece
                })
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(json.dumps(r,ensure_ascii=False) for r in rows)+("\n" if rows else ""),encoding="utf-8")
    manifest={
      "chunks":len(rows),
      "files":len({r["source"] for r in rows}),
      "index_sha256":hashlib.sha256(out.read_bytes()).hexdigest() if out.exists() else None
    }
    out.with_suffix(".manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",default=".")
    ap.add_argument("--include",action="append",default=[
      "ecosystem/docs","ecosystem/integration","ecosystem/swarm","ecosystem/cortex","ecosystem/postgres","ecosystem/supabase"
    ])
    ap.add_argument("--output",default="runtime/harum-knowledge.jsonl")
    args=ap.parse_args()
    print(json.dumps(build(Path(args.root),args.include,Path(args.output)),indent=2))
