from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database.database import createTables, dropTables
from src.routers.v1.ServerRouter import serverRouter

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
