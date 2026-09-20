from __future__ import annotations
import base64, hashlib, json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

def b64(b: bytes) -> str: return base64.urlsafe_b64encode(b).decode().rstrip('=')
def ub64(s: str) -> bytes: return base64.urlsafe_b64decode(s + '='*((4-len(s)%4)%4))
def canonical(x) -> bytes: return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',',':')).encode()
def generate_identity(name: str) -> dict:
    priv=Ed25519PrivateKey.generate(); pub=priv.public_key()
    privb=priv.private_bytes(serialization.Encoding.Raw,serialization.PrivateFormat.Raw,serialization.NoEncryption())
    pubb=pub.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
    return {'name':name,'peer_id':hashlib.sha256(pubb).hexdigest(),'public_key':b64(pubb),'private_key':b64(privb)}
def sign(identity: dict, payload: dict) -> dict:
    body={'issuer':identity['peer_id'],'public_key':identity['public_key'],'payload':payload}
    sig=Ed25519PrivateKey.from_private_bytes(ub64(identity['private_key'])).sign(canonical(body))
    return {**body,'signature':b64(sig)}
def verify(signed: dict) -> dict:
    try:
        body={k:signed[k] for k in ('issuer','public_key','payload')}; pub=ub64(signed['public_key'])
        if hashlib.sha256(pub).hexdigest()!=signed['issuer']: return {'valid':False,'reason':'peer_id_mismatch'}
        Ed25519PublicKey.from_public_bytes(pub).verify(ub64(signed['signature']),canonical(body))
        return {'valid':True,'issuer':signed['issuer']}
    except Exception: return {'valid':False,'reason':'bad_signature'}
