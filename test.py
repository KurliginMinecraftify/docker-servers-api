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

import nbtlib
import json

from nbtlib.tag import Int


with nbtlib.load("minecraft_servers/b267b0c4-1de9-41aa-ad39-b6d0fecb03e3/world/playerdata/8f47df79-cc1a-33e9-91ef-22110edf7627.dat") as file:
    data = json.dumps(file.unpack(), indent=2)
    print(data)


# Вывести весь файл
# print(nbt.items)
