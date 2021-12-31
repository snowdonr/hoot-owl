'''
Created on Dec. 12, 2021

@author: Ryan
'''
import unittest
import sys
import collections

from owl import board
from owl import rules


class Test(unittest.TestCase):
    deck = None
    ruleset = None

    def setUp(self):
        self.ruleset = rules.Rules()
        self.deck = board.Deck(self.ruleset)
        self.deck.create()
        self.board = board.Board(self.ruleset)

    def tearDown(self):
        pass

    def test_draw(self):
        ''' Tests if cards can be drawn until None is returned
            with a total size < rules total '''

        counter = 0
        max_count = 50  # TODO: Read rules and calculate
        while True:
            single_card = self.deck.draw_top_card()
            if single_card is None:
                break
            self.assertTrue(isinstance(single_card, board.Card))
            counter += 1
            self.assertFalse(counter > max_count)

    def test_card_count(self):
        ''' Tests if default rules give the correct number of each type of card '''
        card_counter = collections.Counter()
        for single_card in self.deck:
            self.assertTrue(single_card.color in board.CardColors)
            card_counter[single_card.color] += 1
        for this_color in board.CardColors:  # TODO: match statement from python 3.10
            if this_color == board.CardColors.ANY:
                self.assertTrue(card_counter[this_color] <= 1)
            elif this_color == board.CardColors.SUN:
                self.assertTrue(card_counter[this_color] == self.ruleset.number_of_suns)
            else:
                self.assertTrue(card_counter[this_color] == self.ruleset.card_color_multiple)

    def test_retrieve(self):
        for index, single_card in enumerate(self.deck):
            index_card = self.deck[index]
            draw_card = self.deck.draw_top_card()
            self.assertTrue(single_card == index_card)
            self.assertTrue(single_card == draw_card)

    def test_shuffle(self):
        self.deck.shuffle()
        self.test_card_count()
        self.test_retrieve()
        # TODO: Make sure the order is different

    def test_board_init(self):
        for position_list in self.board.path.values():
            self.assertTrue(6 < len(position_list) < 9)
            last_position = -5
            for position in position_list[:-1]:
                self.assertTrue(position-last_position > 2)
                last_position = position

        for index, owl in enumerate(self.board.owls):
            self.assertTrue(owl.position == index)

    def test_board_advance(self):
        test_owl = self.board.owls[0]
        start_position = test_owl.position
        used_positions = []
        for target_color in board.CardColors:
            if target_color is board.CardColors.ANY or target_color is board.CardColors.SUN:
                continue
            example_card = board.Card(target_color)
            prior_position = test_owl.position
            self.board.advance(test_owl, example_card)
            post_position = test_owl.position
            self.assertTrue(post_position > prior_position)  # Does not apply at goal
            self.assertTrue(self.board.color_at(post_position) == target_color)
            self.assertFalse(test_owl.position in used_positions)
            used_positions.append(test_owl.position)
            test_owl.position = start_position  # TODO: Track in the board


    def test_board_skip(self):
        first_owl = self.board.owls[0]
        second_owl = self.board.owls[1]
        # In order to always skip over a position, the rear owl must initally be neighbouring the front owl
        self.assertTrue(first_owl.position-second_owl.position == -1)
        target_color = board.CardColors.ORANGE
        example_card = board.Card(target_color)
        self.board.advance(first_owl, example_card)
        self.board.advance(second_owl, example_card)
        self.assertTrue(first_owl.position < second_owl.position)
        self.assertTrue(self.board.color_at(first_owl.position) == target_color)
        self.assertTrue(self.board.color_at(second_owl.position) == target_color)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()