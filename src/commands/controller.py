import logging
from functools import wraps
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import getDBSession
from src.exceptions import (
    DatabaseError,
)
from src.servers.repository import ServerRepository

from .models import CommandChoices, ServerPropertiesPatch
from .service import ConsoleService

# from .utils import update_properties

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/commands", tags=["Commands"])


def errorHandler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    return wrapper


@errorHandler
@router.post(
    "/{uuid}/runCommand",
    summary="Send RCON command to minecraft server",
    status_code=201,
)
async def runCommand(
    uuid: UUID4,
    command: Annotated[CommandChoices, Depends()],
    query: str = Query(description="Player nickname or message to send"),
    session: AsyncSession = Depends(getDBSession),
):
    serverRepo = ServerRepository(session)
    server = await serverRepo.getServerByUuid(uuid)

    if not server:
        logger.error("Server not found")
        raise HTTPException(status_code=404, detail="Server not found")

    consoleService = ConsoleService(server)
    await consoleService.run_command(command.command, query)

    return Response(status_code=201)


@errorHandler
@router.patch(
    "/{uuid}/updateProperties", summary="Update server properties file", status_code=200
)
async def updateProperties(
    uuid: UUID4,
    commands: Annotated[ServerPropertiesPatch, Depends()],
    session: AsyncSession = Depends(getDBSession),
):
    serverRepo = ServerRepository(session)
    server = await serverRepo.getServerByUuid(uuid)

    if not server:
        logger.error("Server not found")
        raise HTTPException(status_code=404, detail="Server not found")

    consoleService = ConsoleService(server)
    await consoleService.update_properties(commands)

    return Response(status_code=200)


# @errorHandler
# @router.get("/{uuid}/", summary="Get online/offline players")
# async def getAllPlayers(
#     uuid: UUID4,
#     session: AsyncSession = Depends(getDBSession),
#     ):
#     serverRepo = ServerRepository(session)
#     server = await serverRepo.getServerByUuid(uuid)

#     if not server:
#         logger.error("Server not found")
#         raise HTTPException(status_code=404, detail="Server not found")

#     consoleService = ConsoleService(server)
#     players = await consoleService.get_online_player_names()

#     if not players:
#         logger.error("Players not found")
#         raise HTTPException(status_code=404, detail="Players not found")
#     return players
