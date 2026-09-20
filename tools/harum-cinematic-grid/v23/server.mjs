import http from 'http';
import fs from 'fs';
import path from 'path';
import {fileURLToPath} from 'url';
const root=path.dirname(fileURLToPath(import.meta.url));
const mime={'.html':'text/html','.js':'text/javascript','.wasm':'application/wasm','.gguf':'application/octet-stream','.json':'application/json'};
const port=Number(process.env.PORT||4173);
function safe(url){
  const pathname=decodeURIComponent(new URL(url,'http://x').pathname);
  const mapped=pathname==='/'?'/web/index.html':pathname;
  const full=path.resolve(root,'.'+mapped);
  return full.startsWith(root)?full:null;
}
http.createServer((req,res)=>{
  const f=safe(req.url);
  res.setHeader('Cross-Origin-Opener-Policy','same-origin');
  res.setHeader('Cross-Origin-Embedder-Policy','require-corp');
  res.setHeader('Cross-Origin-Resource-Policy','same-origin');
  res.setHeader('Cache-Control','no-store');
  if(!f||!fs.existsSync(f)||fs.statSync(f).isDirectory()){res.writeHead(404);res.end('not found');return;}
  res.setHeader('Content-Type',mime[path.extname(f)]||'application/octet-stream');
  res.setHeader('Content-Length',fs.statSync(f).size);
  fs.createReadStream(f).pipe(res);
}).listen(port,'127.0.0.1',()=>console.log(JSON.stringify({listening:port})));