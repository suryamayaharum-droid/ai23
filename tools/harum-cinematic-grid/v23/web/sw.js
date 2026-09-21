const CACHE='harum-browser-brain-v23-shell';
const SHELL=['/','/web/index.html','/web/app.js','/web/sw.js'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL))));
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(u.pathname==='/model.gguf') return;
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(x=>{
    const y=x.clone();caches.open(CACHE).then(c=>c.put(e.request,y));return x;
  })));
});