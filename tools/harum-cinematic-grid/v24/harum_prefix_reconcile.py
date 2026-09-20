from __future__ import annotations
import hashlib

def digest(ids):
    h=hashlib.sha256()
    for x in sorted(ids):h.update(bytes.fromhex(x))
    return h.digest()
def reconcile(a_ids,b_ids,leaf_threshold=8,max_depth=16):
    A=sorted(set(a_ids));B=sorted(set(b_ids));stats={'summary_messages':0,'summary_bytes':0,'leaf_id_bytes':0,'nodes':0};missing_at_a=set();missing_at_b=set()
    def walk(a,b,prefix,depth):
        stats['nodes']+=1;pb=(len(prefix)+1)//2;stats['summary_messages']+=2;stats['summary_bytes']+=2*(4+2+pb+32)
        if len(a)==len(b) and digest(a)==digest(b):return
        if len(a)+len(b)<=leaf_threshold or depth>=max_depth:
            stats['leaf_id_bytes']+=32*(len(a)+len(b));sa,sb=set(a),set(b);missing_at_a.update(sb-sa);missing_at_b.update(sa-sb);return
        for nib in '0123456789abcdef':
            aa=[x for x in a if len(x)>depth and x[depth]==nib];bb=[x for x in b if len(x)>depth and x[depth]==nib]
            if aa or bb:walk(aa,bb,prefix+nib,depth+1)
    walk(A,B,'',0);stats['wire_bytes_estimate']=stats['summary_bytes']+stats['leaf_id_bytes'];stats['full_inventory_bytes']=32*(len(A)+len(B));stats['reduction_ratio']=round(1-stats['wire_bytes_estimate']/max(1,stats['full_inventory_bytes']),6)
    return {'missing_at_a':sorted(missing_at_a),'missing_at_b':sorted(missing_at_b),'stats':stats}
