from sqlalchemy.ext.asyncio import AsyncSession

from src.configuration import conf
from src.entities import ServerModel
from src.utils import generate_password

from .models import ServerCreateSchema
from .repository import ServerRepository


class ServerService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.serverRepo = ServerRepository(session)
        self.min_port = conf.docker.minecraft_server_min_port
        self.max_port = conf.docker.minecraft_server_max_port

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
