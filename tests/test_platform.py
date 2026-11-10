from pathlib import Path

from devlaunch.catalog import Service, ServiceCatalog
from devlaunch.platform import DeveloperPlatform


def platform(tmp_path: Path) -> DeveloperPlatform:
    templates = Path(__file__).parents[1] / "templates"
    return DeveloperPlatform(templates, ServiceCatalog(tmp_path / "catalog.json"))


def test_scaffolds_golden_path_and_environment(tmp_path: Path) -> None:
    result = platform(tmp_path).create_service("orders-api", "payments", tmp_path / "services")
    assert result.files_created == 5
    assert result.namespace == "dev-orders-api"
    assert (tmp_path / "services/orders-api/deployment.yaml").exists()
    assert "orders-api" in (tmp_path / "services/orders-api/README.md").read_text()


def test_rejects_invalid_service_name(tmp_path: Path) -> None:
    try:
        platform(tmp_path).create_service("Bad_Name", "team", tmp_path)
    except ValueError as error:
        assert "DNS" in str(error)
    else:
        raise AssertionError("invalid names must fail")


def test_catalog_prevents_duplicate_services(tmp_path: Path) -> None:
    catalog = ServiceCatalog(tmp_path / "catalog.json")
    service = Service("api", "team", "repo", "docs", "dev-api")
    catalog.register(service)
    try:
        catalog.register(service)
    except ValueError as error:
        assert "already exists" in str(error)
    else:
        raise AssertionError("duplicates must fail")


def test_status_updates_are_visible(tmp_path: Path) -> None:
    app = platform(tmp_path)
    app.create_service("status-api", "team", tmp_path / "services")
    app.catalog.update_status("status-api", "healthy")
    assert app.service_status("status-api")["status"] == "healthy"


def test_missing_service_status_fails(tmp_path: Path) -> None:
    try:
        platform(tmp_path).service_status("missing")
    except KeyError as error:
        assert error.args[0] == "missing"
    else:
        raise AssertionError("missing services must fail")


def test_existing_destination_is_not_overwritten(tmp_path: Path) -> None:
    app = platform(tmp_path)
    app.create_service("orders-api", "team", tmp_path / "services")
    try:
        app.create_service("orders-api", "team", tmp_path / "services")
    except FileExistsError:
        pass
    else:
        raise AssertionError("existing output must not be overwritten")
