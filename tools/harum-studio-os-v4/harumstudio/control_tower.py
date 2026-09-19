import json,sqlite3
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlparse
HTML="""<!doctype html><meta charset=utf-8><title>HARUM Studio Control Tower</title><style>body{font-family:system-ui;background:#0b0b0b;color:#eee8dc;margin:32px}pre{padding:16px;border:1px solid #3a352c}</style><h1>HARUM STUDIO OS — Control Tower</h1><pre id=a>loading</pre><script>async function x(){a.textContent=JSON.stringify(await(await fetch('/api/status')).json(),null,2)}x();setInterval(x,5000)</script>"""
def serve(db_path,host="127.0.0.1",port=8787):
 class H(BaseHTTPRequestHandler):
  def do_GET(self):
   if urlparse(self.path).path=="/":
    d=HTML.encode();self.send_response(200);self.end_headers();self.wfile.write(d);return
   c=sqlite3.connect(db_path)
   out={}
   for t in ["projects","sequences","scenes","shots","tasks","assets","workers","jobs","events"]:
    try:out[t]=c.execute(f"select count(*) from {t}").fetchone()[0]
    except:pass
   c.close();d=json.dumps(out).encode();self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(d)
 ThreadingHTTPServer((host,port),H).serve_forever()
