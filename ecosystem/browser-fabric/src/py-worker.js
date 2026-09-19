let ready;
self.onmessage=async ev=>{
  const {id,code}=ev.data||{};
  try{
    if(!ready){
      importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js");
      ready=loadPyodide({indexURL:"https://cdn.jsdelivr.net/pyodide/v0.27.7/full/"});
    }
    const py=await ready;
    const result=await py.runPythonAsync(code);
    self.postMessage({id,ok:true,result:String(result)});
  }catch(error){
    self.postMessage({id,ok:false,error:String(error?.stack||error)});
  }
};