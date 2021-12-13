import enum
import random


class Board(object):
    ''' Handles the state/position of the game elements, success and failure '''
    path = []
    def __init__(self):
        self.positions = []


class Deck(collections.Sequence):
    def __init__(self, rules):
        self._rules = rules
        self._position = 0
        self._card_stack = []

    def create(self):
        rules = self._rules
        for card_type in CardColors:
            if card_type is not CardColors.ANY and card_type is not CardColors.SUN:
                self._card_stack.extend(Card(card_type)*rules.card_color_multiple)
        self._card_stack.extend(Card(CardColors.SUN)*rules.number_of_suns)

    def get_top_card(self):
        if self._position >= len(self._card_stack):
            return None
        result = self._card_stack[self._position]
        self._position += 1
        return result

    def shuffle(self):
        self._position = 0
        random.shuffle(self._card_stack)

    def __getitem__(self, index):
        ''' Does not change the "top card" position '''
        return self._card_stack[index]

    def __len__(self):
        return len(self._card_stack)




class Card(object):
    def __init__(self, color):
        self._color = color


class CardColors(enum.Enum):
    ANY = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()
    ORANGE = enum.auto()
    BLUE = enum.auto()
    PURPLE = enum.auto()
    RED = enum.auto()
    SUN = enum.auto()
