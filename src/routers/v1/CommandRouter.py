import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import getSession
from src.exceptions.DatabaseExceptions import (
    DatabaseError,
)
from src.repositories.ServerRepository import ServerRepository
from src.schemas.pydantic import CommandChoices, ServerPropertiesPatch
from src.services import ConsoleService
from src.utils import update_properties

logger = logging.getLogger(__name__)

commandRouter = APIRouter(prefix="/v1/commands", tags=["Commands"])


@commandRouter.post("/{uuid}/runCommand", status_code=201)
async def runCommand(
    uuid: UUID4,
    command: Annotated[CommandChoices, Depends()],
    query: str | None = Query(description="Player nickname or message to send"),
    session: AsyncSession = Depends(getSession),
):
    try:
        serverRepo = ServerRepository(session)
        server = await serverRepo.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        consoleService = ConsoleService(server)
        await consoleService.run_command(command.command, query)

        return Response(status_code=201)
    except DatabaseError as e:
        logger.error(f"Database error while running command: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@commandRouter.patch("/{uuid}/updateProperties", status_code=200)
async def updateProperties(
    uuid: UUID4,
    command: Annotated[ServerPropertiesPatch, Depends()],
    session: AsyncSession = Depends(getSession),
):
    try:
        serverRepo = ServerRepository(session)
        server = await serverRepo.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        await update_properties(uuid, command.model_dump())

        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error while updating properties: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


__all__ = ["commandRouter"]
