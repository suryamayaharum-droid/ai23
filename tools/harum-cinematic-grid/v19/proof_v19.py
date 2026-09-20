#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,socket,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/"v18"))
from harum_identity import gen
from harum_capability import issue
from harum_living_circuit import build_task
from harum_secure_synapse import request_secure

RT=HERE/"runtime"/"proof";RT.mkdir(parents=True,exist_ok=True)
IDA=RT/"A.identity.json";IDB=RT/"B.identity.json";STATE=RT/"peerB"
for p in (IDA,IDB):
    if p.exists():p.unlink()
if STATE.exists():
    import shutil;shutil.rmtree(STATE)
A=gen(IDA,"A");B=gen(IDB,"B")
cap=issue(IDB,A["peer_id"],["execute"],"harum://tasks/sha256_text",ttl=600)
task=build_task(IDA,cap,"sha256_text",{"text":"HARUM secure synapse v19"},ttl=600,nonce="stable-v19-proof")

def free_port():
    s=socket.socket();s.bind(("127.0.0.1",0));p=s.getsockname()[1];s.close();return p
def start(port):
    code=f"""import sys;sys.path.insert(0,{str(HERE)!r});sys.path.insert(0,{str(HERE.parent/'v18')!r});from harum_secure_synapse import serve;serve('127.0.0.1',{port},{str(STATE)!r},{str(IDB)!r})"""
    p=subprocess.Popen([sys.executable,"-u","-c",code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    line=p.stdout.readline().strip()
    if not line: raise RuntimeError(p.stderr.read())
    return p,json.loads(line)
def stop(p):
    p.terminate()
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:p.kill()

port=free_port();srv,_=start(port)
first=request_secure("127.0.0.1",port,IDA,B["peer_id"],task);stop(srv)
srv2,_=start(port)
second=request_secure("127.0.0.1",port,IDA,B["peer_id"],task)
wrong=False
try:request_secure("127.0.0.1",port,IDA,"0"*64,task)
except Exception:wrong=True
tamper=False
try:request_secure("127.0.0.1",port,IDA,B["peer_id"],task,tamper=True)
except Exception:tamper=True
stop(srv2)
receipt1=first["signed_receipt"];receipt2=second["signed_receipt"];cas_path=Path(receipt1["payload"]["cas"]["path"])
proof={
 "transport":{"type":"TCP + X25519/HKDF-SHA256/ChaCha20-Poly1305","scope":"localhost","separate_processes":True,"physical_hosts":1,"noise_wire_compatible":False},
 "mutual_authentication":{"client_peer":A["peer_id"],"server_peer":B["peer_id"],"server_identity_pinned":True},
 "first_execution":{"ok":first["ok"],"replayed":first["replayed"],"receipt_valid":first["client_verification"]["receipt"]["valid"],"attestation_chain":first["client_verification"]["attestations"]},
 "restart_replay":{"ok":second["ok"],"replayed":second["replayed"],"same_signed_receipt":receipt1==receipt2},
 "aead_tamper_rejected":tamper,"wrong_server_identity_rejected":wrong,
 "cas_integrity":hashlib.sha256(cas_path.read_bytes()).hexdigest()==receipt1["payload"]["cas"]["sha256"],
 "truth":"Real encrypted TCP used between two separate processes on one physical host. Noise-inspired, not libp2p Noise wire compatibility and not a two-machine deployment."
}
(HERE/"PROOF.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2));print(json.dumps(proof,ensure_ascii=False,indent=2))
