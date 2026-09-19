#!/usr/bin/env python3
from __future__ import annotations
import json, os, urllib.parse, urllib.request
from typing import Any

class SupabaseOrganismAdapter:
    """Tiny dependency-free REST/RPC adapter.

    Requires environment variables only at runtime:
      SUPABASE_URL
      SUPABASE_SECRET_KEY (preferred) or SUPABASE_SERVICE_ROLE_KEY (legacy)
    Secrets are never written to HARUM events, Git or Airtable.
    """
    def __init__(self, url:str|None=None, key:str|None=None):
        self.url=(url or os.getenv("SUPABASE_URL","")).rstrip("/")
        self.key=key or os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY","")
        if not self.url or not self.key:
            raise RuntimeError("Supabase runtime credentials are not configured")

    def _request(self,path:str,method:str="GET",body:Any=None)->Any:
        raw=None if body is None else json.dumps(body).encode()
        req=urllib.request.Request(self.url+path,data=raw,method=method)
        req.add_header("apikey",self.key)
        req.add_header("Authorization","Bearer "+self.key)
        if raw is not None:
            req.add_header("Content-Type","application/json")
        req.add_header("Accept","application/json")
        with urllib.request.urlopen(req,timeout=30) as r:
            data=r.read()
            return None if not data else json.loads(data.decode())

    def rpc(self,name:str,payload:dict[str,Any])->Any:
        return self._request("/rest/v1/rpc/"+urllib.parse.quote(name),"POST",payload)

    def heartbeat(self, **state)->Any:
        return self.rpc("harum_heartbeat",{
          "p_node_id":state["node_id"],
          "p_layer":state.get("layer","worker"),
          "p_district":state.get("district"),
          "p_capabilities":state.get("capabilities",[]),
          "p_health":state.get("health","online"),
          "p_load":state.get("load",0),
          "p_hologram_digest":state.get("hologram_digest"),
          "p_vector_clock":state.get("vector_clock",{}),
          "p_state":state.get("state",{})
        })

    def claim(self,node_id:str,capabilities:list[str],lease_seconds:int=120)->Any:
        return self.rpc("harum_claim_task",{
          "p_node_id":node_id,
          "p_capabilities":capabilities,
          "p_lease_seconds":lease_seconds
        })

    def emit(self,event:dict[str,Any])->Any:
        forbidden={"password","token","cookie","api_key","secret"}
        if any(k.lower() in forbidden for k in event.get("payload",{})):
            raise ValueError("secret-like payload field blocked")
        return self._request("/rest/v1/harum_organism_events","POST",event)
