#!/usr/bin/env python3
from __future__ import annotations
import argparse,base64,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
HERE=Path(__file__).resolve().parent
CAT=json.loads((HERE/'RECIPE_CATALOG.json').read_text())
def ub64(s):return base64.urlsafe_b64decode(s+'='*((4-len(s)%4)%4))
def stable(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def check_required(recipe,args):return [k for k in CAT['recipes'][recipe]['required'] if k not in args]

def verify_signed_manifest(sm):
    try:
        body={k:sm[k] for k in ('issuer','public_key','payload')};pub=ub64(sm['public_key'])
        if hashlib.sha256(pub).hexdigest()!=sm['issuer']:return False
        Ed25519PublicKey.from_public_bytes(pub).verify(ub64(sm['signature']),stable(body));return True
    except Exception:return False

def execute(recipe,args,dry_run=False):
    if recipe not in CAT['recipes']:return {'ok':False,'error':'unknown_recipe'}
    missing=check_required(recipe,args)
    if missing:return {'ok':False,'error':'missing_required','missing':missing}
    plan=CAT['recipes'][recipe]['steps']
    if dry_run:return {'ok':True,'recipe':recipe,'steps':plan,'dry_run':True}
    if recipe=='safe_hash':
        b=args['artifact_bytes'].encode() if isinstance(args['artifact_bytes'],str) else bytes(args['artifact_bytes'])
        return {'ok':True,'recipe':recipe,'sha256':hashlib.sha256(b).hexdigest()}
    if recipe=='artifact_verify':
        b=args['artifact_bytes'].encode() if isinstance(args['artifact_bytes'],str) else bytes(args['artifact_bytes']);digest=hashlib.sha256(b).hexdigest()
        if digest!=args['expected_sha256']:return {'ok':False,'error':'hash_mismatch','sha256':digest}
        if not verify_signed_manifest(args['signed_manifest']):return {'ok':False,'error':'bad_manifest_signature'}
        payload=args['signed_manifest']['payload']
        if payload.get('artifact_sha256')!=digest:return {'ok':False,'error':'manifest_hash_scope_mismatch'}
        return {'ok':True,'recipe':recipe,'sha256':digest,'signature_verified':True,'eligible_for_cas':True}
    return {'ok':True,'recipe':recipe,'delegated_steps':plan,'authority':'capability-gated-runtime'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('recipe');ap.add_argument('args_json');ap.add_argument('--dry-run',action='store_true')
    a=ap.parse_args();print(json.dumps(execute(a.recipe,json.loads(a.args_json),a.dry_run),indent=2))