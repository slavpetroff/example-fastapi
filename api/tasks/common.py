from pydantic import BaseModel

from api import get_logger
from api.tasks.brokers import broker


logger = get_logger(__name__)


class HealthCheckResponse(BaseModel):
    status: str


@broker.subscriber("health_check")
async def health_check(data: dict) -> HealthCheckResponse:
    logger.info(f"Received health check: {data}")
    return HealthCheckResponse(status="ok")
