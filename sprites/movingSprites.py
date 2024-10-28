import pygame as pg
import math
import random
import time
from pygame.sprite import Sprite
from pygame import Surface
from pygame.mixer import Sound


# Create Paddle class
class Paddle(Sprite):
    def __init__(self, global_vars):
        super().__init__()
        self.global_vars = global_vars
        self.cfg = global_vars["cfg"]
        self.image = Surface([self.cfg["PADDLE_SIZE"][0], self.cfg["PADDLE_SIZE"][1]])
        self.mask = pg.mask.from_surface(self.image)
        self.image.blit(pg.image.load(self.cfg["PADDLE_IMG"]).convert_alpha(), (0, 0))
        self.image.set_colorkey(self.cfg["BLACK"])
        self.rect = self.image.get_rect()
        self.direction = 0
        self.starting_pos_x = (self.cfg["SCREEN_WIDTH"] // 2) - (
            self.cfg["PADDLE_SIZE"][0] // 2
        )
        self.starting_pos_y = self.cfg["SCREEN_HEIGHT"] - self.cfg["PADDLE_OFFSET"]
        self.rect.x = self.starting_pos_x
        self.rect.y = self.starting_pos_y
        self.timer = time.time()

    def update(self):
        wall_collision = pg.sprite.spritecollide(self, self.global_vars["walls"], False)
        if wall_collision and wall_collision[0].name != 'bottom':
            allowed_direction = self.get_allowed_direction(wall_collision[0].name)
            if self.direction == allowed_direction:
                self.rect.x += self.direction * self.global_vars["paddle_speed"]
        else:
            if (
                self.global_vars["paddle_reset_timer"]
                or not self.global_vars["ball"].launched
            ):
                self.timer = time.time()
                self.global_vars["paddle_reset_timer"] = False
            
            self.rect.x += (
                self.direction
                * self.global_vars["paddle_speed"]
                * (1 + time.time() - self.timer)
            )

    def get_allowed_direction(self, wall):
        # Check if the paddle position is beyond the game area limits,
        # return the allowed direction
        if (
            wall == "left"
            and self.rect.centerx - self.cfg["WALL_THICKNESS"]
            <= self.cfg["PADDLE_SIZE"][0] // 2
        ):
            return 1
        if (
            wall == "right"
            and self.cfg["SCREEN_WIDTH"]
            - self.rect.centerx
            - self.cfg["WALL_THICKNESS"]
            <= self.cfg["PADDLE_SIZE"][0] // 2
        ):
            return -1
        else:
            return self.direction

    def get_direction(self):
        return self.direction

    def set_direction(self, dir):
        self.direction = dir


# Create Ball class
class Ball(Sprite):
    def __init__(self, global_vars) -> None:
        super().__init__()
        self.global_vars = global_vars
        self.cfg = self.global_vars["cfg"]
        self.image = Surface(
            [self.cfg["BALL_RADIUS"] * 2, self.cfg["BALL_RADIUS"] * 2]
        ).convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.image.fill((*self.cfg["BLACK"], 0))
        # pg.draw.circle(self.image, color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS - 2)
        self.image.blit(
            pg.image.load(self.cfg["BALL_IMG"]).convert_alpha(),
            (0, 0),
        )
        self.image.set_colorkey(self.cfg["BLACK"])
        self.rect = self.image.get_rect()
        self.stick_to_paddle()
        # self.speed = global_vars["ball_speed"]
        # self.bricks = global_vars["bricks"]
        self.start_angle = random.randrange(5, 26, 10)
        self.current_angle = self.start_angle
        self.set_trajectory(self.start_angle)  # (0, 0)
        self.direction = (random.choice([1, -1]), -1)
        self.launched = False
        self.speed_angles = {
            0: self.cfg["BALL_SPEED"],
            5: self.cfg["BALL_SPEED"],
            15: self.cfg["BALL_SPEED"],
            25: self.cfg["BALL_SPEED"] + 1,
            35: self.cfg["BALL_SPEED"] + 1,
            45: self.cfg["BALL_SPEED"] + 2,
            55: self.cfg["BALL_SPEED"] + 2,
            65: self.cfg["BALL_SPEED"] + 3,
            75: self.cfg["BALL_SPEED"] + 3,
        }
        self.paddle_sound = Sound(self.cfg["PADDLE_BALL_HIT_SOUND"])
        self.paddle_sound.set_volume(0.5)
        self.shatter_sound = Sound(self.cfg["GLASS_SHATTER_SOUND"])
        self.launch_sound = Sound(self.cfg["PADDLE_BALL_RELEASE_SOUND"])
        self.sounds = {
            "paddle_hit": self.paddle_sound,
            "paddle_enabled": True,
            "wall_enabled": True,
        }

    def stick_to_paddle(self):
        p = self.get_global_paddle_surface()
        self.rect.centerx = p["centerx"]
        self.rect.bottom = p["y"]
        # (
        #     self.global_vars["paddle"].rect.bottom
        #     - self.cfg["PADDLE_SIZE"][1]
        #     - self.cfg["BALL_RADIUS"]
        # )

    def get_global_paddle_surface(self):
        # Returns the x, y of the paddle image surface without the bounding box
        y = self.global_vars["paddle"].rect.bottom - self.cfg["PADDLE_SIZE"][1]
        x = self.global_vars["paddle"].rect.centerx
        lx = self.global_vars["paddle"].rect.left
        rx = self.global_vars["paddle"].rect.right
        return {"centerx": x, "y": y, "leftx": lx, "rightx": rx}

    def update(self):
        if self.launched == False:
            self.stick_to_paddle()
            return
        # print(self.sounds["enabled"])
        # Check for collision with anything
        hit_wall = pg.sprite.spritecollide(self, self.global_vars["walls"], False)
        hit_paddle = pg.sprite.collide_mask(self.global_vars["paddle"], self)
        hit_brick = pg.sprite.spritecollide(self, self.global_vars["bricks"], False)

        if hit_brick:
            # if not pg.mixer.get_busy():
            self.shatter_sound.play()
            self.process_brick_hit(hit_brick)
        elif hit_paddle:
            # if not pg.mixer.get_busy():
            # self.paddle_sound.play()
            self.process_paddle_hit(*hit_paddle)
        # Enable later when floor is fall-through
        elif hit_wall:
            # if not pg.mixer.get_busy():
            # self.paddle_sound.play()
            self.process_wall_hit(hit_wall[0])
        self.process_wall_hit(None)
        self.rect.x += (
            self.global_vars["ball_speed"] * self.trajectory[0] * self.direction[0]
        )
        self.rect.y += (
            self.global_vars["ball_speed"] * self.trajectory[1] * self.direction[1]
        )

    def process_paddle_hit(self, hit_x, hit_y):

        hits = {
            "hit_left": hit_x < self.global_vars["paddle"].rect[2] * 0.2,
            "hit_right": hit_x > self.global_vars["paddle"].rect[2] * 0.8,
            "from_left": self.direction[0] == 1,
            "from_right": self.direction[0] == -1,
            "paddle_same": self.global_vars["paddle"].get_direction()
            == self.direction[0],
            "paddle_diff": self.global_vars["paddle"].get_direction()
            != self.direction[0],
        }

        edge_tilt = 45
        angle_tilt = 10
        if self.global_vars["paddle"].get_direction():
            if hits["paddle_same"] and not (hits["hit_left"] or hits["hit_right"]):
                self.current_angle = min(self.current_angle + angle_tilt, 75)

                self.set_trajectory(self.current_angle)

            elif hits["paddle_diff"] and not (hits["hit_left"] or hits["hit_right"]):
                self.current_angle = self.current_angle - angle_tilt

                self.set_trajectory(abs(self.current_angle))

            elif (
                (hits["hit_left"] and hits["from_left"])
                or (hits["hit_right"] and hits["from_right"])
            ) and hits["paddle_same"]:
                self.current_angle -= edge_tilt + angle_tilt
                self.set_trajectory(abs(self.current_angle))
            elif (
                (hits["hit_left"] and hits["from_left"])
                or (hits["hit_right"] and hits["from_right"])
            ) and hits["paddle_diff"]:
                self.current_angle -= edge_tilt - angle_tilt
                self.set_trajectory(abs(self.current_angle))
            elif (
                (hits["hit_left"] and hits["from_right"])
                or (hits["hit_right"] and hits["from_left"])
            ) and hits["paddle_same"]:
                self.current_angle = edge_tilt + angle_tilt
                self.set_trajectory(self.current_angle)
            elif (
                (hits["hit_left"] and hits["from_right"])
                or (hits["hit_right"] and hits["from_left"])
            ) and hits["paddle_diff"]:
                self.current_angle = edge_tilt - angle_tilt
                self.set_trajectory(self.current_angle)

            if abs(self.current_angle) in self.speed_angles.keys():
                self.global_vars["ball_speed"] = self.speed_angles[
                    abs(self.current_angle)
                ]
            if self.current_angle < 0:
                self.current_angle = abs(self.current_angle)
                self.direction = (-1 * self.direction[0], -1)
                return

        else:
            if edge_tilt == 45:
                if hit_x < 20 and self.direction == (-1, 1):
                    self.current_angle = edge_tilt
                    self.set_trajectory(edge_tilt)
                elif hit_x < 20 and self.direction == (1, 1):
                    self.current_angle -= edge_tilt
                    self.set_trajectory(abs(self.current_angle))
                elif hit_x > 80 and self.direction == (1, 1):
                    self.set_trajectory(edge_tilt)
                elif hit_x > 80 and self.direction == (-1, 1):
                    self.current_angle -= edge_tilt
                    self.set_trajectory(abs(self.current_angle))

                if abs(self.current_angle) in self.speed_angles.keys():
                    self.global_vars["ball_speed"] = self.speed_angles[
                        abs(self.current_angle)
                    ]
                if self.current_angle < 0:
                    self.current_angle = abs(self.current_angle)
                    self.direction = (-1 * self.direction[0], -1)
                    return

        self.direction = (self.direction[0], -1)

    def process_wall_hit(self, wall):
        if not wall:
            # Don't let ball fall out of screen for now
            if (
                self.rect.bottom + self.global_vars["ball_speed"]
                >= self.cfg["SCREEN_HEIGHT"]
            ):
                self.direction = (self.direction[0], -1)

            return
        if wall.name == "left":
            #print(wall.mask)
            # Motion sensor to play sound before ball hits wall
            # wall_dist_vector = wall_dist_horiz / math.sin(
            #     math.radians(self.current_angle)
            # )
            # print(wall_dist_vector)
            # self.rect.x += wall_dist_horiz * self.trajectory[0] * self.direction[0]
            wall_dist_horiz = self.rect.x - self.cfg["WALL_THICKNESS"]
            #  print("Ball hits in ... steps:")
            steps_to_hit = wall_dist_horiz / (
                self.trajectory[0] * self.global_vars["ball_speed"]
            )
            #     self.rect.centery
            #     - ( * self.trajectory[1] * self.direction[1])
            # )
            if (
                # self.rect.x < wall.mask.get_size()[0]
                steps_to_hit <= 2
                and self.direction[0] == -1
                # and not pg.mixer.get_busy()
                #and self.launched
                and self.sounds["wall_enabled"]
            ):
                #   print("Playing at:")
                #   print(self.rect.x)

                self.paddle_sound.play()
                self.sounds["wall_enabled"] = False
            #   print(wall.mask.get_size()[0])

            elif self.direction[0] == 1:  # self.rect.x > wall.mask.get_size()[0]:
                self.sounds["wall_enabled"] = True

            if steps_to_hit < 1 or self.rect.x < self.cfg["WALL_THICKNESS"]:
                #   print("Redirecting at:")
                #   print(self.rect.x)
                self.direction = (1, self.direction[1])
        elif wall.name == "right":
            # print(wall.mask.get_rect())
            wall_dist_horiz = (
                self.cfg["SCREEN_WIDTH"] - self.rect.right - self.cfg["WALL_THICKNESS"]
            )
            #  print("Ball hits in ... steps:")
            steps_to_hit = wall_dist_horiz / (
                self.trajectory[0] * self.global_vars["ball_speed"]
            )
            #   print(steps_to_hit)

            if (
                # self.rect.x < 965
                steps_to_hit <= 2
                and self.direction[0] == 1
                # and not pg.mixer.get_busy()
                #and self.launched
                and self.sounds["wall_enabled"]
            ):
                #   print("Playing at:")
                #   print(self.rect.x)

                self.paddle_sound.play()
                self.sounds["wall_enabled"] = False
            # else:
            elif self.direction[0] == -1:  # self.rect.x < wall.mask.get_rect()[0]:
                self.sounds["wall_enabled"] = True
            if steps_to_hit < 1 or self.rect.x > 965:
                #  print("Redirecting at:")
                #  print(self.rect.x)
                # print(self.rect.x, self.rect.y)
                self.direction = (-1, self.direction[1])
        elif wall.name == "top":
            wall_dist_horiz = self.rect.y - self.cfg["WALL_THICKNESS"]
            # print("Ball hits in ... steps:")
            steps_to_hit = wall_dist_horiz / (
                self.trajectory[1] * self.global_vars["ball_speed"]
            )
            # print(steps_to_hit)

            if (
                steps_to_hit <= 2  # self.rect.y > 18
                and self.direction[1] == -1
                # and not pg.mixer.get_busy()
                #and self.launched
                and self.sounds["wall_enabled"]
            ):
                # print("Playing at:")
                # print(self.rect.y)
                self.paddle_sound.play()
                self.sounds["wall_enabled"] = False

            elif self.direction[1] == 1:  # self.rect.y > wall.mask.get_size()[1]:
                self.sounds["wall_enabled"] = True

            if steps_to_hit < 1 or self.rect.y <= 18:
                #  print("Redirecting at:")
                #  print(self.rect.y)
                # print(self.rect.x, self.rect.y)
                self.direction = (self.direction[0], 1)

        elif wall.name == "bottom":
            p = self.get_global_paddle_surface()
            p_move = int(
                self.global_vars["paddle"].get_direction()
                * self.global_vars["paddle_speed"]
                )
            paddle_dist_vert = p["y"] - self.rect.bottom
            # print("Paddle distance:", paddle_dist_vert)
            steps_to_hit = paddle_dist_vert / (
                self.trajectory[1] * self.global_vars["ball_speed"]
            )
            if steps_to_hit < 2:
              #  print("Steps:", steps_to_hit)
              #  print("new x:")
                future_x = (
                    self.rect.centerx
                    + self.global_vars["ball_speed"]
                    * self.trajectory[0]
                    * self.direction[0]
                )
              #  print(future_x)
              #  print("paddle x:")
              #  print(p["leftx"], p["rightx"])
              #  print(self.sounds["paddle_enabled"])
              #  print(p_move)
              #  print(
              #      range(
              #          p["leftx"] - self.cfg["BALL_RADIUS"] + 1 - p_move,
              #          p["rightx"] + self.cfg["BALL_RADIUS"] + p_move,
              #      )
              #  )
                if (
                    int(future_x)
                    in range(
                        p["leftx"] - self.cfg["BALL_RADIUS"] + 1 - p_move,
                        p["rightx"] + self.cfg["BALL_RADIUS"] + p_move,
                    )
                    and self.direction[1] == 1
                    and self.sounds["paddle_enabled"]
                ):
                    self.paddle_sound.play()
                    self.sounds["paddle_enabled"] = False
                elif self.direction[1] == -1:
                    self.sounds["paddle_enabled"] = True

        else:
            self.direction = (self.direction[0], self.direction[1])

    def process_brick_hit(self, bricks):
        for brick in bricks:
            # Check if brick always persists after loop end!!
            brick.erase()
        opp_side = brick.rect.centerx - self.rect.centerx
        adj_side = brick.rect.centery - self.rect.centery
        hyp = math.sqrt(abs(opp_side) ** 2 + abs(adj_side) ** 2)
        hit_angle = abs(math.degrees(math.asin(opp_side / hyp)))
        x_y_divide = brick.x_y_divide
        #  print("Divide:")
        #  print(x_y_divide)
        if (
            hit_angle < x_y_divide - 5
        ):  # TODO: figure out how to get the ball to never bounce upwards on y-axis
            self.direction = (self.direction[0], -1 * self.direction[1])
        else:
            self.direction = (-1 * self.direction[0], self.direction[1])

    def set_trajectory(self, angle):
        x = math.sin(math.radians(angle))
        y = math.cos(math.radians(angle))
        self.trajectory = (x, y)

    def get_launched(self):
        return self.launched

    def launch(self):
        if not pg.mixer.get_busy():
            self.launch_sound.play()
        self.launched = True
