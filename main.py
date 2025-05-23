import pygame
import graphics
from states import Context
from deck_builder import MainMenuState

def main():
    pygame.init()
    graphics.init()

    context = Context(initial_state=MainMenuState())

    while context.is_running():
        graphics.handle_events()
        context.handle_events()
        graphics.display(context.state)

    pygame.quit()

if __name__ == '__main__':
    main()