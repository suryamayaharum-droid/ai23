from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any

from repository_organism import RepositoryComponent, RepositoryOrganism


_SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")


class RepositoryWorkspace:
    """On-demand, non-executing materialization of repository organs.

    This workspace is a cache for source and data. Cloning a component does not
    import its modules, invoke package managers, run hooks, or execute health probes.
    """

    def __init__(self, root: str | Path, organism: RepositoryOrganism) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.organism = organism

    def _component(self, name: str) -> RepositoryComponent:
        for c in self.organism.components:
            if c.name == name:
                return c
        raise KeyError(name)

    def _path(self, component: RepositoryComponent) -> Path:
        safe = _SAFE_NAME.sub("-", component.name).strip("-") or "component"
        return self.root / safe

    @staticmethod
    def _run(argv: list[str], cwd: Path | None = None) -> str:
        p = subprocess.run(
            argv,
            cwd=str(cwd) if cwd else None,
            check=True,
            capture_output=True,
            text=True,
            timeout=180,
            env=None,
        )
        return p.stdout.strip()

    def materialize(
        self,
        name: str,
        *,
        source_url: str | None = None,
        allow_non_routable: bool = False,
    ) -> dict[str, Any]:
        c = self._component(name)
        if not c.routable and not allow_non_routable:
            raise PermissionError(f"component is not routable: {name}")
        dest = self._path(c)
        url = source_url or f"https://github.com/{c.repository}.git"
        if not dest.exists():
            self._run(
                [
                    "git",
                    "-c",
                    "core.hooksPath=/dev/null",
                    "clone",
                    "--depth=1",
                    "--single-branch",
                    "--branch",
                    c.default_branch,
                    "--no-tags",
                    url,
                    str(dest),
                ]
            )
        else:
            dirty = self._run(["git", "status", "--porcelain"], dest)
            if dirty:
                raise RuntimeError(f"workspace has local modifications: {name}")
            self._run(
                [
                    "git",
                    "-c",
                    "core.hooksPath=/dev/null",
                    "fetch",
                    "--depth=1",
                    "--no-tags",
                    "origin",
                    c.default_branch,
                ],
                dest,
            )
            self._run(
                ["git", "checkout", "-B", c.default_branch, "FETCH_HEAD"],
                dest,
            )
        sha = self._run(["git", "rev-parse", "HEAD"], dest)
        return {
            "component": c.name,
            "repository": c.repository,
            "path": str(dest),
            "commit": sha,
            "branch": c.default_branch,
            "executed_component_code": False,
        }

    def status(self, name: str) -> dict[str, Any]:
        c = self._component(name)
        dest = self._path(c)
        if not dest.exists():
            return {"component": name, "materialized": False}
        return {
            "component": name,
            "materialized": True,
            "path": str(dest),
            "commit": self._run(["git", "rev-parse", "HEAD"], dest),
            "dirty": bool(self._run(["git", "status", "--porcelain"], dest)),
        }
