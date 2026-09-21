import { Wllama } from '/node_modules/@wllama/wllama/esm/index.js';

const MODEL_URL='/model.gguf';
const WASM='/node_modules/@wllama/wllama/esm/wasm/wllama.wasm';
const status=document.querySelector('#status');

async function makeBrain() {
  const w=new Wllama({default:WASM},{allowOffline:true,parallelDownloads:2,suppressNativeLog:true});
  await w.loadModelFromUrl(MODEL_URL,{n_ctx:256,n_threads:2,n_gpu_layers:0});
  return w;
}
async function infer(w,prompt) {
  const r=await w.createChatCompletion({
    messages:[
      {role:'system',content:'You are a tiny local Harum browser sentinel. Answer in one short sentence.'},
      {role:'user',content:prompt}
    ],
    temperature:0,max_tokens:24
  });
  const text=(r.choices?.[0]?.message?.content||'').trim();
  if(!text) throw new Error('empty inference');
  return text;
}
window.harumbrowser={
  async seed(){
    const w=await makeBrain();
    const text=await infer(w,'Say that local browser CPU inference is active.');
    const models=await w.modelManager.getModels();
    await w.exit();
    const out={ok:true,mode:'seed',text,cached_models:models.length,cpu_only:true,cross_origin_isolated:self.crossOriginIsolated};
    status.textContent=JSON.stringify(out,null,2);return out;
  },
  async offlineReplay(){
    const w=await makeBrain();
    const text=await infer(w,'Reply with awake and a short statement about offline memory.');
    const models=await w.modelManager.getModels();
    await w.exit();
    const out={ok:true,mode:'offline-cache',text,cached_models:models.length,cpu_only:true};
    status.textContent=JSON.stringify(out,null,2);return out;
  }
};
if('serviceWorker' in navigator) navigator.serviceWorker.register('/web/sw.js').catch(()=>{});