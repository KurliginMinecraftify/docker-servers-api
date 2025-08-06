from sqlalchemy.ext.asyncio import AsyncSession
from taskiq import TaskiqDepends

from src.tasks.taskiq_broker import broker
from src.core.database import getDBSession
from src.servers.depends import getManager
from src.servers.manager import ContainerManager
from src.servers.repository import ServerRepository


@broker.task
async def create_server_task(
    uuid: str,
    port: int,
    rcon_port: int,
    rcon_password: str,
    version: str,
    manager: ContainerManager = TaskiqDepends(getManager),
):
    await manager.create_server(uuid, port, rcon_port, rcon_password, version)


@broker.task
async def stop_server_task(
    uuid: str,
    manager: ContainerManager = TaskiqDepends(getManager),
):
    await manager.stop_server(uuid)


@broker.task
async def start_server_task(
    uuid: str, manager: ContainerManager = TaskiqDepends(getManager)
):
    await manager.start_server(uuid)


@broker.task
async def restart_server_task(
    uuid: str,
    manager: ContainerManager = TaskiqDepends(getManager),
):
    await manager.restart_server(uuid)


@broker.task
async def delete_server_task(
    uuid: str,
    session: AsyncSession = TaskiqDepends(getDBSession),
    manager: ContainerManager = TaskiqDepends(getManager),
):
    service = ServerRepository(session)

    await manager.remove_server(uuid=str(uuid))
    await service.deleteServerByUuid(uuid)
