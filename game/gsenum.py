import enum
from enum import Flag, auto

class GameState(enum.Enum):
    unknown = "unknown"
    initializing = "initializing"
    initialized = "initialized"
    game_loop_running = "game loop running"
    level_built = "level built"

class GS(Flag):
    initialized = auto()
    ball_moving = auto()
    paddle_moving = auto()