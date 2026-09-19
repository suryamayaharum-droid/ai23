import {detectCapabilities,makeNode} from "./provision.js";
import {benchmarkBrowser} from "./benchmark.js";
import {put} from "./idb.js";

export async function autoProvision(){
  const caps=await detectCapabilities();
  const node=await makeNode();
  const plan={
    node:node.id,
    timestamp:Date.now(),
    profile:"deterministic-cell",
    runtimes:["javascript","indexeddb","service-worker"],
    optional:[],
    constraints:[]
  };
  if(caps.wasm){
    plan.runtimes.push("pyodide-python","transformersjs-wasm");
    plan.profile="wasm-neuron";
  }
  if(caps.webgpu){
    plan.runtimes.push("webllm-webgpu");
    plan.profile="webgpu-brain";
  }else{
    plan.constraints.push("webgpu unavailable: generative browser LLM disabled");
  }
  if((caps.deviceMemoryGB||4)>=4 && caps.wasm){
    plan.optional.push("v86-alpine-linux");
  }else{
    plan.constraints.push("v86 Linux not recommended on this memory profile");
  }
  try{
    plan.benchmark=await benchmarkBrowser();
  }catch(error){
    plan.benchmark={error:String(error)};
  }
  await put("state",{id:"autoprovision-plan",...plan});
  return plan;
}