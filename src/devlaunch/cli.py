import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .catalog import ServiceCatalog
from .platform import DeveloperPlatform


def main() -> None:
    parser = argparse.ArgumentParser(description="DevLaunch self-service platform")
    parser.add_argument("name")
    parser.add_argument("--owner", default="platform-team")
    parser.add_argument("--destination", type=Path, default=Path("generated"))
    args = parser.parse_args()
    templates = Path(__file__).parents[2] / "templates"
    platform = DeveloperPlatform(templates, ServiceCatalog(Path("catalog/services.json")))
    print(
        json.dumps(
            asdict(platform.create_service(args.name, args.owner, args.destination)), indent=2
        )
    )
