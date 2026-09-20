#!/usr/bin/env python3
"""Read-only public SatNOGS data adapter. Never transmits spacecraft commands."""
from __future__ import annotations
import argparse,json,urllib.parse,urllib.request
BASE='https://db.satnogs.org/api'
ALLOWED={'satellites','tle','telemetry','transmitters','modes','artifacts','optical-observations'}
def get(resource,limit=25):
    if resource not in ALLOWED: raise ValueError('resource not allowed')
    req=urllib.request.Request(f'{BASE}/{resource}/',headers={'User-Agent':'HarumPublicSpaceSensor/1.0'})
    with urllib.request.urlopen(req,timeout=20) as r:data=json.loads(r.read())
    if isinstance(data,dict) and 'results' in data:data['results']=data['results'][:limit]
    elif isinstance(data,list):data=data[:limit]
    return data
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('resource',choices=sorted(ALLOWED)); ap.add_argument('--limit',type=int,default=25); a=ap.parse_args()
    print(json.dumps(get(a.resource,a.limit),ensure_ascii=False,indent=2))