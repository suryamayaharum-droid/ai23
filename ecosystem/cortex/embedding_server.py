#!/usr/bin/env python3
from __future__ import annotations
import os,shutil,socket,subprocess,time,urllib.request

def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p

def start_embedding_server():
    server=os.getenv("LLAMA_SERVER") or shutil.which("llama-server")
    if not server:raise RuntimeError("llama-server not installed")
    port=free_port()
    cmd=[
      server,
      "-hf","nomic-ai/nomic-embed-text-v1.5-GGUF:Q4_K_M",
      "--embedding",
      "--host","127.0.0.1",
      "--port",str(port),
      "--no-ui"
    ]
    proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    url=f"http://127.0.0.1:{port}"
    deadline=time.time()+300
    while time.time()<deadline:
        if proc.poll() is not None:
            out=(proc.stdout.read() if proc.stdout else "")[-3000:]
            raise RuntimeError("embedding server exited: "+out)
        try:
            with urllib.request.urlopen(url+"/health",timeout=2) as r:
                if r.status==200:return proc,url
        except Exception:time.sleep(1)
    proc.terminate()
    raise TimeoutError("embedding server startup timed out")
