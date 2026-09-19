import {put,all} from "./idb.js";

export class BrowserScheduler{
  constructor(node,mesh,federation){
    this.node=node;this.mesh=mesh;this.federation=federation;
    this.handlers=new Map();
    mesh.onMessage(m=>this.#onMesh(m));
  }
  register(kind,fn){this.handlers.set(kind,fn);}
  async enqueue(task){
    const t={
      id:task.id||crypto.randomUUID(),kind:task.kind,payload:task.payload||{},
      required:task.required||[],priority:task.priority??50,status:"READY",
      origin:this.node.id,createdAt:Date.now()
    };
    await put("tasks",t);
    this.mesh.send("browser.task.available",{task:t});
    return t;
  }
  async tick(){
    if(!(await this.mesh.electLeader()))return {leader:false};
    const tasks=(await all("tasks"))
      .filter(t=>t.status==="READY")
      .sort((a,b)=>(b.priority-a.priority)||(a.createdAt-b.createdAt));
    const executed=[];
    for(const task of tasks.slice(0,4)){
      const fn=this.handlers.get(task.kind);
      if(!fn)continue;
      const running={...task,status:"RUNNING",leaseOwner:this.node.id,leaseUntil:Date.now()+60000};
      await put("tasks",running);
      try{
        const result=await fn(task.payload,task);
        await put("tasks",{...running,status:"COMPLETED",result,completedAt:Date.now()});
        this.mesh.send("browser.task.completed",{id:task.id,result});
        executed.push(task.id);
      }catch(error){
        await put("tasks",{...running,status:"READY",error:String(error),attempts:(task.attempts||0)+1});
      }
    }
    return {leader:true,executed};
  }
  async reconcile(){
    const now=Date.now();
    for(const t of await all("tasks")){
      if(t.status==="RUNNING"&&t.leaseUntil&&t.leaseUntil<now){
        await put("tasks",{...t,status:(t.attempts||0)>=3?"DEAD":"READY",leaseOwner:null,leaseUntil:null});
      }
    }
  }
  #onMesh(msg){
    if(msg.type==="event"&&msg.topic==="browser.task.available"&&msg.payload?.task){
      const t=msg.payload.task;
      put("tasks",t).catch(()=>{});
    }
  }
}