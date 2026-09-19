#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3, time, uuid
from pathlib import Path

HERE=Path(__file__).resolve().parent
DB=HERE/"runtime"/"event_horizon.db"
SCHEMA="""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS workflows(id TEXT PRIMARY KEY,title TEXT NOT NULL,status TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL,version INTEGER NOT NULL DEFAULT 1,meta TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS steps(id TEXT PRIMARY KEY,workflow TEXT NOT NULL,name TEXT NOT NULL,status TEXT NOT NULL,run_at REAL NOT NULL,lease_until REAL,worker TEXT,retries INTEGER NOT NULL DEFAULT 0,max_retries INTEGER NOT NULL DEFAULT 5,deps TEXT NOT NULL,payload TEXT NOT NULL,result TEXT,error TEXT,idempotency TEXT NOT NULL UNIQUE,created REAL NOT NULL,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,ts REAL NOT NULL,workflow TEXT NOT NULL,entity TEXT NOT NULL,event TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS snapshots(workflow TEXT PRIMARY KEY,seq INTEGER NOT NULL,state TEXT NOT NULL,created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS dead_letters(id TEXT PRIMARY KEY,workflow TEXT NOT NULL,step TEXT NOT NULL,error TEXT NOT NULL,payload TEXT NOT NULL,created REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_steps_due ON steps(status,run_at,lease_until);
"""
def conn():
    c=sqlite3.connect(DB,timeout=30); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c
def ev(c,wf,entity,event,payload):
    c.execute("INSERT INTO events(ts,workflow,entity,event,payload) VALUES(?,?,?,?,?)",(time.time(),wf,entity,event,json.dumps(payload,ensure_ascii=False)))
def create_workflow(title,steps,wid=None):
    wid=wid or uuid.uuid4().hex[:14]; now=time.time(); c=conn()
    c.execute("INSERT OR IGNORE INTO workflows(id,title,status,created,updated,meta) VALUES(?,?,?,?,?,?)",(wid,title,"running",now,now,"{}"))
    for s in steps:
        idem=s.get("idempotency") or hashlib.sha256((wid+s["id"]+json.dumps(s.get("payload",{}),sort_keys=True)).encode()).hexdigest()
        c.execute("""INSERT OR IGNORE INTO steps(id,workflow,name,status,run_at,max_retries,deps,payload,idempotency,created,updated)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?)""",(s["id"],wid,s.get("name",s["id"]),"queued",s.get("run_at",now),s.get("max_retries",5),json.dumps(s.get("deps",[])),json.dumps(s.get("payload",{}),ensure_ascii=False),idem,now,now))
    ev(c,wid,wid,"workflow_created",{"steps":[s["id"] for s in steps]}); c.commit(); c.close(); return wid
def recover_expired(c):
    now=time.time(); rows=list(c.execute("SELECT id,workflow FROM steps WHERE status='running' AND lease_until IS NOT NULL AND lease_until<?",(now,)))
    for r in rows:
        c.execute("UPDATE steps SET status='queued',worker=NULL,lease_until=NULL,updated=? WHERE id=?",(now,r["id"])); ev(c,r["workflow"],r["id"],"lease_recovered",{})
    return len(rows)
def claim(worker,lease_seconds=120):
    c=conn(); c.execute("BEGIN IMMEDIATE"); recover_expired(c); now=time.time()
    rows=list(c.execute("SELECT * FROM steps WHERE status='queued' AND run_at<=? ORDER BY run_at,created",(now,)))
    for r in rows:
        deps=json.loads(r["deps"])
        if deps:
            q="SELECT count(*) c FROM steps WHERE workflow=? AND id IN (%s) AND status='complete'"%(",".join("?"*len(deps)))
            if c.execute(q,[r["workflow"],*deps]).fetchone()["c"]!=len(deps): continue
        c.execute("UPDATE steps SET status='running',worker=?,lease_until=?,updated=? WHERE id=?",(worker,now+lease_seconds,now,r["id"]))
        ev(c,r["workflow"],r["id"],"step_claimed",{"worker":worker,"lease_seconds":lease_seconds}); c.commit()
        out=dict(r); out["payload"]=json.loads(out["payload"]); out["deps"]=deps; c.close(); return out
    c.commit(); c.close(); return None
def complete(step_id,result):
    c=conn(); r=c.execute("SELECT * FROM steps WHERE id=?",(step_id,)).fetchone()
    c.execute("UPDATE steps SET status='complete',result=?,lease_until=NULL,updated=? WHERE id=?",(json.dumps(result,ensure_ascii=False),time.time(),step_id))
    ev(c,r["workflow"],step_id,"step_complete",result)
    remaining=c.execute("SELECT count(*) c FROM steps WHERE workflow=? AND status!='complete'",(r["workflow"],)).fetchone()["c"]
    if remaining==0:
        c.execute("UPDATE workflows SET status='complete',updated=? WHERE id=?",(time.time(),r["workflow"])); ev(c,r["workflow"],r["workflow"],"workflow_complete",{})
    c.commit(); c.close()
def fail(step_id,error):
    c=conn(); r=c.execute("SELECT * FROM steps WHERE id=?",(step_id,)).fetchone(); retries=r["retries"]+1; now=time.time()
    if retries>r["max_retries"]:
        c.execute("UPDATE steps SET status='dead',error=?,lease_until=NULL,retries=?,updated=? WHERE id=?",(error,retries,now,step_id))
        c.execute("INSERT OR REPLACE INTO dead_letters(id,workflow,step,error,payload,created) VALUES(?,?,?,?,?,?)",(step_id,r["workflow"],step_id,error,r["payload"],now))
        ev(c,r["workflow"],step_id,"step_dead_letter",{"error":error,"retries":retries})
    else:
        delay=min(3600,2**retries)
        c.execute("UPDATE steps SET status='queued',error=?,lease_until=NULL,worker=NULL,retries=?,run_at=?,updated=? WHERE id=?",(error,retries,now+delay,now,step_id))
        ev(c,r["workflow"],step_id,"step_retry_scheduled",{"error":error,"retries":retries,"delay":delay})
    c.commit(); c.close()
def snapshot(wf):
    c=conn(); state={"workflow":dict(c.execute("SELECT * FROM workflows WHERE id=?",(wf,)).fetchone()),"steps":[dict(r) for r in c.execute("SELECT id,name,status,run_at,worker,retries,result,error FROM steps WHERE workflow=? ORDER BY created",(wf,))]}
    seq=c.execute("SELECT coalesce(max(seq),0) m FROM events WHERE workflow=?",(wf,)).fetchone()["m"]
    c.execute("INSERT OR REPLACE INTO snapshots(workflow,seq,state,created) VALUES(?,?,?,?)",(wf,seq,json.dumps(state,ensure_ascii=False),time.time())); c.commit(); c.close(); return state
def replay(wf):
    c=conn(); rows=[dict(r) for r in c.execute("SELECT seq,ts,entity,event,payload FROM events WHERE workflow=? ORDER BY seq",(wf,))]; c.close()
    for r in rows:r["payload"]=json.loads(r["payload"])
    return rows
def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    cr=sp.add_parser("create"); cr.add_argument("spec")
    cl=sp.add_parser("claim"); cl.add_argument("--worker",required=True); cl.add_argument("--lease",type=int,default=120)
    co=sp.add_parser("complete"); co.add_argument("step"); co.add_argument("result_json")
    fa=sp.add_parser("fail"); fa.add_argument("step"); fa.add_argument("error")
    ss=sp.add_parser("snapshot"); ss.add_argument("workflow")
    rp=sp.add_parser("replay"); rp.add_argument("workflow")
    a=ap.parse_args()
    if a.cmd=="create":
        spec=json.loads(Path(a.spec).read_text()); res={"workflow":create_workflow(spec["title"],spec["steps"],spec.get("id"))}
    elif a.cmd=="claim": res=claim(a.worker,a.lease)
    elif a.cmd=="complete": complete(a.step,json.loads(a.result_json)); res={"ok":True}
    elif a.cmd=="fail": fail(a.step,a.error); res={"ok":True}
    elif a.cmd=="snapshot": res=snapshot(a.workflow)
    else: res=replay(a.workflow)
    print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
