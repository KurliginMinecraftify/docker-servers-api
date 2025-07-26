import shutil
from pathlib import Path

import javaproperties

from src.configuration import getSettings

settings = getSettings()

server_dir = Path(settings.SERVERS_DIR).resolve()
base_dir = Path(settings.BASE_DIR).resolve()
template_path = base_dir / "static" / "server.properties.template"


async def ensure_server_dir(server_name: str) -> Path:
    server_path = server_dir / server_name
    server_path.mkdir(parents=True, exist_ok=True)
    return server_path


async def remove_server_dir(server_name: str) -> None:
    server_path = server_dir / server_name
    if server_path.exists():
        shutil.rmtree(server_path)


async def create_properties_from_template(server_name: str, rcon_password: str) -> None:
    server_path = await ensure_server_dir(server_name)
    output_path = server_path / "server.properties"

    shutil.copy(template_path, output_path)

    await update_properties(
        server_name,
        {
            "rcon.password": rcon_password,
        },
    )


async def update_properties(server_name, config_values: dict) -> None:
    server_path = await ensure_server_dir(str(server_name))
    properties_path = server_path / "server.properties"

    with properties_path.open("rb") as f:
        props = javaproperties.load(f)

    for k, v in config_values.items():
        if v is not None:
            props[k.replace("_", "-")] = str(v)

    with properties_path.open("w", encoding="utf-8") as f:
        javaproperties.dump(props, f)


__all__ = [
    "ensure_server_dir",
    "remove_server_dir",
    "update_properties",
    "create_properties_from_template",
]
