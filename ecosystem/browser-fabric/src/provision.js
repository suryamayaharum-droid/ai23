export async function detectCapabilities(){
  const storage=await navigator.storage?.estimate?.().catch(()=>({}))||{};
  let webgpu=false,adapterInfo=null;
  if(navigator.gpu){
    try{
      const adapter=await navigator.gpu.requestAdapter();
      webgpu=!!adapter;
      if(adapter?.info) adapterInfo={vendor:adapter.info.vendor,architecture:adapter.info.architecture};
    }catch{}
  }
  return {
    secureContext:isSecureContext,
    serviceWorker:"serviceWorker" in navigator,
    webWorker:"Worker" in window,
    sharedWorker:"SharedWorker" in window,
    broadcastChannel:"BroadcastChannel" in window,
    webLocks:!!navigator.locks,
    indexedDB:"indexedDB" in window,
    wasm:typeof WebAssembly==="object",
    webgpu,
    adapterInfo,
    logicalCores:navigator.hardwareConcurrency||null,
    deviceMemoryGB:navigator.deviceMemory||null,
    storageQuota:storage.quota||null,
    storageUsage:storage.usage||null,
    online:navigator.onLine
  };
}
export async function makeNode(){
  const caps=await detectCapabilities();
  let id=localStorage.getItem("harum-browser-node-id");
  if(!id){id="browser:"+crypto.randomUUID();localStorage.setItem("harum-browser-node-id",id);}
  return {
    id,
    kind:"browser-cell",
    origin:location.origin,
    capabilities:[
      caps.wasm&&"wasm",
      caps.webWorker&&"web_worker",
      caps.webgpu&&"webgpu_llm",
      caps.indexedDB&&"local_state",
      caps.broadcastChannel&&"local_bus",
      caps.webLocks&&"leader_election",
      "offline_checkpoint"
    ].filter(Boolean),
    resources:{cores:caps.logicalCores,memoryGB:caps.deviceMemoryGB,webgpu:caps.webgpu},
    bootedAt:Date.now()
  };
}