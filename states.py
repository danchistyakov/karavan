from pygame.locals import QUIT, MOUSEBUTTONUP, KEYUP, K_ESCAPE
import graphics
from decks import *
from players import *
import pygame
import random
from itertools import chain

class Context:
    def __init__(self, initial_state=None):
        if initial_state:
            self.state = initial_state
        else:
            from deck_builder import MainMenuState
            self.state = MainMenuState()

    def handle_events(self):
        self.state = self.state.handle_events()

    def is_running(self):
        return self.state.is_running()


class State:
    def __init__(self, objects=None, animations=None, transition=False):
        self.objects: dict[str, Button | Card | Deck | Caravan] = objects if objects else {}
        self.animations: list = animations if animations else []
        self.transition = transition

    def handle_events(self):
        return self

    def is_running(self):
        return True


class StandardMode(State):
    def __init__(self, starting_cards=None, objects=None, animations=None, transition=False):
        super().__init__(objects, animations, transition)

        self.starting_cards = starting_cards
        self.objects['anonymous_button'] = Button(0, 0, 0, 0, is_visible=False)
        # Инициализация караванов
        self.objects['player_1_caravan_A'] = Caravan(player=1, caravan='A')
        self.objects['player_1_caravan_B'] = Caravan(player=1, caravan='B')
        self.objects['player_1_caravan_C'] = Caravan(player=1, caravan='C')
        self.objects['player_2_caravan_A'] = Caravan(player=2, caravan='A')
        self.objects['player_2_caravan_B'] = Caravan(player=2, caravan='B')
        self.objects['player_2_caravan_C'] = Caravan(player=2, caravan='C')
        self.caravan_names = [
            'player_1_caravan_A',
            'player_1_caravan_B',
            'player_1_caravan_C',
            'player_2_caravan_A',
            'player_2_caravan_B',
            'player_2_caravan_C'
        ]

        # Счётчики стоимости караванов
        COUNTER_COLOR = (200, 200, 200)
        self.objects['counter_1_caravan_A'] = Button(
            0, 0, 1, 1, 200, 218, '0', is_clickable=False, z_index=500, is_hoverable=False, font_color=COUNTER_COLOR, color=(0, 0, 0, 0)
        )
        self.objects['counter_1_caravan_B'] = Button(
            0, 0, 1, 1, 400, 218, '0', is_clickable=False, z_index=500, is_hoverable=False, font_color=COUNTER_COLOR, color=(0, 0, 0, 0)
        )
        self.objects['counter_1_caravan_C'] = Button(
            0, 0, 1, 1, 600, 218, '0', is_clickable=False, z_index=500, is_hoverable=False, font_color=COUNTER_COLOR, color=(0, 0, 0, 0)
        )
        self.objects['counter_2_caravan_A'] = Button(
            0, 0, 1, 1, 100, 18, '0', is_clickable=False, z_index=500, is_hoverable=False, font_color=COUNTER_COLOR, color=(0, 0, 0, 0)
        )
        self.objects['counter_2_caravan_B'] = Button(
            0, 0, 1, 1, 300, 18, '0', is_clickable=False, z_index=500, is_hoverable=False, font_color=COUNTER_COLOR, color=(0, 0, 0, 0)
        )
        self.objects['counter_2_caravan_C'] = Button(
            0, 0, 1, 1, 500, 18, '0', is_clickable=False, z_index=500, is_hoverable=False, font_color=COUNTER_COLOR, color=(0, 0, 0, 0)
        )
        self.counter_names = [
            'counter_1_caravan_A',
            'counter_1_caravan_B',
            'counter_1_caravan_C',
            'counter_2_caravan_A',
            'counter_2_caravan_B',
            'counter_2_caravan_C',
        ]

        self.objects['go_back_button'] = Button(10, WINDOW_HEIGHT - 69, 128, 64, text='Выход')

        closed_trash_image = pygame.transform.scale(pygame.image.load('assets/images/trash.png'), (96, 96))
        opened_trash_image = pygame.transform.scale(pygame.image.load('assets/images/trash_open.png'), (96, 96))
        self.objects['trash_button'] = Trash(
            WINDOW_WIDTH - 96, WINDOW_HEIGHT - 96, 96, 96, original_image=closed_trash_image, hovered_image=opened_trash_image
        )

        hand_cards, draw_cards = generate_valid_player_and_drawing_deck()
        self.objects['player_1_playing_deck'] = PlayingDeck(player=1, cards=generate_player_1_hand_cards(8, cards=hand_cards))
        self.objects['drawing_deck'] = DrawingDeck(cards=generate_drawing_deck_1_cards(54, cards=draw_cards))

        hand_cards, draw_cards = generate_valid_player_and_drawing_deck()
        self.objects['player_2_playing_deck'] = PlayingDeck(player=2, cards=generate_player_2_hand_cards(8, cards=hand_cards))
        self.objects['drawing_deck_2'] = DrawingDeck(cards=generate_drawing_deck_2_cards(54, cards=draw_cards))

        # Убрано автоматическое добавление карт в караваны
        # Игрок должен сам добавить по одной карте в каждый караван в начальной фазе

        self.player_1_turn = True
        self.player_1_beginning_phase_counter = 3  # Начальная фаза: игрок должен положить по одной карте в каждый караван
        self.player_2 = RandomPlayer()

        self.animation_cooldown = False
        self.animations.append(self.animation_cooldown_handler())

    def handle_events(self):
        if _check_for_quit():
            return Quit(objects=self.objects, animations=self.animations)

        previously_selected = None
        currently_selected = None

        # Обновление счётчиков стоимости караванов
        for counter_name, caravan_name in zip(self.counter_names, self.caravan_names):
            self.objects[counter_name].text = f'{self.objects[caravan_name].calculate_value()}'

        # Обработка наведения мыши
        x, y = pygame.mouse.get_pos()
        for value in self.objects.values():
            value.hover(x, y)
            if value.check_if_selected():
                previously_selected = value.get_selected()

        # Обработка кликов мыши
        for event in pygame.event.get(MOUSEBUTTONUP):
            x, y = event.pos
            if self.objects['go_back_button'].collides_with(x, y):
                return Quit()
            for value in self.objects.values():
                value.click(x, y)
                if value.check_if_selected():
                    currently_selected = value.get_selected()

        # Проверка победы
        if (player := self.check_winning_condition()) is not None:
            return WinState(
                winner=player,
                objects=self.objects,
                animations=self.animations
            )

        # Ход игрока 1: обработка карты из руки
        player_1_playing_deck: PlayingDeck = self.objects['player_1_playing_deck']
        if previously_selected and player_1_playing_deck.contains(previously_selected) and self.player_1_turn and not self.animation_cooldown:
            # Сброс карты
            if currently_selected == self.objects['trash_button'] and self.player_1_beginning_phase_counter == 0:
                self.player_1_turn = False
                player_1_playing_deck.remove_card(previously_selected)
                self.animations.append(self.respace_player_hand_animation(PlayingDeck(cards=player_1_playing_deck.cards[:])))

                player_1_playing_deck.add_card(self.objects['drawing_deck'].cards[0])
                self.objects['drawing_deck'].cards.pop(0)
                self.animations.append(
                    chain(
                        self.translate_card_animation(previously_selected, -200, random.randint(0, WINDOW_HEIGHT), -500),
                        self.wait_animation(.2),
                        self.flip_over_card_animation(player_1_playing_deck.cards[-1]),
                        self.wait_animation(.2),
                        self.respace_player_hand_animation(player_1_playing_deck)
                    )
                )
                return self
            # Добавление карты в караван
            if currently_selected:
                at_deck = None
                # Ограничиваем выбор караванов текущим игроком
                player_caravans = self.caravan_names[:3] if self.player_1_turn else self.caravan_names[3:]
                for name in player_caravans:
                    if self.objects[name].contains(currently_selected):
                        print(f"Caravan {name} contains currently_selected: {currently_selected}")
                        at_deck = name
                        break
                if at_deck:
                    print(f"Selected caravan: {at_deck}")
                    if self.objects[at_deck].check_if_move_is_valid(previously_selected, currently_selected):
                        if self.player_1_beginning_phase_counter > 0:
                            if len(self.objects[at_deck].layers) > 0:
                                print(f"Cannot add to {at_deck}: already has cards in beginning phase")
                                return self
                            else:
                                self.player_1_beginning_phase_counter = max(self.player_1_beginning_phase_counter - 1, 0)
                                print(f"Beginning phase counter decreased to {self.player_1_beginning_phase_counter}")
                        self.player_1_turn = False
                        player_1_playing_deck.remove_card(previously_selected)
                        self.objects[at_deck].add_card_on(previously_selected, currently_selected)
                        currently_selected.is_selected = False
                        if previously_selected.rank not in [RANK_J, RANK_JOKER]:
                            self.animations.append(chain(
                                self.translate_card_on_top_of_card_animation(previously_selected, currently_selected, self.objects[at_deck]),
                                self.remove_outline_card_of_caravan(self.objects[at_deck])
                            ))
                        elif previously_selected.rank == RANK_J:
                            self.animations.append(chain(
                                self.translate_card_on_top_of_card_animation(previously_selected, currently_selected, self.objects[at_deck]),
                                self.remove_outline_card_of_caravan(self.objects[at_deck]),
                                self.wait_animation(.2),
                                self.activate_jack_card_animation(previously_selected, currently_selected, self.objects[at_deck]),
                                self.wait_animation(.5),
                                self.readjust_caravan_animation(self.objects[at_deck])
                            ))
                        else:
                            self.animations.append(chain(
                                self.translate_card_on_top_of_card_animation(previously_selected, currently_selected, self.objects[at_deck]),
                                self.remove_outline_card_of_caravan(self.objects[at_deck]),
                                self.wait_animation(.2),
                                self.activate_joker_card_animation(previously_selected, currently_selected, [self.objects[name] for name in self.caravan_names]),
                                self.wait_animation(.5),
                                self.readjust_caravans_animation([self.objects[name] for name in self.caravan_names])
                            ))
                        if len(player_1_playing_deck.cards) < 5:
                            player_1_playing_deck.add_card(top_card := self.objects['drawing_deck'].cards[0])
                            self.objects['drawing_deck'].remove_card(top_card)
                            last_animation = self.animations.pop()
                            self.animations.append(self.respace_player_hand_animation(PlayingDeck(cards=player_1_playing_deck.cards[:-1])))
                            self.animations.append(chain(
                                last_animation,
                                self.wait_animation(.2),
                                self.flip_over_card_animation(top_card),
                                self.wait_animation(.2),
                                self.respace_player_hand_animation(player_1_playing_deck)
                            ))
                        else:
                            self.animations.append(self.respace_player_hand_animation(player_1_playing_deck))
                        return self
                    else:
                        print(f"Move is not valid for {at_deck}")
                else:
                    print("No valid caravan contains currently_selected")

        # Сброс каравана
        if any(self.objects[name].contains(previously_selected) for name in self.caravan_names[:3]) and self.player_1_turn and not self.animation_cooldown:
            if currently_selected == self.objects['trash_button'] and self.player_1_beginning_phase_counter == 0:
                self.player_1_turn = False
                caravan = None
                for deck in [self.objects[name] for name in self.caravan_names[:3]]:
                    if deck.contains(previously_selected):
                        caravan = deck
                        break
                for i, card in enumerate(caravan.cards[1:]):
                    caravan.remove_card(card)
                    self.animations.append(self.translate_card_animation(card, -200, random.randint(0, WINDOW_HEIGHT), -500, at_deck=f'anonymous_card_{i}'))
                return self

        # Ход игрока 2 (ИИ)
        if not self.player_1_turn and not self.animation_cooldown:
            self.player_1_turn = True
            move_type, move = self.player_2.select_next_move(self.objects['player_2_playing_deck'], [self.objects[name] for name in self.caravan_names])
            if move_type == DISCARD_CARD:
                card = move
                self.objects['player_2_playing_deck'].remove_card(card)
                self.objects['player_2_playing_deck'].add_card(top_deck_card := self.objects['drawing_deck_2'].cards[0])
                self.objects['drawing_deck_2'].remove_card(top_deck_card)
                self.animations.append(chain(
                    self.flip_over_card_animation(card),
                    self.wait_animation(.2),
                    self.translate_card_animation(card, -200, random.randint(0, WINDOW_HEIGHT), -500),
                    self.wait_animation(.2),
                    self.respace_player_hand_animation(self.objects['player_2_playing_deck'], player=2),
                    self.wait_animation(.2)
                ))
            elif move_type == DISCARD_CARAVAN:
                caravan = move
                for i, card in enumerate(caravan.cards[1:]):
                    caravan.remove_card(card)
                    self.animations.append(self.translate_card_animation(card, -200, random.randint(0, WINDOW_HEIGHT), -500, at_deck=f'anonymous_card_{i}'))
            else:
                card, on_top_of_card, caravan = move
                self.objects['player_2_playing_deck'].remove_card(card)
                caravan.add_card_on(card, on_top_of_card)
                if card.rank not in [RANK_J, RANK_JOKER]:
                    self.animations.append(chain(
                        self.flip_over_card_animation(card),
                        self.wait_animation(.2),
                        self.translate_card_on_top_of_card_animation(card, on_top_of_card, caravan),
                        self.remove_outline_card_of_caravan(caravan)
                    ))
                elif card.rank == RANK_J:
                    self.animations.append(chain(
                        self.flip_over_card_animation(card),
                        self.wait_animation(.2),
                        self.translate_card_on_top_of_card_animation(card, on_top_of_card, caravan),
                        self.remove_outline_card_of_caravan(caravan),
                        self.wait_animation(.2),
                        self.activate_jack_card_animation(card, on_top_of_card, caravan),
                        self.wait_animation(.5),
                        self.readjust_caravan_animation(caravan)
                    ))
                else:
                    self.animations.append(chain(
                        self.flip_over_card_animation(card),
                        self.wait_animation(.2),
                        self.translate_card_on_top_of_card_animation(card, on_top_of_card, caravan),
                        self.remove_outline_card_of_caravan(caravan),
                        self.wait_animation(.2),
                        self.activate_joker_card_animation(card, on_top_of_card, [self.objects[name] for name in self.caravan_names]),
                        self.wait_animation(.5),
                        self.readjust_caravans_animation([self.objects[name] for name in self.caravan_names])
                    ))
                player_2_playing_deck = self.objects['player_2_playing_deck']
                if len(player_2_playing_deck.cards) < 5:
                    player_2_playing_deck.add_card(top_card := self.objects['drawing_deck_2'].cards[0])
                    self.objects['drawing_deck_2'].remove_card(top_card)
                    last_animation = self.animations.pop()
                    self.animations.append(self.respace_player_hand_animation(PlayingDeck(cards=player_2_playing_deck.cards[:-1], player=2), player=2))
                    self.animations.append(chain(
                        last_animation,
                        self.wait_animation(.2),
                        self.respace_player_hand_animation(player_2_playing_deck, player=2)
                    ))
                else:
                    self.animations.append(self.respace_player_hand_animation(player_2_playing_deck, player=2))

        if (player := self.check_winning_condition()) is not None:
            return WinState(
                winner=player,
                objects=self.objects,
                animations=self.animations
            )

        return self

    def translate_card_animation(self, card, cx, cy, angle, at_deck='anonymous_card'):
        curr_x, curr_y = card.center
        curr_angle = card.angle
        animation_speed = 45
        for t in range(animation_speed):
            offset_x = curr_x + (cx - curr_x) * t / (animation_speed - 1)
            offset_y = curr_y + (cy - curr_y) * t / (animation_speed - 1)
            offset_angle = curr_angle + (angle - curr_angle) * t / (animation_speed - 1)
            card.set_at(offset_x, offset_y, offset_angle)
            yield {at_deck: card}

    def flip_over_card_animation(self, card):
        curr_image = card.get_image()
        image_w, image_h = curr_image.get_size()
        animation_speed = 20
        for ts in [range(animation_speed), range(animation_speed, -1, -1)]:
            for t in ts:
                offset_image_w = image_w * (1 - t / animation_speed)
                offset_image_h = image_h * (1 + 0.2 * t / animation_speed)
                offset_image = pygame.transform.scale(curr_image, (offset_image_w, offset_image_h))
                card.z_index = 100
                card.set_image(offset_image)
                yield {'anonymous_card': card}
            if ts == range(animation_speed, -1, -1):
                continue
            card.is_flipped = not card.is_flipped
            card.set_at(*card.center, -card.angle)
            curr_image = card.get_image()

    def respace_player_hand_animation(self, deck, player=1):
        positions = list(deck.respace_cards_positions())
        old_positions = [(*card.center, card.angle) for card in deck.cards]
        animation_speed = 45
        for t in range(animation_speed):
            cards = []
            for i, (card, (x, y, angle), (curr_x, curr_y, curr_angle)) in enumerate(zip(deck.cards, positions, old_positions)):
                offset_x = curr_x + (x - curr_x) * t / (animation_speed - 1)
                offset_y = curr_y + (y - curr_y) * t / (animation_speed - 1)
                offset_angle = curr_angle + (angle - curr_angle) * t / (animation_speed - 1)
                card.set_at(offset_x, offset_y, offset_angle)
                card.z_index = i
                cards.append(card)
            yield {f'player_{player}_playing_deck': PlayingDeck(cards=cards, player=player)}

    def wait_animation(self, seconds):
        for t in range(int(graphics.FPS * seconds)):
            yield {'anonymous_button': self.objects['anonymous_button']}

    def translate_card_on_top_of_card_animation(self, card, on_top_of_card, deck):
        angle = random.randint(-5, 0)
        if deck.cards[0] == on_top_of_card:
            return self.translate_card_animation(card, *on_top_of_card.center, angle)
        if card.is_numerical():
            for layer_card, adjacents in deck.layers:
                if layer_card == on_top_of_card or on_top_of_card in adjacents:
                    return self.translate_card_animation(card, layer_card.center[0], layer_card.center[1] + 40, angle)
        if card.is_face():
            for layer_card, adjacents in deck.layers:
                if layer_card == on_top_of_card or on_top_of_card in adjacents:
                    offset_x = len(adjacents) * 20
                    return self.translate_card_animation(card, layer_card.center[0] + offset_x, layer_card.center[1], angle)

    def remove_outline_card_of_caravan(self, deck):
        if 'Placeholder' in str(type(deck.cards[0])):
            deck.cards[0].is_visible = False
        yield {'anonymous_button': self.objects['anonymous_button']}

    def activate_jack_card_animation(self, card, on_top_of_card, deck):
        layer_card, adjacents = None, None
        for layer_card, adjacents in deck.layers:
            if on_top_of_card == layer_card or on_top_of_card in adjacents:
                break
        deck.remove_card(layer_card)
        cards = [card, layer_card, *adjacents]
        for i, c in enumerate(cards):
            self.animations.append(self.translate_card_animation(c, -200, random.randint(0, WINDOW_HEIGHT), -500, at_deck=f'anonymous_card_{i}'))
        yield {f'anonymous_card_{i}': c for i, c in enumerate(cards)}

    def readjust_caravan_animation(self, deck: Caravan):
        starting_x = {1: 200, 2: 100}
        starting_y = {1: 290, 2: 90}
        offset_x = {'A': 0, 'B': 200, 'C': 400}

        player = deck.player
        caravan = deck.caravan

        for i, (layer_card, adjacents) in enumerate(deck.layers):
            layer_card: Card
            self.animations.append(self.translate_card_animation(layer_card, starting_x[player] + offset_x[caravan], starting_y[player] + 40 * i, layer_card.angle, at_deck=f'{str(deck)}_anonymous_card_{i}'))
            for j, adj in enumerate(adjacents):
                adj: Card
                self.animations.append(self.translate_card_animation(adj, starting_x[player] + offset_x[caravan] + 20 * (j + 1), starting_y[player] + 40 * i, adj.angle, at_deck=f'{str(deck)}_anonymous_card__{i}_{j}'))
        yield {'anonymous_button': self.objects['anonymous_button']}

    def activate_joker_card_animation(self, joker, on_top_of_card, decks: list[Caravan]):
        """
        joker – сам джокер-Card
        on_top_of_card – карта, на которую его положили
        decks – все 6 караванов
        """

        # 1. понимаем, какие карты нужно убрать
        if on_top_of_card.rank == RANK_A:  # режим «по масти»
            def must_remove(card):
                return (card.is_numerical()  # только 2-10
                        and card.rank != RANK_A
                        and card.suit == on_top_of_card.suit)
        else:  # режим «по значению»
            target_rank = on_top_of_card.rank

            def must_remove(card):
                return (card.is_numerical()
                        and card.rank == target_rank
                        and card is not on_top_of_card)  # свой «хозяин» не трогаем

        # 2. собираем жертвы (числовая + все прикреплённые к ней картинки)
        victims: list[Card] = []
        for deck in decks:
            # делаем копию итерации, т.к. будем модифицировать layers
            for layer_card, adjacents in deck.layers[:]:
                if must_remove(layer_card):
                    deck.remove_card(layer_card)  # правит value/suit/direction
                    victims.append(layer_card)
                    victims.extend(adjacents)

        # 3. красиво улетаем за экран
        for i, c in enumerate(victims):
            self.animations.append(
                self.translate_card_animation(
                    c, -200, random.randint(0, WINDOW_HEIGHT), -500,
                    at_deck=f'anonymous_card_{i}'
                )
            )

        # 4. отдаём генератору фиктивный кадр, чтобы анимации попали в очередь
        yield {'anonymous_button': self.objects['anonymous_button'],
               **{f'anonymous_card_{i}': c for i, c in enumerate(victims)}}

    def readjust_caravans_animation(self, decks):
        for deck in decks:
            self.animations.append(self.readjust_caravan_animation(deck))
        yield {'anonymous_button': self.objects['anonymous_button']}

    def animation_cooldown_handler(self):
        while True:
            self.animation_cooldown = True
            if len(self.animations) == 1:
                self.animation_cooldown = False
                for key in list(self.objects.keys()):
                    if 'anonymous' in key and 'button' not in key:
                        del self.objects[key]
                for name in self.caravan_names:
                    self.objects[name].update()
            yield {'anonymous_button': self.objects['anonymous_button']}

    def check_winning_condition(self):
        """Возвращает 1, 2 или None (игра продолжается) по официальным правилам Fallout: New Vegas."""

        p1_caravans = [self.objects[name] for name in self.caravan_names[:3]]
        p2_caravans = [self.objects[name] for name in self.caravan_names[3:]]

        p1_values = [c.calculate_value() for c in p1_caravans]
        p2_values = [c.calculate_value() for c in p2_caravans]

        p1_wins = 0
        p2_wins = 0
        draws = 0

        for v1, v2 in zip(p1_values, p2_values):
            in_range1 = 21 <= v1 <= 26
            in_range2 = 21 <= v2 <= 26

            if in_range1 and not in_range2:
                p1_wins += 1
            elif in_range2 and not in_range1:
                p2_wins += 1
            elif in_range1 and in_range2:
                if v1 > v2:
                    p1_wins += 1
                elif v2 > v1:
                    p2_wins += 1
                else:
                    draws += 1  # ничья

        if p1_wins >= 2:
            return 1
        if p2_wins >= 2:
            return 2

        # если у обоих игроков по два проданных каравана
        if p1_wins + draws >= 2 and p2_wins + draws >= 2:
            # ничья по проданным караванам — продолжаем игру
            return None

        return None

    def _compare(self, p1, p2):
        # Ничья по какому-либо каравану — продолжаем
        if any(a == b for a, b in zip(p1, p2)):
            return None

        # Подсчёт побед по каждому из трёх караванов
        p1_wins = 0
        for a, b in zip(p1, p2):
            if b > 26:
                p1_wins += 1
            elif (21 <= a <= 26) and ((26 - a) < (26 - b)):
                p1_wins += 1

        return 1 if p1_wins >= 2 else 2

class Quit(State):
    def __init__(self, objects=None, animations=None, transition=False):
        super().__init__(objects, animations, transition)

    def handle_events(self):
        raise NotImplemented('Quit state should not be handling events.')

    def is_running(self):
        return False


def _check_for_quit():
    if len(pygame.event.get(eventtype=QUIT)) > 0:
        return True
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            return True
        pygame.event.post(event)
    return False


class Button:
    def __init__(self, left, top, width, height, center_x=None, center_y=None, text='', is_clickable=True,
                 is_hovered=False, is_visible=True, z_index=0, is_hoverable=True, font_size=40, font_color=(0, 0, 0), color=(255, 255, 255, 255),
                 original_image=None, hovered_image=None):
        if original_image:
            self.original_image = original_image
            self.image = original_image.copy()
        else:
            self.original_image = pygame.transform.scale(pygame.image.load('assets/images/button.png'), (width, height)).convert_alpha()
            self.image = pygame.transform.scale(pygame.image.load('assets/images/button.png'), (width, height)).convert_alpha()

        self.rect = pygame.Rect(left, top, width, height)
        if center_x and center_y:
            self.rect.center = (center_x, center_y)
        self.center = self.rect.center
        self.text = text
        self.font_size = font_size
        self.font_color = font_color
        self.default_font_color = font_color

        if hovered_image:
            self.hovered_image = hovered_image
        else:
            self.hovered_image = self.image.copy()

        self.is_clickable = is_clickable
        self.is_hoverable = is_hoverable
        self.is_hovered = is_hovered
        self.is_visible = is_visible
        self.z_index = z_index
        self.is_selected = False

    def update(self, scale: tuple[int, int] | None = None, rect: pygame.Rect | None = None,
               center: tuple[float, float] | None = None):
        if scale:
            self.image = pygame.transform.scale(self.image, scale)
            w, h = self.image.get_size()
            self.hovered_image = pygame.Surface((w + 10, h + 10)).convert_alpha()
            self.hovered_image.fill((255, 255, 0, 255))
        if rect:
            self.rect = rect
        if center:
            self.rect.center = center
        self.center = self.rect.center

    def get_hovered_params(self):
        hovered_image_rect = self.hovered_image.get_rect()
        hovered_image_rect.center = self.rect.center
        return self.hovered_image, hovered_image_rect, self.image, self.rect, self.text

    def get_clicked_params(self):
        hovered_image_rect = self.hovered_image.get_rect()
        hovered_image_rect.center = self.rect.center
        return self.hovered_image, hovered_image_rect, self.image, self.rect, self.text

    def hover(self, x, y):
        if self.rect.collidepoint(x, y) and self.is_hoverable:
            self.is_hovered = True
            self.font_color = (255, 255, 255)
        else:
            self.is_hovered = False
            self.is_selected = False
            self.font_color = self.default_font_color

    def click(self, x, y):
        if self.rect.collidepoint(x, y):
            self.is_selected = True
        else:
            self.is_selected = False

    def get_image(self):
        return self.image

    def collides_with(self, x, y):
        return self.rect.collidepoint(x, y)

    def dump(self):
        return [self]

    def check_if_selected(self):
        return self.is_selected

    def get_selected(self):
        return self


class Trash(Button):
    def get_hovered_params(self):
        hovered_image_rect = self.hovered_image.get_rect()
        hovered_image_rect.center = self.rect.center
        return self.hovered_image, hovered_image_rect, self.hovered_image, hovered_image_rect, self.text

    def hover(self, x, y):
        if self.rect.collidepoint(x, y) and self.is_hoverable:
            self.is_hovered = True
            self.font_color = (255, 255, 255)
            self.image = self.hovered_image
        else:
            self.is_hovered = False
            self.is_selected = False
            self.font_color = self.default_font_color
            self.image = self.original_image
class WinState(State):
    def __init__(self, winner, **kwargs):
        super().__init__(**kwargs)
        self.winner = winner
        self.objects['exit_button'] = Button(
            left=WINDOW_WIDTH // 2 - 64, top=WINDOW_HEIGHT // 2 + 50,
            width=128, height=64, text='Выход'
        )
        self.banner = pygame.image.load(
            'assets/images/win_banner.png' if winner == 1
            else 'assets/images/lose_banner.png'
        ).convert_alpha()
        # масштабируем по ширине окна (не обязательно)
        bw, bh = self.banner.get_size()
        if bw > WINDOW_WIDTH * 0.8:
            ratio = (WINDOW_WIDTH * 0.8) / bw
            self.banner = pygame.transform.smoothscale(
                self.banner, (int(bw * ratio), int(bh * ratio))
            )

    def handle_events(self):
        x, y = pygame.mouse.get_pos()
        for obj in self.objects.values():
            obj.hover(x, y)

        for event in pygame.event.get(MOUSEBUTTONUP):
            x, y = event.pos
            for obj in self.objects.values():
                obj.click(x, y)
                if obj.check_if_selected():
                    return Quit()

        return self

    def is_running(self):
        return True
