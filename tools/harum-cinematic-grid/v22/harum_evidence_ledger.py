#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sqlite3,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;DB=HERE/'runtime'/'evidence.db'
SCHEMA="PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS claims(id TEXT PRIMARY KEY,statement TEXT NOT NULL,status TEXT NOT NULL,source_type TEXT NOT NULL,source_ref TEXT,created REAL NOT NULL,updated REAL NOT NULL);"
def conn():c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.executescript(SCHEMA);return c
def add(statement,status='hypothesis',source_type='llm',source_ref=None):
    if status not in {'hypothesis','verified','rejected'}:raise ValueError('bad status')
    i=hashlib.sha256((statement+source_type+str(source_ref)).encode()).hexdigest()[:20];now=time.time();c=conn()
    c.execute('INSERT OR REPLACE INTO claims(id,statement,status,source_type,source_ref,created,updated) VALUES(?,?,?,?,?,?,?)',(i,statement,status,source_type,source_ref,now,now));c.commit();c.close();return i
def promotable(ids):
    c=conn();rows=[c.execute('SELECT status FROM claims WHERE id=?',(i,)).fetchone() for i in ids];c.close()
    return bool(rows) and all(r and r['status']=='verified' for r in rows)
if __name__=='__main__':
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True)
    a=sp.add_parser('add');a.add_argument('statement');a.add_argument('--status',default='hypothesis');a.add_argument('--source-type',default='llm');a.add_argument('--source-ref')
    p=sp.add_parser('promotable');p.add_argument('ids',nargs='+');x=ap.parse_args()
    print(json.dumps({'id':add(x.statement,x.status,x.source_type,x.source_ref)} if x.cmd=='add' else {'promotable':promotable(x.ids)},indent=2))