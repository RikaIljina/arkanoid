import pygame as pg
from PIL import Image
import sys
from pygame import Surface
import os

from game.game import GameManager
from game.gameEnums import GameState as GS
from config import config as CFG

# #KILL = pg.event.Event(pg.USEREVENT, {"KILL": []})

# Create Player class

os.chdir(os.path.join(os.getcwd(), 'arkanoid'))

def main():
    # Initialize the pygame instance
    pg.mixer.pre_init(44100, -16, 4, 512)
    pg.mixer.init()
    pg.font.init()
    pg.init()
    # Initialize the clock
    clock = pg.time.Clock()
    # Initialize the player
    size = [CFG['SCREEN_WIDTH'], CFG['SCREEN_HEIGHT']]

    # Initialize the screen
    screen = pg.display.set_mode(size)
    bg_image = Image.open(CFG['BG_IMG'])

    bg_image = bg_image.resize(size)
    #frame = PIL.Image.open(os.path.join(assets, 'frame.png')
    #frame_mask = PIL.Image.open(os.path.join(assets, 'frame_mask.png')    

    print(bg_image.size)
    mode = bg_image.mode
    size = bg_image.size
    bg_image = bg_image.tobytes()
    bg_image = pg.image.frombytes(bg_image, size, mode)
   
    frame_surf = Surface(size)
    
    frame_surf.blit(bg_image, (0,0))
    frame = pg.image.load(CFG['FRAME_IMG']).convert_alpha()
    
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
    bottom_surf.blit(frame, (0, 0))

#    bottom_surf.fill(BG_COLOR)

    top_surf = Surface(size).convert_alpha()
    top_surf.fill((0, 0, 0, 0))
    top_surf.set_colorkey(CFG['BLACK'])
    
    screen_data = (screen, frame_surf, bottom_surf, top_surf)
    #animator = Animator(*screen_data)
    game = GameManager(CFG, *screen_data)

    # moving = False
    # counter for animations - maybe use time module instead?
    count = 0

    run = True
    while run:

        run = game.process_event()
        #print(pg.mixer.get_init())

        if count == 10000:
            count = 0
        game.run_logic(count)
        #animator.animate(count)
        count += 1

        game.draw_screen()

        clock.tick(60)

    pg.display.quit()
    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
