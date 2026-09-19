#!/usr/bin/env python3
from __future__ import annotations
import argparse, hmac, json, os, queue, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

TOKEN=os.environ.get("HARUM_MESH_TOKEN","")
TASKS=queue.Queue()
RESULTS={}
CAPABILITIES={"python","shell","hash","inventory","qc","checkpoint","json"}

def authorized(headers)->bool:
    if not TOKEN:
        return False
    supplied=headers.get("Authorization","")
    if not supplied.startswith("Bearer "):
        return False
    return hmac.compare_digest(supplied[7:],TOKEN)

class Handler(BaseHTTPRequestHandler):
    server_version="HarumMesh/1.0"

    def _json(self,status:int,payload:Any):
        raw=json.dumps(payload,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path=="/health":
            return self._json(200,{"status":"ok","queue":TASKS.qsize(),"results":len(RESULTS)})
        if self.path=="/capabilities":
            return self._json(200,{"capabilities":sorted(CAPABILITIES)})
        if not authorized(self.headers):
            return self._json(401,{"error":"unauthorized"})
        if self.path=="/pull":
            try:
                task=TASKS.get_nowait()
            except queue.Empty:
                return self._json(204,{})
            return self._json(200,task)
        if self.path.startswith("/result/"):
            rid=self.path.split("/")[-1]
            if rid not in RESULTS:
                return self._json(404,{"error":"not_found"})
            return self._json(200,RESULTS[rid])
        return self._json(404,{"error":"not_found"})

    def do_POST(self):
        if not authorized(self.headers):
            return self._json(401,{"error":"unauthorized"})
        try:
            n=int(self.headers.get("Content-Length","0"))
            payload=json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400,{"error":"invalid_json"})
        if self.path=="/push":
            task={
                "id":payload.get("id") or str(uuid.uuid4()),
                "required":payload.get("required",[]),
                "payload":payload.get("payload",{}),
                "created_at":int(time.time())
            }
            TASKS.put(task)
            return self._json(202,task)
        if self.path=="/complete":
            rid=payload.get("id")
            if not rid:
                return self._json(400,{"error":"id_required"})
            RESULTS[rid]={
                "id":rid,
                "output":payload.get("output"),
                "worker":payload.get("worker"),
                "completed_at":int(time.time())
            }
            return self._json(200,RESULTS[rid])
        return self._json(404,{"error":"not_found"})

    def log_message(self,format,*args):
        return

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--host",default="127.0.0.1")
    ap.add_argument("--port",type=int,default=8765)
    args=ap.parse_args()
    if not TOKEN:
        raise SystemExit("HARUM_MESH_TOKEN must be set in the environment")
    srv=ThreadingHTTPServer((args.host,args.port),Handler)
    print(json.dumps({"listening":f"http://{args.host}:{args.port}","capabilities":sorted(CAPABILITIES)}))
    srv.serve_forever()

if __name__=="__main__":
    main()
