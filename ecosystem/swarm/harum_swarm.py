#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sqlite3, time, uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

DEFAULT_DB = "runtime/harum_swarm.db"
HERE = Path(__file__).resolve().parent
AGENTS_FILE = HERE / "config" / "agents.json"
WORKFLOWS_FILE = HERE / "config" / "workflows.json"

def utc_ts() -> int:
    return int(time.time())

def canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def make_dedupe_key(workflow: str, stage: str, payload: dict[str, Any]) -> str:
    raw = canon({"workflow": workflow, "stage": stage, "payload": payload}).encode()
    return hashlib.sha256(raw).hexdigest()

@dataclass(frozen=True)
class Agent:
    id: str
    district: str
    role: str
    priority: int
    capabilities: tuple[str, ...]

class SwarmCity:
    def __init__(self, db_path: str = DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.bootstrap()

    def bootstrap(self) -> None:
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS agents(
          id TEXT PRIMARY KEY,
          district TEXT NOT NULL,
          role TEXT NOT NULL,
          priority INTEGER NOT NULL,
          capabilities_json TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'ONLINE',
          last_seen INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS tasks(
          id TEXT PRIMARY KEY,
          correlation_id TEXT NOT NULL,
          parent_id TEXT,
          depends_on TEXT,
          workflow TEXT NOT NULL,
          stage TEXT NOT NULL,
          status TEXT NOT NULL,
          priority INTEGER NOT NULL DEFAULT 50,
          required_json TEXT NOT NULL,
          payload_json TEXT NOT NULL,
          assigned_agent TEXT,
          attempts INTEGER NOT NULL DEFAULT 0,
          max_attempts INTEGER NOT NULL DEFAULT 3,
          hops INTEGER NOT NULL DEFAULT 0,
          max_hops INTEGER NOT NULL DEFAULT 12,
          ttl_seconds INTEGER NOT NULL DEFAULT 3600,
          dedupe_key TEXT NOT NULL,
          output_json TEXT,
          error TEXT,
          created_at INTEGER NOT NULL,
          updated_at INTEGER NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_tasks_dedupe_active
        ON tasks(dedupe_key, status)
        WHERE status IN ('BLOCKED','READY','RUNNING','WAITING_EXTERNAL');
        CREATE TABLE IF NOT EXISTS events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          event_id TEXT UNIQUE NOT NULL,
          topic TEXT NOT NULL,
          source TEXT NOT NULL,
          target TEXT,
          correlation_id TEXT NOT NULL,
          task_id TEXT,
          hops INTEGER NOT NULL,
          ttl_seconds INTEGER NOT NULL,
          payload_json TEXT NOT NULL,
          created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS dead_letters(
          id TEXT PRIMARY KEY,
          task_id TEXT NOT NULL,
          reason TEXT NOT NULL,
          snapshot_json TEXT NOT NULL,
          created_at INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, priority DESC, created_at);
        CREATE INDEX IF NOT EXISTS idx_events_topic ON events(topic, seq);
        """)
        self.db.commit()

    def emit(self, topic: str, source: str, correlation_id: str, *,
             task_id: str | None = None, target: str | None = None,
             hops: int = 0, ttl_seconds: int = 3600,
             payload: dict[str, Any] | None = None) -> str:
        event_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO events(event_id,topic,source,target,correlation_id,task_id,hops,ttl_seconds,payload_json,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (event_id, topic, source, target, correlation_id, task_id, hops, ttl_seconds,
             canon(payload or {}), utc_ts())
        )
        self.db.commit()
        return event_id

    def seed_agents(self, config_path: Path = AGENTS_FILE) -> int:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        now = utc_ts()
        count = 0
        for district in data["districts"]:
            for item in district["agents"]:
                self.db.execute(
                    """INSERT INTO agents(id,district,role,priority,capabilities_json,status,last_seen)
                       VALUES(?,?,?,?,?,'ONLINE',?)
                       ON CONFLICT(id) DO UPDATE SET district=excluded.district, role=excluded.role,
                         priority=excluded.priority, capabilities_json=excluded.capabilities_json,
                         status='ONLINE', last_seen=excluded.last_seen""",
                    (item["id"], district["id"], item["role"], int(item["priority"]),
                     canon(item["capabilities"]), now)
                )
                count += 1
        self.db.commit()
        return count

    def agents(self) -> list[Agent]:
        rows = self.db.execute(
            "SELECT * FROM agents WHERE status='ONLINE' ORDER BY priority DESC, id"
        ).fetchall()
        return [
            Agent(r["id"], r["district"], r["role"], r["priority"],
                  tuple(json.loads(r["capabilities_json"])))
            for r in rows
        ]

    def best_agent(self, required: Iterable[str]) -> Agent | None:
        req = set(required)
        candidates = []
        for agent in self.agents():
            caps = set(agent.capabilities)
            if req.issubset(caps):
                candidates.append((agent.priority, len(caps - req), agent.id, agent))
        if not candidates:
            return None
        candidates.sort(key=lambda x: (-x[0], x[1], x[2]))
        return candidates[0][3]

    def submit_task(self, *, workflow: str, stage: str, required: list[str],
                    payload: dict[str, Any], correlation_id: str | None = None,
                    parent_id: str | None = None, depends_on: str | None = None,
                    priority: int = 50, hops: int = 0, max_hops: int = 12,
                    ttl_seconds: int = 3600) -> str:
        if hops > max_hops:
            raise ValueError("max_hops exceeded")
        correlation_id = correlation_id or str(uuid.uuid4())
        key = make_dedupe_key(workflow, stage, payload)
        existing = self.db.execute(
            """SELECT id FROM tasks WHERE dedupe_key=? AND status IN
               ('BLOCKED','READY','RUNNING','WAITING_EXTERNAL')""",
            (key,)
        ).fetchone()
        if existing:
            return str(existing["id"])
        task_id = str(uuid.uuid4())
        status = "BLOCKED" if depends_on else "READY"
        now = utc_ts()
        self.db.execute(
            """INSERT INTO tasks(id,correlation_id,parent_id,depends_on,workflow,stage,status,priority,
               required_json,payload_json,assigned_agent,attempts,max_attempts,hops,max_hops,ttl_seconds,
               dedupe_key,created_at,updated_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (task_id, correlation_id, parent_id, depends_on, workflow, stage, status, priority,
             canon(required), canon(payload), None, 0, 3, hops, max_hops, ttl_seconds, key, now, now)
        )
        self.db.commit()
        self.emit("task.created", "swarm_city", correlation_id, task_id=task_id, hops=hops,
                  ttl_seconds=ttl_seconds,
                  payload={"workflow": workflow, "stage": stage, "required": required})
        return task_id

    def enqueue_workflow(self, workflow: str, payload: dict[str, Any],
                         config_path: Path = WORKFLOWS_FILE) -> list[str]:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        stages = data["workflows"][workflow]
        correlation_id = str(uuid.uuid4())
        previous = None
        parent = None
        created = []
        for index, spec in enumerate(stages):
            task_id = self.submit_task(
                workflow=workflow,
                stage=spec["stage"],
                required=list(spec["requires"]),
                payload=payload,
                correlation_id=correlation_id,
                parent_id=parent,
                depends_on=previous,
                priority=100-index,
                hops=index
            )
            if parent is None:
                parent = task_id
            previous = task_id
            created.append(task_id)
        self.route_ready()
        return created

    def route_ready(self) -> int:
        rows = self.db.execute(
            "SELECT * FROM tasks WHERE status='READY' ORDER BY priority DESC, created_at"
        ).fetchall()
        routed = 0
        now = utc_ts()
        for row in rows:
            if now - row["created_at"] > row["ttl_seconds"]:
                self._dead_letter(row, "ttl_expired")
                continue
            agent = self.best_agent(json.loads(row["required_json"]))
            if not agent:
                self.db.execute(
                    "UPDATE tasks SET status='WAITING_EXTERNAL',updated_at=? WHERE id=?",
                    (now, row["id"])
                )
                self.emit("task.waiting_external", "router", row["correlation_id"],
                          task_id=row["id"], hops=row["hops"],
                          ttl_seconds=row["ttl_seconds"],
                          payload={"required": json.loads(row["required_json"])})
                continue
            self.db.execute(
                "UPDATE tasks SET assigned_agent=?,updated_at=? WHERE id=?",
                (agent.id, now, row["id"])
            )
            self.emit("router.assigned", "router", row["correlation_id"],
                      task_id=row["id"], target=agent.id, hops=row["hops"],
                      ttl_seconds=row["ttl_seconds"],
                      payload={"district": agent.district, "role": agent.role})
            routed += 1
        self.db.commit()
        return routed

    def claim(self, agent_id: str) -> dict[str, Any] | None:
        row = self.db.execute(
            """SELECT * FROM tasks WHERE status='READY' AND assigned_agent=?
               ORDER BY priority DESC, created_at LIMIT 1""", (agent_id,)
        ).fetchone()
        if not row:
            return None
        now = utc_ts()
        self.db.execute(
            """UPDATE tasks SET status='RUNNING',attempts=attempts+1,updated_at=?
               WHERE id=? AND status='READY'""",
            (now, row["id"])
        )
        self.db.commit()
        self.emit("agent.started", agent_id, row["correlation_id"], task_id=row["id"],
                  hops=row["hops"], ttl_seconds=row["ttl_seconds"],
                  payload={"workflow": row["workflow"], "stage": row["stage"]})
        return self.task(row["id"])

    def complete(self, task_id: str, agent_id: str, output: dict[str, Any]) -> None:
        row = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise KeyError(task_id)
        now = utc_ts()
        self.db.execute(
            """UPDATE tasks SET status='COMPLETED',output_json=?,error=NULL,updated_at=?
               WHERE id=?""",
            (canon(output), now, task_id)
        )
        self.emit("task.completed", agent_id, row["correlation_id"], task_id=task_id,
                  hops=row["hops"], ttl_seconds=row["ttl_seconds"], payload=output)
        self.db.execute(
            """UPDATE tasks SET status='READY',updated_at=?
               WHERE depends_on=? AND status='BLOCKED'""",
            (now, task_id)
        )
        self.db.commit()
        self.route_ready()

    def fail(self, task_id: str, agent_id: str, error: str) -> None:
        row = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise KeyError(task_id)
        now = utc_ts()
        attempts = int(row["attempts"])
        if attempts >= int(row["max_attempts"]):
            self._dead_letter(row, error)
            next_status = "DEAD"
        else:
            self.db.execute(
                """UPDATE tasks SET status='READY',error=?,assigned_agent=NULL,updated_at=?
                   WHERE id=?""",
                (error, now, task_id)
            )
            next_status = "READY"
        self.db.commit()
        self.emit("task.failed", agent_id, row["correlation_id"], task_id=task_id,
                  hops=row["hops"], ttl_seconds=row["ttl_seconds"],
                  payload={"error": error, "next_status": next_status, "attempts": attempts})
        if next_status == "READY":
            self.route_ready()

    def _dead_letter(self, row: sqlite3.Row, reason: str) -> None:
        now = utc_ts()
        snapshot = {k: row[k] for k in row.keys()}
        self.db.execute(
            "UPDATE tasks SET status='DEAD',error=?,updated_at=? WHERE id=?",
            (reason, now, row["id"])
        )
        self.db.execute(
            """INSERT INTO dead_letters(id,task_id,reason,snapshot_json,created_at)
               VALUES(?,?,?,?,?)""",
            (str(uuid.uuid4()), row["id"], reason, canon(snapshot), now)
        )
        self.db.commit()

    def task(self, task_id: str) -> dict[str, Any]:
        row = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            raise KeyError(task_id)
        data = dict(row)
        for src, dst in (
            ("required_json","required"),
            ("payload_json","payload"),
            ("output_json","output")
        ):
            if data.get(src):
                data[dst] = json.loads(data[src])
        return data

    def status(self) -> dict[str, Any]:
        task_counts = {
            row["status"]: row["n"]
            for row in self.db.execute("SELECT status,COUNT(*) n FROM tasks GROUP BY status")
        }
        districts = {
            row["district"]: row["n"]
            for row in self.db.execute(
                "SELECT district,COUNT(*) n FROM agents WHERE status='ONLINE' GROUP BY district"
            )
        }
        return {
            "db": str(self.db_path),
            "agents_online": sum(districts.values()),
            "districts": districts,
            "tasks": task_counts,
            "events": self.db.execute("SELECT COUNT(*) FROM events").fetchone()[0],
            "dead_letters": self.db.execute("SELECT COUNT(*) FROM dead_letters").fetchone()[0]
        }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["bootstrap","seed","status","demo"])
    parser.add_argument("--db", default=DEFAULT_DB)
    args = parser.parse_args()
    city = SwarmCity(args.db)
    if args.command == "bootstrap":
        print(json.dumps({"ok": True, "db": str(city.db_path)}, indent=2))
    elif args.command == "seed":
        count = city.seed_agents()
        print(json.dumps({"seeded_agents": count, **city.status()}, ensure_ascii=False, indent=2))
    elif args.command == "status":
        print(json.dumps(city.status(), ensure_ascii=False, indent=2))
    elif args.command == "demo":
        city.seed_agents()
        tasks = city.enqueue_workflow(
            "archive_ingest",
            {"source": "HARUM NOIR", "mode": "dry-run"}
        )
        print(json.dumps({"workflow_tasks": tasks, **city.status()}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
