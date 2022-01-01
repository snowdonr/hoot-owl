'''
@author snowdonr
'''
from __future__ import annotations
import enum
import random
import numpy

from . import rules
from . import board


class Player(object):
    ''' State related to a single player position in the game, with a hand and strategy'''
    
    def __init__(self, setup_board: board.Board, setup_rules: rules.Rules):
        self.board = setup_board
        self.rules = setup_rules
        self.strategy = Strategy()
        self.hand = Hand(setup_board.deck, setup_rules)
        self.strategy_card_lookup = {CardChoice.random: self._get_random_card}
        self.strategy_owl_lookup = {OwlChoice.always_last: self._get_last_owl}

    def do_turn(self):
        owl_choice = self.strategy_owl_lookup[self.strategy.owl_choice_type]
        card_choice = self.strategy_card_lookup[self.strategy.card_choice_type]
        selected_owl = owl_choice()
        selected_card = card_choice()
        self.board.advance(selected_owl, selected_card)

    def _get_random_card(self):
        return random.choice(self.hand.cards)

    def _get_last_owl(self):
        owl_index = numpy.argmin([owl.position for owl in self.board.owls])
        return self.board.owls[owl_index]


class Hand(object):
    ''' '''
    def __init__(self, setup_deck: board.Deck, setup_rules: rules.Rules):
        self.size = 3  # duplicate cards and altered rules means we can't rely on this value when iterating
        self.cards = []
        self.deck = setup_deck

    def play_card(self, card):
        self.cards.remove(card)
        self.draw_up()

    def draw_up(self):
        while(len(self.cards) <= self.size):
            new_card = self.deck.draw_top_card()
            if new_card is None:
                break
            self.cards.append(new_card)


class CardChoice(enum.Enum):
    random = enum.auto()
    most_common = enum.auto()
    furthest = enum.auto()


class OwlChoice(enum.Enum):
    random = enum.auto()
    always_the_same = enum.auto()
    always_last = enum.auto()
    always_furthest = enum.auto()


class Strategy(object):
    ''' Container for which card and owl to use on any given turn for a specific player '''
    def __init__(self):
        self.card_choice_type = CardChoice.random
        self.owl_choice_type = OwlChoice.always_last
