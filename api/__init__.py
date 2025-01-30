import atexit
import datetime
import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue

import orjson
from logging_loki import LokiHandler

from api.config import settings


# TODO: For some reason this doesnt work with settings.LOG_LEVEL
LEVEL = "DEBUG"

# Do not change unless you know what you are doing
multiprocessing.set_start_method("spawn")


class DefaultFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        super().format(record)
        utc_time = datetime.datetime.now(datetime.UTC)
        formatted_time_iso = utc_time.isoformat()
        log_entry = {
            "time": formatted_time_iso,
            "level": record.levelname,
            "message": record.message,
            "logger": record.name,
            "extra": getattr(record, "extra", {}),
        }
        if record.exc_text:
            log_entry["message"] = (
                f"{log_entry["message"]}:\n{record.exc_text}"
            )

        return orjson.dumps(log_entry).decode()


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        return not (("/metrics" in message) or ("/loki" in message))


queue: Queue = Queue(-1)
queue_handler = QueueHandler(queue)

loki_handler = LokiHandler(
    url=settings.LOKI_ENDPOINT,
    tags={
        "service_name": "api",
    },
    version="1",
)
loki_handler.setLevel(LEVEL)
loki_handler.addFilter(EndpointFilter())
loki_handler.setFormatter(DefaultFormatter())

default_handler = logging.StreamHandler()
default_handler.setLevel(LEVEL)
default_handler.addFilter(EndpointFilter())
default_handler.setFormatter(DefaultFormatter())

root_logger = logging.getLogger()
root_logger.addHandler(queue_handler)

debug = settings.ENV == "test"
default_handlers = [
    default_handler,
]

if not debug:
    default_handlers.append(loki_handler)


for name in ["uvicorn", "uvicorn.error", "uvicorn.access", "faststream"]:
    logger = logging.getLogger(name)

    for handler in default_handlers:
        logger.addHandler(handler)

    logger.addFilter(EndpointFilter())
    logger.setLevel(LEVEL)


queue_listener = QueueListener(
    queue,
    *default_handlers,
    respect_handler_level=True,
)
queue_listener.start()

logging.basicConfig(
    level=LEVEL,
    handlers=default_handlers,
)
atexit.register(queue_listener.stop)


def get_logger(logger_name: str) -> logging.Logger:
    default_logger = logging.getLogger(logger_name)
    default_logger.setLevel(LEVEL)
    default_logger.addFilter(EndpointFilter())
    for _handler in default_handlers:
        default_logger.addHandler(_handler)

    return default_logger
