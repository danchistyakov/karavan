from cards import *
from graphics import WINDOW_WIDTH, WINDOW_HEIGHT
import numpy as np
import random

DESC = -1
UNDEFINED = 0
ASC = 1

MIN_CARAVAN_THRESHOLD = 21
MAX_CARAVAN_THRESHOLD = 26


class Deck:
    def __init__(self, cards):
        self.cards: list[Card] = cards

        self.is_hoverable = True

    def add_card(self, card):
        if self.cards:
            card.z_index = max(self.cards[-1].z_index + 1, card.z_index)
        self.cards.append(card)

    def contains(self, card):
        return any(card == s_card for s_card in self.cards)

    def remove_card(self, card):
        if self.contains(card):
            self.cards.remove(card)

    def hover(self, x, y):
        for card in self.cards:
            card.hover(x, y)

    def click(self, x, y):
        for reset_card in self.cards:
            reset_card.is_selected = False

        z_cards = sort_cards_by_z_index(self.cards)
        for card in z_cards:
            if card.collides_with(x, y) and card.is_hoverable:
                card.click(x, y)
                break

    def check_if_selected(self):
        return any(card.is_selected for card in self.cards)

    def get_selected(self):
        for card in self.cards:
            if card.is_selected:
                return card

    def dump(self):
        return self.cards


def sort_cards_by_z_index(cards: list[Card]):
    return list(sorted(cards, key=lambda card: card.z_index, reverse=True))


class PlayingDeck(Deck):
    def __init__(self, player=1, cards=None):
        self.player = player
        if cards is None:
            if self.player == 1:
                cards = generate_player_1_hand_cards(8)
            else:
                cards = generate_player_2_hand_cards(8)
        super().__init__(cards)

        self.is_selected = False

    def add_card(self, card):
        super().add_card(card)
        card.is_hoverable = True

    def respace_cards_positions(self):
        if self.player == 1:
            return generate_player_1_hand_card_positions(len(self.cards))
        if self.player == 2:
            return generate_player_2_hand_card_positions(len(self.cards))


class DrawingDeck(Deck):
    def __init__(self, cards=None):
        if not cards:
            cards = generate_drawing_deck_1_cards(30)
        super().__init__(cards)

        self.is_selected = False


def generate_all_cards():
    return ([Card(rank, suit) for rank in RANKS[:-1] for suit in SUITS[:-2]] +
            [Card(RANK_JOKER, SUIT_BLACK_JOKER), Card(RANK_JOKER, SUIT_RED_JOKER)])


def generate_random_cards(num_cards=None):
    deck = generate_all_cards()
    assert num_cards <= len(deck)
    random.shuffle(deck)
    return deck[:num_cards]


def generate_player_1_hand_cards(num_cards: int = 5, cards=None):
    if cards:
        deck = cards
    else:
        deck = generate_random_cards(num_cards)

    positions = generate_player_1_hand_card_positions(num_cards)
    res = []
    for i, (x, y, angle) in enumerate(positions):
        card = deck[i]
        card.set_at(x, y, angle)
        card.is_flipped = True
        card.z_index = i
        res.append(card)

    return res


def generate_player_2_hand_cards(num_cards: int = 5, cards=None):
    if cards:
        deck = cards
    else:
        deck = generate_random_cards(num_cards)

    positions = generate_player_2_hand_card_positions(num_cards)
    res = []
    for i, (x, y, angle) in enumerate(positions):
        card = deck[i]
        card.set_at(x, y, angle)
        card.is_flipped = False
        card.z_index = i
        res.append(card)

    return res


def generate_player_1_hand_card_positions(num_cards: int = 5):
    if num_cards == 0:
        return []
    if num_cards == 1:
        return [(WINDOW_WIDTH - 50, WINDOW_HEIGHT - 175, 0)]
    x_coords = list(np.linspace(WINDOW_WIDTH - 250, WINDOW_WIDTH - 50, num_cards))
    unit_x_coords = list(np.linspace(25, 225, num_cards))
    unit_y_coords = list(map(lambda x: -np.sqrt(150 ** 2 * (1 - 1 / (225 ** 2) * (x - 225) ** 2)), unit_x_coords))
    offset_x, offset_y = WINDOW_WIDTH - 50 - unit_x_coords[-1], WINDOW_HEIGHT - 175 - unit_y_coords[-1]
    y_coords = list(map(lambda y: y + offset_y, unit_y_coords))
    angles = [40 * (num_cards - 1 - i) / (num_cards - 1) for i in range(num_cards)]
    return list(zip(x_coords, y_coords, angles))


def generate_player_2_hand_card_positions(num_cards: int = 5):
    if num_cards == 0:
        return []
    if num_cards == 1:
        return [(WINDOW_WIDTH - 50, 175, 0)]
    x_coords = list(np.linspace(WINDOW_WIDTH - 250, WINDOW_WIDTH - 50, num_cards))
    unit_x_coords = list(np.linspace(25, 225, num_cards))
    unit_y_coords = list(map(lambda x: -np.sqrt(150 ** 2 * (1 + 1 / (225 ** 2) * (x - 225) ** 2)), unit_x_coords))
    offset_x, offset_y = WINDOW_WIDTH - 50 - unit_x_coords[-1], 175 - unit_y_coords[-1]
    y_coords = list(map(lambda y: y + offset_y - 25, unit_y_coords))
    angles = [-40 * (num_cards - 1 - i) / (num_cards - 1) for i in range(num_cards)]
    return list(zip(x_coords, y_coords, angles))


def generate_drawing_deck_1_cards(num_cards: int = 52, cards: list[Card] = None):
    if not cards:
        cards = generate_random_cards(num_cards)
    for i, card in enumerate(cards):
        card.set_at(WINDOW_WIDTH - 80 - 3 * i / num_cards, WINDOW_HEIGHT // 2, 3 * i / num_cards)
        card.is_flipped = False
        card.is_hoverable = True
        card.z_index = -i - 1
    return cards


def generate_drawing_deck_2_cards(num_cards: int = 52, cards: list[Card] = None):
    if not cards:
        cards = generate_random_cards(num_cards)
    for i, card in enumerate(cards):
        card.set_at(WINDOW_WIDTH - 200 + 3 * i / num_cards, WINDOW_HEIGHT // 2, 3 * i / num_cards)
        card.is_flipped = False
        card.is_hoverable = True
        card.z_index = -i - 1
    return cards


class Caravan(Deck):
    def __init__(self, player=1, caravan='A'):
        super().__init__(cards=generate_starting_caravan(player=player, caravan=caravan))
        self.player = player
        self.caravan = caravan
        self.layers: list[list[Card, list[Card]]] = []
        self.value = 0
        self.suit = UNDEFINED
        self.direction = UNDEFINED

    def calculate_value(self):
        return sum([card.rank * 2 ** len([card for card in adjacents if card.rank == RANK_K]) for card, adjacents in self.layers])

    def calculate_suit(self):
        if not self.layers:
            return UNDEFINED
        card, adjacents = self.layers[-1]
        suit = card.suit
        for adj in adjacents:
            if adj.rank == RANK_Q:
                suit = adj.suit
        return suit

    def calculate_direction(self):
        if len(self.layers) <= 1:
            return UNDEFINED
        card_1 = self.layers[-2][0]
        card_2, adjacents = self.layers[-1]
        if card_1.rank >= card_2.rank:
            direction = DESC  # Yes, if the last two cards have the same rank, FNV considers the caravan as decreasing
        else:
            direction = ASC
        for adj in adjacents:
            if adj.rank == RANK_Q:
                direction *= -1
        return direction

    def add_card_on(self, card: Card, on_top_of_card: Card):
        if not self.layers:
            self.cards[0].is_hoverable = False
            self.cards[0].is_hovered = False
            self.cards[0].is_selected = False
        else:
            self.cards[0].is_visible = False

        self.cards.append(card)

        if card.is_numerical():
            self.layers.append([card, []])
            self.value += card.rank
        if card.is_face():
            for i, (layer_card, adjacents) in enumerate(self.layers):
                if layer_card == on_top_of_card or on_top_of_card in adjacents:
                    adjacents.append(card)
                    break
        self.update()

    def check_if_move_is_valid(self, card: Card, on_top_of_card: Card):
        if card.is_numerical():
            if len(self.layers) == 0:
                return True  # Numerical card can be placed on an empty caravan
            elif len(self.layers) >= 7:
                return False  # Numerical card can't be placed on a caravan with max capacity
            elif (layer_card := self.layers[-1][0]) == on_top_of_card or on_top_of_card in self.layers[-1][1]:
                if (
                        (layer_card.rank > card.rank and self.direction != ASC)
                        or (layer_card.rank < card.rank and self.direction != DESC)
                ):
                    return True  # Numerical card follows caravan order (direction) and can be placed on the caravan
                elif card.suit == self.suit and card.rank != layer_card.rank:
                    return True  # Numerical card matches the suit of the caravan and can be placed on it
                else:
                    return False  # Numerical card can't be placed on caravan as it doesn't follow caravan order (direction) nor matches the caravan suit
            else:
                return False  # Numerical card can't be placed in the middle of the deck, must be placed as the last card
        if card.is_face():
            for layer_card, adjacents in self.layers:
                if on_top_of_card == layer_card or on_top_of_card in adjacents:
                    if len(adjacents) >= 3 and card.rank != RANK_J:
                        return False  # Face card can't be placed on selected card with max capacity of face cards
                    return True  # Face card can be placed on selected card
        return False  # Face card can't be placed on an empty caravan

    def update(self):
        for i, (layer_card, adjacents) in enumerate(self.layers):
            layer_card.z_index = i * 5
            for j, adj in enumerate(adjacents):
                adj.z_index = i * 5 + j + 1
        if len(self.cards) == 1:
            self.cards[0].is_visible = True
            self.cards[0].is_hoverable = True
            self.cards[0].is_flipped = False
        self.value = self.calculate_value()
        self.suit = self.calculate_suit()
        self.direction = self.calculate_direction()

    def remove_card(self, card):
        for i, (layer_card, adjacents) in enumerate(self.layers):
            if card == layer_card or card in adjacents:
                self.layers.pop(i)
                self.cards.remove(layer_card)
                for adj in adjacents:
                    self.cards.remove(adj)
                break
        self.update()
    
    def click(self, x, y):
        for reset_card in self.cards:
            reset_card.is_selected = False

        z_cards = sort_cards_by_z_index(self.cards)
        for card in z_cards:
            if card.collides_with(x, y) and card.is_hoverable:
                card.click(x, y)
                break
        self.update()


def generate_starting_caravan(player: int = 1, caravan: str = 'A'):
    starting_x = {1: 200, 2: 100}
    starting_y = {1: 290, 2: 90}
    offset_x = {'A': 0, 'B': 200, 'C': 400}

    cards = [PlaceholderCard()]
    cards[0].is_hoverable = True
    cards[0].is_flipped = False
    cards[0].set_at(starting_x[player] + offset_x[caravan], starting_y[player], 0)
    cards[0].z_index = -10
    return cards


def generate_valid_player_and_drawing_deck(num_cards: int = 54):
    cards = generate_all_cards()[:num_cards]
    numeric = list(random.sample(cards[:40], 3))
    cards = [card for card in cards if card not in numeric]
    random.shuffle(cards)
    res = numeric + cards[:5], cards[5:]

    return res
