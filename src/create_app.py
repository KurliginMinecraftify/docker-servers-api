from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.tasks.taskiq_broker import broker
from src.core.database import createTables, dropTables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await dropTables()
    await createTables()

    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
    )
    return app
