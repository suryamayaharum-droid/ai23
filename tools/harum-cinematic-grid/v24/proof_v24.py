from pathlib import Path
import hashlib,json,shutil,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from harum_identity import generate_identity
from harum_crystal_store import Store, make_lesson
from harum_crystallizer import crystallize, decide
from harum_prefix_reconcile import reconcile
from harum_drop import export_drop, import_drop

rt=HERE/'runtime'/'ci-proof'
if rt.exists():shutil.rmtree(rt)
rt.mkdir(parents=True)
a=Store(rt/'A.db');b=Store(rt/'B.db')
ids=[generate_identity(x) for x in ('A','B','C')]
examples=[('Check bytes against the manifest SHA-256.','fast'),('Confirm artifact integrity from SHA-256.','deep'),('Verify file bytes match the manifest digest.','browser')]
for (task,model),ident in zip(examples,ids):
    a.add(make_lesson(ident,task_class='artifact_integrity',task=task,action='verify_hash',source_model=model,judge_score=1.0,evidence=['judge-pass']))
rule=crystallize(a,'artifact_integrity')
assert rule['state']=='active'
assert decide(a,'Hash-check another immutable artifact.','artifact_integrity')['llm_required'] is False
for i,(action,model) in enumerate([('verify_signature','fast'),('verify_signature','deep'),('verify_hash','browser')]):
    a.add(make_lesson(ids[i],task_class='peer_authorship',task=f'Authorship {i}',action=action,source_model=model,judge_score=1.0,evidence=['judge-pass']))
assert crystallize(a,'peer_authorship')['state']=='conflicted'
r0=reconcile(a.inventory(),b.inventory());drop=rt/'sync.crystaldrop';export_drop(a,r0['missing_at_b'],drop);import_drop(b,drop);r1=reconcile(a.inventory(),b.inventory());assert not r1['missing_at_a'] and not r1['missing_at_b']
shared=[hashlib.sha256(f's:{i}'.encode()).hexdigest() for i in range(9990)]
a_only=[hashlib.sha256(f'a:{i}'.encode()).hexdigest() for i in range(5)]
b_only=[hashlib.sha256(f'b:{i}'.encode()).hexdigest() for i in range(7)]
large=reconcile(shared+a_only,shared+b_only)
assert set(large['missing_at_a'])==set(b_only) and set(large['missing_at_b'])==set(a_only)
proof={'active_rule':True,'contradiction_quarantined':True,'drop_converged':True,'large_reconciliation':large['stats']}
(HERE/'CI_PROOF.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof,indent=2))
