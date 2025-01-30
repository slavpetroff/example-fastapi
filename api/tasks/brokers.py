from faststream import FastStream
from faststream.asgi.app import AsgiFastStream
from faststream.redis import RedisBroker
from prometheus_client import REGISTRY, make_asgi_app

from api import get_logger
from api.config import settings
from api.utils.tracing import create_tracer_provider, setup_tracing


broker = RedisBroker(
    f"{'rediss' if settings.REDIS.SSL else 'redis'}"
    f"://:{settings.REDIS.PASSWORD}@{settings.REDIS.HOST}"
    f":{settings.REDIS.PORT}",
)


def create_fs_app() -> AsgiFastStream:
    service_name = "worker"

    logger = get_logger(service_name)

    setup_tracing(
        tracer_provider=create_tracer_provider(service_name=service_name),
        broker=broker,
        service_name=service_name,
    )

    return FastStream(broker, logger=logger).as_asgi(
        asgi_routes=[
            ("/metrics", make_asgi_app(REGISTRY)),
        ],
    )
