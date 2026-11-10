from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class Service:
    name: str
    owner: str
    repository: str
    documentation: str
    environment: str
    status: str = "provisioning"


class ServiceCatalog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def list(self) -> list[Service]:
        if not self.path.exists():
            return []
        return [Service(**payload) for payload in json.loads(self.path.read_text(encoding="utf-8"))]

    def register(self, service: Service) -> None:
        services = self.list()
        if any(existing.name == service.name for existing in services):
            raise ValueError(f"service already exists: {service.name}")
        services.append(service)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([asdict(item) for item in services], indent=2) + "\n", encoding="utf-8"
        )

    def update_status(self, name: str, status: str) -> Service:
        services = self.list()
        service = next((item for item in services if item.name == name), None)
        if service is None:
            raise KeyError(name)
        service.status = status
        self.path.write_text(
            json.dumps([asdict(item) for item in services], indent=2) + "\n", encoding="utf-8"
        )
        return service
