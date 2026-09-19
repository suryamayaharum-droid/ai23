from __future__ import annotations
import json
from pathlib import Path
DEFAULT_WEIGHTS={"quality":0.28,"identity":0.30,"speed":0.12,"license":0.18,"cost":0.12}
class DecisionEngine:
    def __init__(self,registry_path,weights=None):
        self.engines=json.loads(Path(registry_path).read_text())["engines"]
        self.weights=weights or DEFAULT_WEIGHTS
    def score(self,e,task,vram,global_publish=True):
        if task not in e["tasks"] or e["min_vram"]>vram:return None
        if global_publish and e["license"]<0.5:return None
        score=sum(float(e[k])*w for k,w in self.weights.items())
        if task in {"portrait_motion","lipsync","multi_reference","i2v"}:
            score-=max(0,0.82-e["identity"])*0.35
        return round(score,4)
    def rank(self,task,vram=0,global_publish=True,limit=5):
        rows=[]
        for e in self.engines:
            s=self.score(e,task,vram,global_publish)
            if s is not None:rows.append({"engine":e["id"],"score":s,**e})
        return sorted(rows,key=lambda x:x["score"],reverse=True)[:limit]
