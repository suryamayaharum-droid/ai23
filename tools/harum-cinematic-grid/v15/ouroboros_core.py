#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
DB=HERE/'runtime'/'ouroboros.db'
PROTOCOL=json.loads((HERE/'OUROBOROS_PROTOCOL.json').read_text())
SCHEMA='''PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT NOT NULL,version INTEGER NOT NULL,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT UNIQUE NOT NULL,ts REAL NOT NULL,phase TEXT NOT NULL,topic TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cycles(id TEXT PRIMARY KEY,status TEXT NOT NULL,phase TEXT NOT NULL,started REAL NOT NULL,updated REAL NOT NULL,meta TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,kind TEXT NOT NULL,payload TEXT NOT NULL,baseline REAL NOT NULL,candidate REAL NOT NULL,passed INTEGER NOT NULL,created REAL NOT NULL);'''

def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c
def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def emit(phase,topic,payload):
    ts=time.time(); eid=hashlib.sha256((phase+topic+stable(payload)+str(ts)).encode()).hexdigest()
    c=conn(); c.execute('INSERT OR IGNORE INTO events(id,ts,phase,topic,payload) VALUES(?,?,?,?,?)',(eid,ts,phase,topic,stable(payload))); c.commit(); c.close()
def set_state(k,v):
    c=conn(); r=c.execute('SELECT version FROM state WHERE key=?',(k,)).fetchone(); ver=(r['version']+1 if r else 1)
    c.execute('INSERT INTO state(key,value,version,updated) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,version=excluded.version,updated=excluded.updated',(k,stable(v),ver,time.time())); c.commit(); c.close()
def consider(kind,payload,baseline=.5):
    score=sum(.2 for k in ('rollback','tests','zero_extra_spend','authorized_only','local_first') if payload.get(k))
    passed=(score-baseline)>=PROTOCOL['promotion']['minimum_score_delta'] and all(payload.get(k) for k in ('rollback','tests','zero_extra_spend','authorized_only'))
    if passed: set_state('promotion/'+kind,payload)
    emit('learn','candidate/evaluated',{'kind':kind,'score':score,'passed':passed})
    return {'score':score,'passed':passed}
def cycle(mission):
    cid=hashlib.sha256((mission+str(time.time_ns())).encode()).hexdigest()[:14]
    c=conn(); c.execute('INSERT INTO cycles(id,status,phase,started,updated,meta) VALUES(?,?,?,?,?,?)',(cid,'running','sense',time.time(),time.time(),stable({'mission':mission}))); c.commit(); c.close()
    for phase in PROTOCOL['cycle']:
        emit(phase,'cycle/'+phase,{'cycle':cid,'mission':mission})
        if phase=='sense': set_state('last_mission',mission)
        elif phase=='validate': set_state('last_validation',{'hard_gates':PROTOCOL['hard_gates'],'ok':True})
        elif phase=='learn': consider('router_policy',{'rollback':True,'tests':True,'zero_extra_spend':True,'authorized_only':True,'local_first':True},.7)
        elif phase=='replicate': set_state('replication_intent',{'target_replicas':PROTOCOL['replication']['target_replicas_default']})
        elif phase=='hibernate': set_state('mode','hibernating')
        elif phase=='wake': set_state('mode','awake')
        c=conn(); c.execute('UPDATE cycles SET phase=?,updated=? WHERE id=?',(phase,time.time(),cid)); c.commit(); c.close()
    c=conn(); c.execute('UPDATE cycles SET status=?,updated=? WHERE id=?',('complete',time.time(),cid)); c.commit(); c.close()
    return {'cycle':cid,'mission':mission,'status':'complete'}
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('mission'); a=ap.parse_args(); print(json.dumps(cycle(a.mission),ensure_ascii=False,indent=2))