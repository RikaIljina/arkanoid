import random
import pygame as pg
from pygame.surface import Surface
from .gameEnums import GameState as GS


class Animator(object):
    def __init__(self, global_vars, screen, bg_image, bottom_surf, top_surf) -> None:
        self.screen = screen
        self.bg = bg_image
        self.bottom_surf = bottom_surf
        self.top_surf = top_surf
        self.timers = {}
        self.counters = {}

    #def pass_data(self, global_vars):
        self.global_vars = global_vars
        self.cfg = global_vars["cfg"]
        self.process_anims = {
            GS.game_loop_running: self.ingame_anims,
            GS.in_menu: self.menu_anims,
        }

    def ingame_anims(self, ticks):
        for key, item in self.global_vars["active_anims"].items():
            match key:
                case "brick_glare":
                    self.animate_glare(ticks, item)
                case "brick_shatter":
                    if item:
                        # self.animate_shatter(ticks, item)
                        pass
    
    def menu_anims(self, ticks):
        pass

    # def ingame_animations(self):
    #     self.animated_brick = self.global_vars["bricks"].sprites()[0]

    def animate(self, ticks):
        # use this to get the correct anim collection
        anim_func = self.process_anims.get(self.global_vars['game_state'])
        if anim_func:
            anim_func(ticks)
        

    def animate_glare(self, ticks, anim):
        if ticks % anim["freq"] < anim["length"]:
            self.bottom_surf.blit(
                self.bg, self.animated_brick.rect, self.animated_brick.rect
            )
            if not self.animated_brick.killed:
                self.animated_brick.animate(self.bottom_surf, ticks % anim["freq"])
                self.global_vars["redraw_bottom"] = True
                # self.screen.blit(self.bottom_surf, (0, 0))
        elif ticks % anim["freq"] == anim["length"]:
            if len(self.global_vars["bricks"].sprites()):
                self.animated_brick = random.choice(
                    self.global_vars["bricks"].sprites()
                )

    def animate_shatter(self, ticks, items):
        if not self.timers.get("shatter"):
            self.timers["shatter"] = ticks
            self.counters["shatter"] = 0
            self.shatter_surf = Surface([100, 70])
            self.shatter_surf.fill((*self.cfg["BLACK"], 0))
            self.shatter_surf.set_colorkey(self.cfg["BLACK"])

        if (ticks - self.timers["shatter"]) % 2 == 0:
            # i = (ticks - self.timers["shatter"]) % 100
            print("shattering")
            self.counters["shatter"] += 1
            for rect in items[:1]:
                self.shatter_surf.fill((*self.cfg["BLACK"], 0))
                self.shatter_surf.set_colorkey(self.cfg["BLACK"])

                rect_new = [
                    rect[0] + 20 + self.counters["shatter"] * 2,
                    rect[1] + 10 + self.counters["shatter"] * 2,
                    50 - self.counters["shatter"],
                    50 - self.counters["shatter"],
                ]

                # Draw animation frame here!
                pg.draw.rect(
                    self.shatter_surf,
                    (155, 232, 229),
                    [
                        50,
                        35 + self.counters["shatter"] * 1.5,
                        25 - self.counters["shatter"],
                        25 - self.counters["shatter"],
                    ],
                )

                # self.top_surf.blit(self.bg, rect_new, rect_new)
                self.global_vars["redraw_top"] = [
                    self.shatter_surf,
                    [rect[0] - 10, rect[1], 100, 70],
                ]  # plus surface size!!

        elif self.counters["shatter"] > 10:
            print("anim finished")
            self.global_vars["active_anims"]["brick_shatter"] = []
            # print(self.global_vars["active_anims"])
            del self.timers["shatter"]
            self.counters["shatter"] = 0
            self.global_vars["redraw_top"] = None
