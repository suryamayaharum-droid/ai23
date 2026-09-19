#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sqlite3, subprocess, shutil, time, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DB = HERE / 'runtime.db'
QUEUE = HERE / 'actions.jsonl'
OUT = HERE / 'outputs'
OUT.mkdir(exist_ok=True)

SCHEMA = """
CREATE TABLE IF NOT EXISTS runtime(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,ts REAL NOT NULL,event TEXT NOT NULL,payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,kind TEXT NOT NULL,status TEXT NOT NULL,payload TEXT NOT NULL,output TEXT,created REAL NOT NULL,updated REAL NOT NULL);
"""

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c

def emit(event, payload):
    c = db()
    c.execute('INSERT INTO events(ts,event,payload) VALUES(?,?,?)', (time.time(), event, json.dumps(payload, ensure_ascii=False)))
    c.commit(); c.close()

def set_state(k, v):
    c = db()
    c.execute('INSERT INTO runtime(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (k, json.dumps(v, ensure_ascii=False)))
    c.commit(); c.close()

def get_state():
    c = db()
    rows = {r['key']: json.loads(r['value']) for r in c.execute('SELECT key,value FROM runtime')}
    c.close(); return rows

def doctor():
    bins = ['python','ffmpeg','ffprobe','git','nvidia-smi']
    out = {b: shutil.which(b) for b in bins}
    gpu = None
    if out['nvidia-smi']:
        try:
            gpu = subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total','--format=csv,noheader'], text=True).strip()
        except Exception:
            pass
    return {'binaries': out, 'gpu': gpu, 'root': str(ROOT), 'runtime_db': str(DB)}

def boot():
    d = doctor()
    set_state('booted_at', time.time())
    set_state('doctor', d)
    set_state('mode', 'assistant-embedded-session-runtime')
    set_state('policy', {'zero_extra_spend': True, 'no_quota_evasion': True, 'external_actions_require_connected_tool_or_authorized_runtime': True})
    emit('boot', d)
    return {'status': 'online', 'mode': 'assistant-embedded-session-runtime', **d}

def queue_action(kind, payload, priority='normal'):
    action = {
        'id': hashlib.sha256((kind + json.dumps(payload, sort_keys=True, ensure_ascii=False) + str(time.time_ns())).encode()).hexdigest()[:16],
        'kind': kind, 'priority': priority, 'status': 'queued', 'created': time.time(), 'payload': payload
    }
    with QUEUE.open('a', encoding='utf-8') as f:
        f.write(json.dumps(action, ensure_ascii=False) + '\n')
    emit('action_queued', action)
    return action

def create_job(kind, payload):
    jid = hashlib.sha256((kind + json.dumps(payload, sort_keys=True, ensure_ascii=False) + str(time.time_ns())).encode()).hexdigest()[:16]
    now = time.time(); c = db()
    c.execute('INSERT INTO jobs(id,kind,status,payload,created,updated) VALUES(?,?,?,?,?,?)', (jid, kind, 'queued', json.dumps(payload, ensure_ascii=False), now, now))
    c.commit(); c.close(); emit('job_created', {'id': jid, 'kind': kind}); return jid

def update_job(jid, status, output=None):
    c = db()
    c.execute('UPDATE jobs SET status=?,output=COALESCE(?,output),updated=? WHERE id=?', (status, output, time.time(), jid))
    c.commit(); c.close(); emit('job_updated', {'id': jid, 'status': status, 'output': output})

def run_scene(project):
    project = Path(project).resolve(); jid = create_job('cpu_scene', {'project': str(project)})
    update_job(jid, 'running')
    p = subprocess.run([sys.executable, str(ROOT/'harum_cinematic.py'), str(project)], capture_output=True, text=True)
    if p.returncode:
        update_job(jid, 'failed'); raise SystemExit(p.stderr[-6000:])
    data = json.loads(p.stdout)
    update_job(jid, 'complete', data['render'])
    return {'job_id': jid, **data}

def qc(media):
    media = Path(media).resolve(); out = OUT / (media.stem + '.qc.json'); jid = create_job('qc', {'media': str(media)})
    update_job(jid, 'running')
    p = subprocess.run([sys.executable, str(ROOT/'harum_qc.py'), str(media), '--out', str(out)], capture_output=True, text=True)
    if p.returncode:
        update_job(jid, 'failed'); raise SystemExit(p.stderr[-6000:])
    update_job(jid, 'complete', str(out))
    report = json.loads(out.read_text(encoding='utf-8')) if out.exists() else {'raw': p.stdout}
    return {'job_id': jid, 'report': report, 'path': str(out)}

def plan_external(task, payload):
    mapping = {'image':'image_generate','gpu_video':'gpu_render','airtable':'airtable_update','github':'github_write','voice':'voice_generate','publish':'social_publish'}
    kind = mapping.get(task, task)
    return queue_action(kind, payload, 'high' if task in {'publish','gpu_video'} else 'normal')

def pending_actions():
    if not QUEUE.exists(): return []
    return [json.loads(x) for x in QUEUE.read_text(encoding='utf-8').splitlines() if x.strip()]

def jobs():
    c = db(); rows = [dict(r) for r in c.execute('SELECT id,kind,status,output,created,updated FROM jobs ORDER BY created DESC LIMIT 50')]; c.close(); return rows

def status():
    return {'state': get_state(), 'jobs': jobs(), 'pending_actions': pending_actions()[-20:]}

def main():
    ap = argparse.ArgumentParser(prog='harum-runtime')
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('boot'); sp.add_parser('doctor'); sp.add_parser('status')
    r = sp.add_parser('run-scene'); r.add_argument('project')
    q = sp.add_parser('qc'); q.add_argument('media')
    e = sp.add_parser('emit'); e.add_argument('task'); e.add_argument('payload_json')
    a = ap.parse_args()
    if a.cmd == 'boot': res = boot()
    elif a.cmd == 'doctor': res = doctor()
    elif a.cmd == 'status': res = status()
    elif a.cmd == 'run-scene': res = run_scene(a.project)
    elif a.cmd == 'qc': res = qc(a.media)
    else: res = plan_external(a.task, json.loads(a.payload_json))
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
