#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
CARRIERS=[
 ("local_file_drop",{"offline":5,"intermittent":5,"nat":5,"low_bw":4,"cost":5,"artifact":5}),
 ("local_lan",{"offline":5,"intermittent":2,"nat":5,"low_bw":3,"cost":5,"artifact":4}),
 ("reticulum",{"offline":5,"intermittent":5,"nat":4,"low_bw":5,"cost":5,"artifact":2}),
 ("libp2p",{"offline":2,"intermittent":3,"nat":5,"low_bw":2,"cost":4,"artifact":4}),
 ("iroh",{"offline":2,"intermittent":3,"nat":5,"low_bw":2,"cost":4,"artifact":5}),
 ("gnunet",{"offline":2,"intermittent":3,"nat":3,"low_bw":2,"cost":5,"artifact":3}),
 ("scion",{"offline":1,"intermittent":2,"nat":2,"low_bw":2,"cost":3,"artifact":4}),
 ("syncthing",{"offline":2,"intermittent":4,"nat":4,"low_bw":2,"cost":5,"artifact":5}),
 ("ipfs",{"offline":1,"intermittent":3,"nat":3,"low_bw":1,"cost":4,"artifact":5}),
 ("tor_i2p_known_peers",{"offline":1,"intermittent":2,"nat":5,"low_bw":2,"cost":4,"artifact":2})
]
def rank(c):
    rows=[]
    for name,m in CARRIERS:
        s=sum(float(w)*m.get(k,0) for k,w in c.items())
        rows.append({"carrier":name,"score":round(s,2)})
    rows.sort(key=lambda x:-x["score"]);return rows
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("conditions_json");a=ap.parse_args()
    print(json.dumps(rank(json.loads(a.conditions_json)),indent=2))
