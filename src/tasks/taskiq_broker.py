import logging

from taskiq import TaskiqEvents, TaskiqState
from taskiq_aio_pika import AioPikaBroker

from src.configuration import conf

log = logging.getLogger(__name__)

broker = AioPikaBroker(
    url=conf.rabbitmq.url,
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def on_worker_startup(state: TaskiqState) -> None:
    logging.basicConfig(
        level=conf.logging.log_level_value,
        format=conf.logging.log_format,
        datefmt=conf.logging.date_format,
    )
    log.info("Worker startup complete, got state: %s", state)
