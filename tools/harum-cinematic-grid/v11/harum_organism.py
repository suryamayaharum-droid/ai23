#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, re, sqlite3, time
from pathlib import Path
from collections import defaultdict

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DB=HERE/'runtime'/'organism.db'
CAPSULES=HERE/'runtime'/'holographic_capsules.jsonl'
EVENTS=HERE/'runtime'/'organism_events.jsonl'
OUT=HERE/'runtime'/'artifacts';OUT.mkdir(parents=True,exist_ok=True)

ORGANS={
 'executive':['plan','prioritize','synthesize'],'research':['research','technology','evidence'],
 'memory':['index','retrieve','continuity'],'brand':['brand','semiotics','identity'],
 'narrative':['story','continuity','open_loops'],'image':['prompts','references','image_qc'],
 'cinema':['shots','editing','video_qc'],'audio':['voice','music','foley'],
 'publishing':['instagram','youtube','metadata'],'growth':['seo','metrics','experiments'],
 'commerce':['products','offers','checkout'],'web':['site','hotmart','vercel'],
 'automation':['event_bus','workflow','scheduler'],'infrastructure':['code','runtime','dependencies'],
 'security':['secrets','licenses','integrity'],'quality':['regression','benchmarks','acceptance']}
CELLS_PER_ORGAN=24
KEYWORDS={
 'executive':['architecture','state','plan','priority'],'research':['research','state_of_the_art','technology','model'],
 'memory':['context','memory','canon','estado','source of truth'],'brand':['brand','palette','harum noir','arte harum','face lock'],
 'narrative':['story','arco','chapter','narrative','noir loop'],'image':['prompt','image','face lock','reference'],
 'cinema':['cinema','video','shot','render','ffmpeg','opencv'],'audio':['audio','voice','music','foley','tts'],
 'publishing':['instagram','youtube','publish','caption','short'],'growth':['seo','metric','analytics','retention','experiment'],
 'commerce':['commerce','product','checkout','price','offer'],'web':['site','hotmart','vercel','landing','web'],
 'automation':['automation','event','queue','workflow','runtime','swarm'],'infrastructure':['github','python','sqlite','import','dependency'],
 'security':['secret','license','token','permission','integrity'],'quality':['qc','benchmark','test','acceptance','regression']}

SCHEMA="""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS cells(id TEXT PRIMARY KEY,organ TEXT NOT NULL,status TEXT NOT NULL,capabilities TEXT NOT NULL,last_seen REAL NOT NULL,last_task TEXT,meta TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS blackboard(key TEXT PRIMARY KEY,value TEXT NOT NULL,clock INTEGER NOT NULL,author TEXT NOT NULL,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS pheromones(topic TEXT PRIMARY KEY,strength REAL NOT NULL,half_life REAL NOT NULL,updated REAL NOT NULL,meta TEXT NOT NULL DEFAULT '{}');
CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,mission TEXT NOT NULL,organ TEXT NOT NULL,status TEXT NOT NULL,priority REAL NOT NULL,preferred_cell TEXT,payload TEXT NOT NULL,result TEXT,error TEXT,created REAL NOT NULL,updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT UNIQUE NOT NULL,ts REAL NOT NULL,actor TEXT NOT NULL,topic TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS missions(id TEXT PRIMARY KEY,title TEXT NOT NULL,status TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL,meta TEXT NOT NULL DEFAULT '{}');
"""

def conn():
    c=sqlite3.connect(DB,timeout=30,check_same_thread=False);c.row_factory=sqlite3.Row;c.executescript(SCHEMA);return c
def stable(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def event(actor,topic,payload):
    ts=time.time();eid=hashlib.sha256((actor+topic+stable(payload)+str(ts)).encode()).hexdigest()
    c=conn();c.execute('INSERT OR IGNORE INTO events(event_id,ts,actor,topic,payload) VALUES(?,?,?,?,?)',(eid,ts,actor,topic,stable(payload)));c.commit();c.close()
    with EVENTS.open('a',encoding='utf-8') as f:f.write(json.dumps({'id':eid,'ts':ts,'actor':actor,'topic':topic,'payload':payload},ensure_ascii=False)+'\n')
def merkle_root(items):
    hs=[hashlib.sha256(x.encode()).digest() for x in sorted(items)]
    if not hs:return hashlib.sha256(b'').hexdigest()
    while len(hs)>1:
        if len(hs)%2:hs.append(hs[-1])
        hs=[hashlib.sha256(hs[i]+hs[i+1]).digest() for i in range(0,len(hs),2)]
    return hs[0].hex()
def blackboard_put(key,value,author):
    c=conn();clock=(c.execute('SELECT max(clock) m FROM blackboard').fetchone()['m'] or 0)+1
    c.execute('INSERT INTO blackboard(key,value,clock,author,updated) VALUES(?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,clock=excluded.clock,author=excluded.author,updated=excluded.updated',(key,stable(value),clock,author,time.time()));c.commit();c.close();event(author,'blackboard/'+key,{'clock':clock})
def pheromone(topic,delta,half_life=900,meta=None):
    now=time.time();c=conn();r=c.execute('SELECT * FROM pheromones WHERE topic=?',(topic,)).fetchone()
    if r:
        age=max(0,now-r['updated']);strength=r['strength']*(0.5**(age/max(1,r['half_life'])))+delta
        c.execute('UPDATE pheromones SET strength=?,half_life=?,updated=?,meta=? WHERE topic=?',(strength,half_life,now,stable(meta or {}),topic))
    else:
        strength=delta;c.execute('INSERT INTO pheromones(topic,strength,half_life,updated,meta) VALUES(?,?,?,?,?)',(topic,strength,half_life,now,stable(meta or {})))
    c.commit();c.close();return strength
def roots():
    c=conn();bb=[r['key']+'='+r['value']+'@'+str(r['clock']) for r in c.execute('SELECT * FROM blackboard')];ev=[r['event_id'] for r in c.execute('SELECT event_id FROM events')];cells=[r['id']+':'+r['capabilities'] for r in c.execute('SELECT id,capabilities FROM cells')];c.close()
    return {'blackboard_root':merkle_root(bb),'event_root':merkle_root(ev),'capability_root':merkle_root(cells)}
def boot():
    c=conn();now=time.time();n=0
    for organ,caps in ORGANS.items():
        for i in range(CELLS_PER_ORGAN):
            cid=f'{organ}.cell.{i:02d}';c.execute('INSERT OR REPLACE INTO cells(id,organ,status,capabilities,last_seen,meta) VALUES(?,?,?,?,?,?)',(cid,organ,'idle',stable(caps),now,stable({'tier':'logical-cell','physical_compute':False})));n+=1
    c.commit();c.close()
    blackboard_put('organism/capability_map',ORGANS,'executive.cell.00')
    blackboard_put('organism/policy',{'zero_extra_spend':True,'local_first':True,'no_quota_evasion':True,'truthful_compute':True},'executive.cell.00')
    return {'status':'online','logical_cells':n,'organs':len(ORGANS),**roots(),'physical_worker_cap':max(1,min(5,os.cpu_count() or 1))}
def files():
    exts={'.md','.json','.py','.yml','.yaml','.txt','.csv'}
    return [p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in exts and '__pycache__' not in p.parts and 'runtime/artifacts' not in p.as_posix()]
def seed(mid,title):
    ps=files();now=time.time();c=conn();c.execute('INSERT OR REPLACE INTO missions(id,title,status,created,updated,meta) VALUES(?,?,?,?,?,?)',(mid,title,'running',now,now,'{}'));idx=0
    for organ in ORGANS:
        of=[p for p in ps if any(k.replace(' ','_') in p.name.lower().replace(' ','_') for k in KEYWORDS[organ])];pool=of or ps
        for i in range(CELLS_PER_ORGAN):
            cid=f'{organ}.cell.{i:02d}';p=pool[(i+idx)%len(pool)];tid=f'{mid}:{cid}';payload={'path':str(p),'keywords':KEYWORDS[organ],'cell':cid}
            c.execute('INSERT OR REPLACE INTO tasks(id,mission,organ,status,priority,preferred_cell,payload,created,updated) VALUES(?,?,?,?,?,?,?,?,?)',(tid,mid,organ,'queued',50.0,cid,stable(payload),now,now));idx+=1
    c.commit();c.close();return len(ps)

SECRET_PATTERNS=[re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*[\'\"]?[A-Za-z0-9_\-]{16,}'),re.compile(r'(?i)cfat_[A-Za-z0-9]{20,}')]

def process(row):
    d=json.loads(row['payload']);p=Path(d['path']);organ=row['organ']
    try:text=p.read_text(encoding='utf-8',errors='ignore')
    except:text=''
    low=text.lower();counts={k:low.count(k.lower()) for k in d['keywords']}
    r={'cell':d['cell'],'organ':organ,'file':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),'bytes':p.stat().st_size if p.exists() else 0,'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None,'keyword_hits':sum(counts.values()),'counts':counts}
    if organ=='security':r['secret_like_patterns']=sum(1 for rx in SECRET_PATTERNS if rx.search(text))
    return row['id'],r
def synthesize(mid):
    c=conn();rows=list(c.execute('SELECT organ,result,status FROM tasks WHERE mission=?',(mid,)));c.close();agg=defaultdict(lambda:{'tasks':0,'complete':0,'keyword_hits':0,'bytes':0,'secret_like_patterns':0})
    for r in rows:
        a=agg[r['organ']];a['tasks']+=1;a['complete']+=r['status']=='complete'
        if r['result']:
            d=json.loads(r['result']);a['keyword_hits']+=d.get('keyword_hits',0);a['bytes']+=d.get('bytes',0);a['secret_like_patterns']+=d.get('secret_like_patterns',0)
    for organ,data in agg.items():blackboard_put('organ/'+organ+'/summary',data,f'{organ}.cell.00')
    rt=roots();routes={cap:o for o,caps in ORGANS.items() for cap in caps}
    with CAPSULES.open('w',encoding='utf-8') as f:
        for organ,caps in ORGANS.items():
            for i in range(CELLS_PER_ORGAN):
                f.write(json.dumps({'cell':f'{organ}.cell.{i:02d}','organ':organ,'capabilities':caps,'global_roots':rt,'routes':routes,'mission':mid,'holographic':True},ensure_ascii=False)+'\n')
    summary={'mission':mid,'organs':len(agg),'logical_cells':len(ORGANS)*CELLS_PER_ORGAN,'task_status':{s:sum(1 for r in rows if r['status']==s) for s in sorted({r['status'] for r in rows})},'organ_summaries':dict(agg),'roots':rt,'capsules':str(CAPSULES)}
    c=conn();c.execute('UPDATE missions SET status=?,updated=?,meta=? WHERE id=?',('complete',time.time(),stable({'capsules':str(CAPSULES),**rt}),mid));c.commit();c.close();return summary
def mission(mid,title):
    seen=seed(mid,title);c=conn();rows=[dict(r) for r in c.execute('SELECT * FROM tasks WHERE mission=? ORDER BY organ,id',(mid,))];c.close();workers=max(1,min(5,os.cpu_count() or 1));t=time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:results=list(ex.map(process,rows))
    c=conn();acc=defaultdict(lambda:{'hits':0,'security':0,'tasks':0})
    for tid,r in results:
        c.execute('UPDATE tasks SET status=?,result=?,updated=? WHERE id=?',('complete',stable(r),time.time(),tid));a=acc[r['organ']];a['hits']+=r.get('keyword_hits',0);a['security']+=r.get('secret_like_patterns',0);a['tasks']+=1
    c.commit();c.close()
    for organ,a in acc.items():
        pheromone('evidence/'+organ,min(10,a['hits']*.01),1800,{'tasks':a['tasks']})
        if a['security']:pheromone('alert/security',min(10,a['security']),3600,{'count':a['security']})
        event(f'{organ}.cell.00','organ/batch_complete',a)
    s=synthesize(mid);s.update({'physical_workers':workers,'elapsed_seconds':round(time.perf_counter()-t,3),'files_seen':seen});return s
def status():
    c=conn();o={'cells':c.execute('SELECT count(*) c FROM cells').fetchone()['c'],'cell_states':{r['status']:r['c'] for r in c.execute('SELECT status,count(*) c FROM cells GROUP BY status')},'blackboard_entries':c.execute('SELECT count(*) c FROM blackboard').fetchone()['c'],'events':c.execute('SELECT count(*) c FROM events').fetchone()['c'],'pheromones':{r['topic']:round(r['strength'],3) for r in c.execute('SELECT topic,strength FROM pheromones ORDER BY strength DESC LIMIT 30')}};c.close();o.update(roots());return o
def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='cmd',required=True);sp.add_parser('boot');sp.add_parser('status');m=sp.add_parser('mission');m.add_argument('title');m.add_argument('--id',default='organism-proof-v11');a=ap.parse_args()
    print(json.dumps(boot() if a.cmd=='boot' else status() if a.cmd=='status' else mission(a.id,a.title),ensure_ascii=False,indent=2,default=dict))
if __name__=='__main__':main()
