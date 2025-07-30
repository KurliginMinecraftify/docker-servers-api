from fastapi import HTTPException

from src.entities import ServerModel

from .console import ConsoleManager
from .models import CommandChoices


class ConsoleService:
    def __init__(self, server: ServerModel):
        self.server = ConsoleManager(
            rcon_host="0.0.0.0",
            rcon_port=server.rcon_port,
            rcon_password=server.rcon_password,
        )

    async def run_command(self, command: CommandChoices, query: str) -> None:
        try:
            await self.server.execute_command(command, query)
        except HTTPException as e:
            raise e
