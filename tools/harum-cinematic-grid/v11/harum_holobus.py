#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

TOKEN='harum-organism-local'

def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def event_id(e): return hashlib.sha256(stable({k:e[k] for k in ('origin','counter','key','value')}).encode()).hexdigest()
def merkle(ids):
    hs=[hashlib.sha256(x.encode()).digest() for x in sorted(ids)]
    if not hs:return hashlib.sha256(b'').hexdigest()
    while len(hs)>1:
        if len(hs)%2:hs.append(hs[-1])
        hs=[hashlib.sha256(hs[i]+hs[i+1]).digest() for i in range(0,len(hs),2)]
    return hs[0].hex()

class Store:
    def __init__(self,path,node):
        self.path=Path(path);self.node=node;self.path.parent.mkdir(parents=True,exist_ok=True)
        c=self.conn();c.executescript("""
        CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,origin TEXT NOT NULL,counter INTEGER NOT NULL,key TEXT NOT NULL,value TEXT NOT NULL,created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS state(key TEXT PRIMARY KEY,value TEXT NOT NULL,counter INTEGER NOT NULL,origin TEXT NOT NULL,event_id TEXT NOT NULL,updated REAL NOT NULL);
        """);c.execute("INSERT OR IGNORE INTO meta(key,value) VALUES('counter','0')");c.commit();c.close()
    def conn(self):
        c=sqlite3.connect(self.path,timeout=30);c.row_factory=sqlite3.Row;return c
    def apply(self,e):
        e=dict(e);e['id']=e.get('id') or event_id(e);c=self.conn()
        val=stable(e['value']) if not isinstance(e['value'],str) else e['value']
        c.execute('INSERT OR IGNORE INTO events(id,origin,counter,key,value,created) VALUES(?,?,?,?,?,?)',(e['id'],e['origin'],int(e['counter']),e['key'],val,e.get('created',time.time())))
        r=c.execute('SELECT counter,origin FROM state WHERE key=?',(e['key'],)).fetchone()
        incoming=(int(e['counter']),e['origin']);current=(r['counter'],r['origin']) if r else (-1,'')
        if incoming>current:
            c.execute('INSERT INTO state(key,value,counter,origin,event_id,updated) VALUES(?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,counter=excluded.counter,origin=excluded.origin,event_id=excluded.event_id,updated=excluded.updated',(e['key'],val,int(e['counter']),e['origin'],e['id'],time.time()))
        c.commit();c.close();return e['id']
    def put(self,key,value):
        c=self.conn();counter=int(c.execute("SELECT value FROM meta WHERE key='counter'").fetchone()['value'])+1;c.execute("UPDATE meta SET value=? WHERE key='counter'",(str(counter),));c.commit();c.close()
        e={'origin':self.node,'counter':counter,'key':key,'value':value,'created':time.time()};e['id']=event_id(e);self.apply(e);return e
    def events(self):
        c=self.conn();rows=[dict(r) for r in c.execute('SELECT * FROM events ORDER BY created,id')];c.close()
        for r in rows:
            try:r['value']=json.loads(r['value'])
            except:pass
        return rows
    def inventory(self):
        es=self.events();return {'node':self.node,'root':merkle([e['id'] for e in es]),'ids':[e['id'] for e in es],'count':len(es)}
    def state(self):
        c=self.conn();rows=[dict(r) for r in c.execute('SELECT * FROM state ORDER BY key')];c.close()
        for r in rows:
            try:r['value']=json.loads(r['value'])
            except:pass
        return rows

def request(url,path,method='GET',payload=None):
    headers={'Authorization':'Bearer '+TOKEN};data=None
    if payload is not None:data=json.dumps(payload).encode();headers['Content-Type']='application/json'
    req=urllib.request.Request(url+path,data=data,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=10) as r:return json.loads(r.read())

def sync(store,peer):
    inv=request(peer,'/inventory');local=store.inventory()
    if inv['root']==local['root']:return {'changed':False,'root':local['root'],'received':0,'sent':0}
    remote_events=request(peer,'/events')['events'];local_ids=set(local['ids']);remote_ids=set(inv['ids']);received=0
    for e in remote_events:
        if e['id'] not in local_ids:store.apply(e);received+=1
    missing=[e for e in store.events() if e['id'] not in remote_ids]
    sent=0
    if missing:request(peer,'/events','POST',{'events':missing});sent=len(missing)
    return {'changed':True,'root':store.inventory()['root'],'received':received,'sent':sent}

def serve(store,host,port):
    class H(BaseHTTPRequestHandler):
        def log_message(self,*args): pass
        def auth(self): return self.headers.get('Authorization')=='Bearer '+TOKEN
        def sendj(self,code,obj):
            b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
        def do_GET(self):
            if not self.auth():return self.sendj(401,{'error':'unauthorized'})
            if self.path=='/inventory':return self.sendj(200,store.inventory())
            if self.path=='/events':return self.sendj(200,{'events':store.events()})
            if self.path=='/state':return self.sendj(200,{'state':store.state(),'inventory':store.inventory()})
            return self.sendj(404,{'error':'not found'})
        def do_POST(self):
            if not self.auth():return self.sendj(401,{'error':'unauthorized'})
            n=int(self.headers.get('Content-Length','0'));d=json.loads(self.rfile.read(n) or b'{}')
            if self.path=='/put':return self.sendj(200,store.put(d['key'],d['value']))
            if self.path=='/events':
                ids=[store.apply(e) for e in d.get('events',[])];return self.sendj(200,{'applied':len(ids)})
            return self.sendj(404,{'error':'not found'})
    ThreadingHTTPServer((host,port),H).serve_forever()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--db',required=True);ap.add_argument('--node',required=True);sp=ap.add_subparsers(dest='cmd',required=True)
    s=sp.add_parser('serve');s.add_argument('--host',default='127.0.0.1');s.add_argument('--port',type=int,required=True)
    p=sp.add_parser('put');p.add_argument('key');p.add_argument('value_json')
    y=sp.add_parser('sync');y.add_argument('peer')
    sp.add_parser('inventory');sp.add_parser('state')
    a=ap.parse_args();st=Store(a.db,a.node)
    if a.cmd=='serve':return serve(st,a.host,a.port)
    if a.cmd=='put':res=st.put(a.key,json.loads(a.value_json))
    elif a.cmd=='sync':res=sync(st,a.peer)
    elif a.cmd=='inventory':res=st.inventory()
    else:res={'state':st.state(),'inventory':st.inventory()}
    print(json.dumps(res,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
