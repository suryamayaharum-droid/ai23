import {put,all} from "./idb.js";

const CHANNEL="harum-organism-browser-v1";
const bc=new BroadcastChannel(CHANNEL);

export class BrowserMesh{
  constructor(node){
    this.node=node;
    this.peers=new Map();
    this.handlers=new Set();
    bc.onmessage=(ev)=>this.#receive(ev.data);
  }
  start(){
    this.heartbeat();
    this.timer=setInterval(()=>this.heartbeat(),15000);
    this.reaper=setInterval(()=>this.reap(),20000);
    return this;
  }
  stop(){clearInterval(this.timer);clearInterval(this.reaper);bc.close();}
  async heartbeat(){
    const msg={type:"heartbeat",node:this.node,ts:Date.now()};
    bc.postMessage(msg);
    await put("state",{id:"self",...msg});
  }
  onMessage(fn){this.handlers.add(fn);return()=>this.handlers.delete(fn);}
  send(topic,payload,target=null){
    const event={
      id:crypto.randomUUID(),type:"event",topic,payload,target,
      source:this.node.id,ts:Date.now(),hops:0
    };
    bc.postMessage(event);
    put("events",event);
    return event;
  }
  reap(){
    const now=Date.now();
    for(const [id,p] of this.peers){
      if(now-p.ts>45000)this.peers.delete(id);
    }
  }
  snapshot(){
    return {self:this.node,peers:[...this.peers.values()].map(x=>x.node)};
  }
  async electLeader(){
    if(navigator.locks?.request){
      let leader=false;
      await navigator.locks.request("harum-browser-leader",{ifAvailable:true},async lock=>{
        leader=!!lock;
      });
      return leader;
    }
    const peers=[this.node,...[...this.peers.values()].map(x=>x.node)].sort((a,b)=>a.id.localeCompare(b.id));
    return peers[0]?.id===this.node.id;
  }
  #receive(msg){
    if(!msg||msg.node?.id===this.node.id||msg.source===this.node.id)return;
    if(msg.type==="heartbeat"&&msg.node?.id){
      this.peers.set(msg.node.id,{node:msg.node,ts:msg.ts||Date.now()});
    }
    for(const fn of this.handlers)fn(msg);
  }
}