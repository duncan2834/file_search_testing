from fastapi import APIRouter
from fastapi_healthchecks.api.router import HealthcheckRouter, Probe
from src.api.endpoints import ask, upload

router = APIRouter()

router.include_router(ask.router, tags=["Ask"])
router.include_router(upload.router, tags=["Upload file"])

router.include_router(
    HealthcheckRouter(
        Probe(
            name="liveness",
            checks=[
                
            ],
        ),
    ),
    prefix="/health",
)
