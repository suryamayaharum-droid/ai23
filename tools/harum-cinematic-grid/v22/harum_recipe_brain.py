#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,urllib.request,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/'RECIPE_SCHEMA.json').read_text())
CAT=json.loads((HERE/'RECIPE_CATALOG.json').read_text())
ALLOWED=set(CAT['recipes'])
RECIPE_GUIDE='; '.join(f"{k}={'/'.join(v['steps'])}" for k,v in CAT['recipes'].items())

def lexical_guard(mission):
    s=mission.lower()
    dangerous=('arbitrary shell','run unknown code','credential guess','bypass quota','scan unknown','satellite command','take over')
    if any(x in s for x in dangerous):
        return {'recipe':'human_review','confidence':1.0,'note':'deterministic danger guard','source':'guard'}
    return None

def model_route(base_url,mission,max_tokens=160):
    payload={'model':'local','messages':[
      {'role':'system','content':'Choose exactly one safe Harum recipe. You are advisory only. Return only JSON matching the supplied grammar. Recipes: '+RECIPE_GUIDE},
      {'role':'user','content':mission}],
      'temperature':0,'max_tokens':max_tokens,'reasoning_effort':'none',
      'chat_template_kwargs':{'enable_thinking':False},'json_schema':SCHEMA}
    req=urllib.request.Request(base_url.rstrip('/')+'/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    t=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as r:data=json.loads(r.read())
    raw=(data['choices'][0]['message'].get('content') or '').strip()
    obj=json.loads(raw)
    if set(obj)!={'recipe','confidence','note'} or obj['recipe'] not in ALLOWED or not 0<=float(obj['confidence'])<=1:
        raise ValueError('invalid recipe proposal')
    obj['source']='local_llm';obj['elapsed_seconds']=round(time.perf_counter()-t,3)
    return obj

def route(base_url,mission):
    g=lexical_guard(mission)
    if g:return g
    try:return model_route(base_url,mission)
    except Exception as e:return {'recipe':'human_review','confidence':0.0,'note':'routing fallback','source':'fallback','error':type(e).__name__}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mission');ap.add_argument('--base-url',default='http://127.0.0.1:8080')
    a=ap.parse_args();print(json.dumps(route(a.base_url,a.mission),ensure_ascii=False,indent=2))