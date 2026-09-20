from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


TRUST_RANK = {
    "core": 100,
    "owned": 90,
    "owned-private": 90,
    "owned-fork": 80,
    "external": 40,
    "untrusted": 0,
}
ROUTABLE_LIFECYCLES = {"active", "adapter"}


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


@dataclass(frozen=True)
class RepositoryComponent:
    name: str
    repository: str
    role: str
    organ: str
    capabilities: tuple[str, ...]
    lifecycle: str
    trust: str
    priority: int
    default_branch: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepositoryComponent":
        return cls(
            name=str(data["name"]),
            repository=str(data["repository"]),
            role=str(data["role"]),
            organ=str(data["organ"]),
            capabilities=tuple(sorted({str(x) for x in data.get("capabilities", [])})),
            lifecycle=str(data.get("lifecycle", "pending")),
            trust=str(data.get("trust", "external")),
            priority=int(data.get("priority", 0)),
            default_branch=str(data.get("default_branch", "main")),
        )

    @property
    def routable(self) -> bool:
        return (
            self.lifecycle in ROUTABLE_LIFECYCLES
            and self.trust != "untrusted"
        )

    def score(self) -> tuple[int, int, str]:
        return (
            self.priority,
            TRUST_RANK.get(self.trust, 0),
            self.name,
        )


class RepositoryOrganism:
    """Declarative federation of repositories.

    Discovery is intentionally side-effect free. Loading the organism never clones,
    imports, executes, probes, or contacts a component. Runtime execution remains
    behind explicit MEAW adapters and bounded capability dispatch.
    """

    def __init__(self, manifest: dict[str, Any]) -> None:
        self.manifest = manifest
        self.components = tuple(
            RepositoryComponent.from_dict(x)
            for x in manifest.get("components", [])
        )
        self._validate()

    @classmethod
    def from_repo(cls, repo_root: str | Path) -> "RepositoryOrganism":
        path = Path(repo_root) / "ecosystem" / "repository_organism.json"
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def _validate(self) -> None:
        if self.manifest.get("schema") != "meaw.repository-organism/v1":
            raise ValueError("unsupported repository organism schema")
        names = [x.name for x in self.components]
        repos = [x.repository for x in self.components]
        if len(names) != len(set(names)):
            raise ValueError("duplicate component names")
        if len(repos) != len(set(repos)):
            raise ValueError("duplicate repositories")
        if not self.components:
            raise ValueError("repository organism cannot be empty")
        authorities = [
            c for c in self.components
            if c.repository == self.manifest.get("authority")
        ]
        if len(authorities) != 1:
            raise ValueError("exactly one repository must match authority")
        if authorities[0].trust != "core":
            raise ValueError("authority repository must be core trust")

    def topology_fingerprint(self) -> str:
        body = {
            "schema": self.manifest["schema"],
            "organism": self.manifest.get("organism"),
            "authority": self.manifest.get("authority"),
            "components": [
                {
                    "name": c.name,
                    "repository": c.repository,
                    "role": c.role,
                    "organ": c.organ,
                    "capabilities": list(c.capabilities),
                    "lifecycle": c.lifecycle,
                    "trust": c.trust,
                    "priority": c.priority,
                    "default_branch": c.default_branch,
                }
                for c in sorted(self.components, key=lambda x: x.name)
            ],
        }
        return hashlib.sha256(_canonical(body)).hexdigest()

    def providers(self, capability: str, include_non_routable: bool = False) -> list[RepositoryComponent]:
        items = [
            c for c in self.components
            if capability in c.capabilities
            and (include_non_routable or c.routable)
        ]
        return sorted(items, key=lambda c: c.score(), reverse=True)

    def route(self, capability: str) -> RepositoryComponent | None:
        providers = self.providers(capability)
        return providers[0] if providers else None

    def capability_map(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        caps = sorted({cap for c in self.components for cap in c.capabilities})
        for cap in caps:
            out[cap] = [c.name for c in self.providers(cap)]
        return out

    def organ_map(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for c in sorted(self.components, key=lambda x: (x.organ, -x.priority, x.name)):
            out.setdefault(c.organ, []).append(c.name)
        return out

    def status(self) -> dict[str, Any]:
        return {
            "organism": self.manifest.get("organism"),
            "authority": self.manifest.get("authority"),
            "nervous_system": self.manifest.get("nervous_system"),
            "component_count": len(self.components),
            "routable_count": sum(1 for x in self.components if x.routable),
            "organ_count": len(self.organ_map()),
            "capability_count": len(self.capability_map()),
            "topology_fingerprint": self.topology_fingerprint(),
        }
