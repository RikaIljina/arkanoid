import PIL.Image
import PIL.ImageChops
import pygame as pg
#import pygame.gfxdraw as gfx
import PIL
#import numpy as np
#import math
import sys
#import random
import os
import tomllib
from config import config as CFG
#from pygame.sprite import Group, Sprite
from pygame import Surface

os.chdir(os.path.join(os.getcwd(), 'arkanoid'))

#from sprites.movingSprites import Paddle, Ball
#from sprites.staticSprites import Wall, Brick
from game.game import GameManager
from game.gsenum import GameState as GS

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
#KILL = pg.event.Event(pg.USEREVENT, {"KILL": []})

LEVEL_1 = iter([
    (x, y)
    for x in range(100, SCREEN_WIDTH - 100, BRICK_SIZE[0])
    for y in range(100, SCREEN_HEIGHT // 2, BRICK_SIZE[1])
])


# Create Player class


def main():
    # Initialize the pygame instance
   # with open('config.toml', 'rb') as f:
   #     config = tomllib.load(f)
    print(CFG['SCREEN_WIDTH'])
    pg.init()
    # Initialize the clock
    clock = pg.time.Clock()
    # Initialize the player
    size = [CFG['SCREEN_WIDTH'], CFG['SCREEN_HEIGHT']]

    # Initialize the screen
    screen = pg.display.set_mode(size)
    bg_image = PIL.Image.open(os.path.join(assets, 'mama_mars.jpg'))
    #print(bg_image.size)
    
    bg_image = bg_image.resize(size)
    #frame = PIL.Image.open(os.path.join(assets, 'frame.png')
    #frame_mask = PIL.Image.open(os.path.join(assets, 'frame_mask.png')    

    print(bg_image.size)
    mode = bg_image.mode
    size = bg_image.size
    bg_image = bg_image.tobytes()
    bg_image = pg.image.frombytes(bg_image, size, mode) # load(os.path.join(assets, bg_image).convert()
    frame_surf = Surface(size)
    
    frame_surf.blit(bg_image, (0,0))
    frame = pg.image.load(os.path.join(assets, 'frame.png')).convert_alpha()
    
    frame_surf.blit(frame, (0,0))
    frame_surf.set_colorkey(CFG['BLACK'])
    
    
    bottom_surf = Surface(size)
   # draw_gradient(*size, 0, bg_surf, BG_COLOR_GRAD)
    bottom_surf.blit(bg_image, (0, 0))
   # frame = pg.image.load(os.path.join(assets, 'frame.png').convert_alpha()
    bottom_surf.blit(frame, (0, 0))
    
    bottom_surf.set_colorkey(CFG['BLACK'])
    
    screen.blit(bottom_surf, (0,0))
    pg.display.flip()
   # bottom_surf.blit(frame, (0, 0))
    
    #bottom_surf.fill(BG_COLOR)

    top_surf = Surface(size).convert_alpha()
    top_surf.fill((0, 0, 0, 0))
    top_surf.set_colorkey(CFG['BLACK'])
    
    game = GameManager(CFG, screen, frame_surf, bottom_surf, LEVEL_1)

    # moving = False
    # counter for animations - maybe use time module instead?
    count = 0
    
    run = True
    while run:
        
        run = game.process_event()

        if game.game_state == GS.game_loop_running:
            if count == 10000:
                count = 0
            game.run_logic(count)
            count += 1

        game.draw_screen(screen, bottom_surf, top_surf)

        clock.tick(60)

    pg.display.quit()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
