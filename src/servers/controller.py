import logging
import traceback
from functools import wraps
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import getDBSession
from src.exceptions import (
    ContainerCreateError,
    ContainerDeleteError,
    ContainerManagerError,
    ContainerStartError,
    ContainerStopError,
    DatabaseError,
    ServerRestartError,
)
from src.tasks import (
    create_server_task,
    delete_server_task,
    restart_server_task,
    start_server_task,
    stop_server_task,
)

from .models import (
    ServerCreateSchema,
    ServerResponseSchema,
)
from .repository import ServerRepository
from .service import ServerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/servers", tags=["Servers"])


def errorHandler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DatabaseError as e:
            logger.error("Database error: %s\n%s", e, traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal server error")
        except ContainerManagerError as e:
            logger.error(f"Container manager error: {e}")
            raise HTTPException(status_code=500, detail="Container manager error")

    return wrapper


@router.get(
    "/{uuid}/",
    summary="Get server by uuid",
    response_model=Optional[ServerResponseSchema],
)
@errorHandler
async def getServerByUuid(uuid: UUID4, session: AsyncSession = Depends(getDBSession)):
    serverRepo = ServerRepository(session)
    server = await serverRepo.getServerByUuid(uuid)

    if not server:
        logger.warning(f"Server with UUID {uuid} not found")
        raise HTTPException(status_code=404, detail="Server not found")

    return server


@router.get("/", summary="Get all servers", response_model=List[ServerResponseSchema])
@errorHandler
async def getAllServers(
    session: AsyncSession = Depends(getDBSession),
):
    serverRepo = ServerRepository(session)
    servers = await serverRepo.getAllServers()

    if not servers:
        logger.warning("Servers not found")
        raise HTTPException(status_code=404, detail="Servers not found")

    return servers


@router.post(
    "/", summary="Add server", response_model=ServerResponseSchema, status_code=201
)
@errorHandler
async def addServer(
    server: Annotated[ServerCreateSchema, Depends()],
    session: AsyncSession = Depends(getDBSession),
):
    try:
        service = ServerService(session)
        newServer = await service.addServer(server)

        await create_server_task.kiq(
            uuid=newServer.uuid,
            port=newServer.port,
            rcon_port=newServer.rcon_port,
            rcon_password=newServer.rcon_password,
            version=server.version,
        )

        return newServer
    except ContainerCreateError as e:
        logger.error(f"Integrity error while adding server: {e}")
        raise HTTPException(status_code=400, detail="Server already exists")


@router.post(
    "/{uuid}/start",
    summary="Start server",
    status_code=201,
    responses={
        201: {"description": "Server started successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@errorHandler
async def startServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getDBSession),
):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await start_server_task.kiq(uuid=server.uuid)
        return Response(status_code=201)
    except ContainerStartError as e:
        logger.error(f"Server manager error while starting server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


@router.post(
    "/{uuid}/restart",
    summary="Restart server",
    status_code=201,
    responses={
        201: {"description": "Server restarted successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@errorHandler
async def restartServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getDBSession),
):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await restart_server_task.kiq(uuid=server.uuid)
        return Response(status_code=201)
    except ServerRestartError as e:
        logger.error(f"Server manager error while starting server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


@router.post(
    "/{uuid}/stop",
    summary="Stop server",
    status_code=201,
    responses={
        201: {"description": "Server stopped successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@errorHandler
async def stopServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getDBSession),
):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await stop_server_task.kiq(uuid=server.uuid)

        return Response(status_code=201)
    except ContainerStopError as e:
        logger.error(f"Integrity error while stopping server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")


@router.delete(
    "/{uuid}/delete",
    summary="Delete server",
    status_code=204,
    responses={
        204: {"description": "Server deleted successfully"},
        404: {"description": "Server not found"},
        500: {"description": "Server manager error"},
    },
)
@errorHandler
async def deleteServer(uuid: UUID4, session: AsyncSession = Depends(getDBSession)):
    try:
        service = ServerRepository(session)
        server = await service.getServerByUuid(uuid)

        if not server:
            logger.warning(f"Server with UUID {uuid} not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await delete_server_task.kiq(uuid)

        return Response(status_code=204)
    except ContainerDeleteError as e:
        logger.error(f"Integrity error while deleting server: {e}")
        raise HTTPException(status_code=500, detail="Server manager error")
