#!/usr/bin/env python3
from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any

from durable_journal import DurableJournal

class BackendUnavailable(RuntimeError):
    pass

class LocalBackend:
    def __init__(self, root:str="runtime/hybrid"):
        self.root=Path(root)
        self.root.mkdir(parents=True,exist_ok=True)
        self.journal=DurableJournal(str(self.root/"journal"))
        self.state_file=self.root/"state.json"
        self.state=json.loads(self.state_file.read_text()) if self.state_file.exists() else {}

    def heartbeat(self,node_id:str,state:dict[str,Any])->dict[str,Any]:
        self.state.setdefault("nodes",{})[node_id]={**state,"last_heartbeat":int(time.time())}
        self._save()
        self.journal.append("heartbeat",{"node_id":node_id,"state":state},source=node_id)
        return self.state["nodes"][node_id]

    def emit(self,event:dict[str,Any])->dict[str,Any]:
        return self.journal.append(
            event["topic"],event.get("payload",{}),
            source=event.get("source","unknown"),
            correlation_id=event.get("correlation_id")
        )

    def _save(self):
        tmp=self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.state_file)

class HybridState:
    """Local-first state with opportunistic Supabase mirroring.

    Local writes are authoritative for availability. Supabase is a durable
    online replica/control plane when configured; its failure never erases the
    local checkpoint.
    """
    def __init__(self, local_root:str="runtime/hybrid"):
        self.local=LocalBackend(local_root)
        self.remote=None
        if os.getenv("SUPABASE_URL") and (
            os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        ):
            try:
                from supabase_adapter import SupabaseOrganismAdapter
                self.remote=SupabaseOrganismAdapter()
            except Exception:
                self.remote=None

    @property
    def mode(self)->str:
        return "hybrid" if self.remote else "local-only"

    def heartbeat(self,node_id:str,**state)->dict[str,Any]:
        local=self.local.heartbeat(node_id,state)
        remote_status="not-configured"
        if self.remote:
            try:
                self.remote.heartbeat(node_id=node_id,**state)
                remote_status="mirrored"
            except Exception as exc:
                remote_status=f"degraded:{type(exc).__name__}"
                self.local.journal.append("supabase.mirror_failed",{
                    "operation":"heartbeat","node_id":node_id,"error":str(exc)
                },source="hybrid_state")
        return {"local":local,"remote":remote_status,"mode":self.mode}

    def emit(self,event:dict[str,Any])->dict[str,Any]:
        local=self.local.emit(event)
        remote_status="not-configured"
        if self.remote:
            try:
                payload={
                    "topic":event["topic"],
                    "source":event.get("source","unknown"),
                    "target":event.get("target"),
                    "payload":event.get("payload",{}),
                    "idempotency_key":event.get("idempotency_key"),
                    "organism_digest":event.get("organism_digest"),
                    "hops":event.get("hops",0),
                    "ttl_seconds":event.get("ttl_seconds",3600)
                }
                self.remote.emit(payload)
                remote_status="mirrored"
            except Exception as exc:
                remote_status=f"degraded:{type(exc).__name__}"
                self.local.journal.append("supabase.mirror_failed",{
                    "operation":"emit","topic":event.get("topic"),"error":str(exc)
                },source="hybrid_state")
        return {"local":local,"remote":remote_status,"mode":self.mode}
