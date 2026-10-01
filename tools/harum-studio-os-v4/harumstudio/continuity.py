import json
from pathlib import Path
from datetime import datetime,timezone
class ContinuityMemory:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.data=json.loads(self.path.read_text()) if self.path.exists() else {"schema":"harum.continuity/1","canon":{},"scenes":{}}
    def save(self):
        self.data["updated_at"]=datetime.now(timezone.utc).isoformat()
        self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2))
    def set_canon(self,key,value):
        self.data["canon"][key]=value; self.save()
    def scene(self,scene_id):
        return self.data["scenes"].setdefault(scene_id,{"facts":{},"shots":{},"open_loops":[]})
    def shot_result(self,scene_id,shot_id,result):
        self.scene(scene_id)["shots"][shot_id]=result; self.save()
