from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repository_organism import RepositoryOrganism


@dataclass(frozen=True)
class RepositoryAdapterSpec:
    component: str
    kind: str
    capabilities: tuple[str, ...]
    mode: str
    command: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepositoryAdapterSpec":
        return cls(
            component=str(data["component"]),
            kind=str(data["kind"]),
            capabilities=tuple(sorted({str(x) for x in data.get("capabilities", [])})),
            mode=str(data.get("mode", "read-index")),
            command=str(data["command"]) if data.get("command") else None,
        )


class RepositoryAdapterRegistry:
    """Explicit adapter registry.

    Merely having a repository or executable installed never grants execution.
    The registry can report availability, but external CLI invocation remains
    a separate bounded dispatch operation.
    """

    def __init__(
        self,
        organism: RepositoryOrganism,
        config: dict[str, Any],
    ) -> None:
        self.organism = organism
        self.config = config
        self.adapters = tuple(
            RepositoryAdapterSpec.from_dict(x)
            for x in config.get("adapters", [])
        )
        self._validate()

    @classmethod
    def from_repo(
        cls,
        repo_root: str | Path,
        organism: RepositoryOrganism,
    ) -> "RepositoryAdapterRegistry":
        path = Path(repo_root) / "systems" / "repository_adapters.json"
        return cls(organism, json.loads(path.read_text(encoding="utf-8")))

    def _validate(self) -> None:
        if self.config.get("schema") != "meaw.repository-adapters/v1":
            raise ValueError("unsupported repository adapter schema")
        known = {c.name for c in self.organism.components}
        names = [x.component for x in self.adapters]
        if len(names) != len(set(names)):
            raise ValueError("one adapter declaration per component is allowed")
        unknown = set(names) - known
        if unknown:
            raise ValueError(f"adapter references unknown components: {sorted(unknown)}")
        if self.config.get("policy", {}).get("auto_execute_external") is not False:
            raise ValueError("external auto-execution must remain disabled")

    def get(self, component: str) -> RepositoryAdapterSpec | None:
        return next((x for x in self.adapters if x.component == component), None)

    def for_capability(self, capability: str) -> list[RepositoryAdapterSpec]:
        providers = {x.name for x in self.organism.providers(capability)}
        return [
            x for x in self.adapters
            if x.component in providers and capability in x.capabilities
        ]

    def availability(self, component: str) -> dict[str, Any]:
        spec = self.get(component)
        if spec is None:
            return {
                "component": component,
                "adapter_declared": False,
                "available": False,
                "reason": "no_explicit_adapter",
            }
        if spec.kind == "index-source":
            return {
                "component": component,
                "adapter_declared": True,
                "kind": spec.kind,
                "mode": spec.mode,
                "available": True,
                "external_execution": False,
            }
        if spec.kind == "optional-cli":
            exe = shutil.which(spec.command or "")
            return {
                "component": component,
                "adapter_declared": True,
                "kind": spec.kind,
                "mode": spec.mode,
                "command": spec.command,
                "available": bool(exe),
                "resolved_executable": exe,
                "external_execution": False,
            }
        return {
            "component": component,
            "adapter_declared": True,
            "kind": spec.kind,
            "available": False,
            "reason": "unsupported_adapter_kind",
        }

    def doctor(self) -> dict[str, Any]:
        rows = [self.availability(x.component) for x in self.adapters]
        return {
            "declared_adapters": len(rows),
            "available": sum(1 for x in rows if x.get("available")),
            "index_only": sum(1 for x in rows if x.get("kind") == "index-source"),
            "cli_present": sum(
                1 for x in rows
                if x.get("kind") == "optional-cli" and x.get("available")
            ),
            "external_auto_execution": False,
            "adapters": rows,
        }
