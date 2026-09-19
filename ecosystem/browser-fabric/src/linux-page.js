const $=id=>document.getElementById(id);
let emulator=null;

function memoryBytes(){
  const gb=navigator.deviceMemory||4;
  if(gb<=2)return 128*1024*1024;
  if(gb<=4)return 256*1024*1024;
  return 512*1024*1024;
}
async function loadV86(){
  if(globalThis.V86)return;
  await new Promise((resolve,reject)=>{
    const s=document.createElement("script");
    s.src="https://cdn.jsdelivr.net/npm/v86@0.5/build/libv86.js";
    s.onload=resolve;s.onerror=()=>reject(new Error("Falha ao carregar v86"));
    document.head.appendChild(s);
  });
}
$("boot").onclick=async()=>{
  if(emulator)return;
  $("status").textContent="Carregando v86 + Alpine Linux…";
  try{
    await loadV86();
    emulator=new globalThis.V86({
      wasm_path:"https://cdn.jsdelivr.net/npm/v86@0.5/build/v86.wasm",
      memory_size:memoryBytes(),
      vga_memory_size:8*1024*1024,
      screen_container:$("screen_container"),
      bios:{url:"https://copy.sh/v86/bios/seabios.bin"},
      vga_bios:{url:"https://copy.sh/v86/bios/vgabios.bin"},
      filesystem:{
        baseurl:"https://copy.sh/v86/images/alpine-rootfs-flat",
        basefs:"https://copy.sh/v86/images/alpine-fs.json"
      },
      autostart:true,
      bzimage_initrd_from_filesystem:true,
      cmdline:"rw root=host9p rootfstype=9p rootflags=trans=virtio,cache=loose modules=virtio_pci tsc=reliable"
    });
    $("status").textContent="Alpine Linux iniciado dentro do navegador. Nenhuma VPS HARUM foi provisionada.";
  }catch(e){
    $("status").textContent="Falha no boot: "+String(e?.stack||e);
  }
};
$("pause").onclick=()=>{if(emulator){emulator.stop();$("status").textContent="Linux pausado.";}}
$("resume").onclick=()=>{if(emulator){emulator.run();$("status").textContent="Linux executando.";}}