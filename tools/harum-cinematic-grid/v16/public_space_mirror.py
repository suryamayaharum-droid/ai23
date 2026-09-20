#!/usr/bin/env python3
"""Public/read-only space mirror. No spacecraft command/control functions."""
from __future__ import annotations
import argparse,json,time,urllib.parse,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
CACHE=HERE/"runtime"/"space_cache";CACHE.mkdir(parents=True,exist_ok=True)
UA="HarumPublicSpaceMirror/1.0"
def fetch(url,key,min_age=0):
    p=CACHE/(key+".json")
    if p.exists() and time.time()-p.stat().st_mtime<min_age:return json.loads(p.read_text())
    req=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(req,timeout=20) as r:data=json.loads(r.read())
    p.write_text(json.dumps(data,ensure_ascii=False));return data
def satnogs(resource,limit=50):
    allowed={"satellites","tle","telemetry","transmitters","modes","artifacts","optical-observations"}
    if resource not in allowed:raise ValueError("resource not allowed")
    d=fetch(f"https://db.satnogs.org/api/{resource}/",f"satnogs_{resource}",300)
    if isinstance(d,dict) and "results" in d:d["results"]=d["results"][:limit]
    elif isinstance(d,list):d=d[:limit]
    return d
def celestrak(query,value,fmt="JSON"):
    if query not in {"CATNR","INTDES","GROUP","NAME","SPECIAL"}:raise ValueError("query not allowed")
    q=urllib.parse.urlencode({query:value,"FORMAT":fmt})
    return fetch("https://celestrak.org/NORAD/elements/gp.php?"+q,"celestrak_"+query+"_"+str(value).replace("/","_"),7200)
if __name__=="__main__":
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    s=sp.add_parser("satnogs");s.add_argument("resource");s.add_argument("--limit",type=int,default=50)
    c=sp.add_parser("celestrak");c.add_argument("query");c.add_argument("value")
    a=ap.parse_args();res=satnogs(a.resource,a.limit) if a.cmd=="satnogs" else celestrak(a.query,a.value);print(json.dumps(res,ensure_ascii=False,indent=2))
