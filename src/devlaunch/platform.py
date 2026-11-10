from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from .catalog import Service, ServiceCatalog


@dataclass(frozen=True, slots=True)
class ProvisioningResult:
    service: str
    namespace: str
    files_created: int
    onboarding_ms: float
    environment_setup_ms: float
    status: str


class DeveloperPlatform:
    def __init__(self, templates: Path, catalog: ServiceCatalog) -> None:
        self.templates = templates
        self.catalog = catalog

    def create_service(self, name: str, owner: str, destination: Path) -> ProvisioningResult:
        if not re.fullmatch(r"[a-z][a-z0-9-]{2,39}", name):
            raise ValueError("service name must be a lowercase DNS label")
        started = time.perf_counter()
        target = destination / name
        if target.exists():
            raise FileExistsError(target)
        template = self.templates / "python-service"
        files_created = 0
        for source in template.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(template)
            output = target / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            rendered = (
                source.read_text(encoding="utf-8")
                .replace("{{ service_name }}", name)
                .replace("{{ owner }}", owner)
            )
            output.write_text(rendered, encoding="utf-8")
            files_created += 1
        environment_started = time.perf_counter()
        namespace = f"dev-{name}"
        environment_plan = target / "environment.json"
        environment_plan.write_text(
            f'{{"namespace":"{namespace}","isolation":"namespace","network_policy":"default-deny"}}\n',
            encoding="utf-8",
        )
        environment_ms = (time.perf_counter() - environment_started) * 1000
        self.catalog.register(
            Service(name, owner, f"https://github.com/example/{name}", f"docs/{name}.md", namespace)
        )
        return ProvisioningResult(
            name,
            namespace,
            files_created + 1,
            round((time.perf_counter() - started) * 1000, 3),
            round(environment_ms, 3),
            "provisioning",
        )

    def service_status(self, name: str) -> dict[str, object]:
        service = next((item for item in self.catalog.list() if item.name == name), None)
        if service is None:
            raise KeyError(name)
        return asdict(service)
