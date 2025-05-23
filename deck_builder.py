import pygame
from pygame.locals import MOUSEBUTTONUP
from states import State, Button, Quit
from decks import generate_all_cards
from cards import CARD_SIZE
import random, math
from graphics import WINDOW_WIDTH, WINDOW_HEIGHT

POOL_SIZE = 40
START_DECK_SIZE = 30
CARD_SCALE = 0.7
SPACING_Y = int(CARD_SIZE * CARD_SCALE * 0.8)
COLS = 8

# Размеры кнопок
MAIN_BTN_WIDTH = 350
MAIN_BTN_HEIGHT = 100
CONFIRM_WIDTH = 250
CONFIRM_HEIGHT = 70
EXIT_BTN_WIDTH = 150
EXIT_BTN_HEIGHT = 50
MAIN_EXIT_BTN_SIZE = 150

class MainMenuState(State):
    def __init__(self):
        super().__init__()
        exit_img = pygame.image.load('assets/images/exit.png').convert_alpha()
        exit_img = pygame.transform.scale(exit_img, (EXIT_BTN_HEIGHT, EXIT_BTN_HEIGHT))
        exit_hover = exit_img.copy()
        exit_hover.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_ADD)
        self.exit_main_btn = Button(
            WINDOW_WIDTH - EXIT_BTN_HEIGHT - 100,
            60,
            EXIT_BTN_HEIGHT,
            EXIT_BTN_HEIGHT,
            text='',
            is_clickable=True,
            z_index=1000,
            original_image=exit_img,
            hovered_image=exit_hover
        )
        self.start_btn = Button(
            0, 0,
            MAIN_BTN_WIDTH,
            MAIN_BTN_HEIGHT,
            center_x=WINDOW_WIDTH//2,
            center_y=WINDOW_HEIGHT//2 - MAIN_BTN_HEIGHT,
            text='Начать игру',
            is_clickable=True,
            z_index=1000
        )
        self.build_btn = Button(
            0, 0,
            MAIN_BTN_WIDTH,
            MAIN_BTN_HEIGHT,
            center_x=WINDOW_WIDTH//2,
            center_y=WINDOW_HEIGHT//2 + MAIN_BTN_HEIGHT,
            text='Выбрать колоду',
            is_clickable=True,
            z_index=1000
        )
        self.objects['exit_main_btn'] = self.exit_main_btn
        self.objects['start_btn'] = self.start_btn
        self.objects['build_btn'] = self.build_btn

    def handle_events(self):
        for event in pygame.event.get(MOUSEBUTTONUP):
            x, y = event.pos
            if self.exit_main_btn.collides_with(x, y):
                return Quit()
            if self.start_btn.collides_with(x, y):
                from states import StandardMode
                return StandardMode()
            if self.build_btn.collides_with(x, y):
                from deck_builder import DeckBuildingState
                return DeckBuildingState()
        return self

    def is_running(self):
        return True

class DeckBuildingState(State):
    def __init__(self):
        super().__init__()
        self.pool = generate_all_cards()
        random.shuffle(self.pool)
        self.pool = self.pool[:POOL_SIZE]

        base_size = CARD_SIZE
        scaled_w = int(base_size * CARD_SCALE)
        scaled_h = int(base_size * CARD_SCALE)
        spacing_x = int(scaled_w * 1.2)
        spacing_y = SPACING_Y

        rows = math.ceil(len(self.pool) / COLS)
        grid_w = spacing_x * (COLS - 1) + scaled_w
        grid_h = spacing_y * (rows - 1) + scaled_h
        margin_x = (WINDOW_WIDTH - grid_w) // 2
        margin_y = (WINDOW_HEIGHT - grid_h) // 2 - 20

        for idx, card in enumerate(self.pool):
            col = idx % COLS
            row = idx // COLS
            cx = margin_x + col * spacing_x + scaled_w // 2
            cy = margin_y + row * spacing_y + scaled_h // 2
            card.set_at(cx, cy, 0)
            card.is_flipped = True
            card.z_index = 10
            card.image = pygame.transform.scale(card.image, (scaled_w, scaled_h))
            card.back_image = pygame.transform.scale(card.back_image, (scaled_w, scaled_h))
            card.rect = card.image.get_rect(center=(cx, cy))
            card.center = (cx, cy)
            self.objects[f'card_{idx}'] = card
            hl_surf = pygame.Surface((scaled_w, scaled_h), pygame.SRCALPHA)
            hl_surf.fill((0, 255, 0, 100))
            hl_btn = Button(
                card.rect.left,
                card.rect.top,
                scaled_w,
                scaled_h,
                text='',
                is_clickable=False,
                z_index=card.z_index - 1,
                original_image=hl_surf
            )
            hl_btn.is_visible = False
            self.objects[f'highlight_{idx}'] = hl_btn

        info_text = f"Выберите {START_DECK_SIZE} карт для колоды"
        info_w, info_h = grid_w, scaled_h // 2
        info_surf = pygame.Surface((info_w, info_h), pygame.SRCALPHA)
        info_surf.fill((0, 0, 0, 180))
        self.info = Button(
            0, 0, info_w, info_h,
            center_x=WINDOW_WIDTH//2,
            center_y=margin_y - info_h // 2 - 10,
            text=info_text,
            is_clickable=False,
            font_size=30,
            font_color=(255,255,255),
            z_index=1000,
            original_image=info_surf
        )
        self.objects['info'] = self.info

        self.confirm = Button(
            WINDOW_WIDTH - CONFIRM_WIDTH - 20,
            WINDOW_HEIGHT - CONFIRM_HEIGHT - 20,
            CONFIRM_WIDTH,
            CONFIRM_HEIGHT,
            text='Начать игру',
            is_clickable=True,
            z_index=1000
        )
        self.objects['confirm'] = self.confirm

        self.exit_btn = Button(
            20,
            WINDOW_HEIGHT - EXIT_BTN_HEIGHT - 20,
            EXIT_BTN_WIDTH,
            EXIT_BTN_HEIGHT,
            text='Выход',
            is_clickable=True,
            z_index=1000
        )
        self.objects['exit_btn'] = self.exit_btn

        self.selected = set()

    def handle_events(self):
        for event in pygame.event.get(MOUSEBUTTONUP):
            x, y = event.pos
            if self.exit_btn.collides_with(x, y):
                from deck_builder import MainMenuState
                return MainMenuState()
            # Выбор и подсветка карт
            for key, obj in list(self.objects.items()):
                if key.startswith('card_') and obj.collides_with(x, y):
                    idx = int(key.split('_')[1])
                    if idx in self.selected:
                        self.selected.remove(idx)
                        obj.is_selected = False
                    elif len(self.selected) < START_DECK_SIZE:
                        self.selected.add(idx)
                        obj.is_selected = True
                    self.info.text = f"Выбрано {len(self.selected)}/{START_DECK_SIZE}"
                    for i in range(len(self.pool)):
                        self.objects[f'highlight_{i}'].is_visible = (i in self.selected)
            if self.confirm.collides_with(x, y) and len(self.selected) == START_DECK_SIZE:
                from states import StandardMode
                chosen = [self.pool[i] for i in sorted(self.selected)]
                return StandardMode(starting_cards=chosen)
        return self

    def is_running(self):
        return True
