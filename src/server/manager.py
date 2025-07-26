import logging

from aiodocker import Docker
from aiodocker.containers import DockerContainer
from aiodocker.exceptions import DockerError

from src.exceptions import (
    ImageNotFoundError,
    ServerDeleteError,
    ServerManagerError,
    ServerNotFoundError,
    ServerStartError,
    ServerStopError,
)
from src.utils import (
    IMAGE_NAME,
    create_properties_from_template,
    ensure_server_dir,
    get_container_config,
    remove_server_dir,
)

DOCKER_PATH = "unix:///var/run/docker.sock"

log = logging.getLogger(__name__)


async def getManager():
    manager = ServerManager()
    try:
        yield manager
    finally:
        await manager.close()


class ServerManager:
    def __init__(self):
        self.docker = Docker(url=DOCKER_PATH)

    async def ensure_image(self) -> None:
        try:
            log.info(f"Found image {IMAGE_NAME}")
            await self.docker.images.inspect(IMAGE_NAME)
        except DockerError:
            try:
                log.info(f"Pulling image {IMAGE_NAME}")
                await self.docker.images.pull(IMAGE_NAME)
            except DockerError as e:
                raise ImageNotFoundError(f"Cannot pull image {IMAGE_NAME}") from e

    async def create_server(
        self, uuid: str, port: int, rcon_port: int, rcon_password: str, version: str
    ) -> None:
        server_dir = await ensure_server_dir(server_name=str(uuid))

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
            raise ServerManagerError(f"Failed to create container: {e}") from e

    async def start_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.start()
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ServerNotFoundError(f"Server '{uuid}' not found") from e
            raise ServerStartError(f"Failed to start server '{uuid}'. {e}") from e

    async def restart_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.restart()
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ServerNotFoundError(f"Server '{uuid}' not found") from e
            raise ServerStartError(f"Failed to start server '{uuid}'. {e}") from e

    async def stop_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.stop()
            log.info(f"Server '{uuid}' stopped")
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ServerNotFoundError(f"Server '{uuid}' not found") from e
            raise ServerStopError(f"Failed to stop server '{uuid}'") from e

    async def remove_server(self, uuid: str) -> None:
        try:
            container = await self.docker.containers.get(f"mc_{uuid}")
            await container.delete(force=True)
            log.info(f"Server '{uuid}' removed")
        except DockerError as e:
            if getattr(e, "status", None) == 404:
                raise ServerNotFoundError(f"Server '{uuid}' not found") from e
            raise ServerDeleteError(f"Server '{uuid}' not found") from e

        await remove_server_dir(uuid)

    async def list_servers(self, active: bool = False) -> list[DockerContainer]:
        containers = await self.docker.containers.list(all=not active)
        return containers

    async def close(self):
        await self.docker.close()


__all__ = ["ServerManager"]
