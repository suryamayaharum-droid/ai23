#!/usr/bin/env python3
from __future__ import annotations
import argparse,hmac,json,os,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from typing import Any

from brain_router import select_brains
from llama_brain import LlamaCppBrain
from assembly import CortexAssembly

API_KEY=os.getenv("HARUM_CORTEX_API_KEY","")

def authorized(headers)->bool:
    if not API_KEY:
        return True
    auth=headers.get("Authorization","")
    return auth.startswith("Bearer ") and hmac.compare_digest(auth[7:],API_KEY)

def messages_to_prompt(messages:list[dict[str,Any]]):
    system=[]
    turns=[]
    for m in messages:
        role=m.get("role","user")
        content=m.get("content","")
        if isinstance(content,list):
            content="\n".join(
              x.get("text","") for x in content
              if isinstance(x,dict) and x.get("type")=="text"
            )
        if role=="system":system.append(str(content))
        else:turns.append(f"{role.upper()}: {content}")
    return "\n".join(system),"\n".join(turns)

class Handler(BaseHTTPRequestHandler):
    server_version="HarumCortex/1.0"

    def reply(self,status:int,obj:Any):
        raw=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers();self.wfile.write(raw)

    def do_GET(self):
        if self.path=="/health":
            return self.reply(200,{"status":"ok","provider":"harum-cortex","local":True})
        if self.path=="/v1/models":
            plan=select_brains("default")
            data=[
              {"id":"harum-cortex:auto","object":"model","owned_by":"harum"},
              {"id":"harum-cortex:council","object":"model","owned_by":"harum"}
            ]+[{"id":x,"object":"model","owned_by":"local-gguf"} for x in plan["brains"]]
            return self.reply(200,{"object":"list","data":data})
        return self.reply(404,{"error":{"message":"not found"}})

    def do_POST(self):
        if not authorized(self.headers):
            return self.reply(401,{"error":{"message":"unauthorized"}})
        if self.path!="/v1/chat/completions":
            return self.reply(404,{"error":{"message":"not found"}})
        try:
            n=int(self.headers.get("Content-Length","0"))
            body=json.loads(self.rfile.read(n) or b"{}")
            model=body.get("model","harum-cortex:auto")
            system,prompt=messages_to_prompt(body.get("messages",[]))
            max_tokens=min(int(body.get("max_tokens",body.get("max_completion_tokens",512))),2048)
            temp=float(body.get("temperature",0.2))

            if model=="harum-cortex:council":
                result=CortexAssembly("default").deliberate(prompt,system)
                final=result.get("final",{})
                text=final.get("text") or json.dumps(result,ensure_ascii=False)
            else:
                plan=select_brains("default")
                wanted=model.split(":",1)[1] if model.startswith("harum-cortex:") else model
                chosen=None
                for m in plan["models"]:
                    if wanted in {"auto",m["id"]}:
                        chosen=m;break
                if chosen is None:
                    chosen=plan["models"][0]
                r=LlamaCppBrain(chosen).infer(
                    system or "You are a local HARUM cognitive cell.",
                    prompt,max_tokens=max_tokens,temperature=temp,seed=42
                )
                text=r["text"]

            now=int(time.time())
            return self.reply(200,{
              "id":"chatcmpl-"+uuid.uuid4().hex,
              "object":"chat.completion",
              "created":now,
              "model":model,
              "choices":[{
                "index":0,
                "message":{"role":"assistant","content":text},
                "finish_reason":"stop"
              }],
              "usage":{"prompt_tokens":0,"completion_tokens":0,"total_tokens":0}
            })
        except Exception as exc:
            return self.reply(500,{"error":{"message":f"{type(exc).__name__}: {exc}"}})

    def log_message(self,format,*args):
        return

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--host",default="127.0.0.1")
    ap.add_argument("--port",type=int,default=8899)
    args=ap.parse_args()
    if args.host not in {"127.0.0.1","localhost","::1"} and not API_KEY:
        raise SystemExit("HARUM_CORTEX_API_KEY required when binding beyond localhost")
    server=ThreadingHTTPServer((args.host,args.port),Handler)
    print(json.dumps({
      "provider":"harum-cortex","url":f"http://{args.host}:{args.port}/v1",
      "auth_required":bool(API_KEY)
    }))
    server.serve_forever()

if __name__=="__main__":
    main()
