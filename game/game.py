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
import time

from pygame.sprite import Group, Sprite
from pygame import Surface

from sprites.movingSprites import Paddle, Ball
from sprites.staticSprites import Wall, Brick
from game.gsenum import GameState as GS

assets = "assets"


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
BG_COLOR_GRAD = [(255, 255, 255), (0, 0, 0)]

BALL_RADIUS = 10
WALL_THICKNESS = 20
# KILL = pg.event.Event(pg.USEREVENT, {"KILL": []})

# LEVEL_1 = iter([
#     (x, y)
#     for x in range(100, SCREEN_WIDTH - 100, BRICK_SIZE[0])
#     for y in range(100, SCREEN_HEIGHT // 2, BRICK_SIZE[1])
# ])


# Create Game Manager class
class GameManager(object):

    def __init__(
        self, CFG, screen, bg_image, bottom_surf, level
    ) -> None:
        self.game_state = GS.initializing
        self.cfg = CFG
        # Put all config data in here!!!
        self.shared_data = {
            "cfg": self.cfg,
            "score": 0,
            "game_speed": self.cfg['GAME_SPEED'],
            "paddle_speed": self.cfg['PADDLE_SPEED'],
            "ball_speed": self.cfg['BALL_SPEED'],
            "kill_list": set(),
            "bricks": [],
            "walls": [],
            "paddle": [],
            "paddle_reset_timer": False
        }
        # self.score = 0
        # self.game_loop = False
        # self.game_speed = speed
        # self.paddle_speed = 6  # *speed / speed
        # self.ball_launched = False
        self.screen = screen
        self.bg = bg_image
        self.bottom_surf = bottom_surf
        # self.kill_list = []
        self.game_state = GS.initialized
        # Run menu here
        # In menu: set game state to in_menu
        self.build_level(level)

    def build_level(self, level):
        self.walls = Group()
        wall_attr = (
            self.cfg["WALL_THICKNESS"],
            self.cfg["SCREEN_HEIGHT"],
            self.cfg["SCREEN_WIDTH"],
        )
        self.walls.add(
            Wall(*wall_attr, "left"),
            Wall(*wall_attr, "right"),
            Wall(*wall_attr, "top"),
        )
        self.shared_data['walls'] = self.walls
        self.bricks = Group()
        self.bricks.add(
            [Brick(coord[0], coord[1], self.shared_data) for coord in level]
        )
        self.shared_data["bricks"] = self.bricks
        self.paddle = Paddle(self.shared_data)
        self.shared_data['paddle'] = self.paddle
        
        # self.clear_paddle = Paddle(BG_COLOR, self.paddle_speed)
        self.ball = Ball(self.shared_data)
        # self.clear_ball = Ball(BG_COLOR, self.paddle.rect, self.game_speed)
        #  self.all_sprites = Group()
        #  self.all_sprites.add(self.walls, self.bricks, self.paddle, self.ball)
        self.static_sprites = Group()
        self.static_sprites.add(self.walls, self.bricks)

        self.moving_sprites = Group()
        # self.moving_sprites.add(self.clear_paddle, self.clear_ball)
        self.moving_sprites.add(self.paddle, self.ball)
        # First brick to animate
        self.animated_brick = self.bricks.sprites()[0]

        self.game_state = GS.level_built

    def process_event(self):
        run = True
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            # User event handling
            # elif event.type == pg.USEREVENT:
            #     # print("Processing kill")
            #     if "KILL" in event.dict:
            #         event.dict["KILL"] = self.kill_sprites(event.dict["KILL"])                
            if event.type == pg.KEYUP:
                if pg.key.name(event.key) == 'left' or pg.key.name(event.key) == 'right':
                    self.shared_data["paddle_reset_timer"] = True

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            run = False
        elif keys[pg.K_LEFT]:
            self.paddle.set_direction(-1)
        elif keys[pg.K_RIGHT]:
            self.paddle.set_direction(1)
        elif keys[pg.K_SPACE]:
            self.ball.launch()
        elif keys[pg.K_d]:
            # debug output
            print(self.bricks)
        else:
            self.paddle.set_direction(0)

        return run

    def run_logic(self, count):

        if self.paddle.get_direction():
            self.paddle.update()
            # Fix ball to paddle if not launched
            if not self.ball.get_launched():
                self.ball.update()
        else:
            pass
        if self.ball.get_launched():
            # self.ball.launched = True
            self.ball.update()

        # Run blink animation
        if count % 100 < 8:
            self.bottom_surf.blit(
                self.bg, self.animated_brick.rect, self.animated_brick.rect
            )
            if not self.animated_brick.killed:
                self.animated_brick.animate(self.bottom_surf, count % 100)
                self.screen.blit(self.bottom_surf, (0, 0))
        elif count % 100 == 8:
            if len(self.bricks.sprites()):
                self.animated_brick = random.choice(self.bricks.sprites())

    def draw_screen(self, screen, bottom_surf, top_surf):
        if self.game_state == GS.level_built:
            self.static_sprites.draw(self.bottom_surf)
            self.screen.blit(self.bottom_surf, (0, 0))
            self.game_state = GS.game_loop_running

        if self.game_state == GS.game_loop_running:
            self.moving_sprites.draw(top_surf)
            self.screen.blit(top_surf, (0, 0))

            pg.display.flip()
            pg.time.delay(self.shared_data["game_speed"])
            sprites = self.shared_data["kill_list"]
            if sprites:
                for sprite in sprites:
                    # sprite is rect here
                    self.bottom_surf.blit(self.bg, sprite, sprite)
                    self.screen.blit(self.bottom_surf, (0, 0))
                self.shared_data["kill_list"] = set()
                self.shared_data["bricks"] = self.bricks
            self.moving_sprites.clear(top_surf, self.bg)
