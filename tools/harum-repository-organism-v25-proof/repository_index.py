from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Iterable

TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".go", ".rs", ".java",
    ".css", ".html", ".sql", ".sh", ".ps1",
}
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", "dist",
    "build", ".next", ".cache",
}


class RepositoryIndex:
    """One searchable virtual filesystem across locally materialized organs."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        c = self._conn()
        c.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS files(
              uri TEXT PRIMARY KEY,
              component TEXT NOT NULL,
              relpath TEXT NOT NULL,
              sha256 TEXT NOT NULL,
              bytes INTEGER NOT NULL,
              indexed REAL NOT NULL DEFAULT (unixepoch())
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS file_fts
              USING fts5(uri UNINDEXED, component, relpath, body);
            """
        )
        c.commit()
        c.close()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    @staticmethod
    def uri(component: str, relpath: str) -> str:
        return f"harum://repo/{component}/{relpath.lstrip('/')}"

    def index_component(
        self,
        component: str,
        root: str | Path,
        max_file_bytes: int = 512_000,
    ) -> dict[str, int]:
        base = Path(root).resolve()
        if not base.is_dir():
            raise FileNotFoundError(base)
        seen: set[str] = set()
        indexed = 0
        skipped = 0
        c = self._conn()
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(base)
            if any(part in SKIP_DIRS for part in rel.parts):
                skipped += 1
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                skipped += 1
                continue
            size = path.stat().st_size
            if size > max_file_bytes:
                skipped += 1
                continue
            data = path.read_bytes()
            try:
                body = data.decode("utf-8")
            except UnicodeDecodeError:
                skipped += 1
                continue
            digest = hashlib.sha256(data).hexdigest()
            uri = self.uri(component, rel.as_posix())
            seen.add(uri)
            existing = c.execute(
                "SELECT sha256,rowid FROM files WHERE uri=?",
                (uri,),
            ).fetchone()
            if existing and existing["sha256"] == digest:
                continue
            if existing:
                c.execute("DELETE FROM file_fts WHERE rowid=?", (existing["rowid"],))
                c.execute(
                    "UPDATE files SET sha256=?,bytes=?,indexed=unixepoch() WHERE uri=?",
                    (digest, size, uri),
                )
                rowid = existing["rowid"]
            else:
                cur = c.execute(
                    "INSERT INTO files(uri,component,relpath,sha256,bytes) VALUES(?,?,?,?,?)",
                    (uri, component, rel.as_posix(), digest, size),
                )
                rowid = cur.lastrowid
            c.execute(
                "INSERT INTO file_fts(rowid,uri,component,relpath,body) VALUES(?,?,?,?,?)",
                (rowid, uri, component, rel.as_posix(), body),
            )
            indexed += 1
        stale = list(
            c.execute(
                "SELECT uri,rowid FROM files WHERE component=?",
                (component,),
            )
        )
        removed = 0
        for row in stale:
            if row["uri"] not in seen:
                c.execute("DELETE FROM file_fts WHERE rowid=?", (row["rowid"],))
                c.execute("DELETE FROM files WHERE uri=?", (row["uri"],))
                removed += 1
        c.commit()
        c.close()
        return {"indexed_or_updated": indexed, "removed": removed, "skipped": skipped}

    def search(self, query: str, limit: int = 20) -> list[dict]:
        c = self._conn()
        rows = [
            dict(r)
            for r in c.execute(
                """SELECT f.uri,f.component,f.relpath,f.sha256,f.bytes,
                          bm25(file_fts) AS rank
                   FROM file_fts
                   JOIN files f ON f.rowid=file_fts.rowid
                   WHERE file_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (query, int(limit)),
            )
        ]
        c.close()
        return rows

    def stats(self) -> dict[str, int]:
        c = self._conn()
        files = c.execute("SELECT count(*) n FROM files").fetchone()["n"]
        components = c.execute(
            "SELECT count(DISTINCT component) n FROM files"
        ).fetchone()["n"]
        c.close()
        return {"files": files, "components": components}
