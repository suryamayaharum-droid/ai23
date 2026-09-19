import {embed} from "./semantic.js";
import {supported as webgpuSupported} from "./webllm.js";

export async function benchmarkBrowser(){
  const result={
    timestamp:Date.now(),
    webgpu:await webgpuSupported(),
    wasm:typeof WebAssembly==="object",
    cores:navigator.hardwareConcurrency||null,
    memoryGB:navigator.deviceMemory||null,
    tests:{}
  };
  const start=performance.now();
  try{
    const vectors=await embed(["carvão gesto presença","banana motor"]);
    result.tests.semanticWasm={
      ok:Array.isArray(vectors)&&vectors.length===2,
      dims:vectors?.[0]?.length||0,
      ms:Math.round(performance.now()-start)
    };
  }catch(error){
    result.tests.semanticWasm={ok:false,error:String(error),ms:Math.round(performance.now()-start)};
  }
  result.profile=result.webgpu?"webgpu-brain":result.tests.semanticWasm.ok?"wasm-neuron":"deterministic-cell";
  return result;
}