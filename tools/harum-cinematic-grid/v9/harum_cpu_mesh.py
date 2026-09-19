#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, sqlite3, subprocess, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE=Path(__file__).resolve().parent
DB=HERE/"runtime"/"cpu_mesh.db"
TOKEN=os.environ.get("HARUM_MESH_TOKEN","local-dev-only")
SCHEMA="""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS workers(id TEXT PRIMARY KEY,cpus INTEGER NOT NULL,status TEXT NOT NULL,last_seen REAL NOT NULL,meta TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,kind TEXT NOT NULL,status TEXT NOT NULL,priority INTEGER NOT NULL,payload TEXT NOT NULL,worker TEXT,result TEXT,error TEXT,created REAL NOT NULL,updated REAL NOT NULL);
"""
def conn():
    c=sqlite3.connect(DB,timeout=30); c.row_factory=sqlite3.Row; c.executescript(SCHEMA); return c
def auth(h): return h.headers.get("Authorization")==f"Bearer {TOKEN}"
def send(h,code,obj):
    b=json.dumps(obj,ensure_ascii=False).encode(); h.send_response(code); h.send_header("Content-Type","application/json"); h.send_header("Content-Length",str(len(b))); h.end_headers(); h.wfile.write(b)
def body(h):
    n=int(h.headers.get("Content-Length","0")); return json.loads(h.rfile.read(n) or b"{}")
class H(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        if not auth(self): return send(self,401,{"error":"unauthorized"})
        if self.path=="/status":
            c=conn(); res={"workers":[dict(r) for r in c.execute("SELECT * FROM workers ORDER BY id")],"tasks":{r["status"]:r["c"] for r in c.execute("SELECT status,count(*) c FROM tasks GROUP BY status")}}; c.close(); return send(self,200,res)
        return send(self,404,{"error":"not found"})
    def do_POST(self):
        if not auth(self): return send(self,401,{"error":"unauthorized"})
        d=body(self); c=conn(); now=time.time()
        if self.path=="/register":
            c.execute("INSERT OR REPLACE INTO workers(id,cpus,status,last_seen,meta) VALUES(?,?,?,?,?)",(d["id"],int(d.get("cpus",1)),"online",now,json.dumps(d.get("meta",{})))); c.commit(); c.close(); return send(self,200,{"ok":True})
        if self.path=="/submit":
            tid=d.get("id") or hashlib.sha256((d["kind"]+json.dumps(d.get("payload",{}),sort_keys=True)+str(time.time_ns())).encode()).hexdigest()[:16]
            c.execute("INSERT OR IGNORE INTO tasks(id,kind,status,priority,payload,created,updated) VALUES(?,?,?,?,?,?,?)",(tid,d["kind"],"queued",int(d.get("priority",50)),json.dumps(d.get("payload",{})),now,now)); c.commit(); c.close(); return send(self,200,{"id":tid})
        if self.path=="/pull":
            c.execute("BEGIN IMMEDIATE"); r=c.execute("SELECT * FROM tasks WHERE status='queued' ORDER BY priority DESC,created LIMIT 1").fetchone()
            if not r: c.commit(); c.close(); return send(self,200,{"task":None})
            c.execute("UPDATE tasks SET status='running',worker=?,updated=? WHERE id=?",(d["worker"],now,r["id"])); c.execute("UPDATE workers SET last_seen=?,status='working' WHERE id=?",(now,d["worker"])); c.commit()
            out=dict(r); out["payload"]=json.loads(out["payload"]); c.close(); return send(self,200,{"task":out})
        if self.path=="/complete":
            st="complete" if d.get("ok",True) else "failed"; c.execute("UPDATE tasks SET status=?,result=?,error=?,updated=? WHERE id=?",(st,json.dumps(d.get("result")),d.get("error"),now,d["id"])); c.execute("UPDATE workers SET last_seen=?,status='online' WHERE id=?",(now,d["worker"])); c.commit(); c.close(); return send(self,200,{"ok":True})
        c.close(); return send(self,404,{"error":"not found"})
def req(url,path,payload):
    r=urllib.request.Request(url+path,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json","Authorization":f"Bearer {TOKEN}"})
    with urllib.request.urlopen(r,timeout=30) as x: return json.loads(x.read())
def run_task(t):
    k=t["kind"]; p=t["payload"]
    if k=="hash": return {"sha256":hashlib.sha256(Path(p["path"]).read_bytes()).hexdigest()}
    if k=="probe":
        x=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration,size","-of","json",p["path"]],capture_output=True,text=True,check=True); return json.loads(x.stdout)
    if k=="sleep": time.sleep(float(p.get("seconds",0.1))); return {"slept":p.get("seconds",0.1)}
    if k=="compile":
        x=subprocess.run([os.environ.get("PYTHON","python"),"-m","py_compile",p["path"]],capture_output=True,text=True); return {"returncode":x.returncode,"stderr":x.stderr[-500:]}
    raise ValueError(f"unsupported task {k}")
def worker(url,wid,max_tasks=0):
    req(url,"/register",{"id":wid,"cpus":os.cpu_count() or 1}); n=0
    while True:
        t=req(url,"/pull",{"worker":wid})["task"]
        if not t:
            if max_tasks and n>=max_tasks: break
            time.sleep(.15); continue
        try: r=run_task(t); req(url,"/complete",{"id":t["id"],"worker":wid,"ok":True,"result":r})
        except Exception as e: req(url,"/complete",{"id":t["id"],"worker":wid,"ok":False,"error":repr(e)})
        n+=1
        if max_tasks and n>=max_tasks: break
def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    c=sp.add_parser("coordinator"); c.add_argument("--host",default="127.0.0.1"); c.add_argument("--port",type=int,default=18765)
    w=sp.add_parser("worker"); w.add_argument("--url",default="http://127.0.0.1:18765"); w.add_argument("--id",required=True); w.add_argument("--max-tasks",type=int,default=0)
    s=sp.add_parser("submit"); s.add_argument("--url",default="http://127.0.0.1:18765"); s.add_argument("kind"); s.add_argument("payload_json"); s.add_argument("--id"); s.add_argument("--priority",type=int,default=50)
    st=sp.add_parser("status"); st.add_argument("--url",default="http://127.0.0.1:18765")
    a=ap.parse_args()
    if a.cmd=="coordinator": ThreadingHTTPServer((a.host,a.port),H).serve_forever()
    elif a.cmd=="worker": worker(a.url,a.id,a.max_tasks)
    elif a.cmd=="submit": print(json.dumps(req(a.url,"/submit",{"id":a.id,"kind":a.kind,"payload":json.loads(a.payload_json),"priority":a.priority}),indent=2))
    else:
        r=urllib.request.Request(a.url+"/status",headers={"Authorization":f"Bearer {TOKEN}"})
        with urllib.request.urlopen(r) as x: print(x.read().decode())
if __name__=="__main__":main()
