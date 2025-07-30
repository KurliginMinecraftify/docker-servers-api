from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.configuration import getSettings
from src.entities import ServerModel
from src.utils import generate_password

from .models import ServerCreateSchema
from .repository import ServerRepository

settings = getSettings()


class ServerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.serverRepo = ServerRepository(session)
        self.min_port = settings.MINECRAFT_SERVER_MIN_PORT
        self.max_port = settings.MINECRAFT_SERVER_MAX_PORT

    async def addServer(self, server: ServerCreateSchema) -> ServerModel:
        used_ports = await self.serverRepo.getAllServersPorts()
        all_ports = [
            (i, i + (self.max_port - self.min_port) // 2)
            for i in range(self.min_port, self.max_port)
        ]
        free_ports = list(set(used_ports).symmetric_difference(all_ports))

        port, rcon_port = free_ports[0]

        newServer = ServerModel(
            port=port,
            rcon_port=rcon_port,
            rcon_password=generate_password(10),
            version=server.version,
        )

        self.session.add(newServer)

        await self.session.commit()
        await self.session.refresh(newServer)

        return newServer

    async def removeServer(self, uuid: UUID4) -> Response:
        server = await self.serverRepo.getServerByUuid(uuid)
        if not server:
            raise HTTPException(
                status_code=404, detail=f"Server with UUID `{uuid}` was not found."
            )

        await self.session.delete(server)
        await self.session.commit()
        return Response(status_code=200)
