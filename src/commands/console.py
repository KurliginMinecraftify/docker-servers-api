import asyncio
import concurrent.futures

from fastapi import HTTPException
from mcrcon import MCRcon

from .models import CommandURLChoice


class ConsoleManager:
    def __init__(self, rcon_host: str, rcon_port: int, rcon_password: str):
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password

    def sync_rcon(self, command: str) -> str:
        with MCRcon(
            host=self.rcon_host, password=self.rcon_password, port=self.rcon_port
        ) as mcr:
            return mcr.command(command)

    async def send_rcon_command(self, command: str) -> str:
        loop = asyncio.get_event_loop()
        with concurrent.futures.ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.sync_rcon, command)

    async def execute_command(self, command: CommandURLChoice, query: str):
        try:
            await self.send_rcon_command(f"{command.value} {query}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
