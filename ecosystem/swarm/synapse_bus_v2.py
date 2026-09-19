#!/usr/bin/env python3
from __future__ import annotations
import fnmatch, json, sqlite3, time, uuid
from pathlib import Path
from typing import Any

HERE=Path(__file__).resolve().parent

class SynapseBusV2:
    def __init__(self, db: sqlite3.Connection):
        self.db=db
        self.db.row_factory=sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS synapse_subscriptions_v2(
          subscriber TEXT NOT NULL,
          pattern TEXT NOT NULL,
          PRIMARY KEY(subscriber,pattern)
        );
        CREATE TABLE IF NOT EXISTS synapse_inbox_v2(
          delivery_id TEXT PRIMARY KEY,
          subscriber TEXT NOT NULL,
          event_id TEXT NOT NULL,
          topic TEXT NOT NULL,
          source TEXT NOT NULL,
          correlation_id TEXT,
          payload_json TEXT NOT NULL,
          organism_digest TEXT,
          status TEXT NOT NULL DEFAULT 'PENDING',
          created_at INTEGER NOT NULL,
          UNIQUE(subscriber,event_id)
        );
        """)
        self.db.commit()

    def seed(self, path: Path|None=None) -> int:
        data=json.loads((path or HERE/"config"/"synapses.json").read_text(encoding="utf-8"))
        count=0
        for item in data["subscriptions"]:
            for pattern in item["topics"]:
                self.db.execute(
                    "INSERT OR IGNORE INTO synapse_subscriptions_v2(subscriber,pattern) VALUES(?,?)",
                    (item["cell"],pattern)
                )
                count+=1
        self.db.commit()
        return count

    def subscribers(self, topic: str) -> list[str]:
        rows=self.db.execute("SELECT subscriber,pattern FROM synapse_subscriptions_v2").fetchall()
        out=set()
        for r in rows:
            if fnmatch.fnmatchcase(topic,r["pattern"]):
                out.add(r["subscriber"])
        return sorted(out)

    def publish(self, *, topic: str, source: str, payload: dict[str,Any],
                organism_digest: str|None=None, correlation_id: str|None=None) -> dict[str,Any]:
        event_id=str(uuid.uuid4())
        corr=correlation_id or str(uuid.uuid4())
        now=int(time.time())
        delivered=[]
        for subscriber in self.subscribers(topic):
            if subscriber==source:
                continue
            did=str(uuid.uuid4())
            self.db.execute(
                """INSERT OR IGNORE INTO synapse_inbox_v2
                   (delivery_id,subscriber,event_id,topic,source,correlation_id,
                    payload_json,organism_digest,status,created_at)
                   VALUES(?,?,?,?,?,?,?,?, 'PENDING',?)""",
                (did,subscriber,event_id,topic,source,corr,
                 json.dumps(payload,ensure_ascii=False,sort_keys=True),
                 organism_digest,now)
            )
            delivered.append(subscriber)
        self.db.commit()
        return {"event_id":event_id,"correlation_id":corr,"topic":topic,"delivered":delivered}

    def pull(self, cell_id: str, limit: int=50) -> list[dict[str,Any]]:
        rows=self.db.execute(
            """SELECT * FROM synapse_inbox_v2
               WHERE subscriber=? AND status='PENDING'
               ORDER BY created_at,delivery_id LIMIT ?""",(cell_id,limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def ack(self, cell_id: str, delivery_id: str) -> None:
        self.db.execute(
            """UPDATE synapse_inbox_v2 SET status='ACK'
               WHERE subscriber=? AND delivery_id=?""",(cell_id,delivery_id)
        )
        self.db.commit()

    def stats(self) -> dict[str,int]:
        rows=self.db.execute(
            "SELECT status,COUNT(*) n FROM synapse_inbox_v2 GROUP BY status"
        ).fetchall()
        return {r["status"]:r["n"] for r in rows}
