import pygame

from states import WinState

# Display surface
display_surf = None

# Window constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
WINDOW_FLAGS = pygame.RESIZABLE | pygame.DOUBLEBUF | 0
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
# Colors
BG_COLOR = (255, 150, 0)
TEXT_COLOR = (0, 0, 0)

BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load('assets/images/background.png'), (WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pygame.time.Clock()
FPS = 80

def init():
    global display_surf
    display_surf = pygame.display.set_mode(
        size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        flags=WINDOW_FLAGS
    )
    pygame.display.set_caption('Caravan')

def handle_events():
    global WINDOW_WIDTH, WINDOW_HEIGHT, display_surf

    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            new_width = max(round(event.w, -2), 600)
            new_height = max(round(event.h, -2), 400)
            WINDOW_WIDTH, WINDOW_HEIGHT = new_width, new_height
            display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=WINDOW_FLAGS)
        else:
            pygame.event.post(event)
    return True

def display(state):
    global display_surf
    display_surf.blit(BACKGROUND_IMAGE, BACKGROUND_IMAGE.get_rect())

    font = pygame.font.Font('assets/font.ttf', size=26)

    for animation in state.animations[:]:
        objects = next(animation, {})
        if not objects:
            state.animations.remove(animation)
            continue
        for key, val in objects.items():
            state.objects[key] = val

    currently_hovered = None
    currently_selected = None
    for object in get_visible_objects(state.objects):
        if object.is_hovered:
            currently_hovered = object
        if object.is_selected:
            currently_selected = object

        display_surf.blit(object.get_image(), object.rect)

        text_surf = font.render(object.text, True, object.font_color).convert_alpha()
        rect = text_surf.get_rect()
        rect.center = object.rect.center
        display_surf.blit(text_surf, rect)

    if currently_hovered == currently_selected and currently_hovered:
        currently_hovered = None

    if currently_selected:
        selected_image, selected_image_rect, image, image_rect, text = currently_selected.get_clicked_params()
        display_surf.blit(selected_image, selected_image_rect)
        display_surf.blit(image, image_rect)

        text_surf = font.render(currently_selected.text, True, currently_selected.font_color).convert_alpha()
        rect = text_surf.get_rect()
        rect.center = image_rect.center
        display_surf.blit(text_surf, rect)
    if currently_hovered:
        hovered_image, hovered_image_rect, image, image_rect, text = currently_hovered.get_hovered_params()
        display_surf.blit(hovered_image, hovered_image_rect)
        display_surf.blit(image, image_rect)

        text_surf = font.render(currently_hovered.text, True, currently_hovered.font_color).convert_alpha()
        rect = text_surf.get_rect()
        rect.center = image_rect.center
        display_surf.blit(text_surf, rect)

    if isinstance(state, WinState):
        font = pygame.font.Font('assets/font.ttf', size=42)
        text = 'Вы выиграли!' if state.winner == 1 else 'Вы проиграли.'
        surf = font.render(text, True, TEXT_COLOR).convert_alpha()
        rect = surf.get_rect()
        rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        display_surf.blit(surf, rect)
        # затемняем фон
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(160)
        overlay.fill((0, 0, 0))
        display_surf.blit(overlay, (0, 0))
        # баннер
        rect = state.banner.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        display_surf.blit(state.banner, rect)

    pygame.display.update()
    clock.tick(FPS)

def get_visible_objects(objects):
    result = []
    for object in objects.values():
        result.extend(object.dump())
    result = [object for object in result if object.is_visible]
    return sorted(result, key=lambda x: x.z_index)