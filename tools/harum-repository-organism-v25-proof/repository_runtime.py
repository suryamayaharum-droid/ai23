from __future__ import annotations

from pathlib import Path
from typing import Any

from repository_bus import RepositorySynapticBus
from repository_index import RepositoryIndex
from repository_organism import RepositoryOrganism
from repository_workspace import RepositoryWorkspace


class RepositoryOrganismRuntime:
    """Composes topology, durable messaging, source workspace and unified index.

    The runtime intentionally stops at the adapter boundary. It can discover,
    route, materialize and index repositories, but it never executes component
    code merely because a component exists in the organism.
    """

    def __init__(self, repo_root: str | Path, state_root: str | Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.state_root = Path(state_root).expanduser().resolve()
        self.state_root.mkdir(parents=True, exist_ok=True)
        self.organism = RepositoryOrganism.from_repo(self.repo_root)
        self.bus = RepositorySynapticBus(
            self.state_root / "repository_bus.db",
            self.organism,
        )
        self.index = RepositoryIndex(
            self.state_root / "repository_index.db",
        )
        self.workspace = RepositoryWorkspace(
            self.state_root / "repos",
            self.organism,
        )

    def status(self) -> dict[str, Any]:
        return {
            **self.organism.status(),
            "bus": self.bus.status(),
            "index": self.index.stats(),
            "workspace_root": str(self.workspace.root),
        }

    def submit(self, source: str, capability: str, payload: Any) -> dict[str, Any]:
        return self.bus.emit(source, capability, payload)

    def materialize_and_index(
        self,
        component: str,
        *,
        source_url: str | None = None,
        allow_non_routable: bool = False,
    ) -> dict[str, Any]:
        materialized = self.workspace.materialize(
            component,
            source_url=source_url,
            allow_non_routable=allow_non_routable,
        )
        indexed = self.index.index_component(
            component,
            materialized["path"],
        )
        return {
            "materialized": materialized,
            "indexed": indexed,
            "component_code_executed": False,
        }

    def search(self, query: str, limit: int = 20) -> list[dict]:
        return self.index.search(query, limit=limit)
