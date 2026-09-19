import {PeerLink} from "./p2p.js";
import {HolographicCRDT} from "./crdt.js";

export class BrowserFederation{
  constructor(node,mesh){
    this.node=node;this.mesh=mesh;
    this.crdt=new HolographicCRDT(node.id);
    this.peers=new Set();
    mesh.onMessage(msg=>{
      if(msg.type==="event"&&msg.topic==="crdt.delta")this.crdt.merge(msg.payload);
    });
  }
  newPeer(onState=()=>{}){
    const peer=new PeerLink({
      onState,
      onPacket:packet=>this.#receive(peer,packet)
    });
    this.peers.add(peer);
    return peer;
  }
  async publish(key,value){
    const fact=await this.crdt.set(key,value);
    const packet={type:"crdt",facts:[fact],source:this.node.id};
    this.mesh.send("crdt.delta",packet);
    for(const p of this.peers)p.send(packet);
    return fact;
  }
  async syncAll(){
    const packet={type:"crdt",...this.crdt.snapshot()};
    for(const p of this.peers)p.send(packet);
    return packet;
  }
  #receive(peer,packet){
    if(packet?.type==="crdt"){
      this.crdt.merge(packet);
      this.mesh.send("crdt.delta",packet);
    }else if(packet?.type==="event"){
      this.mesh.send(packet.topic,packet.payload,packet.target||null);
    }
  }
}