#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, re, shutil, sqlite3, subprocess, threading, time
from pathlib import Path
from collections import defaultdict

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REG=HERE/"city_registry.json"
DB=HERE/"runtime"/"city.db"
EVENTS=HERE/"runtime"/"city_events.jsonl"
ACTIONS=HERE/"runtime"/"external_actions.jsonl"
ART=HERE/"runtime"/"artifacts"
ART.mkdir(parents=True,exist_ok=True)
SCHEMA="""PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS city_state(key TEXT PRIMARY KEY,value TEXT NOT NULL,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS districts(id TEXT PRIMARY KEY,name TEXT,status TEXT,last_heartbeat REAL,meta TEXT);
CREATE TABLE IF NOT EXISTS swarms(id TEXT PRIMARY KEY,district TEXT,status TEXT,circuit TEXT DEFAULT 'closed',failures INTEGER DEFAULT 0,last_heartbeat REAL,meta TEXT);
CREATE TABLE IF NOT EXISTS agents(id TEXT PRIMARY KEY,swarm TEXT,status TEXT,last_heartbeat REAL,meta TEXT);
CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,title TEXT,status TEXT,priority INTEGER,created REAL,updated REAL,meta TEXT);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,mission TEXT,district TEXT,swarm TEXT,path TEXT,sha256 TEXT,kind TEXT,created REAL);
"""
LOCK=threading.RLock()
def conn():
    c=sqlite3.connect(DB,timeout=30,check_same_thread=False); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c
def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def resource_census():
    cpu=os.cpu_count() or 1; mem=None
    try:
        kb=int(re.search(r"MemTotal:\s+(\d+)",Path("/proc/meminfo").read_text()).group(1)); mem=round(kb/1024/1024,2)
    except Exception: pass
    gpu=[]
    if shutil.which("nvidia-smi"):
        try:
            out=subprocess.check_output(["nvidia-smi","--query-gpu=index,name,memory.total","--format=csv,noheader,nounits"],text=True)
            for line in out.splitlines():
                a=line.split(",",2); gpu.append({"index":int(a[0]),"name":a[1].strip(),"vram_mb":int(a[2])})
        except Exception: pass
    return {"cpu_count":cpu,"memory_gb":mem,"gpus":gpu,"local_worker_cap":min(32,max(4,cpu))}
def boot():
    if not REG.exists():
        subprocess.run([os.sys.executable,str(HERE/"city_registry_builder.py")],cwd=str(HERE),check=True)
    reg=json.loads(REG.read_text(encoding="utf-8")); c=conn(); census=resource_census()
    for d in reg["districts"]:
        c.execute("INSERT OR REPLACE INTO districts VALUES(?,?,?,?,?)",(d["id"],d["name"],"idle",time.time(),stable({"governor":d["governor"]})))
        for s in d["swarms"]:
            c.execute("INSERT OR REPLACE INTO swarms VALUES(?,?,?,?,?,?,?)",(s["id"],d["id"],"idle","closed",0,time.time(),"{}"))
            for a in s["agents"]: c.execute("INSERT OR REPLACE INTO agents VALUES(?,?,?,?,?)",(a["id"],s["id"],"idle",time.time(),stable(a)))
    c.commit(); c.close()
    return {"status":"online","districts":reg["district_count"],"swarms":reg["swarm_count"],"agents":reg["agent_role_count"],"resources":census}
def project_files():
    exts={".md",".json",".py",".yml",".yaml",".txt",".csv"}
    return [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in exts and "__pycache__" not in p.parts]
def swarm_job(district,swarm,mission,title):
    files=project_files()
    report={"mission":mission,"district":district,"swarm":swarm,"title":title,"status":"complete","files_seen":len(files)}
    out=ART/f"{mission}.{swarm.replace('.','__')}.json"; out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report
def mission(title,mid):
    reg=json.loads(REG.read_text(encoding="utf-8")); cap=resource_census()["local_worker_cap"]
    jobs=[(d["id"],s["id"]) for d in reg["districts"] for s in d["swarms"]]
    t=time.perf_counter(); reports={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=cap) as ex:
        fs={ex.submit(swarm_job,d,s,mid,title):(d,s) for d,s in jobs}
        for f in concurrent.futures.as_completed(fs):
            d,s=fs[f]; reports[s]=f.result()
    return {"mission":mid,"districts":len(reg["districts"]),"swarms":len(jobs),"agent_roles":reg["agent_role_count"],"local_worker_cap":cap,"complete":len(reports),"elapsed_seconds":round(time.perf_counter()-t,3),
    "truth":"Coordination scales; physical compute remains capped to real resources."}
def main():
    p=argparse.ArgumentParser(); sp=p.add_subparsers(dest="cmd",required=True); sp.add_parser("boot"); m=sp.add_parser("mission"); m.add_argument("title"); m.add_argument("--id",required=True)
    a=p.parse_args(); print(json.dumps(boot() if a.cmd=="boot" else mission(a.title,a.id),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
