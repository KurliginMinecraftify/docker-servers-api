from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.database import createTables, dropTables

from .api import register_routes
from .logging import LogLevels, configure_logging

configure_logging(LogLevels.info)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await dropTables()
    await createTables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


register_routes(app)
