#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,urllib.request,time
from pathlib import Path

HERE=Path(__file__).resolve().parent
SCHEMA=json.loads((HERE/'RECIPE_SCHEMA.json').read_text())
CAT=json.loads((HERE/'RECIPE_CATALOG.json').read_text())
ALLOWED=set(CAT['recipes'])

GUIDE = """
Choose exactly ONE recipe:
- artifact_verify: verify a signed artifact against an expected SHA-256 before accepting it.
- safe_hash: compute SHA-256 only; no signature verification.
- memory_read: read existing canonical memory; do not modify it.
- memory_append: append/write memory only through authorization gates.
- research_only: read/fetch public documentation or evidence without changing protected state.
- human_review: dangerous, ambiguous, unsupported, or authority-escalating request.
Return only JSON matching the supplied grammar. No prose outside JSON.
"""

def lexical_guard(mission):
    s=mission.lower()
    dangerous=(
      'arbitrary shell','run unknown code','credential guess','bypass quota',
      'scan unknown','satellite command','take over','disable guard','ignore authorization'
    )
    if any(x in s for x in dangerous):
        return {'recipe':'human_review','source':'guard','confidence':1.0}
    return None

def model_route(base_url,mission,max_tokens=64):
    payload={
      'model':'local',
      'messages':[
        {'role':'system','content':GUIDE},
        {'role':'user','content':mission}
      ],
      'temperature':0,
      'max_tokens':max_tokens,
      'reasoning_effort':'none',
      'chat_template_kwargs':{'enable_thinking':False},
      'json_schema':SCHEMA
    }
    req=urllib.request.Request(
      base_url.rstrip('/')+'/v1/chat/completions',
      data=json.dumps(payload).encode(),
      headers={'Content-Type':'application/json'}
    )
    started=time.perf_counter()
    with urllib.request.urlopen(req,timeout=300) as r:
        data=json.loads(r.read())
    msg=data['choices'][0]['message']
    raw=(msg.get('content') or '').strip()
    if not raw:
        raw=(msg.get('reasoning_content') or '').strip()
    try:
        obj=json.loads(raw)
    except Exception as e:
        raise ValueError(f'json_parse:{raw[:180]!r}') from e
    if not isinstance(obj,dict) or set(obj)!={'recipe'} or obj['recipe'] not in ALLOWED:
        raise ValueError(f'invalid_recipe_shape:{obj!r}')
    return {
      'recipe':obj['recipe'],
      'source':'local_llm',
      'confidence':None,
      'elapsed_seconds':round(time.perf_counter()-started,3)
    }

def route(base_url,mission):
    guarded=lexical_guard(mission)
    if guarded:
        return guarded
    try:
        return model_route(base_url,mission)
    except Exception as e:
        return {
          'recipe':'human_review',
          'source':'fallback',
          'confidence':0.0,
          'error':type(e).__name__,
          'detail':str(e)[:240]
        }

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('mission')
    ap.add_argument('--base-url',default='http://127.0.0.1:8080')
    a=ap.parse_args()
    print(json.dumps(route(a.base_url,a.mission),ensure_ascii=False,indent=2))
