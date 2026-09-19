import {makeNode,detectCapabilities} from "./provision.js";
import {BrowserMesh} from "./mesh.js";
import {execute} from "./task-runtime.js";
import {loadLocalAI} from "./webllm.js";

const $=id=>document.getElementById(id);
const fmt=x=>JSON.stringify(x,null,2);

if("serviceWorker" in navigator){
  navigator.serviceWorker.register("./sw.js").catch(()=>{});
}

const caps=await detectCapabilities();
const node=await makeNode();
const mesh=new BrowserMesh(node).start();

$("node").textContent=fmt(node);
$("caps").textContent=fmt(caps);

setInterval(async()=>{
  const snap=mesh.snapshot();
  snap.isLeader=await mesh.electLeader().catch(()=>false);
  $("mesh").textContent=fmt(snap);
},1500);

$("python").onclick=async()=>{
  $("out").textContent="Carregando Python/WASM…";
  try{
    $("out").textContent=fmt(await execute({
      kind:"python",
      code:"import sys, platform\n{'python':sys.version.split()[0],'platform':platform.platform(),'answer':17*23}"
    },node));
  }catch(e){$("out").textContent=String(e);}
};

$("ai").onclick=async()=>{
  $("out").textContent="Carregando modelo quantizado no navegador…";
  try{
    const e=await loadLocalAI(p=>{$("out").textContent=fmt(p);});
    $("out").textContent=fmt({status:"READY",model:e.__harumModel,local:true,serverRequired:false});
  }catch(e){$("out").textContent=String(e);}
};

$("run").onclick=async()=>{
  const prompt=$("task").value;
  $("out").textContent="Executando…";
  try{
    let result;
    if(prompt.toLowerCase().includes("arquivo")||prompt.toLowerCase().includes("índice")){
      result=await execute({kind:"inventory"},node);
    }else{
      result=await execute({
        kind:"llm",
        messages:[
          {role:"system",content:"Você é uma célula local HARUM. Seja conciso e não invente resultados."},
          {role:"user",content:prompt}
        ]
      },node);
    }
    $("out").textContent=fmt(result);
    mesh.send("task.completed",{task:prompt,result});
  }catch(e){$("out").textContent=String(e);}
};