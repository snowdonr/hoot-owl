from __future__ import annotations
import typing
import enum
import random
import numpy
import collections.abc

from . import rules
from . import player


class CardColors(enum.Enum):
    ''' 
    The types of card that can be drawn from the deck, with ANY as a wildcard
    for future flexibility

    TODO: The ANY and SUN cards are not standard positions, but using enum
    limits options here. A refactor to split the special cases could be useful'''
    ANY = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()
    ORANGE = enum.auto()
    BLUE = enum.auto()
    PURPLE = enum.auto()
    RED = enum.auto()
    SUN = enum.auto()


class Board(object):
    ''' Handles the state/position of the game elements, success and failure '''
    source_order = "ygobprbprygborpygobprgyobprygborpygborp"  # Path, colors in slightly randomized groups
    source_map = {"y": CardColors.YELLOW, "g": CardColors.GREEN, "o": CardColors.ORANGE,
                  "b": CardColors.BLUE, "p": CardColors.PURPLE, "r": CardColors.RED}

    def __init__(self, ruleset: rules.Rules, add_deck=True, add_players=True, no_sun_cards=True):
        self.rules = ruleset
        self.goal_position = None  # value set with path
        self.players = []
        self.path = collections.defaultdict(list)  # Index = Color, Value = list of ints
        self.owls = []
        for i in range(ruleset.number_of_owls):
            self.owls.append(OwlToken(i))
        if add_deck:
            self._startup_create_deck(no_sun_cards)
        else:
            self.deck = None
        if add_players:
            self._startup_add_players()
        self.finished_owls = 0
        self.sun_position = 0
        self._startup_path_read_order()

    def _startup_create_deck(self, no_sun_cards: bool):
        self.deck = Deck(self.rules)
        self.deck.create(no_sun_cards=no_sun_cards)
        self.deck.shuffle()
    
    def _startup_add_players(self):
        for i in range(self.rules.player_count):
            new_player = player.Player(self, self.rules)
            new_player.hand.draw_up()
            self.players.append(new_player)

    def _startup_path_read_order(self):
        ''' Use the source_order string to setup internal representations '''
        for index, letter in enumerate(self.source_order):
            color_value = self.source_map[letter]
            self.path[color_value].append(index)
        for color_positions in self.path.values():
            color_positions.append(len(self.source_order))
        self.goal_position = len(self.source_order)

    def status_count(self):
        ''' Track how close we are to finishing (the total position of all owls) 
        Only directly comparable with equivalent rules
        '''
        return sum([o.position for o in self.owls])

    def is_finished(self):
        return numpy.all([o.position==self.goal_position for o in self.owls])

    def advance(self, owl: OwlToken, used_card: Card):
        current_position = owl.position
        position_list = self.path[used_card.color]
        for position in position_list:
            if position <= current_position:  # TODO: improve linear search if board is large
                continue
            if position == self.goal_position:
                owl.position = position
                self.finished_owls += 1
                break  # should be done the loop regardless
            found = False
            for other_owl in self.owls:
                if other_owl.position == position:
                    found = True
                    break
            if found:  # this space is occupied
                continue
            owl.position = position  # otherwise update to this spot
            break

    def color_at(self, position: int) -> typing.Optional(CardColors):
        for color, position_list in self.path.items():
            if position in position_list:
                return color
        return None


class OwlToken(object):
    ''' The items that a moved on the board on each turn '''
    def __init__(self, start_position: int):
        self.position = start_position


class Deck(collections.abc.Sequence):
    ''' Collection of colored cards, amount of each is determined by the rules '''
    def __init__(self, rules: rules.Rules):
        self._rules = rules
        self._position = 0
        self._card_stack = []

    def create(self, no_sun_cards=False):
        rules = self._rules
        for card_type in CardColors:
            if card_type is not CardColors.ANY and card_type is not CardColors.SUN:
                self._card_stack.extend([Card(card_type)]*rules.card_color_multiple)
        if not no_sun_cards:
            self._card_stack.extend([Card(CardColors.SUN)]*rules.number_of_suns)

    def draw_top_card(self) -> Card:
        if self._position >= len(self._card_stack):
            return None
        result = self._card_stack[self._position]
        self._position += 1
        return result

    def shuffle(self):
        self._position = 0
        random.shuffle(self._card_stack)

    def __getitem__(self, index: int) -> Card:
        ''' Does not change the "top card" position '''
        if index >= len(self._card_stack):
            raise IndexError('No more cards in deck')
        return self._card_stack[index]

    def __len__(self) -> int:
        return len(self._card_stack)


class Card(object):
    ''' A single playable card, either a SUN card or with the color matching board positions '''
    def __init__(self, color: CardColors):
        self.color = color
