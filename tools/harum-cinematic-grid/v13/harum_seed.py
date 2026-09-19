#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sqlite3,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
DB=HERE/'runtime'/'seed.db'
SCHEMA="""PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY,value TEXT NOT NULL,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,id TEXT UNIQUE NOT NULL,ts REAL NOT NULL,topic TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,status TEXT NOT NULL,priority INTEGER NOT NULL,payload TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL);"""
def conn():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.executescript(SCHEMA);return c
def emit(topic,payload):
 ts=time.time();eid=hashlib.sha256((topic+json.dumps(payload,sort_keys=True)+str(ts)).encode()).hexdigest();c=conn();c.execute('INSERT OR IGNORE INTO events(id,ts,topic,payload) VALUES(?,?,?,?)',(eid,ts,topic,json.dumps(payload,ensure_ascii=False)));c.commit();c.close();return eid
def setv(k,v):
 c=conn();c.execute('INSERT INTO kv(key,value,updated) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated=excluded.updated',(k,json.dumps(v,ensure_ascii=False),time.time()));c.commit();c.close()
def bootstrap():
 setv('mode','hibernating-seed');setv('policy',{'zero_extra_spend':True,'gpu_required':False,'dedicated_server_required':False});emit('seed/bootstrap',{'version':'13.0'});return status()
def status():
 c=conn();out={'kv':{r['key']:json.loads(r['value']) for r in c.execute('SELECT key,value FROM kv')},'events':c.execute('SELECT count(*) c FROM events').fetchone()['c'],'tasks':{r['status']:r['c'] for r in c.execute('SELECT status,count(*) c FROM tasks GROUP BY status')}};c.close();return out
def export_snapshot(out):
 c=conn();snap={'version':'harum.seed.snapshot.v1','created':time.time(),'kv':[dict(r) for r in c.execute('SELECT * FROM kv ORDER BY key')],'events':[dict(r) for r in c.execute('SELECT * FROM events ORDER BY seq')],'tasks':[dict(r) for r in c.execute('SELECT * FROM tasks ORDER BY priority DESC,created')]};c.close();Path(out).write_text(json.dumps(snap,ensure_ascii=False,indent=2),encoding='utf-8');return out
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('bootstrap');sp.add_parser('status');e=sp.add_parser('export');e.add_argument('out');a=ap.parse_args();res=bootstrap() if a.cmd=='bootstrap' else status() if a.cmd=='status' else {'output':export_snapshot(a.out)};print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
