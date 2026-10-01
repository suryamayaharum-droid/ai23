from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from repository_organism import RepositoryOrganism


def _stable(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class RepositorySynapticBus:
    """Durable capability-routed bus for the repository organism.

    The bus stores messages and receipts only. It never imports or executes
    repository code. A runtime adapter must claim a message for the selected
    component and perform bounded work separately.
    """

    def __init__(self, db_path: str | Path, organism: RepositoryOrganism) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.organism = organism
        c = self._conn()
        c.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS messages(
                id TEXT PRIMARY KEY,
                created REAL NOT NULL,
                source TEXT NOT NULL,
                capability TEXT NOT NULL,
                target TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                claimed REAL,
                claim_token TEXT,
                attempts INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS receipts(
                id TEXT PRIMARY KEY,
                message_id TEXT NOT NULL,
                created REAL NOT NULL,
                target TEXT NOT NULL,
                result TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_messages_target_status
              ON messages(target,status,created);
            """
        )
        c.commit()
        c.close()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    def emit(self, source: str, capability: str, payload: Any) -> dict[str, Any]:
        target = self.organism.route(capability)
        if target is None:
            raise LookupError(f"no routable provider for capability: {capability}")
        created = time.time()
        canonical = {
            "source": source,
            "capability": capability,
            "target": target.name,
            "payload": payload,
            "created": created,
        }
        mid = hashlib.sha256(_stable(canonical).encode("utf-8")).hexdigest()
        c = self._conn()
        c.execute(
            """INSERT OR IGNORE INTO messages
               (id,created,source,capability,target,payload,status)
               VALUES(?,?,?,?,?,?,'queued')""",
            (mid, created, source, capability, target.name, _stable(payload)),
        )
        c.commit()
        c.close()
        return {"id": mid, "target": target.name, "status": "queued"}

    def claim(self, target: str, limit: int = 10, lease_seconds: int = 300) -> list[dict[str, Any]]:
        now = time.time()
        c = self._conn()
        # Recover abandoned claims first.
        c.execute(
            """UPDATE messages SET status='queued',claim_token=NULL,claimed=NULL
               WHERE status='claimed' AND claimed < ?""",
            (now - lease_seconds,),
        )
        rows = list(
            c.execute(
                """SELECT * FROM messages
                   WHERE target=? AND status='queued'
                   ORDER BY created LIMIT ?""",
                (target, int(limit)),
            )
        )
        out = []
        for r in rows:
            token = hashlib.sha256(f"{r['id']}:{now}:{target}".encode()).hexdigest()
            changed = c.execute(
                """UPDATE messages
                   SET status='claimed',claimed=?,claim_token=?,attempts=attempts+1
                   WHERE id=? AND status='queued'""",
                (now, token, r["id"]),
            ).rowcount
            if not changed:
                continue
            out.append(
                {
                    "id": r["id"],
                    "source": r["source"],
                    "capability": r["capability"],
                    "target": r["target"],
                    "payload": json.loads(r["payload"]),
                    "claim_token": token,
                }
            )
        c.commit()
        c.close()
        return out

    def ack(self, message_id: str, target: str, claim_token: str, result: Any) -> dict[str, Any]:
        c = self._conn()
        row = c.execute(
            "SELECT * FROM messages WHERE id=?",
            (message_id,),
        ).fetchone()
        if row is None:
            c.close()
            raise KeyError(message_id)
        if row["target"] != target or row["claim_token"] != claim_token or row["status"] != "claimed":
            c.close()
            raise PermissionError("claim does not authorize this acknowledgement")
        rid = hashlib.sha256(
            _stable({"message_id": message_id, "target": target, "result": result}).encode()
        ).hexdigest()
        c.execute(
            "INSERT OR IGNORE INTO receipts(id,message_id,created,target,result) VALUES(?,?,?,?,?)",
            (rid, message_id, time.time(), target, _stable(result)),
        )
        c.execute(
            "UPDATE messages SET status='complete' WHERE id=?",
            (message_id,),
        )
        c.commit()
        c.close()
        return {"receipt_id": rid, "message_id": message_id, "status": "complete"}

    def status(self) -> dict[str, int]:
        c = self._conn()
        rows = {
            r["status"]: r["n"]
            for r in c.execute("SELECT status,count(*) n FROM messages GROUP BY status")
        }
        receipts = c.execute("SELECT count(*) n FROM receipts").fetchone()["n"]
        c.close()
        return {**rows, "receipts": receipts}
