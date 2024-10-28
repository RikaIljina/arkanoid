import pygame as pg
import math

from pygame.sprite import Sprite
from pygame import Surface


# Create Brick class
class Brick(Sprite):
    def __init__(self, x, y, global_vars) -> None:
        super().__init__()
        self.global_vars = global_vars
        self.cfg = global_vars["cfg"]
        self.image = Surface(self.cfg["BRICK_SIZE"]).convert_alpha()
        self.image.fill((*self.cfg["BLACK"], 0))

        self.mask = pg.mask.from_surface(self.image)
        # self.image.fill(BG_COLOR)
        # pg.draw.rect(self.image, color, ((0, 0), BRICK_SIZE), border_radius=5)
        # draw_gradient(*BRICK_SIZE, 3, self.image, BRICK_GRAD)
        # pg.draw.rect(self.image, BORDER_COLOR, ((0, 0), BRICK_SIZE), 3, 3)
        brick = pg.image.load(self.cfg["BRICK_IMG"]).convert_alpha()
        bs = Surface(self.cfg["BRICK_SIZE"]).convert_alpha()
        bs.fill((*self.cfg["BLACK"], 0))
        bs.blit(brick, (0, 0))

        self.image.blit(bs, (0, 0))
        self.image.set_colorkey(self.cfg["BLACK"])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hyp = math.sqrt(
            abs(self.cfg["BRICK_SIZE"][0] / 2) ** 2
            + abs(self.cfg["BRICK_SIZE"][1] / 2) ** 2
        )
        self.x_y_divide = math.degrees(
            math.asin((self.cfg["BRICK_SIZE"][0] / 2) / self.hyp)
        )
        self.killed = False
        self.anim = [
            pg.image.load(self.cfg["BRICK_ANIMS"][i]).convert_alpha()
            for i in range(0, len(self.cfg["BRICK_ANIMS"]))
        ]
        self.anim.append(brick)

        if not self.global_vars["active_anims"]["brick_glare"].get("first_brick"):
            self.global_vars["active_anims"]["brick_glare"].update(
                {"length": len(self.anim), "freq": 100}
            )
            self.global_vars["active_anims"]["brick_glare"].update(
                {"first_brick": self}
            )

    def animate(self, surf, i):
        # brick_list = Group()
        # self.image.blit(pg.image.load(os.path.join(assets, 'brick_anim_1.png'), (0,0))
        self.image.fill((*self.cfg["BLACK"], 0))
        self.image.set_colorkey(self.cfg["BLACK"])
        self.image.blit((self.anim[int(i)]), (0, 0))
        surf.blit(self.image, self.rect)

    #        surf.blit(self.image, self.rect)

    def erase(self):
        if not self.killed:
            self.killed = True
            self.global_vars["kill_list"].add(tuple(self.rect))

            if self.global_vars["active_anims"].get("brick_shatter"):
                self.global_vars["active_anims"]["brick_shatter"].append(self.rect)
            else:
                self.global_vars["active_anims"].update({"brick_shatter": [self.rect]})

            self.kill()


# Create Wall class
class Wall(Sprite):
    def __init__(self, name, global_vars) -> None:
        super().__init__()
        self.global_vars = global_vars
        self.cfg = global_vars["cfg"]
        self.name = name
        # self.image = Surface(size)
        #        self.mask = pg.mask.Mask((size[0]+6, size[1]+6)) #pg.mask.from_surface(self.image)
        self.thickness = self.cfg["WALL_THICKNESS"]
        self.scr_height = self.cfg["SCREEN_HEIGHT"]
        self.scr_width = self.cfg["SCREEN_WIDTH"]
        self.collision_margin = global_vars["paddle_speed"] + 4
        # self.rect.x = pos[0]
        # self.rect.y = pos[1]
        self.build()

    def build(self):
        match self.name:
            case "left":
                size = (self.thickness + self.collision_margin + 10, self.scr_height)
                pos = (0, self.thickness + self.collision_margin)
            case "right":
                size = (self.thickness + self.collision_margin + 10, self.scr_height)
                pos = (
                    self.scr_width - self.thickness - self.collision_margin - 10,
                    self.thickness + self.collision_margin,
                )
            case "top":
                size = (self.scr_width, self.thickness + self.collision_margin + 10)
                pos = (0, 0)
            case "bottom":
                size = (self.scr_width, self.thickness + self.collision_margin + 50)
                pos = (
                    0,
                    self.cfg["SCREEN_HEIGHT"]
                    - self.cfg["PADDLE_OFFSET"]
                    - size[1] // 2,
                )

        self.image = Surface(size)
        #    if self.name == "bottom":
        #self.image.fill((50,50,50))
        self.rect = self.image.get_rect()
        self.mask = pg.mask.Mask(size)
        # (size[0] + self.collision_margin, size[1] + self.collision_margin)

        self.mask.fill()
        # print(self.mask.get_rect())
        self.rect.x = pos[0]
        self.rect.y = pos[1]
