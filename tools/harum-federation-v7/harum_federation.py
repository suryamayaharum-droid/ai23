#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, re, shutil, sqlite3, subprocess, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
REG=HERE/"federation_registry.json"
DB=HERE/"runtime"/"federation.db"
EVENTS=HERE/"runtime"/"event_bus.jsonl"
ACTIONS=HERE/"runtime"/"external_actions.jsonl"
ART=HERE/"runtime"/"artifacts"
ART.mkdir(parents=True,exist_ok=True)

SCHEMA="""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS swarms(id TEXT PRIMARY KEY,status TEXT NOT NULL,last_run REAL,summary TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS agents(id TEXT PRIMARY KEY,swarm TEXT NOT NULL,status TEXT NOT NULL,last_heartbeat REAL,meta TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,title TEXT NOT NULL,status TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL,meta TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT,ts REAL NOT NULL,mission TEXT NOT NULL,sender TEXT NOT NULL,recipient TEXT NOT NULL,topic TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,mission TEXT NOT NULL,swarm TEXT NOT NULL,path TEXT NOT NULL,sha256 TEXT NOT NULL,kind TEXT NOT NULL,created REAL NOT NULL);
"""

def conn():
    c=sqlite3.connect(DB,timeout=30); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c

def emit(actor,event,payload,mission="system"):
    rec={"ts":time.time(),"mission":mission,"actor":actor,"event":event,"payload":payload}
    with EVENTS.open("a",encoding="utf-8") as f:f.write(json.dumps(rec,ensure_ascii=False)+"\n")
    return rec

def heartbeat(agent,swarm,status="idle",meta=None):
    c=conn()
    c.execute("""INSERT INTO agents(id,swarm,status,last_heartbeat,meta) VALUES(?,?,?,?,?)
    ON CONFLICT(id) DO UPDATE SET status=excluded.status,last_heartbeat=excluded.last_heartbeat,meta=excluded.meta""",
    (agent,swarm,status,time.time(),json.dumps(meta or {},ensure_ascii=False)))
    c.commit(); c.close()

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def safe_scan(root):
    exts={".md",".json",".py",".yml",".yaml",".txt",".csv"}
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts and "__pycache__" not in p.parts]

def secret_audit(files):
    pats=[re.compile(r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),re.compile(r"(?i)cfat_[A-Za-z0-9]{20,}")]
    hits=[]
    for p in files[:800]:
        try:t=p.read_text(encoding="utf-8",errors="ignore")
        except Exception:continue
        if any(rx.search(t) for rx in pats):hits.append(str(p.relative_to(ROOT)))
    return hits

def register_artifact(mission,swarm,path,kind="report"):
    p=Path(path); aid=hashlib.sha256((mission+swarm+str(p)+sha(p)).encode()).hexdigest()[:16]
    c=conn(); c.execute("INSERT OR REPLACE INTO artifacts(id,mission,swarm,path,sha256,kind,created) VALUES(?,?,?,?,?,?,?)",(aid,mission,swarm,str(p),sha(p),kind,time.time())); c.commit(); c.close()

def queue_external(action,mission):
    a={"id":hashlib.sha256((mission+json.dumps(action,sort_keys=True)+str(time.time_ns())).encode()).hexdigest()[:16],"mission":mission,"status":"queued","created":time.time(),**action}
    with ACTIONS.open("a",encoding="utf-8") as f:f.write(json.dumps(a,ensure_ascii=False)+"\n")
    return a

def swarm_report(swarm,mission):
    reg=json.loads(REG.read_text(encoding="utf-8")); s=next(x for x in reg["swarms"] if x["id"]==swarm)
    for a in s["agents"]:heartbeat(a["id"],swarm,"working")
    files=safe_scan(ROOT); report={"swarm":swarm,"mission":mission,"agents":[a["id"] for a in s["agents"]],"status":"complete","findings":{},"actions":[]}
    if swarm=="executive":report["findings"]={"governance":"federated","swarm_count":len(reg["swarms"]),"agent_count":reg["agent_count"]}
    elif swarm=="research":
        report["findings"]={"research_docs":len([p for p in files if "RESEARCH" in p.name.upper()])}; report["actions"].append({"kind":"research_refresh","payload":{"scope":"public current technologies"}})
    elif swarm=="memory":report["findings"]={"indexed_files":len(files),"canonical_candidates":[str(p.relative_to(ROOT)) for p in files if "CANON" in p.name.upper() or "ESTADO" in p.name.upper()][:30]}
    elif swarm=="brand":report["findings"]={"gate":"identity before volume","brand_docs":[str(p.relative_to(ROOT)) for p in files if "BIBLIA" in p.name.upper() or "BRAND" in p.name.upper()][:30]}
    elif swarm=="narrative":report["findings"]={"rule":"pay open loops within 1–3 chapters","story_files":[str(p.relative_to(ROOT)) for p in files if "STORY" in p.name.upper() or "ARC" in p.name.upper()][:30]}
    elif swarm=="image":
        report["findings"]={"prompt_files":[str(p.relative_to(ROOT)) for p in files if "PROMPT" in p.name.upper()][:30]}; report["actions"].append({"kind":"image_generate","payload":{"mode":"canonical_only","gate":"face lock"}})
    elif swarm=="cinematic":
        p=subprocess.run(["ffmpeg","-version"],capture_output=True,text=True) if shutil.which("ffmpeg") else None
        report["findings"]={"ffmpeg":bool(p),"version":p.stdout.splitlines()[0] if p and p.stdout else None}
    elif swarm=="audio":report["findings"]={"fallback":"offline procedural/eSpeak","audio_docs":[str(p.relative_to(ROOT)) for p in files if "AUDIO" in p.name.upper() or "VOICE" in p.name.upper()][:20]}
    elif swarm=="publishing":
        report["findings"]={"targets":["Instagram Harum Noir","YouTube @arteharum"],"rule":"never mark published without confirmation"}; report["actions"].append({"kind":"publish_sync","payload":{"targets":["Instagram","YouTube"],"requires_connector":True}})
    elif swarm=="growth":report["findings"]={"rule":"learn after enough observations","metric_files":[str(p.relative_to(ROOT)) for p in files if "METRIC" in p.name.upper() or "BENCH" in p.name.upper()][:20]}
    elif swarm=="commerce":report["findings"]={"gate":"checkout/delivery validation before direct sale claims"}
    elif swarm=="web":report["actions"].append({"kind":"web_audit","payload":{"targets":["Hotmart","site","Vercel"],"requires_connector_or_work":True}})
    elif swarm=="crm":report["actions"].append({"kind":"crm_sync","payload":{"requires_authorized_source":True}})
    elif swarm=="automation":report["findings"]={"event_bus":str(EVENTS),"runtime_files":len([p for p in files if "RUNTIME" in p.name.upper() or "SWARM" in p.name.upper()])}
    elif swarm=="infrastructure":report["findings"]={"python":sys.version.split()[0],"git":bool(shutil.which("git")),"file_count":len(files)}
    elif swarm=="security":
        hits=secret_audit(files); report["findings"]={"secret_like_files_count":len(hits),"secret_like_files":hits[:20],"policy":"never print secret values"}
        if hits:report["actions"].append({"kind":"security_review","payload":{"files":hits[:20],"severity":"high"}})
    out=ART/f"{mission}.{swarm}.json"; out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8"); register_artifact(mission,swarm,out)
    for a in s["agents"]:heartbeat(a["id"],swarm,"idle",{"last_mission":mission})
    return report

def boot():
    reg=json.loads(REG.read_text(encoding="utf-8")); c=conn()
    for s in reg["swarms"]:
        c.execute("INSERT OR REPLACE INTO swarms(id,status,last_run,summary) VALUES(?,?,?,?)",(s["id"],"idle",None,"{}"))
        for a in s["agents"]:c.execute("INSERT OR REPLACE INTO agents(id,swarm,status,last_heartbeat,meta) VALUES(?,?,?,?,?)",(a["id"],s["id"],"idle",time.time(),json.dumps(a,ensure_ascii=False)))
    c.commit();c.close();emit("executive.president","federation_boot",{"swarms":len(reg["swarms"]),"agents":reg["agent_count"]})
    return {"status":"online","swarms":len(reg["swarms"]),"agents":reg["agent_count"],"db":str(DB)}

def mission(title,mission_id=None,max_workers=24):
    reg=json.loads(REG.read_text(encoding="utf-8"));mid=mission_id or hashlib.sha256((title+str(time.time_ns())).encode()).hexdigest()[:12]
    now=time.time();c=conn();c.execute("INSERT OR REPLACE INTO missions(id,title,status,created,updated,meta) VALUES(?,?,?,?,?,?)",(mid,title,"running",now,now,"{}"));c.commit();c.close()
    swarms=[s["id"] for s in reg["swarms"]];reports={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_workers,len(swarms))) as ex:
        fut={ex.submit(swarm_report,s,mid):s for s in swarms}
        for f in concurrent.futures.as_completed(fut):
            s=fut[f]
            try:reports[s]=f.result()
            except Exception as e:reports[s]={"swarm":s,"status":"failed","error":repr(e)}
    actions=[queue_external(a,mid) for r in reports.values() for a in r.get("actions",[])]
    summary={"mission":mid,"title":title,"swarms_total":len(swarms),"swarms_complete":sum(1 for r in reports.values() if r.get("status")=="complete"),"agents_registered":reg["agent_count"],"external_actions":len(actions),"security_alerts":reports.get("security",{}).get("findings",{}).get("secret_like_files_count",0)}
    master=ART/f"{mid}.federation_summary.json";master.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8");register_artifact(mid,"executive",master,"summary")
    c=conn();c.execute("UPDATE missions SET status='complete',updated=?,meta=? WHERE id=?",(time.time(),json.dumps(summary,ensure_ascii=False),mid));c.commit();c.close();emit("executive.president","mission_complete",summary,mid)
    return summary

def status():
    c=conn();out={"agents_online":c.execute("SELECT count(*) c FROM agents WHERE status!='offline'").fetchone()["c"],"agent_states":{r["status"]:r["c"] for r in c.execute("SELECT status,count(*) c FROM agents GROUP BY status")},"missions":[dict(r) for r in c.execute("SELECT id,title,status,created,updated FROM missions ORDER BY created DESC LIMIT 20")],"artifacts":c.execute("SELECT count(*) c FROM artifacts").fetchone()["c"]};c.close()
    if ACTIONS.exists():out["pending_external_actions"]=[json.loads(x) for x in ACTIONS.read_text(encoding="utf-8").splitlines() if x.strip()][-50:]
    return out

def main():
    ap=argparse.ArgumentParser(prog="harum-federation");sp=ap.add_subparsers(dest="cmd",required=True);sp.add_parser("boot");sp.add_parser("status");m=sp.add_parser("mission");m.add_argument("title");m.add_argument("--id");m.add_argument("--workers",type=int,default=24);a=ap.parse_args()
    res=boot() if a.cmd=="boot" else mission(a.title,a.id,a.workers) if a.cmd=="mission" else status()
    print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
