from pathlib import Path
import aiofiles

import javaproperties

from src.configuration import conf

server_dir = Path(conf.docker.server_dir).resolve()
base_dir = Path(conf.docker.base_dir).resolve()
template_path = base_dir / "static" / "server.properties.template"


async def update_properties(server_name: str, config_values: dict) -> None:
    server_path = server_dir / server_name
    properties_path = server_path / "server.properties"

    async with aiofiles.open(properties_path, "rb") as f:
        props = javaproperties.load(f)

    for k, v in config_values.items():
        if v is not None:
            props[k.replace("_", "-")] = str(v)

    async with aiofiles.open(properties_path, "w", encoding="utf-8") as f:
        javaproperties.dump(props, f)
