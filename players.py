import random

from decks import PlayingDeck, Caravan


DISCARD_CARD = 0
DISCARD_CARAVAN = 1
PLAY_CARD = 2


class Player:
    def __init__(self, player=2):
        self.player = player
        self.beginning_phase_counter = 3

    def find_possible_moves(self, playing_deck: PlayingDeck, caravans: Caravan):
        possibilities = {
            DISCARD_CARD: playing_deck.cards,  # List of cards
            DISCARD_CARAVAN: [],  # List of non-empty owned caravans
            PLAY_CARD: []  # List of tuples of the form: (card, on_top_of_card, deck)
        }
        player_caravans = caravans[:3] if self.player == 1 else caravans[3:]

        for caravan in player_caravans:
            if caravan.layers:
                possibilities[DISCARD_CARAVAN].append(caravan)

        for card in playing_deck.cards:
            if card.is_numerical():
                for caravan in player_caravans:
                    on_top_of_card = caravan.cards[0]
                    if caravan.layers:
                        on_top_of_card = caravan.layers[-1][0]
                    if caravan.check_if_move_is_valid(card, on_top_of_card):
                        possibilities[PLAY_CARD].append((card, on_top_of_card, caravan))
            if card.is_face():
                for caravan in caravans:
                    for on_top_of_card in caravan.cards[1:]:
                        if caravan.check_if_move_is_valid(card, on_top_of_card):
                            possibilities[PLAY_CARD].append((card, on_top_of_card, caravan))

        return possibilities


class RandomPlayer(Player):
    def __init__(self, player=2):
        super().__init__(player)

    def select_next_move(self, playing_deck: PlayingDeck, caravans: Caravan):
        possibilities = self.find_possible_moves(playing_deck, caravans)

        if self.beginning_phase_counter > 0:
            self.beginning_phase_counter -= 1
            return self.select_next_move_in_beginning_phase(possibilities[PLAY_CARD])

        r = random.random()
        if r < 0.95 and possibilities[PLAY_CARD]:
            return PLAY_CARD, random.choice(possibilities[PLAY_CARD])
        elif r < 0.99 and possibilities[DISCARD_CARD]:
            return DISCARD_CARD, random.choice(possibilities[DISCARD_CARD])
        elif possibilities[DISCARD_CARAVAN]:
            return DISCARD_CARAVAN, random.choice(possibilities[DISCARD_CARAVAN])
        else:
            if possibilities[PLAY_CARD]:
                return PLAY_CARD, random.choice(possibilities[PLAY_CARD])
            else:
                return DISCARD_CARD, random.choice(possibilities[DISCARD_CARD])

    def select_next_move_in_beginning_phase(self, possibilities):
        result = []

        for card, on_top_of_card, caravan in possibilities:
            if card.is_numerical() and not caravan.layers:
                result.append((card, on_top_of_card, caravan))

        return PLAY_CARD, random.choice(result)
