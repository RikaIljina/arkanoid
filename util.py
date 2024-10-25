




def draw_gradient(width, height, border, surf, colors):
    gradient_colors = colors  # colors used
    num_gradient_steps = height - border*2  # Number of steps in the gradient
    gradient_step = 1 / num_gradient_steps

    for i in range(num_gradient_steps):
        color = tuple(
            int(
                gradient_colors[0][c] * (1 - gradient_step * i)
                + gradient_colors[1][c] * gradient_step * i
            )
            for c in range(3)
        )
        #print(i)
       # my_rect = pg.Rect(0, i, width, 1)
        #new_surf = Surface([0, width])
        #surf.blit(new_surf, (0, 0))
        pg.draw.rect(surf, color, (border, i + border, width - border, 1))
    #    screen.blit(surf, (0, 0))
       # pg.display.flip()
       # print(color)
    return surf
