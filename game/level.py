from pygame.sprite import Group
from sprites.movingSprites import Paddle, Ball
from sprites.staticSprites import Wall, Brick

class Level(object):
    def __init__(self, global_vars) -> None:
        self.cfg = global_vars['cfg']
        self.global_vars = global_vars
        self.level_dict = {
            1: '''iter(
            [
                (x, y)
                for x in range(
                    self.cfg["BRICK_SIZE"][0] + self.cfg["WALL_THICKNESS"],
                    self.cfg["SCREEN_WIDTH"]
                    - self.cfg["BRICK_SIZE"][0]
                    - self.cfg["WALL_THICKNESS"],
                    self.cfg["BRICK_SIZE"][0],
                )
                for y in range(
                    self.cfg["BRICK_SIZE"][0] + self.cfg["WALL_THICKNESS"],
                    self.cfg["SCREEN_HEIGHT"] // 2,
                    self.cfg["BRICK_SIZE"][1],
                )
            ]
        )'''
        }

    def build_level(self, n):
        level_setup = eval(self.level_dict[n])
        walls = Group()
        walls.add(
            Wall("left", self.global_vars),
            Wall("right", self.global_vars),
            Wall("top", self.global_vars),
            Wall("bottom", self.global_vars),
            
        )
        self.global_vars["walls"] = walls
        bricks = Group()
        bricks.add([Brick(coord[0], coord[1], self.global_vars) for coord in level_setup])
        self.global_vars["bricks"] = bricks
        paddle = Paddle(self.global_vars)
        self.global_vars["paddle"] = paddle

        ball = Ball(self.global_vars)
        self.global_vars["ball"] = ball
        
        
      #  return eval(self.level_dict[n])

    def get_level(self, n):
        match n:
            case 1:
                return self.build_level(n)