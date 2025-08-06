import shutil
from pathlib import Path
import aiofiles

import javaproperties

from src.configuration import conf

server_dir = Path(conf.docker.server_dir).resolve()
base_dir = Path(conf.docker.base_dir).resolve()
template_path = base_dir / "static" / "server.properties.template"


def ensure_server_dir(server_name: str) -> Path:
    server_path = server_dir / server_name
    server_path.mkdir(parents=True, exist_ok=True)
    return server_path


def remove_server_dir(server_name: str) -> None:
    server_path = server_dir / server_name
    if server_path.exists():
        shutil.rmtree(server_path)


async def create_properties_from_template(server_name: str, rcon_password: str) -> None:
    server_path = ensure_server_dir(server_name)
    output_path = server_path / "server.properties"

    shutil.copy(template_path, output_path)

    async with aiofiles.open(output_path, "rb") as f:
        props = javaproperties.load(f)

    props["rcon.password"] = rcon_password

    async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
        javaproperties.dump(props, f)
