export class LinuxBrowserAdapter{
  constructor(){
    this.mode=null;this.instance=null;
  }
  async capabilities(){
    return {
      pyodide:true,
      v86_possible:typeof WebAssembly==="object",
      webcontainers_optional:true,
      note:"Full Linux emulation is optional and heavier than WASM/Python."
    };
  }
  async bootV86(opts={}){
    if(!opts.libUrl||!opts.wasmUrl||!opts.biosUrl||!opts.vgaBiosUrl||!opts.imageUrl){
      throw new Error("v86 assets/image URLs required; HARUM does not silently download or redistribute OS images");
    }
    if(!globalThis.V86){
      await new Promise((resolve,reject)=>{
        const s=document.createElement("script");s.src=opts.libUrl;
        s.onload=resolve;s.onerror=reject;document.head.appendChild(s);
      });
    }
    this.instance=new globalThis.V86({
      wasm_path:opts.wasmUrl,
      memory_size:opts.memorySize||128*1024*1024,
      vga_memory_size:opts.vgaMemorySize||8*1024*1024,
      bios:{url:opts.biosUrl},
      vga_bios:{url:opts.vgaBiosUrl},
      cdrom:{url:opts.imageUrl},
      screen_container:opts.screenContainer||undefined,
      autostart:true
    });
    this.mode="v86";
    return this.instance;
  }
}