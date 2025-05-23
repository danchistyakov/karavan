import math

import pygame


RANK_A = 1
RANK_2 = 2
RANK_3 = 3
RANK_4 = 4
RANK_5 = 5
RANK_6 = 6
RANK_7 = 7
RANK_8 = 8
RANK_9 = 9
RANK_10 = 10
RANK_J = 11
RANK_Q = 12
RANK_K = 13
RANK_JOKER = 14

SUIT_SPADES = 1
SUIT_HEARTS = 2
SUIT_DIAMONDS = 3
SUIT_CLUBS = 4
SUIT_BLACK_JOKER = 5
SUIT_RED_JOKER = 6

RANKS = [RANK_A, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RANK_9, RANK_10, RANK_J, RANK_Q, RANK_K, RANK_JOKER]
RANK_NAMES = ['A', '02', '03', '04', '05', '06', '07', '08', '09', '10', 'J', 'Q', 'K', 'joker']

SUITS = [SUIT_SPADES, SUIT_HEARTS, SUIT_DIAMONDS, SUIT_CLUBS, SUIT_BLACK_JOKER, SUIT_RED_JOKER]
SUIT_NAMES = ['spades', 'hearts', 'diamonds', 'clubs', 'black', 'red']

CARD_SIZE = 128

card_images = {}
for rank, rank_name in zip(RANKS, RANK_NAMES):
    if rank == RANK_JOKER:
        card_images[(RANK_JOKER, SUIT_BLACK_JOKER)] = pygame.image.load('assets/cards/card_black_joker_alt.png')
        card_images[(RANK_JOKER, SUIT_RED_JOKER)] = pygame.image.load('assets/cards/card_red_joker_alt.png')
        continue
    for suit, suit_name in zip(SUITS[:-2], SUIT_NAMES[:-2]):
        card_images[(rank, suit)] = pygame.image.load(f'assets/cards/card_{suit_name}_{rank_name}.png')

for card in card_images:
    card_images[card] = pygame.transform.scale(card_images[card], (CARD_SIZE, CARD_SIZE))


class Card:
    def __init__(self, rank, suit):
        self.rank: int = rank
        self.suit: int = suit
        self.original_image = card_images[(self.rank, self.suit)].convert_alpha()
        self.original_back_image = pygame.image.load('assets/cards/card_back.png').convert_alpha()
        self.original_back_image = pygame.transform.scale(self.original_back_image, (CARD_SIZE, CARD_SIZE))
        self.image = card_images[(self.rank, self.suit)].convert_alpha()

        self.back_image = self.original_back_image.copy()

        self.hovered_image = self.image.copy()
        self.hovered_image.fill((255, 255, 0, 255), special_flags=pygame.BLEND_MULT)

        self.clicked_image = self.image.copy()
        self.clicked_image.fill((0, 255, 0, 255), special_flags=pygame.BLEND_MULT)

        self.rect = self.image.get_rect()
        self.center = self.rect.center

        self.top_left = (int(23 * CARD_SIZE / 128) - CARD_SIZE // 2, int(4 * CARD_SIZE / 128) - CARD_SIZE // 2)
        self.top_right = (int(106 * CARD_SIZE / 128) - CARD_SIZE // 2, int(4 * CARD_SIZE / 128) - CARD_SIZE // 2)
        self.bottom_left = (int(23 * CARD_SIZE / 128) - CARD_SIZE // 2, int(124 * CARD_SIZE / 128) - CARD_SIZE // 2)
        self.bottom_right = (int(106 * CARD_SIZE / 128) - CARD_SIZE // 2, int(124 * CARD_SIZE / 128) - CARD_SIZE // 2)

        self.angle = 0

        self.is_visible = True
        self.is_hoverable = True
        self.is_hovered = False
        self.is_selected = False
        self.is_flipped = False
        self.is_flipping = False
        self.z_index = 10
        self.text = ''
        self.font_color = (0, 0, 0, 0)

    def is_numerical(self):
        return RANK_A <= self.rank <= RANK_10

    def is_face(self):
        return RANK_J <= self.rank <= RANK_JOKER

    def hover(self, x, y):
        if not self.is_hoverable:
            return
        if self.collides_with(x, y):
            self.is_hovered = True
        else:
            self.is_hovered = False

    def click(self, x, y):
        if not self.is_hoverable:
            return
        if self.collides_with(x, y):
            self.is_selected = True
        else:
            self.is_selected = False

    def get_hovered_params(self):
        self.hovered_image = self.image.copy()
        self.hovered_image.fill((255, 255, 0, 255), special_flags=pygame.BLEND_MULT)

        hovered_image = self.hovered_image
        if not self.is_flipped:
            hovered_image = self.back_image.copy()
            hovered_image.fill((255, 255, 0, 255), special_flags=pygame.BLEND_MULT)
        return hovered_image, self.rect, hovered_image, self.rect, self.text

    def get_clicked_params(self):
        self.clicked_image = self.image.copy()
        self.clicked_image.fill((0, 255, 0, 255), special_flags=pygame.BLEND_MULT)

        clicked_image = self.clicked_image
        if not self.is_flipped:
            clicked_image = self.back_image.copy()
            clicked_image.fill((0, 255, 0, 255), special_flags=pygame.BLEND_MULT)
        return clicked_image, self.rect, clicked_image, self.rect, self.text

    def set_at(self, center_x, center_y, angle):
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.back_image = pygame.transform.rotate(self.original_back_image, angle)
        self.rect = self.image.get_rect()
        self.rect.center = center_x, center_y
        self.center = center_x, center_y
        self.angle = angle

    def collides_with(self, x, y):
        if not self.rect.collidepoint(x, y):
            return False

        vertices = [self.top_left, self.top_right, self.bottom_right, self.bottom_left]
        radians = math.radians(self.angle)
        sin, cos = math.sin(radians), math.cos(radians)
        vxs = [cx * cos + cy * sin + self.center[0] for cx, cy in vertices]
        vys = [-cx * sin + cy * cos + self.center[1] for cx, cy in vertices]

        is_inside = False
        j = len(vxs) - 1

        for i in range(len(vxs)):
            if (vys[i] > y) != (vys[j] > y) and x < (vxs[j] - vxs[i]) * (y - vys[i]) / (vys[j] - vys[i]) + vxs[i]:
                is_inside = not is_inside
            j = i

        return is_inside

    def get_image(self):
        return self.image if self.is_flipped else self.back_image

    def set_image(self, image):
        if self.is_flipped:
            self.image = image
        else:
            self.back_image = image

        self.hovered_image = self.get_image().copy()
        self.hovered_image.fill((255, 255, 0, 255), special_flags=pygame.BLEND_MULT)

        self.clicked_image = self.get_image().copy()
        self.clicked_image.fill((0, 255, 0, 255), special_flags=pygame.BLEND_MULT)

    def dump(self):
        return [self]

    def check_if_selected(self):
        return self.is_selected

    def get_selected(self):
        return self

    def __str__(self):
        return f'{RANK_NAMES[self.rank - 1]} {SUIT_NAMES[self.suit - 1]}'


class PlaceholderCard(Card):
    def __init__(self):
        super().__init__(RANK_A, SUIT_CLUBS)
        self.original_back_image = pygame.image.load('assets/cards/card_empty_outline.png').convert_alpha()
        self.original_back_image = pygame.transform.scale(self.original_back_image, (CARD_SIZE, CARD_SIZE))

        self.back_image = self.original_back_image.copy()

        self.original_hovered_image = pygame.image.load('assets/cards/card_empty.png').convert_alpha()
        self.hovered_image = self.original_hovered_image.copy()
        self.hovered_image = pygame.transform.scale(self.hovered_image, (CARD_SIZE, CARD_SIZE))
        self.hovered_image.fill((255, 255, 0, 255), special_flags=pygame.BLEND_MULT)

        self.clicked_image = self.image.copy()
        self.clicked_image.fill((0, 255, 0, 255), special_flags=pygame.BLEND_MULT)

    def get_hovered_params(self):
        return self.hovered_image, self.rect, self.hovered_image, self.rect, self.text

    def set_at(self, center_x, center_y, angle):
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.back_image = pygame.transform.rotate(self.original_back_image, angle)
        self.hovered_image = pygame.transform.scale(self.original_hovered_image, (CARD_SIZE, CARD_SIZE))
        self.hovered_image = pygame.transform.rotate(self.hovered_image, angle)
        self.hovered_image.fill((255, 255, 0, 255), special_flags=pygame.BLEND_MULT)
        self.rect = self.image.get_rect()
        self.rect.center = center_x, center_y
        self.center = center_x, center_y
        self.angle = angle
