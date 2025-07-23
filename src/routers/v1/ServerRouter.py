import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import getSession
from src.docker.manager import ServerManager, getManager
from src.exceptions.DatabaseExceptions import (
    DatabaseError,
    ServerCreateError,
    ServerDeleteError,
)
from src.exceptions.DockerExceptions import (
    ServerStartError,
    ServerStopError,
)
from src.repositories.ServerRepository import ServerRepository
from src.schemas.pydantic import (
    ServerActivationSchema,
    ServerCreateSchema,
    ServerResponseSchema,
)
from src.services import ServerService

logger = logging.getLogger(__name__)

serverRouter = APIRouter(prefix="/v1/servers", tags=["Servers"])


@serverRouter.get("/{uuid}", response_model=Optional[ServerResponseSchema])
async def getServerByUuid(uuid: UUID4, session: AsyncSession = Depends(getSession)):
    try:
        serverRepo = ServerRepository(session)
        server = await serverRepo.getServerByUuid(uuid)

        if server is None:
            logger.warning(f"Server with UUID {uuid} not found")
            raise HTTPException(status_code=404, detail="Server not found")

        return server
    except DatabaseError as e:
        logger.error(f"Database error while retrieving server {uuid}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@serverRouter.get("/", response_model=List[ServerResponseSchema])
async def getAllServers(session: AsyncSession = Depends(getSession)):
    try:
        serverRepo = ServerRepository(session)
        servers = await serverRepo.getAllServers()

        if not servers:
            logger.warning("No servers found")
            raise HTTPException(status_code=404, detail="No servers found")

        return servers
    except DatabaseError as e:
        logger.error(f"Database error while retrieving all servers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@serverRouter.post("/", response_model=ServerResponseSchema, status_code=201)
async def addServer(
    server: Annotated[ServerCreateSchema, Depends()],
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerService(session)
        newServer = await service.addServerToDatabase(server)

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
    except DatabaseError as e:
        logger.error(f"Database error while adding server: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@serverRouter.post("/start", response_model=ServerResponseSchema, status_code=201)
async def startServer(
    server: Annotated[ServerActivationSchema, Depends()],
    serverManager: ServerManager = Depends(getManager),
):
    try:
        await serverManager.start_server(uuid=server.uuid)
        return Response(status_code=201)
    except ServerStartError as e:
        logger.error(f"Integrity error while starting server: {e}")
        raise HTTPException(status_code=400, detail="Server already strated")


@serverRouter.post("/stop", response_model=ServerResponseSchema, status_code=201)
async def stopServer(
    server: Annotated[ServerActivationSchema, Depends()],
    serverManager: ServerManager = Depends(getManager),
):
    try:
        await serverManager.stop_server(uuid=server.uuid)
        return Response(status_code=201)
    except ServerStopError as e:
        logger.error(f"Integrity error while stopping server: {e}")
        raise HTTPException(status_code=400, detail="Server already stopped")


@serverRouter.delete("/{uuid}")
async def deleteServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getSession),
    serverManager: ServerManager = Depends(getManager),
):
    try:
        service = ServerService(session)
        deletion = await service.removeServerFromDatabase(uuid)

        await serverManager.remove_server(uuid=str(uuid))

        if not deletion:
            logger.warning(f"Server with UUID {uuid} not found")
            raise HTTPException(status_code=404, detail="Server not found")

        return Response(status_code=204)
    except ServerDeleteError as e:
        logger.error(f"Integrity error while deleting server: {e}")
        raise HTTPException(status_code=400, detail="Server does not exists")
    except DatabaseError as e:
        logger.error(f"Database error while deleting server {uuid}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


__all__ = ["serverRouter"]
