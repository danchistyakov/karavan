import pygame
import graphics
from states import Context


def start():
    pygame.init()
    graphics.init()

    context = Context()
    while context.is_running():
        graphics.handle_events()
        context.handle_events()
        graphics.display(context.state)

    pygame.quit()
