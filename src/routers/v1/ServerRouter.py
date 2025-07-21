import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import getSession
from src.repositories.ServerRepository import ServerRepository
from src.schemas.pydantic import ServerCreateSchema, ServerResponseSchema
from src.services import ServerService

logger = logging.getLogger(__name__)

serverRouter = APIRouter(
    prefix="/v1/servers",
    tags=["Servers"]
)


@serverRouter.get("/{uuid}", response_model=Optional[ServerResponseSchema])
async def getServerByUuid(
    uuid: UUID4, 
    session: AsyncSession = Depends(getSession)
):
    try:
        serverRepo = ServerRepository(session)
        server = await serverRepo.getServerByUuid(uuid)

        if server is None:
            logger.warning(f"Server with UUID {uuid} not found")
            raise HTTPException(status_code=404, detail="Server not found")

        return server
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving server {uuid}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@serverRouter.post("/", response_model=ServerResponseSchema, status_code=201)
async def addServer(
    server: Annotated[ServerCreateSchema, Depends()], 
    session: AsyncSession = Depends(getSession)
):
    try:
        service = ServerService(session)
        newServer = await service.addServerToDatabase(server)
        return newServer
    except IntegrityError as e:
        logger.error(f"Integrity error while adding server: {e}")
        raise HTTPException(status_code=400, detail="Server already exists")
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding server: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@serverRouter.delete("/{uuid}")
async def deleteServer(
    uuid: UUID4,
    session: AsyncSession = Depends(getSession)
):
    try:
        service = ServerService(session)
        deletion = await service.removeServerFromDatabase(uuid)

        if not deletion:
            logger.warning(f"Server with UUID {uuid} not found")
            raise HTTPException(status_code=404, detail="Server not found")

        return Response(status_code=204)
    except SQLAlchemyError as e:
        logger.error(f"Database error while deleting server {uuid}: {e}")
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
    except SQLAlchemyError as e:
        logger.error(f"Database error while retrieving all servers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


__all__ = [
    "serverRouter"
]
