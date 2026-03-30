from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter(
    prefix="/health",
    tags=["system-health"],
)


class HealthStatus(BaseModel):
    status: str = 'ok'
    time: datetime = Field(default_factory=lambda: datetime.now(tz=ZoneInfo('America/Sao_Paulo')))
    version: str = '1.0.0'

    def is_operational(self) -> bool:
        return self.status == 'ok'


class HealthReport(BaseModel):
    checks: list[HealthStatus]

    def has_failures(self):
        return any(not c.is_operational() for c in self.checks)


def perform_system_checks() -> HealthReport:
    results = [HealthStatus(status='ok')]
    return HealthReport(checks=results)


@router.get("/", response_model=HealthReport)
def get_system_health():
    report = perform_system_checks()

    if report.has_failures():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is degraded"
        )

    return report
