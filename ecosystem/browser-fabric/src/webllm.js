let engine=null;
export async function supported(){
  if(!navigator.gpu)return false;
  try{return !!(await navigator.gpu.requestAdapter());}catch{return false;}
}
export async function loadLocalAI(progress=()=>{}){
  if(engine)return engine;
  if(!(await supported()))throw new Error("WebGPU indisponível neste navegador");
  const webllm=await import("https://esm.run/@mlc-ai/web-llm");
  const candidates=[
    "Qwen2.5-0.5B-Instruct-q4f16_1-MLC",
    "Llama-3.2-1B-Instruct-q4f16_1-MLC"
  ];
  let last;
  for(const model of candidates){
    try{
      const worker=new Worker("./src/llm-worker.js",{type:"module"});
      engine=await webllm.CreateWebWorkerMLCEngine(
        worker,
        model,
        {
          initProgressCallback:progress,
          appConfig:{...webllm.prebuiltAppConfig,cacheBackend:"indexeddb"}
        }
      );
      engine.__harumModel=model;
      engine.__harumWorker=worker;
      return engine;
    }catch(e){
      last=e;
      if(engine?.__harumWorker)engine.__harumWorker.terminate();
      engine=null;
    }
  }
  throw last||new Error("Nenhum modelo WebLLM compatível conseguiu carregar");
}
export async function complete(messages,opts={}){
  const e=await loadLocalAI(opts.onProgress||(()=>{}));
  const out=await e.chat.completions.create({
    messages,
    temperature:opts.temperature??0.1,
    max_tokens:opts.max_tokens??256
  });
  return {model:e.__harumModel,text:out.choices?.[0]?.message?.content||""};
}