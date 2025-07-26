from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from src.database.database import createTables, dropTables
from src.routers.v1.CommandRouter import commandRouter
from src.routers.v1.ServerRouter import serverRouter

from .logging import configure_logging

configure_logging()

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


app.include_router(serverRouter)
app.include_router(commandRouter)
