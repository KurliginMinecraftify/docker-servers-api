from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ServerModel import ServerModel
from src.repositories.ServerRepository import ServerRepository
from src.schemas.pydantic.ServerSchema import ServerCreateSchema
from src.utils import generate_password


class ServerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.serverRepo = ServerRepository(session)

    async def addServerToDatabase(self, server: ServerCreateSchema) -> ServerModel:
        used_ports = await self.serverRepo.getAllServersPorts()
        all_ports = [(i, i + 100) for i in range(25500, 25600)]
        free_ports = list(set(used_ports).symmetric_difference(all_ports))

        port, rcon_port = free_ports[0]

        newServer = ServerModel(
            port=port,
            rcon_port=rcon_port,
            rcon_password=generate_password(10),
            version=server.version,
        )

        self.session.add(newServer)

        try:
            await self.session.commit()
            await self.session.refresh(newServer)
            return newServer
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail="Database error while creating server"
            )

    async def removeServerFromDatabase(self, uuid: UUID4) -> Response:
        server = await self.serverRepo.getServerByUuid(uuid)
        if not server:
            raise HTTPException(
                status_code=404, detail=f"Server with UUID `{uuid}` was not found."
            )

        try:
            await self.session.delete(server)
            await self.session.commit()
            return Response(status_code=200)

        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(
                status_code=400,
                detail="Cannot delete server: there are still users linked to it.",
            )

        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail="A database error occurred while deleting the server.",
            )

        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=500, detail=f"An unexpected error occurred: {str(e)}"
            )


__all__ = ["ServerService"]
