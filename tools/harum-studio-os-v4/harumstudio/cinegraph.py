DEPARTMENTS={
 "development":["story","research"],"art":["lookdev","reference"],
 "previs":["shot_design","camera"],"motion":["portrait_motion","i2v","lipsync","tracking"],
 "editorial":["edit","timeline","subtitles"],"sound":["tts","foley","mix"],
 "color":["grade","aces"],"qc":["technical_qc","continuity_qc","license_qc"],
 "distribution":["package","metadata","publish"]
}

def topological(tasks):
    by={t["id"]:t for t in tasks}
    deps={t["id"]:set(t.get("depends_on",[])) for t in tasks}
    out=[]
    while deps:
        ready=sorted(k for k,v in deps.items() if not v)
        if not ready: raise ValueError("cycle in task graph")
        for k in ready:
            out.append(by[k]); deps.pop(k)
        for v in deps.values(): v.difference_update(ready)
    return out

def scene_graph(scene):
    tasks=[]; prev=None
    for s in scene["shots"]:
        sid=s["shot_id"]; a=f"{sid}:prep"; b=f"{sid}:render"; c=f"{sid}:qc"
        tasks += [
          {"id":a,"department":"previs","kind":"shot_design","depends_on":[] if prev is None else [prev]},
          {"id":b,"department":"motion","kind":s["task"],"depends_on":[a]},
          {"id":c,"department":"qc","kind":"technical_qc","depends_on":[b]}
        ]
        prev=c
    tasks += [
      {"id":f'{scene["scene_id"]}:edit',"department":"editorial","kind":"edit","depends_on":[prev] if prev else []},
      {"id":f'{scene["scene_id"]}:sound',"department":"sound","kind":"mix","depends_on":[f'{scene["scene_id"]}:edit']},
      {"id":f'{scene["scene_id"]}:masterqc',"department":"qc","kind":"continuity_qc","depends_on":[f'{scene["scene_id"]}:sound']},
      {"id":f'{scene["scene_id"]}:package',"department":"distribution","kind":"package","depends_on":[f'{scene["scene_id"]}:masterqc']}
    ]
    return {"scene_id":scene["scene_id"],"tasks":tasks}
