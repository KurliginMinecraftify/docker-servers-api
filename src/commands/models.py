from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

seed_maximum = 2**48 - 1


class CommandURLChoice(Enum):
    kick = "kick"
    ban = "ban"
    unban = "pardon"
    whitelist = "whitelist"
    dewhitelist = "dewhitelist"
    op = "op"
    deop = "deop"
    say = "say"


class CommandChoices(BaseModel):
    command: CommandURLChoice


class GameModeEnum(str, Enum):
    survival = "survival"
    creative = "creative"
    adventure = "adventure"
    spectator = "spectator"


class DifficultyEnum(str, Enum):
    peaceful = "peaceful"
    easy = "easy"
    normal = "normal"
    hard = "hard"


class ServerPropertiesPatch(BaseModel):
    max_players: Optional[int] = Field(default=None, ge=1, le=20)
    force_gamemode: Optional[bool] = None
    spawn_protection: Optional[int] = Field(default=None, ge=1, le=29_999_984)
    allow_flight: Optional[bool] = None
    allow_nether: Optional[bool] = None
    difficulty: Optional[DifficultyEnum] = None
    enable_command_block: Optional[bool] = None
    gamemode: Optional[GameModeEnum] = None
    generate_structures: Optional[bool] = None
    hardcore: Optional[bool] = None
    level_seed: Optional[int] = Field(default=None, ge=0, le=seed_maximum)
    online_mode: Optional[bool] = None
    pvp: Optional[bool] = None
    spawn_animals: Optional[bool] = None
    spawn_monsters: Optional[bool] = None
    spawn_npcs: Optional[bool] = None
    white_list: Optional[bool] = None
