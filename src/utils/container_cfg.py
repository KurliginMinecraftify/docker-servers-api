IMAGE_NAME = "itzg/minecraft-server"


def get_container_config(
    server_dir: str,
    port: int,
    rcon_port: int,
    rcon_password: str,
    version: str = "latest",
) -> dict:
    container_config = {
        "Image": IMAGE_NAME,
        "Env": [
            "EULA=TRUE",
            "ENABLE_RCON=true",
            f"RCON_PASSWORD={rcon_password}",
            f"VERSION={version}",
            "OVERRIDE_SERVER_PROPERTIES=FALSE",
        ],
        "HostConfig": {
            "Binds": [f"{server_dir}:/data"],
            "PortBindings": {
                "25565/tcp": [{"HostPort": str(port)}],
                "25575/tcp": [{"HostPort": str(rcon_port)}],
            },
        },
        "ExposedPorts": {"25565/tcp": {}, "25575/tcp": {}},
    }

    return container_config


__all__ = ["get_container_config", "IMAGE_NAME"]
