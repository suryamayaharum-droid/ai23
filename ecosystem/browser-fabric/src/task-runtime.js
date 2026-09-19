import {runPython} from "./python.js";
import {complete,supported as aiSupported} from "./webllm.js";
import {all,put} from "./idb.js";

export async function execute(task,node){
  const t={id:task.id||crypto.randomUUID(),createdAt:Date.now(),...task};
  await put("tasks",{...t,status:"RUNNING",node:node.id});
  try{
    let result;
    if(t.kind==="python"){
      result={kind:"python",output:await runPython(t.code)};
    }else if(t.kind==="inventory"){
      const stores={};
      for(const name of ["events","tasks","state","artifacts"])stores[name]=(await all(name)).length;
      result={kind:"inventory",stores};
    }else if(t.kind==="llm"){
      if(!(await aiSupported()))throw new Error("WebGPU local inference unavailable");
      result={kind:"llm",...(await complete(t.messages||[{role:"user",content:t.prompt||""}],t.options||{}))};
    }else{
      throw new Error("unsupported task kind: "+t.kind);
    }
    await put("tasks",{...t,status:"COMPLETED",node:node.id,result,completedAt:Date.now()});
    return result;
  }catch(error){
    await put("tasks",{...t,status:"FAILED",node:node.id,error:String(error),completedAt:Date.now()});
    throw error;
  }
}