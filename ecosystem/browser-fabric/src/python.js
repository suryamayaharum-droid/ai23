let worker;
const pending=new Map();
function getWorker(){
  if(!worker){
    worker=new Worker("./src/py-worker.js");
    worker.onmessage=e=>{
      const p=pending.get(e.data.id);if(!p)return;
      pending.delete(e.data.id);
      e.data.ok?p.resolve(e.data.result):p.reject(new Error(e.data.error));
    };
  }
  return worker;
}
export function runPython(code){
  return new Promise((resolve,reject)=>{
    const id=crypto.randomUUID();
    pending.set(id,{resolve,reject});
    getWorker().postMessage({id,code});
  });
}