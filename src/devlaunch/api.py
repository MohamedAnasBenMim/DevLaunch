from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .catalog import ServiceCatalog
from .platform import DeveloperPlatform

app = FastAPI(title="DevLaunch", version="1.0.0")
platform = DeveloperPlatform(Path("templates"), ServiceCatalog(Path("catalog/services.json")))


class ServiceRequest(BaseModel):
    name: str
    owner: str


@app.get("/catalog")
def catalog() -> list[dict[str, object]]:
    return [platform.service_status(service.name) for service in platform.catalog.list()]


@app.post("/services")
def create(request: ServiceRequest) -> dict[str, object]:
    try:
        result = platform.create_service(request.name, request.owner, Path("generated"))
        return asdict(result)
    except (ValueError, FileExistsError) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
