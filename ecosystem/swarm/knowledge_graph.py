#!/usr/bin/env python3
from __future__ import annotations
import json, sqlite3, time, hashlib
from pathlib import Path
from typing import Any

def canon(x:Any)->str:
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))

class KnowledgeGraph:
    def __init__(self, db_path:str="runtime/harum_knowledge.db"):
        self.path=Path(db_path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(self.path)
        self.db.row_factory=sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS kg_nodes(
          node_id TEXT PRIMARY KEY,
          kind TEXT NOT NULL,
          label TEXT NOT NULL,
          source TEXT,
          data_json TEXT NOT NULL DEFAULT '{}',
          confidence REAL NOT NULL DEFAULT 1.0,
          updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS kg_edges(
          edge_id TEXT PRIMARY KEY,
          src TEXT NOT NULL,
          rel TEXT NOT NULL,
          dst TEXT NOT NULL,
          weight REAL NOT NULL DEFAULT 1.0,
          evidence_json TEXT NOT NULL DEFAULT '[]',
          updated_at INTEGER NOT NULL,
          FOREIGN KEY(src) REFERENCES kg_nodes(node_id),
          FOREIGN KEY(dst) REFERENCES kg_nodes(node_id)
        );
        CREATE INDEX IF NOT EXISTS kg_nodes_kind_idx ON kg_nodes(kind,label);
        CREATE INDEX IF NOT EXISTS kg_edges_src_idx ON kg_edges(src,rel);
        CREATE INDEX IF NOT EXISTS kg_edges_dst_idx ON kg_edges(dst,rel);
        """)
        self.db.commit()

    def upsert(self,node_id:str,kind:str,label:str,*,source:str|None=None,
               data:dict[str,Any]|None=None,confidence:float=1.0)->str:
        now=int(time.time())
        self.db.execute(
            """INSERT INTO kg_nodes(node_id,kind,label,source,data_json,confidence,updated_at)
               VALUES(?,?,?,?,?,?,?)
               ON CONFLICT(node_id) DO UPDATE SET
                 kind=excluded.kind,label=excluded.label,source=excluded.source,
                 data_json=excluded.data_json,confidence=excluded.confidence,
                 updated_at=excluded.updated_at""",
            (node_id,kind,label,source,canon(data or {}),float(confidence),now)
        )
        self.db.commit()
        return node_id

    def relate(self,src:str,rel:str,dst:str,*,weight:float=1.0,
               evidence:list[dict[str,Any]]|None=None)->str:
        raw=f"{src}|{rel}|{dst}"
        edge_id=hashlib.sha256(raw.encode()).hexdigest()[:24]
        now=int(time.time())
        self.db.execute(
            """INSERT INTO kg_edges(edge_id,src,rel,dst,weight,evidence_json,updated_at)
               VALUES(?,?,?,?,?,?,?)
               ON CONFLICT(edge_id) DO UPDATE SET
                 weight=excluded.weight,evidence_json=excluded.evidence_json,
                 updated_at=excluded.updated_at""",
            (edge_id,src,rel,dst,float(weight),canon(evidence or []),now)
        )
        self.db.commit()
        return edge_id

    def neighbors(self,node_id:str,rel:str|None=None)->list[dict[str,Any]]:
        q="""SELECT e.rel,e.weight,n.* FROM kg_edges e
             JOIN kg_nodes n ON n.node_id=e.dst WHERE e.src=?"""
        params=[node_id]
        if rel:
            q+=" AND e.rel=?"; params.append(rel)
        q+=" ORDER BY e.weight DESC,n.label"
        return [dict(r) for r in self.db.execute(q,params).fetchall()]

    def search(self,text:str,limit:int=25)->list[dict[str,Any]]:
        pat=f"%{text}%"
        rows=self.db.execute(
            """SELECT * FROM kg_nodes
               WHERE label LIKE ? OR data_json LIKE ?
               ORDER BY confidence DESC,updated_at DESC LIMIT ?""",
            (pat,pat,limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def export(self)->dict[str,Any]:
        nodes=[dict(r) for r in self.db.execute("SELECT * FROM kg_nodes ORDER BY kind,label")]
        edges=[dict(r) for r in self.db.execute("SELECT * FROM kg_edges ORDER BY src,rel,dst")]
        return {"nodes":nodes,"edges":edges}

def seed_from_configs(graph:KnowledgeGraph, root:Path|None=None)->dict[str,int]:
    root=root or Path(__file__).resolve().parent
    agents=json.loads((root/"config"/"agents.json").read_text(encoding="utf-8"))
    city=json.loads((root/"config"/"city_v8_airtable_snapshot.json").read_text(encoding="utf-8"))
    resources=json.loads((root/"config"/"resource_profiles.json").read_text(encoding="utf-8"))

    for d in agents["districts"]:
        did="district:"+d["id"]
        graph.upsert(did,"district",d["id"],source="agents.json")
        for a in d["agents"]:
            aid="agent:"+a["id"]
            graph.upsert(aid,"agent",a["id"],source="agents.json",data=a)
            graph.relate(did,"contains",aid)
            for c in a["capabilities"]:
                cid="cap:"+c
                graph.upsert(cid,"capability",c,source="agents.json")
                graph.relate(aid,"provides",cid)

    for d in city["districts"]:
        did="macro-district:"+d["name"]
        graph.upsert(did,"macro-district",d["name"],source="city_v8_airtable_snapshot.json",data=d)
    for s in city["swarms"]:
        sid="swarm:"+s["name"]
        graph.upsert(sid,"swarm",s["name"],source="city_v8_airtable_snapshot.json",data=s)
        graph.relate("macro-district:"+s["district"],"contains",sid)

    for r in resources["resources"]:
        rid="resource:"+r["id"]
        graph.upsert(rid,"resource",r["id"],source="resource_profiles.json",data=r)
        for c in r.get("capabilities",[]):
            cid="cap:"+c
            graph.upsert(cid,"capability",c,source="resource_profiles.json")
            graph.relate(rid,"provides",cid)

    return {
      "nodes":graph.db.execute("SELECT COUNT(*) FROM kg_nodes").fetchone()[0],
      "edges":graph.db.execute("SELECT COUNT(*) FROM kg_edges").fetchone()[0]
    }

if __name__=="__main__":
    g=KnowledgeGraph()
    print(json.dumps(seed_from_configs(g),ensure_ascii=False,indent=2))
