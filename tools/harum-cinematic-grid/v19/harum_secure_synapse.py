#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, json, os, socket, struct, time, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"v18"))
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.exceptions import InvalidTag
from harum_identity import sign, verify, load
from harum_living_circuit import Circuit
from harum_attestation import build_chain, verify_chain

MAX_FRAME=2*1024*1024
PROTO="HARUM-SECURE-SYNAPSE-v1"

def b64(b): return base64.urlsafe_b64encode(b).decode().rstrip("=")
def ub64(s): return base64.urlsafe_b64decode(s + "="*((4-len(s)%4)%4))
def stable(x): return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
def recv_exact(sock,n):
    out=bytearray()
    while len(out)<n:
        b=sock.recv(n-len(out))
        if not b: raise EOFError("connection closed")
        out.extend(b)
    return bytes(out)
def send_plain(sock,obj):
    b=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()
    if len(b)>MAX_FRAME: raise ValueError("frame too large")
    sock.sendall(struct.pack("!I",len(b))+b)
def recv_plain(sock):
    n=struct.unpack("!I",recv_exact(sock,4))[0]
    if n>MAX_FRAME: raise ValueError("frame too large")
    return json.loads(recv_exact(sock,n))
def raw_x_pub(priv):
    return priv.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
def derive(shared,client_signed,server_signed):
    transcript=hashlib.sha256(stable({"client":client_signed,"server":server_signed})).digest()
    material=HKDF(algorithm=hashes.SHA256(),length=64,salt=transcript,info=PROTO.encode()).derive(shared)
    return material[:32],material[32:],transcript.hex()

class SecureChannel:
    def __init__(self,sock,send_key,recv_key,send_label,recv_label):
        self.sock=sock;self.send=ChaCha20Poly1305(send_key);self.recv=ChaCha20Poly1305(recv_key)
        self.send_seq=0;self.recv_seq=0;self.send_label=send_label.encode();self.recv_label=recv_label.encode()
    def _nonce(self,n): return n.to_bytes(12,"big")
    def send_obj(self,obj,tamper=False):
        seq=self.send_seq; self.send_seq+=1
        plain=json.dumps(obj,ensure_ascii=False,separators=(",",":")).encode()
        aad=PROTO.encode()+b"|"+self.send_label+b"|"+seq.to_bytes(8,"big")
        ct=bytearray(self.send.encrypt(self._nonce(seq),plain,aad))
        if tamper and ct: ct[len(ct)//2]^=1
        self.sock.sendall(struct.pack("!I",len(ct))+ct)
    def recv_obj(self):
        seq=self.recv_seq; self.recv_seq+=1
        n=struct.unpack("!I",recv_exact(self.sock,4))[0]
        if n>MAX_FRAME: raise ValueError("frame too large")
        ct=recv_exact(self.sock,n)
        aad=PROTO.encode()+b"|"+self.recv_label+b"|"+seq.to_bytes(8,"big")
        return json.loads(self.recv.decrypt(self._nonce(seq),ct,aad))

def client_handshake(sock,identity_path,expected_server_peer):
    ident=load(identity_path);eph=X25519PrivateKey.generate()
    payload={"type":"harum.secure.hello.v1","proto":PROTO,"role":"client","peer_id":ident["peer_id"],"public_key":ident["public_key"],"ephemeral":b64(raw_x_pub(eph)),"nonce":b64(os.urandom(16)),"ts":time.time()}
    client_signed=sign(identity_path,payload);send_plain(sock,client_signed);server_signed=recv_plain(sock)
    sv=verify(server_signed)
    if not sv.get("valid"): raise PermissionError("bad_server_signature")
    sp=server_signed.get("payload",{})
    if sp.get("type")!="harum.secure.hello.v1" or sp.get("role")!="server": raise PermissionError("bad_server_hello")
    if sv["issuer"]!=expected_server_peer: raise PermissionError("unexpected_server_peer")
    if sp.get("client_peer")!=ident["peer_id"] or sp.get("client_ephemeral")!=payload["ephemeral"]: raise PermissionError("server_transcript_mismatch")
    shared=eph.exchange(X25519PublicKey.from_public_bytes(ub64(sp["ephemeral"])))
    c2s,s2c,th=derive(shared,client_signed,server_signed)
    return SecureChannel(sock,c2s,s2c,"c2s","s2c"),{"server_peer":sv["issuer"],"transcript_hash":th}

def server_handshake(sock,identity_path):
    client_signed=recv_plain(sock);cv=verify(client_signed)
    if not cv.get("valid"): raise PermissionError("bad_client_signature")
    cp=client_signed.get("payload",{})
    if cp.get("type")!="harum.secure.hello.v1" or cp.get("role")!="client": raise PermissionError("bad_client_hello")
    if cp.get("peer_id")!=cv["issuer"]: raise PermissionError("client_peer_mismatch")
    ident=load(identity_path);eph=X25519PrivateKey.generate()
    payload={"type":"harum.secure.hello.v1","proto":PROTO,"role":"server","peer_id":ident["peer_id"],"public_key":ident["public_key"],"ephemeral":b64(raw_x_pub(eph)),"nonce":b64(os.urandom(16)),"ts":time.time(),"client_peer":cv["issuer"],"client_ephemeral":cp["ephemeral"]}
    server_signed=sign(identity_path,payload);send_plain(sock,server_signed)
    shared=eph.exchange(X25519PublicKey.from_public_bytes(ub64(cp["ephemeral"])))
    c2s,s2c,th=derive(shared,client_signed,server_signed)
    return SecureChannel(sock,s2c,c2s,"s2c","c2s"),{"client_peer":cv["issuer"],"transcript_hash":th}

class SecureServer:
    def __init__(self,state_dir,identity_path):
        self.identity=identity_path;self.ident=load(identity_path);self.circuit=Circuit(state_dir,identity_path)
    def process(self,envelope,meta):
        cap=envelope.get("capability",{})
        if cap.get("issuer")!=self.ident["peer_id"]: return {"ok":False,"error":"capability_wrong_authority"}
        result=self.circuit.handle(envelope)
        if not result.get("ok"): return result
        receipt=result["signed_receipt"];task_id=receipt["payload"]["task_id"]
        stages=[
          ("secure_handshake",{"transcript_hash":meta["transcript_hash"],"client_peer":meta["client_peer"]}),
          ("capability_authorized",{"authority":cap["issuer"],"resource":cap["payload"]["resource"]}),
          ("task_executed",{"kind":receipt["payload"]["kind"],"replayed":result.get("replayed",False)}),
          ("cas_committed",{"sha256":receipt["payload"]["cas"]["sha256"]}),
          ("receipt_signed",{"receipt_issuer":receipt["issuer"]})
        ]
        result["attestations"]=build_chain(self.identity,task_id,stages)
        return result

def serve(host,port,state_dir,identity_path):
    server=SecureServer(state_dir,identity_path)
    s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind((host,port));s.listen(20)
    print(json.dumps({"listening":s.getsockname()[1],"peer_id":server.ident["peer_id"]}),flush=True)
    while True:
        conn,_=s.accept()
        with conn:
            try:
                ch,meta=server_handshake(conn,identity_path)
                res=server.process(ch.recv_obj(),meta)
                ch.send_obj(res)
            except (InvalidTag,EOFError,PermissionError,ValueError):
                continue
            except Exception:
                continue

def request_secure(host,port,identity_path,expected_server_peer,envelope,tamper=False):
    with socket.create_connection((host,port),timeout=5) as s:
        ch,meta=client_handshake(s,identity_path,expected_server_peer)
        ch.send_obj(envelope,tamper=tamper)
        res=ch.recv_obj()
        if res.get("ok"):
            rv=verify(res.get("signed_receipt",{}))
            if not rv.get("valid") or rv["issuer"]!=expected_server_peer: raise PermissionError("bad_receipt_signature")
            task_id=res["signed_receipt"]["payload"]["task_id"]
            av=verify_chain(res.get("attestations",[]),task_id,expected_server_peer)
            if not av.get("valid"): raise PermissionError("bad_attestation_chain")
            res["client_verification"]={"receipt":rv,"attestations":av,"handshake":meta}
        return res
