from __future__ import annotations

import json
import statistics
import tempfile
from pathlib import Path

from .catalog import ServiceCatalog
from .platform import DeveloperPlatform


def benchmark(iterations: int = 25) -> dict[str, float | int]:
    onboarding = []
    environment = []
    templates = Path(__file__).parents[2] / "templates"
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        platform = DeveloperPlatform(templates, ServiceCatalog(root / "catalog.json"))
        for index in range(iterations):
            result = platform.create_service(
                f"service-{index:02d}", "platform-team", root / "services"
            )
            onboarding.append(result.onboarding_ms)
            environment.append(result.environment_setup_ms)
    return {
        "services_scaffolded": iterations,
        "median_onboarding_ms": round(statistics.median(onboarding), 3),
        "p95_onboarding_ms": round(sorted(onboarding)[int(iterations * 0.95) - 1], 3),
        "median_environment_setup_ms": round(statistics.median(environment), 3),
    }


def main() -> None:
    report = benchmark()
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/benchmark.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
