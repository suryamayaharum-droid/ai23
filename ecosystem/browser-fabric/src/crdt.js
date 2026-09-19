import {put,all} from "./idb.js";

function cmp(a,b){
  if((a.clock||0)!==(b.clock||0))return (a.clock||0)-(b.clock||0);
  return String(a.node||"").localeCompare(String(b.node||""));
}

export class HolographicCRDT{
  constructor(nodeId){
    this.nodeId=nodeId;
    this.clock=Number(localStorage.getItem("harum-lamport")||0);
    this.map=new Map();
  }
  tick(remote=0){
    this.clock=Math.max(this.clock,Number(remote)||0)+1;
    localStorage.setItem("harum-lamport",String(this.clock));
    return this.clock;
  }
  async set(key,value){
    const fact={id:crypto.randomUUID(),key,value,clock:this.tick(),node:this.nodeId,ts:Date.now()};
    this.mergeFact(fact);
    await put("state",{id:"fact:"+fact.key,...fact});
    return fact;
  }
  mergeFact(fact){
    this.tick(fact.clock);
    const cur=this.map.get(fact.key);
    if(!cur||cmp(cur,fact)<0)this.map.set(fact.key,fact);
  }
  merge(packet){
    for(const f of packet?.facts||[])this.mergeFact(f);
    return this.snapshot();
  }
  snapshot(){
    return {
      node:this.nodeId,clock:this.clock,
      facts:[...this.map.values()].sort((a,b)=>a.key.localeCompare(b.key))
    };
  }
  digest(){
    const raw=JSON.stringify(this.snapshot().facts.map(({id,...x})=>x));
    return crypto.subtle.digest("SHA-256",new TextEncoder().encode(raw))
      .then(b=>[...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join(""));
  }
}