from __future__ import annotations
import json,re,sqlite3,time,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
DB=HERE/"runtime"/"lessons.db"
def conn():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
    c.executescript("""PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS lessons(id TEXT PRIMARY KEY,task TEXT NOT NULL,decision TEXT NOT NULL,
    expected_tool TEXT,source_model TEXT NOT NULL,judge_score REAL NOT NULL,approved INTEGER NOT NULL,created REAL NOT NULL);""")
    return c
def put(task,decision,expected_tool,source_model,judge_score):
    if judge_score<1.0:return None
    body=json.dumps(decision,ensure_ascii=False,sort_keys=True)
    i=hashlib.sha256((task+body+source_model).encode()).hexdigest()[:24]
    c=conn();c.execute("INSERT OR IGNORE INTO lessons VALUES(?,?,?,?,?,?,1,?)",(i,task,body,expected_tool,source_model,judge_score,time.time()));c.commit();c.close();return i
def toks(s):return set(re.findall(r"[a-zA-Z0-9_]+",s.lower()))
def search(task,limit=3):
    q=toks(task);c=conn();rows=[dict(r) for r in c.execute("SELECT * FROM lessons WHERE approved=1")];c.close()
    for r in rows:
        t=toks(r["task"]);r["similarity"]=len(q&t)/max(1,len(q|t));r["decision"]=json.loads(r["decision"])
    rows.sort(key=lambda x:(-x["similarity"],-x["judge_score"],-x["created"]))
    return rows[:limit]
