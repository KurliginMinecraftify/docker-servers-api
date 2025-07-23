import logging
from typing import Optional

from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.exceptions import DatabaseError, ServerCreateError, ServerDeleteError
from src.models.ServerModel import ServerModel

logger = logging.getLogger(__name__)


class ServerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def getServerByPort(self, port: int) -> Optional[ServerModel]:
        try:
            query = select(ServerModel).where(ServerModel.port == port)
            result = await self.db.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.exception(f"Error getting server by port {port}: {e}")
            raise DatabaseError from e

    async def getServerByUuid(self, uuid: UUID4) -> Optional[ServerModel]:
        try:
            query = select(ServerModel).where(ServerModel.uuid == uuid)
            result = await self.db.execute(query)
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.exception(f"Error getting server by UUID {uuid}: {e}")
            raise DatabaseError from e

    async def getAllServers(self) -> Optional[list[ServerModel]]:
        try:
            query = select(ServerModel)
            result = await self.db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.exception(f"Error getting list of all servers: {e}")
            raise DatabaseError from e

    async def getAllServersPorts(self) -> Optional[list[(int, int)]]:
        try:
            query = select(ServerModel)
            result = await self.db.execute(query)
            return [
                (result.port, result.rcon_port) for result in result.scalars().all()
            ]
        except SQLAlchemyError as e:
            logger.exception(f"Error getting all servers ports: {e}")
            raise DatabaseError from e

    async def createServer(self, data: dict) -> Optional[ServerModel]:
        try:
            newServer = ServerModel(**data)
            self.db.add(newServer)
            await self.db.commit()
            await self.db.refresh(newServer)
            return newServer
        except IntegrityError as e:
            await self.db.rollback()
            logger.exception(f"Error creating server: {e}")
            raise ServerCreateError(
                "Server creation failed due to integrity error"
            ) from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Unknown error while creating server: {e}")
            raise DatabaseError from e

    async def deleteServerByUuid(self, uuid: UUID4) -> bool:
        try:
            server = await self.getServerByUuid(uuid)
            if not server:
                logger.warning(f"Server with UUID {uuid} not found")
                return False

            await self.db.delete(server)
            await self.db.commit()
            return True
        except IntegrityError as e:
            await self.db.rollback()
            logger.exception(f"Error deleting server {uuid}: {e}")
            raise ServerDeleteError(
                "Server deletion failed due to integrity error"
            ) from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.exception(f"Unknown error while deleting server {uuid}: {e}")
            return False
