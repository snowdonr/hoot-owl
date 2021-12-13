'''
@author snowdonr
'''
import enum


class Player(object):
    ''' State related to a single player position in the game, with a hand and strategy'''
    def __init__(self):
        self.strategy = Strategy()
        self.hand = Hand()

    def do_turn(self, board):
        return update


class Hand(object):
    ''' '''
    def __init__(self):
        self.size = 3  # duplicate cards and altered rules means we can't rely on this value when iterating
        self.cards = []


class ColorChoice(enum.Enum):
    random = enum.auto()
    most_common = enum.auto()
    furthest = enum.auto()


class OwlChoice(enum.Enum):
    random = enum.auto()
    always_last = enum.auto()
    always_furthest = enum.auto()


class Strategy(object):
    ''' Which card and owl to use on any given turn for a specific player '''
    def __init__(self):
        self.card_choice_type = ColorChoice.random
        self.owl_choice_type = OwlChoice.random
