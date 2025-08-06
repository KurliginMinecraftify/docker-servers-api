import logging

from aiodocker import Docker
from aiodocker.containers import DockerContainer
from aiodocker.exceptions import DockerError

from src.configuration import conf
from src.exceptions import (
    ContainerDeleteError,
    ContainerManagerError,
    ContainerNotFoundError,
    ContainerStartError,
    ContainerStopError,
)
from src.utils import get_container_config

from .utils import (
    create_properties_from_template,
    ensure_server_dir,
    remove_server_dir,
)

log = logging.getLogger(__name__)


class ContainerManager:
    def __init__(self):
        self.docker = Docker(url=conf.docker.docker_path)

    async def create_server(
        self, uuid: str, port: int, rcon_port: int, rcon_password: str, version: str
    ) -> None:
        server_dir = ensure_server_dir(server_name=str(uuid))

        container_config = get_container_config(
            server_dir=server_dir,
            port=port,
            rcon_port=rcon_port,
            rcon_password=rcon_password,
            version=version,
        )

        try:
            await self.docker.containers.create(
                name=f"mc_{uuid}", config=container_config
            )

            await create_properties_from_template(
                server_name=str(uuid), rcon_password=rcon_password
            )

            log.info(f"Server '{uuid}' running on port {port}")
        except DockerError as e:
            raise ContainerManagerError(f"Failed to create container: {e}") from e

    async def start_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.start()
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ContainerNotFoundError(f"Server '{uuid}' not found") from e
            raise ContainerStartError(f"Failed to start server '{uuid}'. {e}") from e

    async def restart_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.restart()
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ContainerNotFoundError(f"Server '{uuid}' not found") from e
            raise ContainerStartError(f"Failed to start server '{uuid}'. {e}") from e

    async def stop_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.stop()
            log.info(f"Server '{uuid}' stopped")
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ContainerNotFoundError(f"Server '{uuid}' not found") from e
            raise ContainerStopError(f"Failed to stop server '{uuid}'") from e

    async def remove_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.delete(force=True)

            remove_server_dir(uuid)
            log.info(f"Server '{uuid}' removed")
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ContainerNotFoundError(f"Server '{uuid}' not found") from e
            raise ContainerDeleteError(f"Server '{uuid}' not found") from e

    async def list_servers(self, active: bool = False) -> list[DockerContainer]:
        containers = await self.docker.containers.list(all=not active)
        return containers

    async def close(self):
        await self.docker.close()
