#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3, time
from typing import Any

class Homeostasis:
    def __init__(self, db: sqlite3.Connection):
        self.db=db
        self.db.row_factory=sqlite3.Row

    def inspect(self) -> dict[str,Any]:
        now=int(time.time())
        stale_agents=[
            r["id"] for r in self.db.execute(
                "SELECT id FROM agents WHERE ?-last_seen>7200",(now,)
            )
        ]
        counts={r["status"]:r["n"] for r in self.db.execute(
            "SELECT status,COUNT(*) n FROM tasks GROUP BY status"
        )}
        dead=self.db.execute("SELECT COUNT(*) FROM dead_letters").fetchone()[0]
        waiting=int(counts.get("WAITING_EXTERNAL",0))
        ready=int(counts.get("READY",0))
        severity="healthy"
        signals=[]
        if stale_agents:
            severity="degraded"; signals.append({"type":"stale_cells","cells":stale_agents})
        if dead:
            severity="degraded"; signals.append({"type":"dead_letters","count":dead})
        if waiting>10:
            severity="degraded"; signals.append({"type":"external_bottleneck","count":waiting})
        if ready>50:
            severity="degraded"; signals.append({"type":"queue_pressure","count":ready})
        return {
            "status":severity,
            "signals":signals,
            "task_counts":counts,
            "dead_letters":dead,
            "checked_at":now
        }
