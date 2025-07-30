import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import getDBSession
from src.exceptions import (
    DatabaseError,
)
from src.servers.repository import ServerRepository
from src.utils import update_properties

from .models import CommandChoices, ServerPropertiesPatch
from .service import ConsoleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/commands", tags=["Commands"])


@router.post("/{uuid}/runCommand", status_code=201)
async def runCommand(
    uuid: UUID4,
    command: Annotated[CommandChoices, Depends()],
    query: str | None = Query(description="Player nickname or message to send"),
    session: AsyncSession = Depends(getDBSession),
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


@router.patch("/{uuid}/updateProperties", status_code=200)
async def updateProperties(
    uuid: UUID4,
    command: Annotated[ServerPropertiesPatch, Depends()],
    session: AsyncSession = Depends(getDBSession),
):
    try:
        serverRepo = ServerRepository(session)
        server = await serverRepo.getServerByUuid(uuid)

        if not server:
            logger.error("Server not found")
            raise HTTPException(status_code=404, detail="Server not found")

        update_properties(uuid, command.model_dump())

        return Response(status_code=200)
    except DatabaseError as e:
        logger.error(f"Database error while running command: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    except Exception as e:
        logger.error(f"Error while updating properties: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
