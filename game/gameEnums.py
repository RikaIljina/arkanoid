import enum
from enum import Flag, auto

class GameState(enum.Enum):
    unknown = "unknown"
    initializing = "initializing"
    initialized = "initialized"
    in_menu = "in menu"
    preparing_level = "preparing level"
    level_built = "level built"
    level_drawn = "level drawn"
    game_loop_running = "game loop running"
    

# class GS(Flag):
#     initialized = auto()
#     ball_moving = auto()
#     paddle_moving = auto()