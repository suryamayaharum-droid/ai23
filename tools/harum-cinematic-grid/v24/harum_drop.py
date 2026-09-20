from __future__ import annotations
import hashlib,json,zipfile,time
from pathlib import Path
from harum_crystal_store import Store

def export_drop(store:Store,ids,out):
    capsules=[store.get_capsule(lid) for lid in ids if store.get_capsule(lid)]
    manifest={'format':'harum.crystal.drop.v1','created':time.time(),'lesson_ids':[c['lesson_id'] for c in capsules]};manifest['root']=hashlib.sha256(''.join(sorted(manifest['lesson_ids'])).encode()).hexdigest();out=Path(out)
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
        for c in capsules:z.writestr(f"lessons/{c['lesson_id']}.json",json.dumps(c,ensure_ascii=False,indent=2))
    return manifest
def import_drop(store:Store,path):
    accepted=[]
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json'));ids=sorted(m['lesson_ids']);root=hashlib.sha256(''.join(ids).encode()).hexdigest()
        if root!=m['root']:raise ValueError('drop root mismatch')
        for lid in ids:
            c=json.loads(z.read(f'lessons/{lid}.json'));store.add(c);accepted.append(lid)
    return {'accepted':accepted,'inventory':store.inventory()}
