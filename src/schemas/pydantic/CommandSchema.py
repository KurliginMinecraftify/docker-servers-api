from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

seed_maximum = 2**48 - 1


class CommandURLChoice(Enum):
    kick = "kick"
    ban = "ban"
    unban = "unban"
    whitelist = "whitelist"
    dewhitelist = "dewhitelist"
    op = "op"
    deop = "deop"
    say = "say"


class CommandChoices(BaseModel):
    command: CommandURLChoice


class ServerPropertiesPatch(BaseModel):
    allow_flight: Optional[bool] = None
    allow_nether: Optional[bool] = None
    difficulty: Optional[int] = Field(default=None, ge=0, le=3)
    enable_command_block: Optional[bool] = None
    gamemode: Optional[int] = Field(default=None, ge=0, le=3)
    generate_structures: Optional[bool] = None
    hardcore: Optional[bool] = None
    level_seed: Optional[int] = Field(default=None, ge=0, le=seed_maximum)
    online_mode: Optional[bool] = None
    pvp: Optional[bool] = None
    spawn_animals: Optional[bool] = None
    spawn_monsters: Optional[bool] = None
    spawn_npcs: Optional[bool] = None
    white_list: Optional[bool] = None
