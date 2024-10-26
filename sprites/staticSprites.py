import PIL.Image
import PIL.ImageChops
import pygame as pg
import pygame.gfxdraw as gfx
import PIL
import numpy as np
import math
import sys
import random
import os

from pygame.sprite import Group, Sprite
from pygame import Surface


assets = 'assets'


GREEN = (0, 255, 0)
BORDER_COLOR = (17, 71, 97)
BRICK_COLOR = (7, 102, 147)
BALL_COLOR = (15, 133, 29)
PADDLE_COLOR = (97, 13, 75)
BLUE = (0, 0, 255)
BG_COLOR = (248, 248, 231)
BLACK = (0, 0, 0)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
PADDLE_SIZE = [100, 20]
BRICK_SIZE = [80, 40]
BRICK_GRAD = [(110, 220, 180), (0, 90, 180)]
WALL_GRAD = [(110, 70, 90), (30, 0, 10)]
BG_COLOR_GRAD = [(255, 255, 255), (0,0,0)]

BALL_RADIUS = 10
WALL_THICKNESS = 20

KILL = pg.event.Event(pg.USEREVENT, {"KILL": []})


# Create Brick class
class Brick(Sprite):
    def __init__(self, x, y, global_vars) -> None:
        super().__init__()
        self.image = Surface(BRICK_SIZE).convert_alpha()
        self.image.fill((*BLACK, 0))
        
        self.mask = pg.mask.from_surface(self.image)
       # self.image.fill(BG_COLOR)
        #pg.draw.rect(self.image, color, ((0, 0), BRICK_SIZE), border_radius=5)
       # draw_gradient(*BRICK_SIZE, 3, self.image, BRICK_GRAD)
       # pg.draw.rect(self.image, BORDER_COLOR, ((0, 0), BRICK_SIZE), 3, 3)
        brick = pg.image.load(os.path.join(assets, 'brick.png')).convert_alpha()
        bs = Surface(BRICK_SIZE).convert_alpha()
        bs.fill((*BLACK, 0))
        bs.blit(brick, (0,0))
        
        self.image.blit(bs, (0,0))
        self.image.set_colorkey(BLACK)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.global_vars = global_vars
        self.hyp = math.sqrt(abs(BRICK_SIZE[0] / 2) ** 2 + abs(BRICK_SIZE[1] / 2) ** 2)
        self.x_y_divide = math.degrees(math.asin((BRICK_SIZE[0] / 2) / self.hyp))
        self.killed = False
        self.anim = [pg.image.load(os.path.join(assets, f'brick_anim_{i}.png')).convert_alpha() for i in range(1, 8)]
        self.anim.append(brick)
        # gradient_colors = [(255, 255, 255), (0,0,0)]
        # gradient_step = 10
        # color = tuple(int(gradient_colors[0][c] * (1 - gradient_step * i) + gradient_colors[1][c] * gradient_step * i) for c in range(3))

    def animate(self, surf, i):
        #brick_list = Group()
        #self.image.blit(pg.image.load(os.path.join(assets, 'brick_anim_1.png'), (0,0))
        self.image.fill((*BLACK, 0))
        self.image.set_colorkey(BLACK)
        self.image.blit((self.anim[int(i)]), (0,0))
        surf.blit(self.image, self.rect)
#        surf.blit(self.image, self.rect)

        
    def erase(self):
        if not self.killed:
            self.killed = True
            self.global_vars['kill_list'].add(tuple(self.rect))
            self.kill()
            #KILL.dict["KILL"].append(self)
            #pg.event.post(KILL)
            #            self.game.kill_list.append(self)
            #self.image.set_colorkey(BLACK)
           # self.image.fill(BG_COLOR)
           # self.image.set_colorkey(BG_COLOR)
            


# Create Wall class
class Wall(Sprite):
    def __init__(self, thickness, scr_height, scr_width, name) -> None:
        super().__init__()
        self.name = name
        #self.image = Surface(size)
#        self.mask = pg.mask.Mask((size[0]+6, size[1]+6)) #pg.mask.from_surface(self.image)
        self.thickness = thickness
        self.scr_height = scr_height
        self.scr_width = scr_width
        #self.rect.x = pos[0]
        #self.rect.y = pos[1]
        self.build()
        
    def build(self):
        match self.name:
            case 'left':
                size = (self.thickness, self.scr_height)
                pos = (0, self.thickness)
            case 'right':
                size = (self.thickness, self.scr_height)
                pos = (self.scr_width - self.thickness, self.thickness)
            case 'top':
                size = (self.scr_width, self.thickness)
                pos = (0, 0)

        self.image = Surface(size)
        self.rect = self.image.get_rect()
        self.mask = pg.mask.Mask((size[0] + 6, size[1] + 6))
        self.mask.fill()
        self.rect.x = pos[0]
        self.rect.y = pos[1]