'''
Created on Dec. 30, 2021

@author: Ryan
'''
import unittest

from owl import board
from owl import rules


class Test(unittest.TestCase):
    ruleset = None

    def setUp(self):
        self.ruleset = rules.Rules()
        self.deck = board.Deck(self.ruleset)
        self.deck.create()
        self.board = board.Board(self.ruleset, no_sun_cards=True)

    def tearDown(self):
        pass

    def test_play(self):
        turn_counter = 0
        while not self.board.is_finished():
            for selected_player in self.board.players:
                selected_player.do_turn()
                turn_counter += 1
                if turn_counter > 1000:
                    self.assertTrue(False)
                    return
        print(f"Count: {turn_counter}")

    def test_status(self):
        last_status = self.board.status_count()
