from fastapi import FastAPI

from src.commands.controller import router as commandRouter
from src.servers.controller import router as serverRouter


def register_routes(app: FastAPI):
    app.include_router(serverRouter)
    app.include_router(commandRouter)
