#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, socket, sqlite3, struct, time
from pathlib import Path
from harum_identity import sign, verify
from harum_capability import check as capability_check

MAX_FRAME=2*1024*1024
def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def recv_exact(sock,n):
    out=bytearray()
    while len(out)<n:
        b=sock.recv(n-len(out))
        if not b: raise EOFError("connection closed")
        out.extend(b)
    return bytes(out)
def send_frame(sock,obj):
    b=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()
    if len(b)>MAX_FRAME: raise ValueError("frame too large")
    sock.sendall(struct.pack("!I",len(b))+b)
def recv_frame(sock):
    n=struct.unpack("!I",recv_exact(sock,4))[0]
    if n>MAX_FRAME: raise ValueError("frame too large")
    return json.loads(recv_exact(sock,n))

class Circuit:
    def __init__(self,state_dir,server_identity):
        self.state=Path(state_dir); self.state.mkdir(parents=True,exist_ok=True)
        self.cas=self.state/"cas"/"objects"; self.cas.mkdir(parents=True,exist_ok=True)
        self.db=self.state/"circuit.db"; self.identity=server_identity
        c=self.conn(); c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS tasks(
          task_id TEXT PRIMARY KEY, issuer TEXT NOT NULL, kind TEXT NOT NULL,
          request TEXT NOT NULL, receipt TEXT NOT NULL, result_sha TEXT NOT NULL,
          created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL,
          topic TEXT NOT NULL, payload TEXT NOT NULL);
        """); c.commit(); c.close()
    def conn(self):
        c=sqlite3.connect(self.db,timeout=30); c.row_factory=sqlite3.Row; return c
    def event(self,topic,payload):
        c=self.conn(); c.execute("INSERT INTO events(ts,topic,payload) VALUES(?,?,?)",
          (time.time(),topic,json.dumps(payload,ensure_ascii=False))); c.commit(); c.close()
    def cas_put(self,obj):
        b=stable(obj); d=sha_bytes(b); p=self.cas/d[:2]/d; p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists(): p.write_bytes(b)
        return {"sha256":d,"bytes":len(b),"path":str(p)}
    def execute(self,kind,args):
        if kind=="sha256_text":
            text=str(args.get("text",""))
            return {"sha256":hashlib.sha256(text.encode()).hexdigest(),"length":len(text)}
        if kind=="canonical_json_hash":
            value=args.get("value")
            return {"sha256":sha_bytes(stable(value)),"canonical_bytes":len(stable(value))}
        raise PermissionError("task kind not allowlisted")
    def handle(self,envelope):
        if envelope.get("type")!="harum.task.v1": return {"ok":False,"error":"wrong_envelope_type"}
        signed_task=envelope.get("signed_task",{})
        sv=verify(signed_task)
        if not sv.get("valid"): return {"ok":False,"error":"bad_task_signature","detail":sv}
        p=signed_task.get("payload",{})
        if p.get("type")!="harum.task.payload.v1": return {"ok":False,"error":"wrong_payload_type"}
        if time.time()>float(p.get("expires",0)): return {"ok":False,"error":"task_expired"}
        task_id=p.get("task_id")
        c=self.conn(); row=c.execute("SELECT receipt FROM tasks WHERE task_id=?",(task_id,)).fetchone(); c.close()
        if row:
            self.event("task/replay",{"task_id":task_id})
            return {"ok":True,"replayed":True,"signed_receipt":json.loads(row["receipt"])}
        cap_check=capability_check(envelope.get("capability",{}),sv["issuer"],"execute",f"harum://tasks/{p.get('kind')}")
        if not cap_check.get("allowed"): return {"ok":False,"error":"capability_denied","detail":cap_check}
        try: result=self.execute(p.get("kind"),p.get("args",{}))
        except Exception as e: return {"ok":False,"error":"execution_denied","detail":type(e).__name__+":"+str(e)}
        cas=self.cas_put({"task_id":task_id,"result":result})
        receipt_payload={"type":"harum.receipt.v1","task_id":task_id,"request_issuer":sv["issuer"],
          "kind":p.get("kind"),"result":result,"cas":cas,"completed":time.time()}
        signed_receipt=sign(self.identity,receipt_payload)
        c=self.conn(); c.execute("INSERT INTO tasks(task_id,issuer,kind,request,receipt,result_sha,created) VALUES(?,?,?,?,?,?,?)",
          (task_id,sv["issuer"],p.get("kind"),json.dumps(envelope,ensure_ascii=False),
           json.dumps(signed_receipt,ensure_ascii=False),cas["sha256"],time.time())); c.commit(); c.close()
        self.event("task/complete",{"task_id":task_id,"result_sha":cas["sha256"]})
        return {"ok":True,"replayed":False,"signed_receipt":signed_receipt}

def serve(host,port,state_dir,identity):
    c=Circuit(state_dir,identity)
    s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind((host,port)); s.listen(20)
    print(json.dumps({"listening":s.getsockname()[1]}),flush=True)
    while True:
        conn,_=s.accept()
        with conn:
            try:res=c.handle(recv_frame(conn))
            except Exception as e:res={"ok":False,"error":"server_exception","detail":type(e).__name__+":"+str(e)}
            send_frame(conn,res)

def request(host,port,envelope):
    with socket.create_connection((host,port),timeout=5) as s:
        send_frame(s,envelope); return recv_frame(s)

def build_task(client_identity,capability,kind,args,ttl=120,nonce=None):
    nonce=nonce or os.urandom(12).hex()
    material={"kind":kind,"args":args,"nonce":nonce}; task_id=sha_bytes(stable(material))
    payload={"type":"harum.task.payload.v1","task_id":task_id,"kind":kind,"args":args,
      "nonce":nonce,"created":time.time(),"expires":time.time()+ttl}
    return {"type":"harum.task.v1","signed_task":sign(client_identity,payload),"capability":capability}
