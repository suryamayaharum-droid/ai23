#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sqlite3,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
DB=HERE/"runtime"/"nervous.db"
STACK=json.loads((HERE/"STANDARD_STACK.json").read_text())
SCHEMA="""PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT UNIQUE NOT NULL,ts REAL NOT NULL,origin TEXT NOT NULL,topic TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT NOT NULL,clock INTEGER NOT NULL,origin TEXT NOT NULL,updated REAL NOT NULL);
"""
def conn(): c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.executescript(SCHEMA);return c
def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def emit(origin,topic,payload):
    ts=time.time();eid=hashlib.sha256((origin+topic+stable(payload)+str(ts)).encode()).hexdigest();c=conn()
    c.execute("INSERT OR IGNORE INTO events(id,ts,origin,topic,payload) VALUES(?,?,?,?,?)",(eid,ts,origin,topic,stable(payload)));c.commit();c.close();return eid
def put(origin,key,value):
    c=conn();clock=c.execute("SELECT coalesce(max(clock),0)m FROM state").fetchone()["m"]+1
    c.execute("INSERT INTO state(key,value,clock,origin,updated) VALUES(?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,clock=excluded.clock,origin=excluded.origin,updated=excluded.updated",(key,stable(value),clock,origin,time.time()));c.commit();c.close();emit(origin,"state/"+key,{"clock":clock})
def boot():
    for x in STACK["core"]: put("nervous-system","capability/"+x,{"status":"canonical"})
    put("nervous-system","policy/default_stack",STACK);return status()
def status():
    c=conn();r={"events":c.execute("SELECT count(*)c FROM events").fetchone()["c"],"state_entries":c.execute("SELECT count(*)c FROM state").fetchone()["c"],"canonical_default":STACK["canonical_default"],"core_count":len(STACK["core"])};c.close();return r
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("cmd",choices=["boot","status"]);a=ap.parse_args();print(json.dumps(boot() if a.cmd=="boot" else status(),ensure_ascii=False,indent=2))
