#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, sqlite3, time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

def canonical(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()

class HolographicState:
    """CRDT-inspired replicated organism state.

    Each cell owns a monotonic logical clock. Facts are immutable and merged by
    unique fact_id; the materialized view resolves a key deterministically by
    (clock, cell_id, fact_id). This gives every cell a compact view of the whole
    organism without requiring direct cell-to-cell calls.
    """
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS cell_clock(
          cell_id TEXT PRIMARY KEY,
          clock INTEGER NOT NULL DEFAULT 0,
          updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS organism_facts(
          fact_id TEXT PRIMARY KEY,
          cell_id TEXT NOT NULL,
          clock INTEGER NOT NULL,
          key TEXT NOT NULL,
          value_json TEXT NOT NULL,
          value_digest TEXT NOT NULL,
          created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_facts_key ON organism_facts(key, clock DESC);
        """)
        self.db.commit()

    def _tick(self, cell_id: str) -> int:
        now = int(time.time())
        row = self.db.execute("SELECT clock FROM cell_clock WHERE cell_id=?", (cell_id,)).fetchone()
        clock = (int(row["clock"]) if row else 0) + 1
        self.db.execute(
            """INSERT INTO cell_clock(cell_id,clock,updated_at) VALUES(?,?,?)
               ON CONFLICT(cell_id) DO UPDATE SET clock=excluded.clock, updated_at=excluded.updated_at""",
            (cell_id, clock, now),
        )
        return clock

    def publish(self, cell_id: str, key: str, value: Any) -> str:
        clock = self._tick(cell_id)
        now = int(time.time())
        vd = digest(value)
        fid = digest({"cell": cell_id, "clock": clock, "key": key, "value": vd})
        self.db.execute(
            """INSERT OR IGNORE INTO organism_facts
               (fact_id,cell_id,clock,key,value_json,value_digest,created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (fid, cell_id, clock, key, canonical(value), vd, now),
        )
        self.db.commit()
        return fid

    def vector_clock(self) -> dict[str,int]:
        return {r["cell_id"]: int(r["clock"]) for r in self.db.execute("SELECT * FROM cell_clock")}

    def export_since(self, peer_clock: dict[str,int] | None = None) -> dict[str,Any]:
        peer_clock = peer_clock or {}
        rows = self.db.execute("SELECT * FROM organism_facts ORDER BY created_at, fact_id").fetchall()
        facts = [
            dict(r) for r in rows
            if int(r["clock"]) > int(peer_clock.get(r["cell_id"], 0))
        ]
        return {"vector_clock": self.vector_clock(), "facts": facts}

    def merge(self, packet: dict[str,Any]) -> int:
        added = 0
        for f in packet.get("facts", []):
            cur = self.db.execute("SELECT 1 FROM organism_facts WHERE fact_id=?", (f["fact_id"],)).fetchone()
            if cur:
                continue
            self.db.execute(
                """INSERT INTO organism_facts
                   (fact_id,cell_id,clock,key,value_json,value_digest,created_at)
                   VALUES(?,?,?,?,?,?,?)""",
                (f["fact_id"], f["cell_id"], int(f["clock"]), f["key"],
                 f["value_json"], f["value_digest"], int(f["created_at"])),
            )
            row = self.db.execute("SELECT clock FROM cell_clock WHERE cell_id=?", (f["cell_id"],)).fetchone()
            if not row or int(row["clock"]) < int(f["clock"]):
                self.db.execute(
                    """INSERT INTO cell_clock(cell_id,clock,updated_at) VALUES(?,?,?)
                       ON CONFLICT(cell_id) DO UPDATE SET clock=excluded.clock,updated_at=excluded.updated_at""",
                    (f["cell_id"], int(f["clock"]), int(time.time())),
                )
            added += 1
        self.db.commit()
        return added

    def view(self) -> dict[str,Any]:
        rows = self.db.execute(
            """SELECT * FROM organism_facts
               ORDER BY key ASC, clock DESC, cell_id DESC, fact_id DESC"""
        ).fetchall()
        out: dict[str,Any] = {}
        for r in rows:
            if r["key"] not in out:
                out[r["key"]] = json.loads(r["value_json"])
        return out

    def organism_digest(self) -> str:
        return digest({"clock": self.vector_clock(), "view": self.view()})

def build_capability_hologram() -> dict[str,Any]:
    agents = json.loads((HERE/"config"/"agents.json").read_text(encoding="utf-8"))
    missions = json.loads((HERE/"config"/"missions.json").read_text(encoding="utf-8"))
    plugins = json.loads((HERE/"config"/"plugin_fabric.json").read_text(encoding="utf-8"))
    cells = []
    for district in agents["districts"]:
        for a in district["agents"]:
            cells.append({
                "cell": a["id"],
                "district": district["id"],
                "role": a["role"],
                "capabilities": sorted(a["capabilities"]),
                "priority": a["priority"],
            })
    body = {
        "schema": "harum.hologram.v1",
        "cells": sorted(cells, key=lambda x: x["cell"]),
        "missions": missions["missions"],
        "resources": plugins["resources"],
    }
    body["capability_digest"] = digest(body)
    return body
