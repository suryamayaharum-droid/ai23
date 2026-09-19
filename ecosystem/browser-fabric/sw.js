const CACHE="harum-browser-fabric-v3";
const CORE=[
  "./","./index.html","./manifest.webmanifest",
  "./src/app.js","./src/idb.js","./src/mesh.js","./src/provision.js",
  "./src/python.js","./src/py-worker.js","./src/webllm.js","./src/llm-worker.js",
  "./src/semantic.js","./src/semantic-worker.js","./src/benchmark.js",
  "./src/task-runtime.js","./src/crdt.js","./src/p2p.js","./src/federation.js",
  "./src/scheduler.js","./src/linux.js"
];
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE))));
self.addEventListener("activate",e=>e.waitUntil(
  caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
    .then(()=>self.clients.claim())
));
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(r=>{
    const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return r;
  })));
});