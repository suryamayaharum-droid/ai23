#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BACKLOG=HERE/"city_backlog.json"
RUNTIME=HERE/"runtime"; RUNTIME.mkdir(exist_ok=True)
QUEUE=RUNTIME/"autopilot_external.jsonl"
STATE=RUNTIME/"autopilot_state.json"
from harum_otel import get_tracer, status as otel_status
tracer=get_tracer()
def files():
    exts={".md",".json",".py",".yml",".yaml",".txt",".csv"}
    return [p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in exts and "__pycache__" not in p.parts]
def queue_external(m):
    rec={"id":m["id"],"title":m["title"],"task":m["task"],"priority":m["priority"],"status":"queued","created":time.time()}
    with QUEUE.open("a",encoding="utf-8") as f:f.write(json.dumps(rec,ensure_ascii=False)+"\n")
    return rec
def index_project(m):
    ps=files(); canonical=[]
    for p in ps:
        n=p.name.lower()
        if any(x in n for x in ("contexto","estado","biblia","canon","engine","architecture","research","voice","face")): canonical.append(str(p.relative_to(ROOT)))
    out=RUNTIME/"HARUM_SOURCE_OF_TRUTH_INDEX_v8_1.md"
    out.write_text("\n".join(["# HARUM — Source of Truth Index v8.1","",f"Arquivos textuais indexados: {len(ps)}","","## Fontes prioritárias"]+[f"- \`{x}\`" for x in sorted(canonical)[:160]])+"\n",encoding="utf-8")
    return {"output":str(out),"indexed":len(ps),"canonical_candidates":len(canonical)}
def audit_identity(m):
    ps=files(); counts={"face_lock":0,"voice_lock":0,"brand":0,"noir":0}; matches=[]
    for p in ps:
        try:t=p.read_text(encoding="utf-8",errors="ignore").lower()
        except:continue
        hit=False
        for k,term in [("face_lock","face lock"),("voice_lock","voice lock"),("brand","arte harum"),("noir","harum noir")]:
            if term in t: counts[k]+=1; hit=True
        if hit and len(matches)<100:matches.append(str(p.relative_to(ROOT)))
    out=RUNTIME/"identity_audit.json"; data={"counts":counts,"sample_files":matches,"gate":"FACE > CABELO > ROUPA > PALETA > MOVIMENTO > VOZ > VERDADE > CTA"}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); return {"output":str(out),**data}
def runtime_census(m):
    cpu=os.cpu_count() or 1; mem=None
    try: kb=int(re.search(r"MemTotal:\\s+(\\d+)",Path("/proc/meminfo").read_text()).group(1)); mem=round(kb/1024/1024,2)
    except: pass
    gpu=[]
    if shutil.which("nvidia-smi"):
        try: gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader"],text=True).splitlines()
        except: pass
    data={"cpu":cpu,"memory_gb":mem,"gpu":gpu,"ffmpeg":bool(shutil.which("ffmpeg")),"python":sys.version.split()[0],"otel":otel_status()}
    out=RUNTIME/"runtime_census.json"; out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); return {"output":str(out),**data}
def metrics_plan(m):
    data={"loop":["publication metrics","video technical benchmark","identity/continuity QC","editorial review","router update"],"guard":"Autotune cannot remove cost/license/identity gates.","minimum_observation_rule":"Do not infer performance from a single post or tiny sample."}
    out=RUNTIME/"metrics_learning_loop.json"; out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); return {"output":str(out),**data}
LOCAL={"index_project":index_project,"audit_identity":audit_identity,"runtime_census":runtime_census,"metrics_plan":metrics_plan}
def run_one(m):
    with tracer.start_as_current_span(f"mission.{m['id']}") as span:
        span.set_attribute("harum.priority",m["priority"]); span.set_attribute("harum.mode",m["mode"]); t=time.perf_counter()
        r=queue_external(m) if m["mode"]=="external" else LOCAL[m["task"]](m)
        return {"id":m["id"],"status":"queued_external" if m["mode"]=="external" else "complete","elapsed":round(time.perf_counter()-t,4),"result":r}
def cycle():
    plan=json.loads(BACKLOG.read_text(encoding="utf-8"))["missions"]; state={"updated":time.time(),"complete":[],"queued_external":[],"blocked":[]}; done=set(); pending={m["id"]:m for m in plan}
    while pending:
        ready=[m for m in pending.values() if set(m.get("deps",[]))<=done]
        if not ready: state["blocked"]+=list(pending); break
        ready.sort(key=lambda x:-x["priority"]); local=[m for m in ready if m["mode"]=="local"]; external=[m for m in ready if m["mode"]=="external"]
        if local:
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(local),max(1,os.cpu_count() or 1))) as ex:
                for r in ex.map(run_one,local): state["complete"].append(r); done.add(r["id"]); pending.pop(r["id"],None)
        for m in external:
            r=run_one(m); state["queued_external"].append(r); done.add(r["id"]); pending.pop(r["id"],None)
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8"); return state
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("cmd",choices=["cycle","status"]); a=ap.parse_args()
    print(json.dumps(cycle() if a.cmd=="cycle" else json.loads(STATE.read_text()) if STATE.exists() else {},ensure_ascii=False,indent=2))
