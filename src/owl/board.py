from __future__ import annotations
import typing
import enum
import random
import collections.abc

import rules


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

    def __init__(self, rules: rules.Rules):
        self.goal_position = None  # value set with path
        self.path = collections.defaultdict(list)  # Index = Color, Value = list of ints
        self.owls = []
        for i in range(rules.number_of_owls):
            self.owls.append(OwlToken(i))
        self.finished_owls = 0
        self.sun_position = 0
        self.startup_path_read_order()

    def startup_path_read_order(self):
        ''' Use the source_order string to setup internal representations '''
        for index, letter in enumerate(self.source_order):
            color_value = self.source_map[letter]
            self.path[color_value].append(index)
        for color_positions in self.path.values():
            color_positions.append(len(self.source_order))
        self.goal_position = len(self.source_order)

    def advance(self, owl: OwlToken, used_card: Card):
        current_position = owl.position
        position_list = self.path[used_card.color]
        for candidate_position in position_list:
            if candidate_position <= current_position:  # TODO: improve linear search if board is large
                continue
            if candidate_position == self.goal_position:
                owl.position = candidate_position
                self.finished_owls += 1
                break  # should be done the loop regardless
            found = False
            for other_owl in self.owls:
                if other_owl.position == candidate_position:
                    found = True
                    break
            if found:  # this space is occupied
                continue
            owl.position = candidate_position  # otherwise update to this spot
            break

    def color_at(self, position: int) -> CardColors | None:
        for color, position_list in self.path.items():
            if position in position_list:
                return color
        return None


class OwlToken(object):
    ''' The items that are moved on the board on each turn '''
    def __init__(self, start_position: int):
        self.position = start_position


class Deck(collections.abc.Sequence):
    ''' Collection of colored cards, amount of each is determined by the rules '''
    def __init__(self, rules: rules.Rules):
        self._rules = rules
        self._position = 0
        self._card_stack = []

    def create(self):
        ''' Build the deck according to the rules provided, with colours grouped and Suns last '''
        rules = self._rules
        for card_type in CardColors:
            if card_type is not CardColors.ANY and card_type is not CardColors.SUN:
                self._card_stack.extend([Card(card_type)]*rules.card_color_multiple)
        self._card_stack.extend([Card(CardColors.SUN)]*rules.number_of_suns)

    def draw_top_card(self) -> Card | None:
        ''' Draw the next card from the deck, or None if empty '''
        if self._position >= len(self._card_stack):
            return None
        result = self._card_stack[self._position]
        self._position += 1
        return result

    def shuffle(self, seed: typing.Optional[int] = None):
        """Reset the deck and randomize the order.

        If `seed` is provided the shuffle will be repeatable (uses a local
        Random instance so it does not alter the global random state).
        """
        self._position = 0
        if seed is None:
            random.shuffle(self._card_stack)
        else:
            rnd = random.Random(seed)
            rnd.shuffle(self._card_stack)

    def __getitem__(self, index: slice[typing.Any, typing.Any, typing.Any] | int) -> typing.Sequence[Card]:
        ''' Does not change the "top card" position '''
        if isinstance(index, slice):
            return self._card_stack[index]
        if isinstance(index, int):
            if abs(index) >= len(self._card_stack):
                raise IndexError(f'No Cards available in deck at point {index}')
            return self._card_stack[index]

    def __len__(self) -> int:
        ''' Total number of cards in the deck, 0 if deck has not been created '''
        return len(self._card_stack)


class Card(object):
    ''' A single playable card, either a SUN card or with the color matching board positions '''
    def __init__(self, color: CardColors):
        self.color = color
