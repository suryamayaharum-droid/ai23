#!/usr/bin/env python3
from __future__ import annotations
import json, time, uuid
from typing import Any
from harum_swarm import SwarmCity, canon

class SubagentFactory:
    def __init__(self, city: SwarmCity):
        self.city=city
        self.city.db.execute("""
        CREATE TABLE IF NOT EXISTS agent_instances(
          instance_id TEXT PRIMARY KEY,
          parents_json TEXT NOT NULL,
          purpose TEXT NOT NULL,
          capabilities_json TEXT NOT NULL,
          scope_json TEXT NOT NULL,
          status TEXT NOT NULL,
          created_at INTEGER NOT NULL,
          expires_at INTEGER NOT NULL,
          last_heartbeat INTEGER NOT NULL
        )
        """)
        self.city.db.commit()

    def spawn(self, *, parents: list[str], purpose: str,
              capabilities: list[str], scope: dict[str,Any],
              ttl_seconds: int=1800) -> str:
        rows=self.city.db.execute(
            "SELECT id,capabilities_json FROM agents WHERE id IN (%s)" %
            ",".join("?" for _ in parents), parents
        ).fetchall()
        found={r["id"] for r in rows}
        missing=set(parents)-found
        if missing:
            raise ValueError(f"unknown parent agents: {sorted(missing)}")
        inherited=set()
        for r in rows:
            inherited.update(json.loads(r["capabilities_json"]))
        requested=set(capabilities)
        if not requested.issubset(inherited):
            raise ValueError(
                "subagent capability escalation blocked: " +
                ",".join(sorted(requested-inherited))
            )
        now=int(time.time())
        instance_id="sub-"+uuid.uuid4().hex[:12]
        self.city.db.execute(
            """INSERT INTO agent_instances(instance_id,parents_json,purpose,
               capabilities_json,scope_json,status,created_at,expires_at,last_heartbeat)
               VALUES(?,?,?,?,?,'ONLINE',?,?,?)""",
            (instance_id,canon(parents),purpose,canon(sorted(requested)),
             canon(scope),now,now+ttl_seconds,now)
        )
        self.city.db.commit()
        corr=str(uuid.uuid4())
        self.city.emit(
            "subagent.spawned","subagent_factory",corr,target=instance_id,
            ttl_seconds=ttl_seconds,
            payload={"parents":parents,"purpose":purpose,
                     "capabilities":sorted(requested),"scope":scope}
        )
        return instance_id

    def heartbeat(self, instance_id: str) -> None:
        now=int(time.time())
        self.city.db.execute(
            "UPDATE agent_instances SET last_heartbeat=? WHERE instance_id=? AND status='ONLINE'",
            (now,instance_id)
        )
        self.city.db.commit()

    def retire(self, instance_id: str, reason: str="completed") -> None:
        row=self.city.db.execute(
            "SELECT * FROM agent_instances WHERE instance_id=?",(instance_id,)
        ).fetchone()
        if not row:
            return
        self.city.db.execute(
            "UPDATE agent_instances SET status='RETIRED' WHERE instance_id=?",
            (instance_id,)
        )
        self.city.db.commit()
        self.city.emit(
            "subagent.retired","subagent_factory",str(uuid.uuid4()),
            target=instance_id,payload={"reason":reason}
        )

    def reap_expired(self) -> int:
        now=int(time.time())
        rows=self.city.db.execute(
            "SELECT instance_id FROM agent_instances WHERE status='ONLINE' AND expires_at<?",
            (now,)
        ).fetchall()
        for r in rows:
            self.retire(r["instance_id"],"ttl_expired")
        return len(rows)

    def active(self) -> list[dict[str,Any]]:
        rows=self.city.db.execute(
            "SELECT * FROM agent_instances WHERE status='ONLINE' ORDER BY created_at"
        ).fetchall()
        out=[]
        for r in rows:
            d=dict(r)
            d["parents"]=json.loads(d.pop("parents_json"))
            d["capabilities"]=json.loads(d.pop("capabilities_json"))
            d["scope"]=json.loads(d.pop("scope_json"))
            out.append(d)
        return out
