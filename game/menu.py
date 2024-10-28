from pygame.surface import Surface
import pygame as pg
import pygame_menu
import pygame_menu.events
import pygame_menu.themes
from pygame.sprite import Group, Sprite

from .gameEnums import GameState as GS


class Menu(object):
    def __init__(self, global_vars, game) -> None:
        self.game = game
        self.global_vars = global_vars
        self.cfg = global_vars["cfg"]
        self.my_font = pg.font.SysFont("Courier New", 100)
        self.button_font = pg.font.SysFont("Courier New", 24)
        self.buttons = Group()

    def build_menu(self):
        full_size = [self.cfg["SCREEN_WIDTH"], self.cfg["SCREEN_HEIGHT"]]
        self.bg = Surface(full_size)
        self.bg.fill(self.cfg["BG_COLOR"])
        self.menu_bg_surf = Surface(full_size)
        self.menu_bg_surf.fill(self.cfg["BG_COLOR"])
        text_surface = self.my_font.render("ARKANOID", True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        self.menu_bg_surf.blit(
            text_surface, (full_size[0] // 2 - text_rect.centerx, 100)
        )
        # self.menu = pygame_menu.Menu('', 400, 400, theme=pygame_menu.themes.THEME_GREEN)
        # self.menu.add.button('Play', self.play)
        # self.menu.add.button('Quit', pygame_menu.events.EXIT)
        # self.menu.mainloop(self.game.screen)
        self.buttons.add(
            [
                Button("PLAY", self.global_vars, *(200, 300)),
                Button("QUIT", self.global_vars, *(200, 400)),
            ]
        )
        # self.menu_bg_surf.blit(self.create_button('PLAY'), (200,300))
        # self.menu_bg_surf.blit(self.create_button('QUIT'), (200,500))
        print(self.buttons)
        self.buttons.sprites()[0].set_active()
        self.buttons.draw(self.menu_bg_surf)

        return self.menu_bg_surf

    def update(self):
        for button in self.buttons.sprites():
            button.check_hover()
        self.buttons.clear(self.menu_bg_surf, self.bg)
        self.buttons.draw(self.menu_bg_surf)
        return self.menu_bg_surf

    def play(self):
        # self.menu.close()
        self.game.game_state = GS.preparing_level
        print("trying to play")

    # self.menu.disable()

    # self.game.build_level()

    # def create_button(self, text_):
    #     button = Surface([200, 70])
    #     button.fill([*self.cfg['BLACK'], 100])
    #     button.set_colorkey(self.cfg['BLACK'])
    #     button_rect = button.get_rect()
    #     pg.draw.rect(button, self.cfg['GREEN'], button_rect, 6, 5)
    #     text = self.button_font.render(text_, True, (190, 100, 190))
    #     text_rect = text.get_rect()
    #     print(button_rect.size[0], button_rect.size[1])
    #     button.blit(text, (button_rect.size[0] // 2 - text_rect.centerx, button_rect.size[1] // 2 - text_rect.centery))
    #     self.buttons.add(button)
    #     return button


class Button(Sprite):
    def __init__(self, text_, global_vars, x, y) -> None:
        super().__init__()
        self.text = text_
        self.x = x
        self.y = y
        self.global_vars = global_vars
        self.cfg = global_vars["cfg"]
        self.active = False
        self.hovering = False

        self.image = Surface(self.cfg["BRICK_SIZE"]).convert_alpha()
        self.image.fill((*self.cfg["BLACK"], 0))
        self.button_font = pg.font.SysFont("Courier New", 24)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.mask = pg.mask.from_surface(self.image)
        
        self.hover_blend = Surface(self.rect.size).convert_alpha()
        self.hover_blend.fill((170, 170, 220))
        self.hover_blend.set_alpha(200)
        self.make_button()

    def set_active(self):
        self.active = True
        pg.draw.rect(
            self.image,
            self.cfg["GREEN"],
            ((0, 0), self.rect.size),
            width=3,
            border_radius=5,
        )

    def check_hover(self):
        mouse = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse) and not self.hovering:
            self.hovering = True
            self.image.blit(self.hover_blend, (0,0))
            if self.active:
                self.set_active()
        elif not self.rect.collidepoint(mouse) and self.hovering:
            self.hovering = False
            self.image.fill((*self.cfg["BLACK"], 0))
            self.image.blit(self.bs, (0, 0))
            if self.active:
                self.set_active()

            
            #self.make_button(True)

    def make_button(self):
        brick = pg.image.load(self.cfg["BRICK_IMG"]).convert_alpha()
        self.bs = Surface(self.cfg["BRICK_SIZE"]).convert_alpha()
        self.bs.fill((*self.cfg["BLACK"], 0))
        self.bs.blit(brick, (0, 0))
        
        text = self.button_font.render(self.text, True, (190, 100, 190)).convert_alpha()
        text_rect = text.get_rect()
        print(self.rect.size[0], self.rect.size[1])
        self.bs.blit(
            text,
            (
                self.rect.size[0] // 2 - text_rect.centerx,
                self.rect.size[1] // 2 - text_rect.centery,
            ),
        )
        self.image.blit(self.bs, (0, 0))
        self.image.set_colorkey(self.cfg["BLACK"])

