import logging
from functools import wraps
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import getSession
from src.exceptions.DatabaseExceptions import (
    DatabaseError,
    ServerCreateError,
    ServerDeleteError,
)
from src.exceptions.DockerExceptions import (
    ServerManagerError,
    ServerRestartError,
    ServerStartError,
    ServerStopError,
)
from src.repositories.ServerRepository import ServerRepository
from src.schemas.pydantic import (
    ServerCreateSchema,
    ServerResponseSchema,
)
from src.server.manager import ServerManager, getManager
from src.services import ServerService

logger = logging.getLogger(__name__)

serverRouter = APIRouter(prefix="/v1/servers", tags=["Servers"])


def handle_db_and_manager_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
        except ServerManagerError as e:
            logger.error(f"Server manager error: {e}")
            raise HTTPException(status_code=500, detail="Server manager error")

    return wrapper


@serverRouter.get("/{uuid}", summary="Get server by uuid", response_model=Optional[ServerResponseSchema])
@handle_db_and_manager_errors
async def getServerByUuid(uuid: UUID4, session: AsyncSession = Depends(getSession)):
    serverRepo = ServerRepository(session)
    server = await serverRepo.getServerByUuid(uuid)

    if server is None:
        logger.warning(f"Server with UUID {uuid} not found")
        raise HTTPException(status_code=404, detail="Server not found")

    return server


@serverRouter.get("/", summary="Get all servers", response_model=List[ServerResponseSchema])
@handle_db_and_manager_errors
async def getAllServers(session: AsyncSession = Depends(getSession)):
    serverRepo = ServerRepository(session)
    servers = await serverRepo.getAllServers()

    if not servers:
        logger.warning("No servers found")
        raise HTTPException(status_code=404, detail="No servers found")

    return servers


@serverRouter.post("/", summary="Add server", response_model=ServerResponseSchema, status_code=201)
@handle_db_and_manager_errors
async def addServer(
    server: Annotated[ServerCreateSchema, Depends()],
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerService(session)
        newServer = await service.addServer(server)

        await serverManager.create_server(
            uuid=newServer.uuid,
            port=newServer.port,
            rcon_port=newServer.rcon_port,
            rcon_password=newServer.rcon_password,
            version=server.version,
        )
        return newServer
    except ServerCreateError as e:
        logger.error(f"Integrity error while adding server: {e}")
        raise HTTPException(status_code=400, detail="Server already exists")


@serverRouter.post(
    "/{uuid}/start",
    summary="Start server",
    status_code=201,
    responses={
        201: {"description": "Server started successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@handle_db_and_manager_errors
async def startServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await serverManager.start_server(uuid=server.uuid)
        return Response(status_code=201)
    except ServerStartError as e:
        logger.error(f"Server manager error while starting server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


@serverRouter.post(
    "/{uuid}/restart",
    summary="Restart server",
    status_code=201,
    responses={
        201: {"description": "Server restarted successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@handle_db_and_manager_errors
async def restartServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await serverManager.restart_server(uuid=server.uuid)
        return Response(status_code=201)
    except ServerRestartError as e:
        logger.error(f"Server manager error while starting server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


@serverRouter.post(
    "/{uuid}/stop",
    summary="Stop server",
    status_code=201,
    responses={
        201: {"description": "Server stopped successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@handle_db_and_manager_errors
async def stopServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await serverManager.stop_server(uuid=server.uuid)

        return Response(status_code=201)
    except ServerStopError as e:
        logger.error(f"Integrity error while stopping server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


@serverRouter.delete(
    "/{uuid}/delete",
    summary="Delete server",
    status_code=204,
    responses={
        204: {"description": "Server deleted successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@handle_db_and_manager_errors
async def deleteServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerService(session)
        server = await service.get_by_uuid(uuid)

        if not server:
            logger.warning(f"Server with UUID {uuid} not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await serverManager.remove_server(uuid=str(uuid))
        await service.removeServer(uuid)

        return Response(status_code=204)
    except ServerDeleteError as e:
        logger.error(f"Integrity error while deleting server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


__all__ = ["serverRouter"]
