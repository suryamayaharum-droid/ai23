let worker=null;
const pending=new Map();
function getWorker(){
  if(!worker){
    worker=new Worker("./src/semantic-worker.js",{type:"module"});
    worker.onmessage=e=>{
      const p=pending.get(e.data.id);if(!p)return;
      pending.delete(e.data.id);
      e.data.ok?p.resolve(e.data.vectors):p.reject(new Error(e.data.error));
    };
  }
  return worker;
}
export function embed(texts){
  const arr=Array.isArray(texts)?texts:[texts];
  return new Promise((resolve,reject)=>{
    const id=crypto.randomUUID();
    pending.set(id,{resolve,reject});
    getWorker().postMessage({id,texts:arr});
  });
}
export function cosine(a,b){
  let dot=0,na=0,nb=0;
  for(let i=0;i<Math.min(a.length,b.length);i++){
    dot+=a[i]*b[i];na+=a[i]*a[i];nb+=b[i]*b[i];
  }
  return dot/(Math.sqrt(na)*Math.sqrt(nb)||1);
}
export async function semanticRank(query,items,key="text",limit=5){
  if(!items.length)return [];
  const vectors=await embed([query,...items.map(x=>String(x[key]||""))]);
  const q=vectors[0];
  return items.map((item,i)=>({...item,semanticScore:cosine(q,vectors[i+1])}))
    .sort((a,b)=>b.semanticScore-a.semanticScore)
    .slice(0,limit);
}