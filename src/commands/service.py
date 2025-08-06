import socket
from typing import List

from fastapi import HTTPException

from src.entities import ServerModel

from .console import ConsoleManager
from .models import CommandChoices, ServerPropertiesPatch
from .utils import update_properties


class ConsoleService:
    def __init__(self, server: ServerModel):
        self.uuid = server.uuid
        self.server = ConsoleManager(
            rcon_host="localhost",
            rcon_port=server.rcon_port,
            rcon_password=server.rcon_password,
        )

    async def run_command(self, command: CommandChoices, query: str) -> None:
        try:
            await self.server.execute_command(command, query)
        except ConnectionRefusedError as e:
            raise HTTPException(
                status_code=503, detail="RCON connection refused"
            ) from e
        except socket.timeout as e:
            raise HTTPException(
                status_code=504, detail="RCON connection timed out"
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Unexpected server error"
            ) from e
        except HTTPException as e:
            raise e

    async def update_properties(self, properties: ServerPropertiesPatch):
        await update_properties(
            server_name=str(self.uuid), config_values=properties.model_dump(mode="json")
        )

    # async def get_online_player_names(self) -> List[str]:
    #     response = await self.server.get_players_list()

    #     players = response.split(":")[1].strip().split(", ")

    #     return players if players != [""] else []
