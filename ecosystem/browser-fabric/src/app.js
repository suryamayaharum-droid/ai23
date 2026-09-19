import {makeNode,detectCapabilities} from "./provision.js";
import {BrowserMesh} from "./mesh.js";
import {execute} from "./task-runtime.js";
import {loadLocalAI} from "./webllm.js";
import {BrowserFederation} from "./federation.js";
import {BrowserScheduler} from "./scheduler.js";
import {autoProvision} from "./autoprovision.js";

const $=id=>document.getElementById(id);
const fmt=x=>JSON.stringify(x,null,2);

if("serviceWorker" in navigator){
  navigator.serviceWorker.register("./sw.js").catch(()=>{});
}

const caps=await detectCapabilities();
const node=await makeNode();
const mesh=new BrowserMesh(node).start();
const federation=new BrowserFederation(node,mesh);
const scheduler=new BrowserScheduler(node,mesh,federation);

scheduler.register("inventory",async()=>execute({kind:"inventory"},node));
scheduler.register("python",async payload=>execute({kind:"python",code:payload.code},node));
scheduler.register("llm",async payload=>execute({kind:"llm",messages:payload.messages},node));

$("node").textContent=fmt(node);
$("caps").textContent=fmt(caps);

setInterval(async()=>{
  await scheduler.reconcile();
  await scheduler.tick().catch(()=>{});
  const snap=mesh.snapshot();
  snap.isLeader=await mesh.electLeader().catch(()=>false);
  $("mesh").textContent=fmt(snap);
  $("crdt").textContent=fmt(federation.crdt.snapshot());
},2500);

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
  $("out").textContent="Carregando modelo quantizado no Web Worker…";
  try{
    const e=await loadLocalAI(p=>{$("out").textContent=fmt(p);});
    $("out").textContent=fmt({status:"READY",model:e.__harumModel,worker:true,local:true,serverRequired:false});
  }catch(e){$("out").textContent=String(e);}
};

$("run").onclick=async()=>{
  const prompt=$("task").value;
  $("out").textContent="Executando…";
  try{
    let result;
    if(prompt.toLowerCase().includes("registro")||prompt.toLowerCase().includes("índice")){
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

let peer=null;
const newPeer=()=>{
  peer=federation.newPeer(s=>$("peer").textContent=fmt({state:s,crdt:federation.crdt.snapshot()}));
  return peer;
};
$("offer").onclick=async()=>{
  $("signal").value=await newPeer().createOffer();
};
$("answer").onclick=async()=>{
  const p=newPeer();
  $("signal").value=await p.acceptOffer($("signal").value);
};
$("accept").onclick=async()=>{
  if(!peer)newPeer();
  await peer.acceptAnswer($("signal").value);
  $("peer").textContent=fmt({state:"answer-accepted"});
};
$("publishState").onclick=async()=>{
  let value;
  try{value=JSON.parse($("stateValue").value);}catch{value=$("stateValue").value;}
  await federation.publish($("stateKey").value,value);
  $("crdt").textContent=fmt(federation.crdt.snapshot());
};
$("syncState").onclick=async()=>{
  await federation.syncAll();
  $("crdt").textContent=fmt(federation.crdt.snapshot());
};
$("provision").onclick=async()=>{
  $("provisionOut").textContent="Detectando e provisionando…";
  try{$("provisionOut").textContent=fmt(await autoProvision());}
  catch(e){$("provisionOut").textContent=String(e);}
};
