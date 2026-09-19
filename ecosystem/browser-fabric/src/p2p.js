export class PeerLink{
  constructor({onPacket=()=>{},onState=()=>{}}={}){
    this.pc=new RTCPeerConnection({iceServers:[]});
    this.dc=null;
    this.onPacket=onPacket;this.onState=onState;
    this.pc.onconnectionstatechange=()=>this.onState(this.pc.connectionState);
    this.pc.ondatachannel=e=>this.#attach(e.channel);
  }
  #attach(dc){
    this.dc=dc;
    dc.onopen=()=>this.onState("data-open");
    dc.onclose=()=>this.onState("data-closed");
    dc.onmessage=e=>{
      try{this.onPacket(JSON.parse(e.data));}catch{}
    };
  }
  send(packet){
    if(this.dc?.readyState==="open"){
      this.dc.send(JSON.stringify(packet));return true;
    }
    return false;
  }
  async createOffer(){
    this.#attach(this.pc.createDataChannel("harum-organism"));
    const offer=await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);
    await this.#waitIce();
    return this.#encode(this.pc.localDescription);
  }
  async acceptOffer(encoded){
    await this.pc.setRemoteDescription(this.#decode(encoded));
    const answer=await this.pc.createAnswer();
    await this.pc.setLocalDescription(answer);
    await this.#waitIce();
    return this.#encode(this.pc.localDescription);
  }
  async acceptAnswer(encoded){
    await this.pc.setRemoteDescription(this.#decode(encoded));
  }
  async #waitIce(){
    if(this.pc.iceGatheringState==="complete")return;
    await new Promise(resolve=>{
      const f=()=>{
        if(this.pc.iceGatheringState==="complete"){
          this.pc.removeEventListener("icegatheringstatechange",f);resolve();
        }
      };
      this.pc.addEventListener("icegatheringstatechange",f);
      setTimeout(resolve,8000);
    });
  }
  #encode(desc){
    const raw=JSON.stringify({type:desc.type,sdp:desc.sdp});
    return btoa(unescape(encodeURIComponent(raw)));
  }
  #decode(encoded){
    const raw=decodeURIComponent(escape(atob(encoded.trim())));
    return JSON.parse(raw);
  }
}