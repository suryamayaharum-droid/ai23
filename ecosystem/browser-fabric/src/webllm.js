let engine=null;
export async function supported(){
  if(!navigator.gpu)return false;
  try{return !!(await navigator.gpu.requestAdapter());}catch{return false;}
}
export async function loadLocalAI(progress=()=>{}){
  if(engine)return engine;
  if(!(await supported())) throw new Error("WebGPU indisponível neste navegador");
  const webllm=await import("https://esm.run/@mlc-ai/web-llm");
  const candidates=[
    "Qwen2.5-0.5B-Instruct-q4f16_1-MLC",
    "Llama-3.2-1B-Instruct-q4f16_1-MLC"
  ];
  let last;
  for(const model of candidates){
    try{
      engine=await webllm.CreateMLCEngine(model,{initProgressCallback:progress});
      engine.__harumModel=model;
      return engine;
    }catch(e){last=e;}
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