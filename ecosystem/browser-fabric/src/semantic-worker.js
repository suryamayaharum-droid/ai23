let extractor=null;
async function getExtractor(){
  if(extractor)return extractor;
  const {pipeline}=await import("https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.0.0");
  extractor=await pipeline(
    "feature-extraction",
    "Xenova/all-MiniLM-L6-v2",
    {device:"wasm",dtype:"q4"}
  );
  return extractor;
}
self.onmessage=async ev=>{
  const {id,texts}=ev.data||{};
  try{
    const pipe=await getExtractor();
    const out=await pipe(texts,{pooling:"mean",normalize:true});
    self.postMessage({id,ok:true,vectors:out.tolist()});
  }catch(error){
    self.postMessage({id,ok:false,error:String(error?.stack||error)});
  }
};