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


# Create Paddle class
class Paddle(Sprite):
    def __init__(self, walls, global_vars):
        super().__init__()
        self.image = Surface(PADDLE_SIZE)
        self.mask = pg.mask.from_surface(self.image)
        # self.image.fill(color)
        # pg.draw.rect(self.image, color, ((0, 0), PADDLE_SIZE), 0, 5)
        # pg.draw.rect(self.image, BG_COLOR, ((0, 0), PADDLE_SIZE), 2, 5)
        self.image.blit(
            pg.image.load(os.path.join(assets, "paddle.png")).convert_alpha(), (0, 0)
        )
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.direction = 0
        self.starting_pos_x = (SCREEN_WIDTH // 2) - (PADDLE_SIZE[0] // 2)
        self.starting_pos_y = SCREEN_HEIGHT - 50
        self.rect.x = self.starting_pos_x
        self.rect.y = self.starting_pos_y
        self.global_vars = global_vars
        self.walls = walls
        self.speed = global_vars["paddle_speed"]

    def update(self):
        wall_collision = pg.sprite.spritecollide(self, self.walls, False)
        if wall_collision:
            allowed_direction = self.get_allowed_direction(wall_collision[0].name)
            if self.direction == allowed_direction:
                self.rect.x += self.direction * self.speed
        else:
            self.rect.x += self.direction * self.speed

    def get_allowed_direction(self, wall):
        # Check if the paddle position is beyond the game area limits,
        # return the allowed direction
        if wall == "left":
            return 1
        if wall == "right":
            return -1

    def get_direction(self):
        return self.direction

    def set_direction(self, dir):
        self.direction = dir


# Create Ball class
class Ball(Sprite):
    def __init__(self, color, paddle, walls, global_vars) -> None:
        super().__init__()
        self.image = Surface([BALL_RADIUS * 2, BALL_RADIUS * 2]).convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.image.fill((*BLACK, 0))
        # pg.draw.circle(self.image, color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS - 2)
        self.image.blit(
            pg.image.load(os.path.join(assets, "ball_purple.png")).convert_alpha(),
            (0, 0),
        )
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.paddle = paddle
        self.stick_to_paddle()
        self.walls = walls
        self.speed = global_vars["game_speed"] * 6
        self.bricks = global_vars["bricks"]
        self.global_vars = global_vars
        self.start_angle = 15
        self.current_angle = self.start_angle
        self.trajectory = self.get_trajectory(self.start_angle)  # (0, 0)
        self.direction = (1, -1)
        self.launched = False
        self.speed_angles = {
            0: self.speed,
            5: self.speed,
            15: self.speed,
            25: self.speed + 1,
            35: self.speed + 1,
            45: self.speed + 2,
            55: self.speed + 2,
            65: self.speed + 3,
            75: self.speed + 3,
        }

    def stick_to_paddle(self):
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.y = self.paddle.rect.y - BALL_RADIUS * 2

    def update(self):
        if self.launched == False:
            self.stick_to_paddle()
            return
            # self.launched = True
            #        if self.within_limits(self.speed) == self.direction:
            # Starting trajectory at angle 5
            # self.trajectory = self.get_trajectory(self.start_angle)

        # Check for collision with anything
        hit_wall = pg.sprite.spritecollide(self, self.walls, False)
        hit_paddle = pg.sprite.collide_mask(self.paddle, self)
        hit_brick = pg.sprite.spritecollide(self, self.global_vars["bricks"], False)

        if hit_brick:
            self.direction = self.process_brick_hit(hit_brick)
        elif hit_paddle:
            # print(hit_paddle)
            self.direction = self.process_paddle_hit(hit_paddle[0])
        # Enable later when floor is fall-through
        elif hit_wall:
            self.direction = self.process_wall_hit(hit_wall[0].name)
        self.direction = self.process_wall_hit(None)
        self.rect.x += self.speed * self.trajectory[0] * self.direction[0]
        self.rect.y += self.speed * self.trajectory[1] * self.direction[1]

    def process_paddle_hit(self, hit_x):
        # print(pg.sprite.collide_mask(paddle, self))
        # Change angle tilt depending on paddle side (-1 or 1)
        # Check against paddle size!!!
        hits = {
            "hit_left": hit_x < 20,
            "hit_right": hit_x > 80,
            "from_left": self.direction[0] == 1,
            "from_right": self.direction[0] == -1,
            "paddle_same": self.paddle.get_direction() == self.direction[0],
            "paddle_diff": self.paddle.get_direction() != self.direction[0],
        }
        angle_tilt = self.current_angle if 20 < hit_x < 80 else 45
        if self.paddle.get_direction():
            if hits["paddle_same"] and not (hits["hit_left"] or hits["hit_right"]):
                self.current_angle = min(angle_tilt + 10, 75)
                # print(self.current_angle)
                # self.speed += 0.5
                if self.current_angle in self.speed_angles.keys():
                    self.speed = self.speed_angles[self.current_angle]
                self.trajectory = self.get_trajectory(self.current_angle)
            elif hits["paddle_diff"] and not (hits["hit_left"] or hits["hit_right"]):
                self.current_angle = angle_tilt - 10
                # print(self.current_angle)
                # self.speed = max(3, self.speed - 0.5)
                if abs(self.current_angle) in self.speed_angles.keys():
                    self.speed = self.speed_angles[abs(self.current_angle)]
                self.trajectory = self.get_trajectory(abs(self.current_angle))
                if self.current_angle < 0:
                    self.current_angle = abs(self.current_angle)
                    return (-1 * self.direction[0], -1)
            elif (
                (hits["hit_left"] and hits["from_left"])
                or (hits["hit_right"] and hits["from_right"])
            ) and hits["paddle_same"]:
                self.current_angle -= angle_tilt + 10
                self.trajectory = self.get_trajectory(abs(self.current_angle))
            elif (
                (hits["hit_left"] and hits["from_left"])
                or (hits["hit_right"] and hits["from_right"])
            ) and hits["paddle_diff"]:
                self.current_angle -= angle_tilt - 10
                self.trajectory = self.get_trajectory(abs(self.current_angle))
            elif (
                (hits["hit_left"] and hits["from_right"])
                or (hits["hit_right"] and hits["from_left"])
            ) and hits["paddle_same"]:
                self.current_angle = angle_tilt + 10
                self.trajectory = self.get_trajectory(self.current_angle)
            elif (
                (hits["hit_left"] and hits["from_right"])
                or (hits["hit_right"] and hits["from_left"])
            ) and hits["paddle_diff"]:
                self.current_angle = angle_tilt - 10
                self.trajectory = self.get_trajectory(self.current_angle)
            
            if self.current_angle < 0:
                    self.current_angle = abs(self.current_angle)
                    return (-1 * self.direction[0], -1)

        else:
            if angle_tilt == 45:
                print("45, current:", self.current_angle)
                if hit_x < 20 and self.direction == (-1, 1):
                    print("coming from the right")
                    self.trajectory = self.get_trajectory(angle_tilt)
                elif hit_x < 20 and self.direction == (1, 1):
                    print("coming from the left")
                    self.current_angle -= angle_tilt
                    self.trajectory = self.get_trajectory(abs(self.current_angle))
                elif hit_x > 80 and self.direction == (1, 1):
                    print("coming from the left")
                    self.trajectory = self.get_trajectory(angle_tilt)
                elif hit_x > 80 and self.direction == (-1, 1):
                    print("coming from the right")
                    self.current_angle -= angle_tilt
                    self.trajectory = self.get_trajectory(abs(self.current_angle))
                print(self.current_angle)
                print(self.direction)
                if self.current_angle < 0:
                    self.current_angle = abs(self.current_angle)
                    print("abs:", (-1 * self.direction[0]))
                    return (-1 * self.direction[0], -1)

                # self.trajectory = self.get_trajectory(angle_tilt)

        return (self.direction[0], -1)

    def process_wall_hit(self, wall):
        if wall == "left":
            # print(self.rect.x, self.rect.y)
            return (1, self.direction[1])
        elif wall == "right":
            # print(self.rect.x, self.rect.y)
            return (-1, self.direction[1])
        elif wall == "top":
            # print(self.rect.x, self.rect.y)
            return (self.direction[0], 1)
        # Don't let ball fall out of screen for now
        elif self.rect.bottom + self.speed >= SCREEN_HEIGHT:
            return (self.direction[0], -1)
        else:
            return (self.direction[0], self.direction[1])

    def process_brick_hit(self, bricks):
        for brick in bricks:
            # Check if brick always persists after loop end!!
            brick.erase()
        opp_side = brick.rect.centerx - self.rect.centerx
        adj_side = brick.rect.centery - self.rect.centery
        hyp = math.sqrt(abs(opp_side) ** 2 + abs(adj_side) ** 2)
        hit_angle = abs(math.degrees(math.asin(opp_side / hyp)))
        x_y_divide = brick.x_y_divide

        if hit_angle < x_y_divide:
            #     print(self.speed)
            return (self.direction[0], -1 * self.direction[1])
        else:
            return (-1 * self.direction[0], self.direction[1])

    def get_trajectory(self, angle):
        x = math.sin(math.radians(angle))
        y = math.cos(math.radians(angle))
        return (x, y)

    def get_launched(self):
        return self.launched

    def launch(self):
        self.launched = True
