from __future__ import annotations
import hashlib, json, re, sqlite3, time
from pathlib import Path
from harum_identity import sign, verify, canonical

def normalize_task(s: str) -> str: return re.sub(r'\s+',' ',s.strip().lower())
def task_fingerprint(task: str) -> str: return hashlib.sha256(normalize_task(task).encode()).hexdigest()
def capsule_id(signed: dict) -> str: return hashlib.sha256(canonical(signed)).hexdigest()
def make_lesson(identity: dict, *, task_class: str, task: str, action: str, source_model: str, judge_score: float=1.0, evidence=None, tags=None) -> dict:
    payload={'type':'harum.lesson.v1','task_class':task_class,'task':task,'task_fingerprint':task_fingerprint(task),'action':action,'source_model':source_model,'judge_score':float(judge_score),'evidence':evidence or [],'tags':sorted(set(tags or [])),'created':time.time()}
    signed=sign(identity,payload); return {'lesson_id':capsule_id(signed),'signed':signed}
class Store:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        c=self.conn();c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS lessons(lesson_id TEXT PRIMARY KEY,task_class TEXT NOT NULL,task TEXT NOT NULL,task_fp TEXT NOT NULL,action TEXT NOT NULL,source_model TEXT NOT NULL,validator TEXT NOT NULL,judge_score REAL NOT NULL,signed_json TEXT NOT NULL,created REAL NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_lessons_fp ON lessons(task_fp);
        CREATE INDEX IF NOT EXISTS idx_lessons_class ON lessons(task_class);
        CREATE TABLE IF NOT EXISTS rules(task_class TEXT PRIMARY KEY,action TEXT,state TEXT NOT NULL,support_count INTEGER NOT NULL,model_count INTEGER NOT NULL,validator_count INTEGER NOT NULL,evidence_root TEXT NOT NULL,updated REAL NOT NULL);
        """);c.commit();c.close()
    def conn(self): c=sqlite3.connect(self.path,timeout=30);c.row_factory=sqlite3.Row;return c
    def add(self,capsule):
        signed=capsule['signed'];v=verify(signed)
        if not v.get('valid'): raise ValueError('invalid lesson signature')
        p=signed['payload']
        if p.get('type')!='harum.lesson.v1': raise ValueError('wrong lesson type')
        lid=capsule_id(signed)
        if lid!=capsule['lesson_id']: raise ValueError('lesson id mismatch')
        if p['task_fingerprint']!=task_fingerprint(p['task']): raise ValueError('task fingerprint mismatch')
        c=self.conn();c.execute('INSERT OR IGNORE INTO lessons VALUES(?,?,?,?,?,?,?,?,?,?)',(lid,p['task_class'],p['task'],p['task_fingerprint'],p['action'],p['source_model'],v['issuer'],float(p['judge_score']),json.dumps(capsule,ensure_ascii=False),float(p['created'])));c.commit();c.close();return lid
    def inventory(self):
        c=self.conn();ids=[r['lesson_id'] for r in c.execute('SELECT lesson_id FROM lessons ORDER BY lesson_id')];c.close();return ids
    def get_capsule(self,lid):
        c=self.conn();r=c.execute('SELECT signed_json FROM lessons WHERE lesson_id=?',(lid,)).fetchone();c.close();return json.loads(r['signed_json']) if r else None
    def exact(self,task):
        fp=task_fingerprint(task);c=self.conn();rows=[dict(r) for r in c.execute('SELECT * FROM lessons WHERE task_fp=? AND judge_score>=1.0 ORDER BY created DESC',(fp,))];c.close();return rows
    def by_class(self,task_class):
        c=self.conn();rows=[dict(r) for r in c.execute('SELECT * FROM lessons WHERE task_class=? AND judge_score>=1.0 ORDER BY created',(task_class,))];c.close();return rows
    def put_rule(self,task_class,action,state,support_count,model_count,validator_count,root):
        c=self.conn();c.execute('INSERT INTO rules VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(task_class) DO UPDATE SET action=excluded.action,state=excluded.state,support_count=excluded.support_count,model_count=excluded.model_count,validator_count=excluded.validator_count,evidence_root=excluded.evidence_root,updated=excluded.updated',(task_class,action,state,support_count,model_count,validator_count,root,time.time()));c.commit();c.close()
    def rule(self,task_class):
        c=self.conn();r=c.execute('SELECT * FROM rules WHERE task_class=?',(task_class,)).fetchone();c.close();return dict(r) if r else None
    def rules(self):
        c=self.conn();rows=[dict(r) for r in c.execute('SELECT * FROM rules ORDER BY task_class')];c.close();return rows
