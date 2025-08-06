# import asyncio
# from aiodocker import Docker

# async def main():
#     docker = Docker(url='npipe:////./pipe/dockerDesktopLinuxEngine')
#     info = await docker.system.info()
#     print(info)
#     await docker.close()

# asyncio.run(main())

# from enum import Enum
# from pydantic import BaseModel
# from typing import Optional

# class GameModeEnum(str, Enum):
#     survival = "survival"
#     creative = "creative"

# class Model(BaseModel):
#     gamemode: Optional[GameModeEnum]

# m = Model(gamemode=GameModeEnum.survival)

# print(m.model_dump(mode="json"))  # ✅ {'gamemode': 'survival'}
# print(dict(m))         # ❌ {'gamemode': <GameModeEnum.survival: 'survival'>}

# import nbtlib
# import json

# from nbtlib.tag import Int


# with nbtlib.load("minecraft_servers/c9a9966c-d4fa-44fb-98e9-580f8359ae19/world/playerdata/8f47df79-cc1a-33e9-91ef-22110edf7627.dat") as file:
#     data = json.dumps(file.unpack(), indent=2)
#     print(data)


# print(nbt.items)


# import json
# import nbtlib
# from pathlib import Path

# def get_players_from_dat_files(playerdata_path: Path) -> list[dict]:
#     players = []

#     for file in playerdata_path.glob("*.dat"):
#         try:
#             with nbtlib.load(file) as nbt:
#                 unpacked = nbt.unpack()

#                 # UUID из названия файла
#                 uuid = file.stem

#                 # Попытка получить ник
#                 name = None
#                 if "bukkit" in unpacked and "lastKnownName" in unpacked["bukkit"]:
#                     name = unpacked["bukkit"]["lastKnownName"]
#                 elif "LastKnownName" in unpacked:
#                     name = unpacked["LastKnownName"]
#                 else:
#                     name = "<unknown>"

#                 players.append({
#                     "uuid": uuid,
#                     "name": name,
#                     "online": False  # Пока заглушка
#                 })

#         except Exception as e:
#             print(f"[Ошибка] Не удалось прочитать {file}: {e}")

#     return players


# if __name__ == "__main__":
#     playerdata_dir = Path("minecraft_servers/c9a9966c-d4fa-44fb-98e9-580f8359ae19/world/playerdata")  # замени <server_id>
#     players = get_players_from_dat_files(playerdata_dir)

#     for player in players:
#         status = "🟢 Online" if player["online"] else "⚪ Offline"
#         print(f"{player['name']} ({player['uuid']}) - {status}")


import json
from pathlib import Path
from typing import Dict, List
from mcrcon import MCRcon  # pip install mcrcon

# === Пути ===
BASE_PATH = Path("minecraft_servers/c9a9966c-d4fa-44fb-98e9-580f8359ae19")
USERCACHE_PATH = BASE_PATH / "usercache.json"
PLAYERDATA_PATH = BASE_PATH / "world/playerdata"

# === usercache.json: UUID -> Name ===
def load_usercache(path: Path = USERCACHE_PATH) -> Dict[str, str]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return {entry["uuid"]: entry["name"] for entry in data}
    except FileNotFoundError:
        return {}

# === Все UUID из .dat файлов ===
def get_all_player_uuids(path: Path = PLAYERDATA_PATH) -> List[str]:
    return [file.stem for file in path.glob("*.dat")]

# === Онлайн-игроки через RCON ===
def get_online_player_names(rcon_host: str, rcon_pass: str, rcon_port: int = 25575) -> List[str]:
    try:
        with MCRcon(rcon_host, rcon_pass, port=rcon_port) as mcr:
            response = mcr.command("list")
            if ":" in response:
                return response.split(":")[1].strip().split(", ")
            return []
    except Exception:
        return []
    
def gather_all_players(rcon_host: str, rcon_pass: str, rcon_port: int) -> List[dict]:
    usercache = load_usercache()
    uuids = get_all_player_uuids()
    online_names = get_online_player_names(rcon_host, rcon_pass, rcon_port=rcon_port)

    name_to_uuid = {v: k for k, v in usercache.items()}

    players = []

    for uuid in uuids:
        name = usercache.get(uuid, "<unknown>")
        is_online = name in online_names
        players.append({
            "uuid": uuid,
            "name": name,
            "is_online": is_online
        })

    for name in online_names:
        uuid = name_to_uuid.get(name)
        if uuid and uuid not in uuids:
            players.append({
                "uuid": uuid,
                "name": name,
                "is_online": True
            })

    return players


def run_player_sync():
    RCON_HOST = "127.0.0.1"
    RCON_PASS = "Ig4B5g1up6"
    RCON_PORT = 25642

    players = gather_all_players(
        rcon_host=RCON_HOST,
        rcon_pass=RCON_PASS,
        rcon_port=RCON_PORT
    )

    for player in players:
        status = "🟢" if player["is_online"] else "⚪"
        print(f"{status} {player['name']} ({player['uuid']})")

# Запуск
if __name__ == "__main__":
    run_player_sync()