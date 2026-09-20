from __future__ import annotations
import hashlib
from collections import defaultdict
from harum_crystal_store import Store

def root(ids): return hashlib.sha256(''.join(sorted(ids)).encode()).hexdigest()
def crystallize(store: Store, task_class: str, min_support=3, min_models=2, min_validators=2):
    rows=store.by_class(task_class);actions=defaultdict(list)
    for r in rows: actions[r['action']].append(r)
    all_ids=[r['lesson_id'] for r in rows]
    if not rows:
        store.put_rule(task_class,None,'insufficient',0,0,0,root([]));return store.rule(task_class)
    if len(actions)>1:
        store.put_rule(task_class,None,'conflicted',len(rows),len({r['source_model'] for r in rows}),len({r['validator'] for r in rows}),root(all_ids));return store.rule(task_class)
    action,next_rows=next(iter(actions.items()));models=len({r['source_model'] for r in next_rows});validators=len({r['validator'] for r in next_rows})
    state='active' if len(next_rows)>=min_support and models>=min_models and validators>=min_validators else 'insufficient'
    store.put_rule(task_class,action,state,len(next_rows),models,validators,root(all_ids));return store.rule(task_class)
def decide(store: Store, task: str, task_class: str):
    exact=store.exact(task)
    if exact:
        acts={r['action'] for r in exact}
        if len(acts)==1:return {'route':'exact_crystal','action':next(iter(acts)),'llm_required':False,'evidence':[r['lesson_id'] for r in exact]}
    rule=store.rule(task_class)
    if rule and rule['state']=='active':return {'route':'class_rule','action':rule['action'],'llm_required':False,'evidence_root':rule['evidence_root']}
    return {'route':'needs_inference','action':None,'llm_required':True,'rule_state':rule['state'] if rule else None}
