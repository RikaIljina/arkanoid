import pygame as pg

from pygame.sprite import Group
from pygame.surface import Surface

from .gameEnums import GameState as GS
from .level import Level
from .animator import Animator
from .menu import Menu


# Create Game Manager class
class GameManager(object):

    def __init__(self, CFG, screen, bg_image, bottom_surf, top_surf) -> None:
        self.game_state = GS.initializing
        self.cfg = CFG
        # Put all config data in here!!!
        self.shared_data = {
            "cfg": self.cfg,
            "game_state": self.game_state,
            "score": 0,
            "game_speed": self.cfg["GAME_SPEED"],
            "paddle_speed": self.cfg["PADDLE_SPEED"],
            "ball_speed": self.cfg["BALL_SPEED"],
            "kill_list": set(),
            "bricks": [],
            "walls": [],
            "paddle": [],
            "ball": [],
            "paddle_reset_timer": False,
            "redraw_bottom": False,
            "redraw_top": None,
            "active_anims": {
                "brick_glare": {},
            },
        }
        self.animator = Animator(
            self.shared_data, screen, bg_image, bottom_surf, top_surf
        )
        self.menu = Menu(self.shared_data, self)
        self.level = Level(self.shared_data)
        self.screen = screen
        self.bg = bg_image
        self.bottom_surf = bottom_surf
        self.top_surf = top_surf
        self.game_state = GS.initialized
        self.process_input = {
            GS.game_loop_running: self.ingame_keys,
            GS.in_menu: self.menu_keys,
        }
        self.process_draw = {
            GS.game_loop_running: self.draw_game,
            GS.in_menu: self.draw_menu,
            GS.level_built: self.draw_level,
        }
        self.process_state = {
            GS.preparing_level: self.build_level,
            #GS.level_drawn: 
        }
        # Run menu here
        self.show_menu()
        # In menu: set game state to in_menu
        #self.build_level()
        # self.animator.pass_data(self.shared_data)
        #print(pg.mixer.get_init())

    def show_menu(self):
        self.game_state = GS.in_menu
        self.menu_surf = self.menu.build_menu()
        print("In menu!")
        #self.menu.play()
        # on menu close:


    def build_level(self):
        if self.game_state == GS.preparing_level:
            self.level.get_level(1)

            self.static_sprites = Group()
            self.static_sprites.add(
                self.shared_data["walls"], self.shared_data["bricks"]
            )

            self.moving_sprites = Group()
            self.moving_sprites.add(
                self.shared_data["paddle"], self.shared_data["ball"]
            )
            # First brick to animate

            self.game_state = GS.level_built

    def ingame_keys(self, key):
        match key:
            case "left":
                self.shared_data["paddle"].set_direction(-1)
            case "right":
                self.shared_data["paddle"].set_direction(1)
            case "space":
                if not self.shared_data["ball"].get_launched():
                    self.shared_data["ball"].launch()
            case "idle":
                if self.shared_data["paddle"].get_direction():
                    self.shared_data["paddle"].set_direction(0)

    def menu_keys(self, key):
        pass

    def process_event(self):
        run = True
        key_binding_func = self.process_input.get(self.game_state)
        state_func = self.process_state.get(self.game_state)
        if state_func:
            state_func()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            # User event handling
            # elif event.type == pg.USEREVENT:
            #     # print("Processing kill")
            #     if "KILL" in event.dict:
            #         event.dict["KILL"] = self.kill_sprites(event.dict["KILL"])
            if event.type == pg.KEYUP:
                if (
                    pg.key.name(event.key) == "left"
                    or pg.key.name(event.key) == "right"
                ):
                    self.shared_data["paddle_reset_timer"] = True

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            run = False
        elif keys[pg.K_LEFT]:
            if key_binding_func:
                key_binding_func("left")
        #            self.shared_data["paddle"].set_direction(-1)
        elif keys[pg.K_RIGHT]:
            if key_binding_func:
                key_binding_func("right")
        elif keys[pg.K_SPACE]:
            if key_binding_func:
                key_binding_func("space")
        elif keys[pg.K_d]:
            # debug output
            print(self.shared_data["bricks"])
        else:
            if key_binding_func:
                key_binding_func("idle")

        return run

    def run_logic(self, count):
        if self.game_state == GS.in_menu:
            # check for mouse
            self.menu_surf = self.menu.update()
            

        if self.game_state == GS.game_loop_running:
            if self.shared_data["paddle"].get_direction():
                self.shared_data["paddle"].update()
                # Fix ball to paddle if not launched
                if not self.shared_data["ball"].get_launched():
                    # self.shared_data["paddle_reset_timer"] = True
                    self.shared_data["ball"].update()

            else:
                pass
            if self.shared_data["ball"].get_launched():
                # self.ball.launched = True
                self.shared_data["ball"].update()

            # Running blink animation in Animator
            self.animator.animate(count)

    def draw_screen(self):
        draw_func = self.process_draw.get(self.game_state)
        if draw_func:
            draw_func()

        # if self.game_state == GS.level_built:
        #     self.static_sprites.draw(self.bottom_surf)
        #     self.screen.blit(self.bottom_surf, (0, 0))
        #     self.game_state = GS.game_loop_running

        # if self.game_state == GS.game_loop_running:
        #     if self.shared_data["redraw_bottom"]:
        #         self.screen.blit(self.bottom_surf, (0, 0))
        #         self.shared_data["redraw_bottom"] = False
        #     if self.shared_data["redraw_top"]:
        #         shatter_surf, rect = self.shared_data["redraw_top"]
        #         self.top_surf.blit(shatter_surf, rect)

        #     self.moving_sprites.draw(self.top_surf)
        #     self.screen.blit(self.top_surf, (0, 0))

        #     pg.display.flip()
        #     pg.time.delay(self.shared_data["game_speed"])

        #     self.process_kill_list()

        #     self.moving_sprites.clear(self.top_surf, self.bg)
        #     if self.shared_data["redraw_top"]:
        #         # shatter_surf.fill((0,0,0,0))
        #         print(rect)
        #         self.top_surf.blit(self.bottom_surf, rect, rect)


    def draw_game(self):
        if self.shared_data["redraw_bottom"]:
            self.screen.blit(self.bottom_surf, (0, 0))
            self.shared_data["redraw_bottom"] = False
        if self.shared_data["redraw_top"]:
            shatter_surf, rect = self.shared_data["redraw_top"]
            self.top_surf.blit(shatter_surf, rect)

        self.moving_sprites.draw(self.top_surf)
        self.screen.blit(self.top_surf, (0, 0))

        pg.display.flip()
        pg.time.delay(self.shared_data["game_speed"])

        self.process_kill_list()

        self.moving_sprites.clear(self.top_surf, self.bg)
        if self.shared_data["redraw_top"]:
            # shatter_surf.fill((0,0,0,0))
            print(rect)
            self.top_surf.blit(self.bottom_surf, rect, rect)
            
    
    def draw_level(self):

       # bottom_surf = Surface(self.bg.size)
    # draw_gradient(*size, 0, bg_surf, BG_COLOR_GRAD)
       # bottom_surf.blit(self.bg, (0, 0))
    # frame = pg.image.load(os.path.join(assets, 'frame.png').convert_alpha()
        self.bottom_surf.blit(self.bg, (0, 0))
        
        self.bottom_surf.set_colorkey(self.cfg['BLACK'])

#        self.screen.blit(self.bottom_surf, (0,0))
        self.static_sprites.draw(self.bottom_surf)
        self.screen.blit(self.bottom_surf, (0, 0))
        self.game_state = GS.game_loop_running
    
    def draw_menu(self):
        self.screen.blit(self.bottom_surf, (0, 0))
        self.screen.blit(self.menu_surf, (0, 0))
        pg.display.flip()

        #self.build_level()
      #  print('loop end')
        

    def process_kill_list(self):
        sprites = self.shared_data["kill_list"]
        if sprites:
            for sprite in sprites:
                # animate sprite explosion
                # sprite is rect here
                # print(sprite)
                self.bottom_surf.blit(self.bg, sprite, sprite)
            self.shared_data["kill_list"] = set()
            self.shared_data["redraw_bottom"] = True
            # self.screen.blit(self.bottom_surf, (0, 0))
