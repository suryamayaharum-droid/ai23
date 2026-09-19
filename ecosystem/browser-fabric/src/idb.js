export function openDB(){
  return new Promise((resolve,reject)=>{
    const req=indexedDB.open("harum-browser-fabric",1);
    req.onupgradeneeded=()=>{
      const db=req.result;
      for(const name of ["events","tasks","state","artifacts"]){
        if(!db.objectStoreNames.contains(name)) db.createObjectStore(name,{keyPath:"id"});
      }
    };
    req.onsuccess=()=>resolve(req.result);
    req.onerror=()=>reject(req.error);
  });
}
export async function put(store,obj){
  const db=await openDB();
  return new Promise((resolve,reject)=>{
    const tx=db.transaction(store,"readwrite");
    tx.objectStore(store).put(obj);
    tx.oncomplete=()=>resolve(obj);
    tx.onerror=()=>reject(tx.error);
  });
}
export async function all(store){
  const db=await openDB();
  return new Promise((resolve,reject)=>{
    const tx=db.transaction(store,"readonly");
    const req=tx.objectStore(store).getAll();
    req.onsuccess=()=>resolve(req.result);
    req.onerror=()=>reject(req.error);
  });
}